; MiniOS - Kernel (Stage 2)
; Real-mode kernel with text UI and command shell
; Loaded at 0x1000:0x0000 by boot.asm

[BITS 16]
[ORG 0x0000]

; ============================================================
; Kernel entry point (called via far jump from bootloader)
; ============================================================
start:
    ; Set up segment registers
    mov ax, cs
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0xFFFE

    ; Hide cursor
    mov ah, 0x01
    mov cx, 0x2000
    int 0x10

    ; Clear screen to blue background
    call cls_blue

    ; Print welcome screen
    call print_banner

    ; Get system info
    call detect_memory
    call get_cpu_info

    ; Main shell loop
.shell_loop:
    call print_prompt
    call read_line

    ; Parse and execute command
    mov si, input_buffer
    call execute_command

    jmp .shell_loop

; ============================================================
; Clear screen - blue background
; ============================================================
cls_blue:
    push ax
    push cx
    push di
    push es

    mov ax, 0xB800
    mov es, ax
    xor di, di
    mov cx, 2000       ; 80*25
    mov ax, 0x1720     ; white on blue, space char
    rep stosw

    pop es
    pop di
    pop cx
    pop ax
    ret

; ============================================================
; Clear screen - black background
; ============================================================
cls_black:
    push ax
    push cx
    push di
    push es

    mov ax, 0xB800
    mov es, ax
    xor di, di
    mov cx, 2000
    mov ax, 0x0720     ; light gray on black
    rep stosw

    pop es
    pop di
    pop cx
    pop ax
    ret

; ============================================================
; Print banner
; ============================================================
print_banner:
    mov si, banner_top
    call print_string_color

    mov si, banner_line1
    call print_string_color

    mov si, banner_line2
    call print_string_color

    mov si, banner_line3
    call print_string_color

    mov si, banner_bottom
    call print_string_color

    ret

; ============================================================
; Print colored string at current position
; String format: each byte pair = (char, color)
; Terminated by byte 0
; ============================================================
print_string_color:
    push ax
    push bx
    push cx
    push di
    push es

    mov ax, 0xB800
    mov es, ax

    ; Get cursor position
    mov ah, 0x03
    mov bh, 0
    int 0x10
    ; DH = row, DL = column
    mov al, 80
    mul dh
    xor dh, dh
    add ax, dx
    shl ax, 1           ; *2 for word offset
    mov di, ax

.next_char:
    lodsb
    test al, al
    jz .done

    ; Get color from next byte
    mov ah, [si]
    inc si

    stosw               ; write char+attr to video memory
    jmp .next_char

.done:
    ; Update cursor position
    shr di, 1
    mov ax, di
    mov bl, 80
    div bl
    mov dh, al
    mov dl, ah
    mov ah, 0x02
    mov bh, 0
    int 0x10

    pop es
    pop di
    pop cx
    pop bx
    pop ax
    ret

; ============================================================
; Print prompt
; ============================================================
print_prompt:
    mov si, prompt_str
    call print_string_color
    ret

; ============================================================
; Print newline
; ============================================================
newline:
    push ax
    push bx
    push cx
    mov ah, 0x03
    mov bh, 0
    int 0x10
    inc dh
    mov dl, 0
    mov ah, 0x02
    int 0x10
    pop cx
    pop bx
    pop ax
    ret

; ============================================================
; Print string with newline (plain, current color)
; ============================================================
puts:
    push ax
    push si
.loop:
    lodsb
    test al, al
    jz .done
    mov ah, 0x0E
    mov bh, 0
    int 0x10
    jmp .loop
.done:
    pop si
    pop ax
    ret

; ============================================================
; Print character with attribute at current position
; AL = char, AH = attribute
; ============================================================
putchar_color:
    push bx
    push cx
    push di
    push es

    mov cx, ax
    mov ah, 0x03
    mov bh, 0
    int 0x10
    mov ax, 0xB800
    mov es, ax
    mov al, 80
    mul dh
    xor dh, dh
    add ax, dx
    shl ax, 1
    mov di, ax
    mov ax, cx
    stosw

    pop es
    pop di
    pop cx
    pop bx
    ret

