BIN = proof-carrying

# Toolchain
CC = avr-gcc
LD = avr-gcc
AS = avr-as
AR = avr-ar
NM = avr-nm
OBJCOPY = avr-objcopy
STRIP = avr-strip

MCU = atmega328p
# mcu clock frequency
CLK = 16000000
OBJECTDIR = obj

APP_SOURCEFILES = main.c
SOURCEDIRS = ../libs ../libs/aes128 ../libs/serial ../libs/hmac
CORE_SOURCEFILES = messaging.c util.c avr-asm-macros.S serial.c
CORE_SOURCEFILES += hmac-sha1.c sha1-asm.S
CORE_SOURCEFILES += aes_dec.S aes_enc.S aes_invsbox.S aes_keyschedule.S aes_sbox.S gf256mul.S

vpath %.c $(SOURCEDIRS)
vpath %.S $(SOURCEDIRS)

CFLAGS = -mmcu=$(MCU) -Wall -Os -gdwarf-2 -fno-strict-aliasing -DF_CPU=$(CLK) #-ffixed-r2
CFLAGS += ${addprefix -I,$(SOURCEDIRS)}
ASFLAGS += -mmcu=$(MCU)
LDFLAGS += -mmcu=$(MCU)

oname = ${patsubst %.c,%.o,${patsubst %.S,%.o,$(1)}}
soname = ${patsubst %.c,%.s.o,$(1)}

CORE_OBJECTFILES = ${addprefix $(OBJECTDIR)/,${call oname, $(CORE_SOURCEFILES)}}
APP_OBJECTFILES = ${addprefix $(OBJECTDIR)/,${call oname, $(APP_SOURCEFILES)}}

# Default target is the HEX
all: ${BIN}.hex

# Linking and packing objects to ELF
${BIN}.elf: ${CORE_OBJECTFILES} ${APP_OBJECTFILES}
	${LD} ${LDFLAGS} -o $@ $^

# Linking and packing objects to ihex for flashing with avrdude
%.hex: %.elf
	${OBJCOPY} $^ --pad-to=0x7800 --gap-fill=0x00 -O ihex $@

# App C --> s target.
$(OBJECTDIR)/%.s: %.c | $(OBJECTDIR)
	${CC} ${CFLAGS} -S -o $@ $^

# uVisor CORE c --> o target
$(OBJECTDIR)/%.o: %.c | $(OBJECTDIR)
	$(CC) $(CFLAGS) -c $< -o $@

# uVisor CORE S --> s target
$(OBJECTDIR)/%.s: %.S | $(OBJECTDIR)
	$(CPP) $(CFLAGS) -o $@ $<

# uVisor CORE S --> o target
$(OBJECTDIR)/%.o: $(OBJECTDIR)/%.s | $(OBJECTDIR)
	$(AS) $(ASFLAGS) -o $@ $<

# Create objectdir if removed by clean
$(OBJECTDIR):
	mkdir $@

clean:
	-rm -f ${BIN}.elf
	-rm -f ${BIN}.hex
	-rm -f ${BIN}.bin
	-rm -rf ${OBJECTDIR}

distclean: clean

flash:
	avrdude -p $(MCU) -c arduino -U flash:w:${BIN}.hex -P /dev/ttyACM0 -b 115200
size:
		avr-size -A --mcu=${MCU} ${BIN}.elf
