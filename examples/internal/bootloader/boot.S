
.code16
.global start
.extern kmain

start:
    cli
    mov $0, %ax
    mov %ax, %ds
    mov %ax, %es
    mov %ax, %ss
    mov $0x7c00, %sp
    
    # Read sectors from disk
    mov $0x02, %ah      # BIOS read sector function
    mov $1, %al         # Number of sectors to read (Load 1 sector/512 bytes)
    mov $0, %ch         # Cylinder 0
    mov $0, %dh         # Head 0
    mov $2, %cl         # Start from sector 2
    # dl already contains the boot drive number
    mov $0, %bx         # Segment 0
    mov %bx, %es
    mov $0x7e00, %bx    # Destination buffer
    int $0x13           # BIOS interrupt
    jc disk_error

    # Load GDT
    lgdt gdt_descriptor

    # Switch to Protected Mode
    mov %cr0, %eax
    or $1, %eax
    mov %eax, %cr0

    # Jump to 32-bit code segment
    ljmp $0x08, $protected_mode

disk_error:
    jmp .

.code32
protected_mode:
    # Set up 32-bit data segments
    mov $0x10, %ax
    mov %ax, %ds
    mov %ax, %es
    mov %ax, %fs
    mov %ax, %gs
    mov %ax, %ss

    # Set up stack
    mov $0x7c00, %esp

    call kmain
    hlt

gdt_start:
    .quad 0 # Null descriptor

    # Code Segment (Offset 0x08)
    .word 0xffff    # Limit (low)
    .word 0x0       # Base (low)
    .byte 0x0       # Base (middle)
    .byte 0x9a      # Access (exec, read)
    .byte 0xcf      # Granularity
    .byte 0x0       # Base (high)

    # Data Segment (Offset 0x10)
    .word 0xffff    # Limit (low)
    .word 0x0       # Base (low)
    .byte 0x0       # Base (middle)
    .byte 0x92      # Access (read/write)
    .byte 0xcf      # Granularity
    .byte 0x0       # Base (high)

gdt_end:

gdt_descriptor:
    .word gdt_end - gdt_start - 1
    .long gdt_start

.fill 510-(.-start), 1, 0
.word 0xaa55