; ============================================================
; Read a line of input from keyboard
; Stores at input_buffer, null-terminated
; ============================================================
read_line:
    push ax
    push di

    mov di, input_buffer
    xor cl, cl          ; character count

.input_loop:
    ; Wait for keypress
    mov ah, 0
    int 0x16

    cmp al, 0x0D        ; Enter
    je .enter

    cmp al, 0x08        ; Backspace
    je .backspace

    ; Check if printable (0x20 to 0x7E)
    cmp al, 0x20
    jb .input_loop
    cmp al, 0x7E
    ja .input_loop

    ; Check buffer not full (max 255 chars)
    cmp cl, 254
    jae .input_loop

    ; Store character
    stosb
    inc cl

    ; Echo to screen
    mov ah, 0x0E
    mov bh, 0
    int 0x10

    jmp .input_loop

.backspace:
    test cl, cl
    jz .input_loop

    dec di
    dec cl

    ; Move cursor back, print space, move cursor back
    mov ah, 0x03
    mov bh, 0
    int 0x10
    dec dl
    mov ah, 0x02
    int 0x10

    mov al, ' '
    mov ah, 0x0E
    int 0x10

    mov ah, 0x03
    mov bh, 0
    int 0x10
    dec dl
    mov ah, 0x02
    int 0x10

    jmp .input_loop

.enter:
    ; Null-terminate
    mov byte [di], 0

    ; Print newline
    call newline

    pop di
    pop ax
    ret

; ============================================================
; String comparison (SI = str1, DI = str2) -> ZF set if equal
; ============================================================
strcmp:
    push si
    push di
.loop:
    mov al, [si]
    mov ah, [di]
    test al, al
    jz .end
    cmp al, ah
    jne .not_equal
    inc si
    inc di
    jmp .loop
.end:
    test ah, ah
    jnz .not_equal
    pop di
    pop si
    ret                     ; equal
.not_equal:
    pop di
    pop si
    or al, 1                ; clear ZF
    ret

; ============================================================
; Execute command (SI = command string)
; ============================================================
execute_command:
    push ax
    push si
    push di

    ; Skip leading spaces
.skip_spaces:
    lodsb
    cmp al, ' '
    je .skip_spaces
    dec si                  ; back to first non-space char

    ; Get first word length
    mov di, si
    xor cl, cl
.count_word:
    mov al, [di]
    test al, al
    jz .got_word
    cmp al, ' '
    je .got_word
    inc di
    inc cl
    jmp .count_word
.got_word:
    test cl, cl
    jz .done

    ; Copy command to cmd_buffer
    push si
    mov di, cmd_buffer
    mov ch, cl
.copy_cmd:
    mov al, [si]
    mov [di], al
    inc si
    inc di
    dec ch
    jnz .copy_cmd
    mov byte [di], 0
    pop si

    ; Get argument (rest after command)
    add si, cx
    call skip_spaces_fn
    mov di, arg_buffer
.copy_arg:
    lodsb
    test al, al
    jz .arg_done
    stosb
    jmp .copy_arg
.arg_done:
    mov byte [di], 0

    ; Match commands
    mov si, cmd_buffer

    ; help
    mov di, cmd_help
    call strcmp
    je .do_help

    ; cls / clear
    mov di, cmd_cls
    call strcmp
    je .do_cls
    mov di, cmd_clear
    call strcmp
    je .do_cls

    ; info / sysinfo
    mov di, cmd_info
    call strcmp
    je .do_info

    ; time
    mov di, cmd_time
    call strcmp
    je .do_time

    ; date
    mov di, cmd_date
    call strcmp
    je .do_date

    ; echo
    mov di, cmd_echo
    call strcmp
    je .do_echo

    ; color
    mov di, cmd_color
    call strcmp
    je .do_color

    ; reboot
    mov di, cmd_reboot
    call strcmp
    je .do_reboot

    ; shutdown
    mov di, cmd_shutdown
    call strcmp
    je .do_shutdown

    ; uptime
    mov di, cmd_uptime
    call strcmp
    je .do_uptime

    ; mem
    mov di, cmd_mem
    call strcmp
    je .do_mem

    ; calc
    mov di, cmd_calc
    call strcmp
    je .do_calc

    ; Unknown command
    mov si, msg_unknown
    call puts
    mov si, cmd_buffer
    call puts
    mov si, msg_newline
    call puts
    jmp .done

