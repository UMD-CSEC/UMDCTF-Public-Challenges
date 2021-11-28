0000000000600080 <.towel>:
    jmp    0x6000b9
    push   rbp
    rex.WRB
    rex.R
    rex.XB push r12
    rex.RX sub eax,0x333c5f49
    pop    rdi
    rex.B jae 0x6000de
    rex.WB je 0x6000f3
    rex.WB jae 0x6000f6
    push   rsp
    push   0x655f7369
    rex.B jae 0x6000f9
    pop    rdi
    xor    esp,DWORD PTR [rdi]
    push   rbx
    pop    rdx
    sbb    DWORD PTR [rbx],edi
    add    dh,BYTE PTR [rcx+rdi*2+0x3f]
    cmp    DWORD PTR [rip+0x68156c4b],eax        # 0x68756cfc
    pop    rax
    rex.XB
    sub    DWORD PTR ds:[rdx],ebp
    add    BYTE PTR [rax],bh
    sub    DWORD PTR [rax-0x73],ecx
    xor    eax,0xffffffc2
    xor    rdi,rdi
    inc    al
    add    rdx,0x7
    syscall 
    mov    ecx,0x3
    inc    rdx
    mov    rsi,QWORD PTR [ecx*8+0x600099]
    mov    r10,QWORD PTR [ecx*8+0x600081]
    xor    al,al
    inc    al
    xor    rsi,r10
    push   rsi
    lea    rsi,[rsp]
    push   rcx
    syscall 
    pop    rcx
    loop   0x6000d3
    xor    rdi,rdi
    mul    rdi
    mov    al,0x3c
    syscall 
