#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

def find_cjk_font():
    # 优先使用 fc-list 查找系统安装的 CJK 字体
    try:
        out = subprocess.check_output(["fc-list", ":lang=zh", "file"], text=True)
        for line in out.splitlines():
            path = line.split(":")[0].strip()
            if os.path.exists(path):
                return path
    except Exception:
        pass

    candidates = [
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    raise FileNotFoundError("未找到中文字体，请先执行 apt-get install -y fonts-wqy-zenhei 或 fonts-noto-cjk")

def render_char_16x16(font, ch):
    img = Image.new("1", (16, 16), 0)
    draw = ImageDraw.Draw(img)
    try:
        bbox = draw.textbbox((0, 0), ch, font=font)
        y_off = -1 if bbox[3] > 16 else 0
    except Exception:
        y_off = 0
    draw.text((0, y_off), ch, fill=1, font=font)
    data = []
    for y in range(16):
        b0 = 0
        b1 = 0
        for x in range(8):
            if img.getpixel((x, y)):
                b0 |= (0x80 >> x)
            if img.getpixel((x + 8, y)):
                b1 |= (0x80 >> x)
        data.append(b0)
        data.append(b1)
    return data

def dump_range(f, array_name, start_cp, end_cp, font):
    count = end_cp - start_cp + 1
    f.write(f"// Range U+{start_cp:04X} .. U+{end_cp:04X} ({count} chars)\n")
    f.write(f"const unsigned char {array_name}[{count * 32}] = {{\n")
    for cp in range(start_cp, end_cp + 1):
        raw = render_char_16x16(font, chr(cp))
        hex_str = ",".join(f"0x{b:02X}" for b in raw)
        f.write(f"    {hex_str},\n")
    f.write("};\n\n")

def main():
    font_path = find_cjk_font()
    print(f"Using font: {font_path}")
    font = ImageFont.truetype(font_path, 14)

    out_path = os.path.join("src", "font_chs.c") if os.path.isdir("src") else "font_chs.c"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("// Auto-generated full CJK 16x16 bitmap font\n\n")
        # 1. CJK 标点符号 + 日文平假名/片假名 (U+3000..U+30FF, 256 字)
        dump_range(f, "chs_sym_glyphs", 0x3000, 0x30FF, font)
        # 2. 全角 ASCII 与中文全角标点 ()！：？ (U+FF00..U+FF5E, 95 字)
        dump_range(f, "chs_fw_glyphs", 0xFF00, 0xFF5E, font)
        # 3. CJK 基本汉字全集 (U+4E00..U+9FA5, 20902 字，涵盖简繁日所有常用与生僻汉字)
        dump_range(f, "chs_cjk_glyphs", 0x4E00, 0x9FA5, font)

        f.write("""const unsigned char* get_chs_glyph(unsigned int cp) {
    if (cp >= 0x4E00 && cp <= 0x9FA5)
        return &chs_cjk_glyphs[(cp - 0x4E00) * 32];
    if (cp >= 0x3000 && cp <= 0x30FF)
        return &chs_sym_glyphs[(cp - 0x3000) * 32];
    if (cp >= 0xFF00 && cp <= 0xFF5E)
        return &chs_fw_glyphs[(cp - 0xFF00) * 32];
    return 0;
}
""")
    print(f"Successfully generated {out_path}!")

if __name__ == "__main__":
    main()