.do_help:    call cmd_help_fn    ; jmp .done
.do_cls:     call cls_black      ; jmp .done
.do_info:    call cmd_info_fn    ; jmp .done
.do_time:    call cmd_time_fn    ; jmp .done
.do_date:    call cmd_date_fn    ; jmp .done
.do_echo:    call cmd_echo_fn    ; jmp .done
.do_color:   call cmd_color_fn   ; jmp .done
.do_reboot:  call cmd_reboot_fn  ; jmp .done
.do_shutdown: call cmd_shutdown_fn; jmp .done
.do_uptime:  call cmd_uptime_fn  ; jmp .done
.do_mem:     call cmd_mem_fn     ; jmp .done
.do_calc:    call cmd_calc_fn    ; jmp .done

.done:
    pop di
    pop si
    pop ax
    ret

; ============================================================
; Skip spaces helper
; ============================================================
skip_spaces_fn:
    push ax
.loop:
    lodsb
    cmp al, ' '
    je .loop
    dec si
    pop ax
    ret

; ============================================================
; COMMAND: help
; ============================================================
cmd_help_fn:
    mov si, help_text
    call puts
    ret

; ============================================================
; COMMAND: info
; ============================================================
cmd_info_fn:
    mov si, info_os_name
    call puts

    ; CPU info
    mov si, info_cpu_str
    call puts
    mov si, cpu_model
    call puts
    call newline

    ; Memory
    mov si, info_mem_str
    call puts
    mov ax, [mem_low_kb]
    call print_dec
    mov si, info_kb_str
    call puts
    call newline

    ; Drive
    mov si, info_drive_str
    call puts
    mov al, [boot_drive]
    call print_hex_byte
    call newline

    ret

; ============================================================
; COMMAND: time
; ============================================================
cmd_time_fn:
    call get_rtc_time
    mov si, info_time_prefix
    call puts
    call print_time
    ret

; ============================================================
; COMMAND: date
; ============================================================
cmd_date_fn:
    call get_rtc_date
    mov si, info_date_prefix
    call puts
    call print_date
    ret

; ============================================================
; COMMAND: echo
; ============================================================
cmd_echo_fn:
    mov si, arg_buffer
    cmp byte [si], 0
    je .done
    call puts
    call newline
.done:
    ret

; ============================================================
; COMMAND: color (set foreground color)
; color 0-15
; ============================================================
cmd_color_fn:
    mov si, arg_buffer
    mov al, [si]
    test al, al
    jz .show
    ; Parse number
    call parse_dec
    cmp bl, 16
    jae .show
    shl bl, 4
    or bl, 0x0F
    mov [current_attr], bl
    ret
.show:
    mov si, msg_color_usage
    call puts
    ret

; ============================================================
; COMMAND: reboot
; ============================================================
cmd_reboot_fn:
    mov si, msg_rebooting
    call puts
    int 0x19

; ============================================================
; COMMAND: shutdown (QEMU shutdown via 0x604 port)
; ============================================================
cmd_shutdown_fn:
    mov si, msg_shutdown
    call puts
    mov ax, 0x2000
    mov dx, 0x604
    out dx, ax
    ; Fallback: try 0x4004
    mov dx, 0x4004
    mov ax, 0x3400
    out dx, ax
    ret

; ============================================================
; COMMAND: uptime (fake - just shows boot time)
; ============================================================
cmd_uptime_fn:
    mov si, msg_uptime
    call puts
    ret

; ============================================================
; COMMAND: mem - show memory map
; ============================================================
cmd_mem_fn:
    mov si, info_mem_map
    call puts
    mov ax, [mem_low_kb]
    call print_dec
    mov si, info_kb_str
    call puts
    call newline

    mov ax, [mem_high_mb]
    call print_dec
    mov si, info_mb_str
    call puts
    call newline
    ret

