#.SILENT:

# ---{ BUILD CONFIGURATION }--- #
MMCE ?= 1
DS34 ?= 0
TMANIP ?= 1
ETH ?= 0
UDPFS ?= 1
EXFAT ?= 1
DVRP ?= 1
IOP_RESET ?= 1
XFROM ?= 1
UDPTTY ?= 0
MX4SIO ?= 1
SIO2MAN ?= 1
PPC_UART ?= 0
SIO_DEBUG ?= 0
DEBUG ?= 0
LCDVD ?= LATEST#or LEGACY
# ----------------------------- #
.SILENT:

BIN_NAME = $(HAS_EXFAT)$(HAS_DS34)$(HAS_ETH)$(HAS_UDPFS)$(HAS_MX4SIO)$(HAS_MMCE)$(HAS_DVRP)$(HAS_XFROM)$(HAS_EESIO)$(HAS_UDPTTY)$(HAS_PPCTTY)$(HAS_IOP_RESET)
ifeq ($(DEBUG), 0)
  EE_BIN = UNC-BOOT$(BIN_NAME).ELF
  EE_BIN_PKD = BOOT$(BIN_NAME).ELF
else
  EE_BIN = UNC-BOOT.ELF
  EE_BIN_PKD = BOOT.ELF
endif
EE_OBJS = main.o main_actions.o main_boot.o main_modules.o main_menu.o main_title.o main_info_screens.o main_console_info.o main_gameid.o main_gameid_table.o neutrino_gameid.o main_history.o init.o main_startup.o main_fileops.o main_exploit_installer.o kelf_signer.o config.o config_screen.o config_startup.o config_network.o config_advanced.o gui.o gui_colors.o gui_neutrino.o virtual_keyboard.o elf.o draw.o draw_gs.o draw_text.o loader_elf.o filer.o filer_device.o filer_mount.o filer_fileops.o filer_actions.o filer_browser.o filer_copy.o \
	gui_sort.o gui_texteditor.o gui_hdd0_format.o psu_functions.o save_formats.o save_crypto.o save_lzari.o save_manager.o save_vmc.o \
	poweroff_irx.o iomanx_irx.o filexio_irx.o ps2dev9_irx.o dev9_poweroff_irx.o \
	ps2hdd_irx.o ps2fs_irx.o usbd_irx.o mcman_irx.o mcserv_irx.o \
	cdvd_irx.o xparam_irx.o vmcman_irx.o ps2kbd_irx.o \
	hdd.o hdd_header_injector.o hdl_rpc.o hdl_info_irx.o editor.o editor_menu.o editor_input.o editor_rules.o editor_file.o timer.o icon.o lang.o popstarter.o popstarter_path.o popstarter_vcd.o popstarter_gameid.o popstarter_elf.o ember.o \
	font_uLE.o font_chs.o makeicon.o chkesr.o allowdvdv_irx.o \
	exploit_system_xlf_header.o exploit_xsystem_xlf_header.o exploit_dtl_system_xlf_header.o exploit_xlf_body.o \
	exploit_osdsys_kernel.o exploit_osd110_kernel.o \
	exploit_jpn_sys.o exploit_usa_sys.o exploit_eur_sys.o exploit_chn_sys.o \
	exploit_list_icn.o \
	secrsif_irx.o exploit_ioprp_img.o

EE_INCS := -I$(PS2DEV)/gsKit/include -I$(PS2SDK)/ports/include -Iinclude

EE_LDFLAGS := -L$(PS2DEV)/gsKit/lib -L$(PS2SDK)/ports/lib -Liop/oldlibs/libcdvd/lib -s -Wl,--no-warn-mismatch
EE_MATH_LIB := -lm
ifneq ($(wildcard$(PS2SDK)/ee/lib/libmf.a),)
EE_MATH_LIB := -lmf
endif

# Newer PS2SDK libpatches can have backward intra-archive references.
EE_LIBS = -Wl,--start-group -lgskit -ldmakit -lmc -lhdd -lkbd $(EE_MATH_LIB) \
			-lcdvd -lc -lfileXio -lpatches -lpoweroff -ldebug -lz
EE_CFLAGS := -mgpopt -G10240 -G0 -DNEWLIB_PORT_AWARE -D_EE

ifneq ($(DEBUG), 0)
    EE_CFLAGS += -DULE_DEBUG_BUILD
endif

# Locate bin2s across old/new PS2SDK layouts and PATH.
BIN2S_TOOL ?=
ifneq ($(wildcard$(PS2SDK)/bin/bin2s),)
BIN2S_TOOL := $(PS2SDK)/bin/bin2s
else ifneq ($(wildcard$(PS2DEV)/bin/bin2s),)
BIN2S_TOOL := $(PS2DEV)/bin/bin2s
else ifneq ($(wildcard /usr/local/ps2dev/bin/bin2s),)
BIN2S_TOOL := /usr/local/ps2dev/bin/bin2s
else ifneq ($(wildcard$(CURDIR)/scripts/bin2s-fallback.sh),)
BIN2S_TOOL := sh $(CURDIR)/scripts/bin2s-fallback.sh
else
BIN2S_TOOL := $(shell command -v bin2s 2>/dev/null)
endif
ifeq ($(strip $(BIN2S_TOOL)),)$(error bin2s not found. Install PS2SDK tools, or set BIN2S_TOOL=/full/path/to/bin2s)
endif
BIN2S = @$(BIN2S_TOOL)

ifeq ($(LCDVD),LEGACY)$(info -- Building with legacy libcdvd)
  EE_CFLAGS += -DLIBCDVD_LEGACY
  CDVD_SOURCE = iop/cdvd.irx
  EE_INCS += -Iiop/oldlibs/libcdvd/ee
  EE_LIBS += -lcdvdfs
else
  EE_CFLAGS += -DLIBCDVD_LATEST
  CDVD_SOURCE = iop/__precompiled/cdfs.irx
  ifneq ($(wildcard$(PS2SDK)/iop/irx/cdfs.irx),)
    CDVD_SOURCE = $(PS2SDK)/iop/irx/cdfs.irx
  endif
endif
SECR_LIB_SOURCE := thirdparty/ps2sdk-master/ee/rpc/secr/src/libsecr.c
IOPREBOOT_INC_DIR := $(PS2SDK)/ee/iopreboot/include
ifneq ($(wildcard thirdparty/ps2sdk-master/ee/iopreboot/include/iopcontrol_special.h),)
    IOPREBOOT_INC_DIR := thirdparty/ps
