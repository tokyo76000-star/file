#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, subprocess
from PIL import Image, ImageDraw, ImageFont

def find_cjk_font():
    try:
        out = subprocess.check_output(["fc-list", ":lang=zh", "file"], text=True)
        for line in out.splitlines():
            p = line.split(":")[0].strip()
            if os.path.exists(p):
                return p
    except Exception:
        pass
    for root, _, files in os.walk("/usr/share/fonts"):
        for f in files:
            if any(k in f.lower() for k in ["wqy", "noto", "cjk", "droid", "zenhei"]):
                return os.path.join(root, f)
    raise FileNotFoundError("No CJK font found")

def render_char(font, ch):
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
        b0, b1 = 0, 0
        for x in range(8):
            if img.getpixel((x, y)):
                b0 |= (0x80 >> x)
            if img.getpixel((x + 8, y)):
                b1 |= (0x80 >> x)
        data.extend([b0, b1])
    return data

def dump_range(f, name, s_cp, e_cp, font):
    f.write(f"const unsigned char {name}[{(e_cp - s_cp + 1) * 32}] = {{\n")
    for cp in range(s_cp, e_cp + 1):
        raw = render_char(font, chr(cp))
        f.write("  " + ",".join(f"0x{b:02X}" for b in raw) + ",\n")
    f.write("};\n\n")

def main():
    font = ImageFont.truetype(find_cjk_font(), 14)
    out_path = os.path.join("src", "font_chs.c")
    with open(out_path, "w", encoding="utf-8") as f:
        dump_range(f, "chs_sym_glyphs", 0x3000, 0x30FF, font)
        dump_range(f, "chs_fw_glyphs", 0xFF00, 0xFF5E, font)
        dump_range(f, "chs_cjk_glyphs", 0x4E00, 0x9FA5, font)
        f.write("""const unsigned char* get_chs_glyph(unsigned int cp) {
    if (cp >= 0x4E00 && cp <= 0x9FA5) return &chs_cjk_glyphs[(cp - 0x4E00) * 32];
    if (cp >= 0x3000 && cp <= 0x30FF) return &chs_sym_glyphs[(cp - 0x3000) * 32];
    if (cp >= 0xFF00 && cp <= 0xFF5E) return &chs_fw_glyphs[(cp - 0xFF00) * 32];
    return 0;
}
""")
    print(f"Generated {out_path} successfully!")

if __name__ == "__main__":
    main()