; ============================================================
; COMMAND: calc - simple expression evaluator
; Format: calc <num1> <op> <num2>
; ============================================================
cmd_calc_fn:
    mov si, arg_buffer
    call parse_calc
    ret

; ============================================================
; Parse calc expression: "3 + 4" -> print result
; ============================================================
parse_calc:
    push ax
    push bx
    push cx

    mov si, arg_buffer
    cmp byte [si], 0
    je .usage

    ; Parse first number
    call parse_dec
    mov al, bl
    mov [calc_val1], al

    ; Skip spaces
.skip1:
    lodsb
    cmp al, ' '
    je .skip1
    dec si

    ; Get operator
    lodsb
    mov [calc_op], al

    ; Skip spaces
.skip2:
    lodsb
    cmp al, ' '
    je .skip2
    dec si

    ; Parse second number
    call parse_dec
    mov [calc_val2], bl

    ; Calculate
    mov al, [calc_val1]
    mov bl, [calc_val2]

    mov cl, [calc_op]
    cmp cl, '+'
    je .add
    cmp cl, '-'
    je .sub
    cmp cl, '*'
    je .mul
    cmp cl, '/'
    je .div
    cmp cl, '%'
    je .mod

    mov si, msg_bad_op
    call puts
    jmp .done

.add:
    add al, bl
    mov [calc_result], al
    jmp .show_result
.sub:
    sub al, bl
    mov [calc_result], al
    jmp .show_result
.mul:
    mul bl
    mov [calc_result], al
    jmp .show_result
.div:
    test bl, bl
    jz .div_zero
    div bl
    mov [calc_result], al
    jmp .show_result
.mod:
    test bl, bl
    jz .div_zero
    div bl
    mov [calc_result], ah     ; remainder
    jmp .show_result
.div_zero:
    mov si, msg_div_zero
    call puts
    jmp .done

.show_result:
    mov si, msg_result_prefix
    call puts
    mov al, [calc_val1]
    call print_dec
    mov al, [calc_op]
    mov ah, 0x0E
    int 0x10
    mov al, [calc_val2]
    call print_dec
    mov si, msg_equals
    call puts
    mov al, [calc_result]
    call print_dec_signed
    call newline
    jmp .done

.usage:
    mov si, msg_calc_usage
    call puts

.done:
    pop cx
    pop bx
    pop ax
    ret

; ============================================================
; Parse decimal number (SI = string) -> BL = value
; ============================================================
parse_dec:
    push ax
    push cx
    xor bl, bl
.loop:
    lodsb
    test al, al
    jz .done
    cmp al, '0'
    jb .done
    cmp al, '9'
    ja .done
    sub al, '0'
    mov cl, al
    mov al, bl
    mov bl, 10
    mul bl
    add al, cl
    mov bl, al
    jmp .loop
.done:
    dec si
    pop cx
    pop ax
    ret

; ============================================================
; Print decimal number (AL = unsigned value)
; ============================================================
print_dec:
    push ax
    push bx
    push cx
    push dx

    xor cx, cx
    mov bl, 10
.loop:
    xor ah, ah
    div bl
    push ax
    inc cx
    test al, al
    jnz .loop

.print:
    pop ax
    mov al, ah
    add al, '0'
    mov ah, 0x0E
    int 0x10
    loop .print

    pop dx
    pop cx
    pop bx
    pop ax
    ret

; ============================================================
; Print decimal signed (AL = signed value)
; ============================================================
print_dec_signed:
    test al, al
    jns .positive
    push ax
    mov al, '-'
    mov ah, 0x0E
    int 0x10
    pop ax
    neg al
.positive:
    call print_dec
    ret

; ============================================================
; Print hex byte (AL = value)
; ============================================================
print_hex_byte:
    push ax
    push cx
    mov ah, al
    shr al, 4
    call .print_nibble
    mov al, ah
    and al, 0x0F
    call .print_nibble
    pop cx
    pop ax
    ret
.print_nibble:
    add al, '0'
    cmp al, '9'
    jbe .done
    add al, 7
