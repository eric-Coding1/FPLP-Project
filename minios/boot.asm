; MiniOS - Boot sector (Stage 1)
; Loads kernel from disk sectors and jumps to it
; NASM - flat binary, loaded at 0x7C00 by BIOS

[BITS 16]
[ORG 0x7C00]

; ============================================================
; Boot sector entry
; ============================================================
start:
    ; Set up segment registers
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00

    ; Save boot drive number (passed by BIOS in DL)
    mov [boot_drive], dl

    ; Print welcome
    mov si, msg_booting
    call print_string

    ; Load kernel from disk (sectors 1-63, about 31KB)
    mov bx, KERNEL_LOAD_SEG
    mov es, bx
    xor bx, bx           ; ES:BX = KERNEL_LOAD_SEG:0x0000
    mov ah, 0x02         ; BIOS read sectors function
    mov al, 63           ; sectors to read
    mov ch, 0            ; cylinder 0
    mov cl, 2            ; start at sector 2 (sector 1 is the boot sector)
    mov dh, 0            ; head 0
    mov dl, [boot_drive] ; drive number
    int 0x13

    jc disk_error

    ; Print OK and jump to kernel
    mov si, msg_ok
    call print_string

    ; Jump to kernel (far jump to KERNEL_LOAD_SEG:0x0000)
    jmp KERNEL_LOAD_SEG:0x0000

; ============================================================
; Disk error handler
; ============================================================
disk_error:
    mov si, msg_error
    call print_string
    mov si, msg_reboot
    call print_string
    xor ax, ax
    int 0x16           ; wait for key
    int 0x19           ; reboot

; ============================================================
; Print null-terminated string (SI = string addr)
; ============================================================
print_string:
    push ax
    mov ah, 0x0E       ; BIOS teletype output
.loop:
    lodsb
    test al, al
    jz .done
    int 0x10
    jmp .loop
.done:
    pop ax
    ret

; ============================================================
; Data
; ============================================================
boot_drive  db 0
msg_booting db "MiniOS v1.0 booting...", 0x0D, 0x0A, 0
msg_ok      db "OK", 0x0D, 0x0A, 0
msg_error   db "ERROR: Disk read failed!", 0x0D, 0x0A, 0
msg_reboot  db "Press any key to reboot...", 0

KERNEL_LOAD_SEG equ 0x1000

; ============================================================
; Boot sector padding and signature
; ============================================================
times 510 - ($ - $$) db 0
dw 0xAA55
