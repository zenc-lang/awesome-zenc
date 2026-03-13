
CC = gcc
ZC = ../../zc
LD = ld
OBJCOPY = objcopy

CFLAGS = -m32 -ffreestanding -fno-pie -fno-stack-protector -nostdlib -O2 -Wall
LDFLAGS = -m elf_i386 -T linker.ld

all: boot.bin

boot.bin: boot.o kernel.o
	$(LD) $(LDFLAGS) -o boot.elf boot.o kernel.o
	$(OBJCOPY) -O binary boot.elf boot.bin
	truncate -s 1024 boot.bin
	@echo "Bootloader built: boot.bin (Size: $$(stat -c %s boot.bin) bytes)"

boot.o: boot.S
	$(CC) $(CFLAGS) -c boot.S -o boot.o

kernel.o: kernel.c
	$(CC) $(CFLAGS) -c kernel.c -o kernel.o

kernel.c: kernel.zc
	$(ZC) transpile --freestanding kernel.zc
	mv out.c kernel.c

clean:
	rm -f *.o *.bin *.elf kernel.c