.done:
    mov ah, 0x0E
    int 0x10
    ret

; ============================================================
; Print time (from RTC)
; ============================================================
print_time:
    push ax
    mov al, [rtc_hour]
    call print_hex_byte
    mov al, ':'
    mov ah, 0x0E
    int 0x10
    mov al, [rtc_minute]
    call print_hex_byte
    mov al, ':'
    mov ah, 0x0E
    int 0x10
    mov al, [rtc_second]
    call print_hex_byte
    call newline
    pop ax
    ret

; ============================================================
; Print date (from RTC)
; ============================================================
print_date:
    push ax
    mov al, [rtc_year]
    call print_hex_byte
    mov al, [rtc_century]
    call print_hex_byte
    mov al, '-'
    mov ah, 0x0E
    int 0x10
    mov al, [rtc_month]
    call print_hex_byte
    mov al, '-'
    mov ah, 0x0E
    int 0x10
    mov al, [rtc_day]
    call print_hex_byte
    call newline
    pop ax
    ret

; ============================================================
; Get RTC time
; ============================================================
get_rtc_time:
    push ax
    ; Seconds
    mov al, 0
    out 0x70, al
    in al, 0x71
    mov [rtc_second], al
    ; Minutes
    mov al, 2
    out 0x70, al
    in al, 0x71
    mov [rtc_minute], al
    ; Hours
    mov al, 4
    out 0x70, al
    in al, 0x71
    mov [rtc_hour], al
    pop ax
    ret

; ============================================================
; Get RTC date
; ============================================================
get_rtc_date:
    push ax
    ; Year
    mov al, 9
    out 0x70, al
    in al, 0x71
    mov [rtc_year], al
    ; Century
    mov al, 0x32
    out 0x70, al
    in al, 0x71
    mov [rtc_century], al
    ; Month
    mov al, 8
    out 0x70, al
    in al, 0x71
    mov [rtc_month], al
    ; Day
    mov al, 7
    out 0x70, al
    in al, 0x71
    mov [rtc_day], al
    pop ax
    ret

; ============================================================
; Detect memory using BIOS int 0x15, EAX=0xE820
; ============================================================
detect_memory:
    push ax
    push bx
    push cx
    push di
    push es

    ; Start with E820
    mov di, e820_map
    xor ebx, ebx
    xor bp, bp          ; entry count
    mov edx, 0x534D4150 ; 'SMAP'
    mov eax, 0xE820
    mov ecx, 20         ; 20 bytes per entry
    int 0x15
    jc .use_old_method
    mov edx, 0x534D4150
    cmp eax, edx
    jne .use_old_method
    test ebx, ebx
    jz .done_mem
    jmp .next_entry

.loop:
    mov eax, 0xE820
    mov ecx, 20
    int 0x15
    jc .done_e820
    mov edx, 0x534D4150
.next_entry:
    jcxz .skip_entry
    inc bp
    add di, 20
.skip_entry:
    test ebx, ebx
    jnz .loop

.done_e820:
    ; Sum up memory from E820 map
    ; For simplicity, just take the first usable region
    mov di, e820_map
    cmp bp, 0
    je .use_old_method
    mov eax, [di+8]     ; length low
    mov ecx, [di+12]    ; length high
    ; Convert to KB
    shr eax, 10
    mov [mem_low_kb], ax
    ; Convert to MB
    shr eax, 10
    mov [mem_high_mb], ax
    jmp .done_mem

.use_old_method:
    ; Use int 0x12 for low memory
    int 0x12
    mov [mem_low_kb], ax

    ; Use int 0x15, AX=0xE801 for extended memory
    mov ax, 0xE801
    int 0x15
    jc .done_mem
    ; CX/AX = extended memory in 1KB blocks (below 16MB)
    ; DX/BX = extended memory in 64KB blocks (above 16MB)
    add ax, cx          ; total extended memory in KB
    shr ax, 10          ; to MB
    add ax, 1           ; add low 1MB
    mov [mem_high_mb], ax

.done_mem:
    pop es
    pop di
    pop cx
    pop bx
    pop ax
    ret

; ============================================================
; Get CPU info using CPUID
; ============================================================
get_cpu_info:
    push ax
    push bx
    push cx
    push dx
    push di

    ; Check if CPUID is supported
    pushfd
    pop eax
    mov ecx, eax
    xor eax, 0x200000
    push eax
    popfd
    pushfd
    pop eax
    cmp eax, ecx
    je .no_cpuid

    ; Get vendor string
    mov eax, 0
    cpuid
    mov [cpu_vendor], ebx
    mov [cpu_vendor+4], edx
    mov [cpu_vendor+8], ecx
    mov byte [cpu_vendor+12], 0

    ; Get brand string
    mov di, cpu_model
    mov eax, 0x80000002
    cpuid
    mov [di], eax
    mov [di+4], ebx
    mov [di+8], ecx
    mov [di+12], edx
    add di, 16

    mov eax, 0x80000003
    cpuid
    mov [di], eax
    mov [di+4], ebx
    mov [di+8], ecx
    mov [di+12], edx
    add di, 16

    mov eax, 0x80000004
    cpuid
    mov [di], eax
    mov [di+4], ebx
    mov [di+8], ecx
    mov [di+12], edx

    jmp .done_cpu

.no_cpuid:
    mov di, cpu_model
    mov word [di], '?'
    mov byte [di+2], 0

.done_cpu:
    pop di
    pop dx
    pop cx
    pop bx
    pop ax
    ret

; ============================================================
; Data section
; ============================================================

; ---- Banner ----
banner_top:    db 0xDA, 0x19, 0xC4, 0x19, 0xC4, 0x19, 0xC4, 0x19, 0xC4, 0x19, 0xC4, 0x19, 0xC4, 0x19, 0xC4, 0x19, 0xC4, 0x19, 0xC4, 0x19, 0xC4, 0x19, 0xC4, 0x19, 0xC4, 0x19, 0xC4, 0x19, 0xC4, 0x19, 0xC4, 0x19, 0xBF, 0

banner_line1:  db 0xB3, 0x1F, ' ', 0x1F, ' ', 0x1F, 'M', 0x1C, 'i', 0x1C, 'n', 0x1C, 'i', 0x1C, 'O', 0x1C, 'S', 0x1C, ' ', 0x1C, 'v', 0x1C, '1', 0x1C, '.', 0x1C, '0', 0x1C, ' ', 0x1F, ' ', 0x1F, 0xB3, 0

banner_line2:  db 0xB3, 0x1F, ' ', 0x1F, ' ', 0x1F, ' ', 0x1F, 'x', 0x1F, '8', 0x1F, '6', 0x1F, ' ', 0x1F, 'O', 0x1F, 'S', 0x1F, ' ', 0x1F, ' ', 0x1F, ' ', 0x1F, ' ', 0x1F, 0xB3, 0

banner_line3:  db 0xB3, 0x1F, ' ', 0x1F, ' ', 0x1F, ' ', 0x1E, 'T', 0x1E, 'y', 0x1E, 'p', 0x1E, 'e', 0x1E, ' ', 0x1E, 'h', 0x1E, 'e', 0x1E, 'l', 0x1E, 'p', 0x1E, ' ', 0x1F, ' ', 0x1F, 0xB3, 0

banner_bottom: db 0xC0, 0x19, 0xC4, 0x19, 0xC4, 0x19, 0xC4, 0x19, 0xC4, 0x19, 0xC4, 0x19, 0xC4, 0x19, 0xC4, 0x19, 0xC4, 0x19, 0xC4, 0x19, 0xC4, 0x19, 0xC4, 0x19, 0xC4, 0x19, 0xC4, 0x19, 0xC4, 0x19, 0xC4, 0x19, 0xD9, 0

; ---- Prompt ----
prompt_str:    db '[', 0x0A, 'M', 0x0F, 'i', 0x0F, 'n', 0x0F, 'i', 0x0F, 'O', 0x0F, 'S', 0x0F, ']', 0x0A, '$ ', 0x0F, 0

; ---- Messages ----
msg_unknown:   db "Unknown command: ", 0
msg_newline:   db 0x0D, 0x0A, 0
msg_rebooting: db "Rebooting...", 0x0D, 0x0A, 0
msg_shutdown:  db "Shutting down...", 0x0D, 0x0A, 0
msg_uptime:    db "Boot: T+0 minutes (uptime tracking not implemented)", 0x0D, 0x0A, 0
msg_div_zero:  db "Error: Division by zero!", 0x0D, 0x0A, 0
msg_bad_op:    db "Error: Unknown operator (use + - * / %)", 0x0D, 0x0A, 0
msg_equals:    db " = ", 0
msg_result_prefix: db "  ", 0
msg_calc_usage: db "Usage: calc <num> <op> <num>", 0x0D, 0x0A
                db "  Operators: + - * / %", 0x0D, 0x0A, 0
msg_color_usage: db "Usage: color <0-15>", 0x0D, 0x0A, 0

; ---- Help text ----
help_text:  db 0x0D, 0x0A
            db "╔══════════════════════════╗", 0x0D, 0x0A
            db "║    MiniOS Command Help   ║", 0x0D, 0x0A
            db "╚══════════════════════════╝", 0x0D, 0x0A
            db "  help     - Show this help", 0x0D, 0x0A
            db "  cls      - Clear screen", 0x0D, 0x0A
            db "  info     - System info", 0x0D, 0x0A
            db "  time     - Current time", 0x0D, 0x0A
            db "  date     - Current date", 0x0D, 0x0A
            db "  echo <t> - Print text", 0x0D, 0x0A
            db "  color <n>- Set color (0-15)", 0x0D, 0x0A
            db "  mem      - Memory info", 0x0D, 0x0A
            db "  calc     - Calculator", 0x0D, 0x0A
            db "  uptime   - System uptime", 0x0D, 0x0A
            db "  reboot   - Restart", 0x0D, 0x0A
            db "  shutdown - Power off", 0x0D, 0x0A, 0

; ---- Info texts ----
info_os_name:    db 0x0D, 0x0A
                 db "MiniOS v1.0 - x86 Real-Mode Operating System", 0x0D, 0x0A
                 db "Copyright (c) 2026 Eric", 0x0D, 0x0A, 0
info_cpu_str:    db "CPU: ", 0
info_mem_str:    db "Memory: ", 0
info_kb_str:     db " KB", 0
info_mb_str:     db " MB", 0
info_mem_map:    db "Memory Map:", 0x0D, 0x0A
                 db "  Low Memory: ", 0
info_drive_str:  db "Boot Drive: 0x", 0
info_time_prefix: db "Time: ", 0
info_date_prefix: db "Date: ", 0

; ---- Command strings ----
cmd_help     db "help", 0
cmd_cls      db "cls", 0
cmd_clear    db "clear", 0
cmd_info     db "info", 0
cmd_time     db "time", 0
cmd_date     db "date", 0
cmd_echo     db "echo", 0
cmd_color    db "color", 0
cmd_reboot   db "reboot", 0
cmd_shutdown db "shutdown", 0
cmd_uptime   db "uptime", 0
cmd_mem      db "mem", 0
cmd_calc     db "calc", 0

; ---- Variables ----
current_attr db 0x0F       ; white on black

; RTC values
rtc_second   db 0
rtc_minute   db 0
rtc_hour     db 0
rtc_day      db 0
rtc_month    db 0
rtc_year     db 0
rtc_century  db 0

; Memory info
mem_low_kb   dw 0
mem_high_mb  dw 0

; CPU info
cpu_vendor   times 13 db 0
cpu_model    times 49 db 0

; E820 memory map buffer
e820_map     times 20*32 db 0   ; 32 entries

; Calc temporaries
calc_val1    db 0
calc_val2    db 0
calc_op      db 0
calc_result  db 0

; Buffers
input_buffer times 256 db 0
cmd_buffer   times 64 db 0
arg_buffer   times 192 db 0

boot_drive   db 0

; ============================================================
; Pad to fill remaining sectors (up to 31KB from sector 2-63)
; ============================================================
times (63*512) - ($ - $$) db 0
