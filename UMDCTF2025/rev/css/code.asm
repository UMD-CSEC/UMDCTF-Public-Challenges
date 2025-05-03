; 0-13: values from flag format
.rom 14 14
.rom 15 12
.rom 16 2
.rom 17 7
.rom 18 4
.rom 19 15
.rom 20 5
.rom 21 6
.rom 22 8
.rom 23 10
.rom 24 3

.rom 28 1
.rom 29 0
; flag format check
ffmtcheck:
	rld1    ~~, r2, r3                         ; load rom[r2] (r3 doesn't matter because it's 0)
	cff     fail, rom, r2                      ; check if rom[r2] matches expected output at r2
	ublk                                       ; unblock shift-resets
	add1    r2, r2, ~~                         ; r2 += 1
	jle     ffmtcheck, r2, rom+14              ; if r2 <= 14, jump to ffmtcheck
; main loop
	mov     r14, rom+29, ~~                    ; r14 = 0 (offset, high bits)
	xor     r15, r14, r14                      ; r15 = 0 (offset, low bits)
	add1    t12, t12, ~~                       ; t12[0] = 1
	mov     t12+1, rom+24, ~~                  ; t12[1] = 3
	mov     t12+2, rom+24, ~~                  ; t12[2] = 3
	mov     t12+3, rom+17, ~~                  ; t12[3] = 7
mainloop:
; copy rom[r14,r15 + 64] to r1, rom[r14,r15 + 65] to r2
	add     r14, rom+18, r14                   ; r14 += rom[18] = 4
	rld2    ~~, flags, ~~                      ; if carry, load +256
	rld1    ~~, r15, r14                       ; load rom[r14,r15]
	mov     r1, rom, ~~                        ; load cell into r1
	add1    r15, r15, ~~                       ; r15 += 1
	rld1    ~~, r15, r14                       ; load rom[r14,r15]
	mov     r2, rom+1, ~~                      ; load next cell into r2
	ublk                                       ; unblock shift-resets
	sub     r14, r14, rom+18                   ; reset r14 (subtract rom[18] = 4)
	xor     r13, rom+16, rom+24                ; r13 = (rom[16] = 2) ^ (rom[24] = 3) = 1
; transform t12 based on r1, r2
	mov     p3, rom+15, ~~                     ; p3 = rom[15] = 12 (offset, high bits)
	xor     r4, r1, r1                         ; r4 = 0 (offset, low bits)
hashloop:
	mpld    ~~, r4, p3                         ; load t12[p3,r4]
	prng    t12, t12, r1                       ; t12[p3,r4], flags = prng(t12[p3,r4], r1)
	ublk                                       ; unblock shift-resets
	xor     r1, flags, r2                      ; r1 = flags ^ r2
	add1    r4, r4, ~~                         ; r4 += 1
	add     p3, p3, flags                      ; p3 += carry
	jne     hashloop, p3, rom+14               ; if p3 != 14, loop
	jmp     ecmul                              ; call ecmul (t2 = (t12 * Q)[0])
ecmul<--14:
	xor     mem, t2, t2+1                      ; mem[0] = t2[0] ^ t2[1]
	xor     mem+1, t2+3, t2+2                  ; mem[1] = t2[2] ^ t2[3]
	lsc     r8, r15, r14                       ; r8, flags = spine1[r14,r15], spine2[r14,r15]
	xor     r9, flags, mem+1                   ; r9 = flags ^ mem[1]
	xor     r10, r8, mem                       ; r10 = r8 ^ mem[0]
	ham     r8, r9, r10                        ; r8 = hamming distance from spine
	add     acc, acc, r8                       ; acc[0] += r8
	add     acc+1, acc+1, flags                ; acc[1] += carry
	add     acc+2, acc+2, flags                ; acc[2] += carry
	and     r13, rom+15, r13                   ; r13 = 0 (AND with rom[15] = 12)
	mov     p3, flags, ~~                      ; p3 = 1
	jmp     ecmul                              ; call ecmul (t2 = (t12 * P)[0])
ecmul<--1:
	jne     keepgoing, r14, rom+14             ; if r14 != rom[14] = 14, skip next check
	je      pass, r15, rom+17                  ; if r15 == rom[17] = 7, exit (r14*16 + r15 = 231)
keepgoing:
; copy t2 to t12
	xor     r1, r1, r1                         ; r1 = 0 (offset, low bits)
	xor     r2, r1, rom+16                     ; r2 = rom[16] = 2 (offset, high bits)
copy:
	mpld    ~~, r1, r2                         ; load t2[r2,r1]
	add10   r2, r2, ~~                         ; go to t12 (r2 += 10)
	mpld    ~~, r1, r2                         ; load t12[r2,r1]
	mov     t12, t2, ~~                        ; t12[r2,r1] = t2[r2,r1]
	ublk                                       ; unblock shift-resets
	add     r2, r2, rom+21                     ; go back to t2 (add rom[21] = 6)
	add1    r1, r1, r1                         ; r1 += 1
	add     r2, flags, r2                      ; r2 += carry
	jl      copy, r2, rom+18                   ; if r2 < rom[18] = 4, loop

	add1    r15, r15, ~~                       ; r15 += 1
	add     r14, r14, flags                    ; r14 += carry
	jmp     mainloop                           ; jump to mainloop
pass:
; check error count
	jne     fail, rom+29, acc+2                ; if acc[2] != 0, fail
	jne     fail, rom+29, acc+1                ; if acc[1] != 0, fail
	jge     fail, acc, rom+16                  ; if acc[0] >= rom[16] = 2, fail
; at this point, t2 is (t12 * P)[0]
; copy t2 to acc
	mov     acc, t2, ~~                        ; acc[0] = t2[0]
	mov     acc+1, t2+1, ~~                    ; acc[1] = t2[1]
	mov     acc+2, t2+2, ~~                    ; acc[2] = t2[2]
	mov     acc+3, t2+3, ~~                    ; acc[3] = t2[3]
	mov     acc+4, t2+4, ~~                    ; acc[4] = t2[4]
	mov     acc+5, t2+5, ~~                    ; acc[5] = t2[5]
	mov     acc+6, t2+6, ~~                    ; acc[6] = t2[6]
	mov     acc+7, t2+7, ~~                    ; acc[7] = t2[7]
	mov     acc+8, t2+8, ~~                    ; acc[8] = t2[8]
	mov     acc+9, t2+9, ~~                    ; acc[9] = t2[9]
	mov     acc+10, t2+10, ~~                  ; acc[10] = t2[10]
	mov     acc+11, t2+11, ~~                  ; acc[11] = t2[11]
	mov     acc+12, t2+12, ~~                  ; acc[12] = t2[12]
	mov     acc+13, t2+13, ~~                  ; acc[13] = t2[13]
	mov     acc+14, t2+14, ~~                  ; acc[14] = t2[14]
	mov     acc+15, t2+15, ~~                  ; acc[15] = t2[15]
	mov     acc+16, t2+16, ~~                  ; acc[16] = t2[16]
	mov     acc+17, t2+17, ~~                  ; acc[17] = t2[17]
	mov     acc+18, t2+18, ~~                  ; acc[18] = t2[18]
	mov     acc+19, t2+19, ~~                  ; acc[19] = t2[19]
	mov     acc+20, t2+20, ~~                  ; acc[20] = t2[20]
	mov     acc+21, t2+21, ~~                  ; acc[21] = t2[21]
	mov     acc+22, t2+22, ~~                  ; acc[22] = t2[22]
	mov     acc+23, t2+23, ~~                  ; acc[23] = t2[23]
	mov     acc+24, t2+24, ~~                  ; acc[24] = t2[24]
	mov     acc+25, t2+25, ~~                  ; acc[25] = t2[25]
	mov     acc+26, t2+26, ~~                  ; acc[26] = t2[26]
	mov     acc+27, t2+27, ~~                  ; acc[27] = t2[27]
	mov     acc+28, t2+28, ~~                  ; acc[28] = t2[28]
	mov     acc+29, t2+29, ~~                  ; acc[29] = t2[29]
	mov     acc+30, t2+30, ~~                  ; acc[30] = t2[30]
	mov     acc+31, t2+31, ~~                  ; acc[31] = t2[31]
	xor     p3, rom+23, p3                     ; p3 ^= rom[23] = 10 (p3 is 11 now)
	mov     r13, p3, ~~                        ; r13 = 11
	jmp     ecmul                              ; call ecmul (t2 = (t12 * Q)[0])
ecmul<--11:
; now t2 is (t12 * Q)[0]
; copy t2 to t12
	xor     r1, r1, r1                         ; r1 = 0 (offset, low bits)
	xor     r2, r1, rom+16                     ; r2 = rom[16] = 2 (offset, high bits)
copy2:
	mpld    ~~, r1, r2                         ; load t2[r2,r1]
	add10   r2, r2, ~~                         ; go to t12 (r2 += 10)
	mpld    ~~, r1, r2                         ; load t12[r2,r1]
	mov     t12, t2, ~~                        ; t12[r2,r1] = t2[r2,r1]
	ublk                                       ; unblock shift-resets
	add     r2, r2, rom+21                     ; go back to t2 (add rom[21] = 6)
	add1    r1, r1, r1                         ; r1 += 1
	add     r2, flags, r2                      ; r2 += carry
	jl      copy2, r2, rom+18                  ; if r2 < rom[18] = 4, loop
; special multiply * (t12, 1)
	add1    r13, r13, ~~                       ; r13 += 1 (r13 is 12 now)
	jmp     ecmul                              ; call ecmul (t2 = (punctured * (t12, 1))[0])
ecmul<--12:
	jne     fail, acc, t2                      ; fail if acc[0] != t2[0]
	jne     fail, acc+1, t2+1                  ; fail if acc[1] != t2[1]
	jne     fail, acc+2, t2+2                  ; fail if acc[2] != t2[2]
	jne     fail, acc+3, t2+3                  ; fail if acc[3] != t2[3]
	jne     fail, acc+4, t2+4                  ; fail if acc[4] != t2[4]
	jne     fail, acc+5, t2+5                  ; fail if acc[5] != t2[5]
	jne     fail, acc+6, t2+6                  ; fail if acc[6] != t2[6]
	jne     fail, acc+7, t2+7                  ; fail if acc[7] != t2[7]
	jne     fail, acc+8, t2+8                  ; fail if acc[8] != t2[8]
	jne     fail, acc+9, t2+9                  ; fail if acc[9] != t2[9]
	jne     fail, acc+10, t2+10                ; fail if acc[10] != t2[10]
	jne     fail, acc+11, t2+11                ; fail if acc[11] != t2[11]
	jne     fail, acc+12, t2+12                ; fail if acc[12] != t2[12]
	jne     fail, acc+13, t2+13                ; fail if acc[13] != t2[13]
	jne     fail, acc+14, t2+14                ; fail if acc[14] != t2[14]
	jne     fail, acc+15, t2+15                ; fail if acc[15] != t2[15]
	jne     fail, acc+16, t2+16                ; fail if acc[16] != t2[16]
	jne     fail, acc+17, t2+17                ; fail if acc[17] != t2[17]
	jne     fail, acc+18, t2+18                ; fail if acc[18] != t2[18]
	jne     fail, acc+19, t2+19                ; fail if acc[19] != t2[19]
	jne     fail, acc+20, t2+20                ; fail if acc[20] != t2[20]
	jne     fail, acc+21, t2+21                ; fail if acc[21] != t2[21]
	jne     fail, acc+22, t2+22                ; fail if acc[22] != t2[22]
	jne     fail, acc+23, t2+23                ; fail if acc[23] != t2[23]
	jne     fail, acc+24, t2+24                ; fail if acc[24] != t2[24]
	jne     fail, acc+25, t2+25                ; fail if acc[25] != t2[25]
	jne     fail, acc+26, t2+26                ; fail if acc[26] != t2[26]
	jne     fail, acc+27, t2+27                ; fail if acc[27] != t2[27]
	jne     fail, acc+28, t2+28                ; fail if acc[28] != t2[28]
	jne     fail, acc+29, t2+29                ; fail if acc[29] != t2[29]
	jne     fail, acc+30, t2+30                ; fail if acc[30] != t2[30]
	jne     fail, acc+31, t2+31                ; fail if acc[31] != t2[31]
	halt    success
fail:
	halt    fail

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

addmodp: ; adds t0, t2 -> t2 mod 2^127-1. uses r1, r2, r3. returns via p1
	xor     r1, r1, r1                         ; r1 = 0 (offset, high bits)
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
	xor     r3, r3, r3                         ; r3 = 0 (old carry bit)
addmodp-top:
	mpld    ~~, r2, r1                         ; load t0[r1,r2]
	add2    r1, r1, ~~                         ; go to t2
	mpld    ~~, r2, r1                         ; load t2[r1,r2]
	add     t2, t2, r3                         ; t2[r1,r2] += r3 (carry)
	mov     r3, flags, ~~                      ; r3 = carry bit
	add     t2, t0, t2                         ; t2[r1,r2] = t0[r1,r2] + t2[r1,r2]
	ublk                                       ; unblock shift-resets
	add     r3, flags, r3                      ; r3 = carry bit
	add     r1, r1, rom+14                     ; r1 += rom[14] = 14 (goes back to t0)
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, r1, flags                      ; r1 += carry
	jne     addmodp-top, r1, rom+16            ; if r1 != rom[16] = 2, jump to top
	jg      addmodp-red, t2+31, rom+17         ; if msb > rom[17] = 7, we need to reduce
	jl      addmodp-done, t2+31, rom+17        ; if msb < rom[17] = 7, we're done
; at this point, we know the msb is 7, now we check that all other bytes are 15
addmodp-chk:
	mpld    ~~, r2, r1                         ; load t2[r1,r2]
	mov     r3, t2, ~~                         ; r3 = t2[r1,r2]
	ublk                                       ; unblock shift-resets
	jne     addmodp-done, r3, rom+19           ; if r3 != 15, we're done
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, flags, r1                      ; r1 += carry
	je      addmodp-chk, r1, rom+16            ; if r1 == rom[16] = 2, jump to chk
	jne     addmodp-done, r2, rom+19           ; if r2 != rom[19] = 15, we're done
; at this point, r1 is 3 and r2 is 15. t2 is exactly 2^127 - 1, which reduces to 0
	xor     r3, r3, r3                         ; r3 = 0
	sub1    r1, r1, ~~                         ; r1 -= 1 (should be 2 now)
	add1    r2, r2, ~~                         ; r2 += 1 (should be 0 now)
addmodp-zero:
	mpld    ~~, r2, r1                         ; load t2[r1,r2]
	mov     t2, r3, ~~                         ; t2[r1,r2] = 0
	ublk                                       ; unblock shift-resets
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, r1, flags                      ; r1 += carry
	jne     addmodp-zero, r1, rom+18           ; if r1 != rom[18] = 4, jump to top
	jmp     addmodp-done                       ; t2 is 0, we're done
addmodp-red:
; msb is >7, subtract 2^127 and add 1
	and     t2+31, t2+31, rom+17               ; t2 msb &= rom[17] = 7
	mov     r1, rom+16, ~~                     ; r1 = rom[16] = 2 (t2)
	xor     r2, r2, r2                         ; r2 = 0
	xor     r3, r3, r3                         ; r3 = 0
addmodp-redtop:
	mpld    ~~, r2, r1                         ; load t2[r1,r2]
	add1    t2, t2, ~~                         ; t2[r1,r2] += 1
	ublk                                       ; unblock shift-resets
	je      addmodp-done, flags, r3            ; if no carry, we're done
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, r1, flags                      ; r1 += carry
	jl      addmodp-redtop, r1, rom+18         ; if r1 < rom[18] = 4, jump to redtop
addmodp-done:
; return based on p1
	je      addmodp<--2, p1, rom+16            ; rom[16] = 2
	je      addmodp<--15, p1, rom+19           ; rom[19] = 15
	je      addmodp<--6, p1, rom+21            ; rom[21] = 6
	je      addmodp<--8, p1, rom+22            ; rom[22] = 8
	je      addmodp<--4, p1, rom+18            ; rom[18] = 4
	je      addmodp<--14, p1, rom+14           ; rom[14] = 14
	je      addmodp<--10, p1, rom+23           ; rom[23] = 10
;	je      addmodp<--5, p1, rom+20            ; rom[20] = 5
	je      addmodp<--12, p1, rom+15           ; rom[15] = 12
	je      addmodp<--3, p1, rom+24            ; rom[24] = 3
	je      addmodp<--7, p1, rom+17            ; rom[17] = 7
	je      addmodp<--0, p1, rom+29            ; rom[29] = 0
	jl      addmodp<--1, p1, rom+16            ; jump if p1 < (rom[16] = 2)
	jl      addmodp<--9, p1, rom+23            ; jump if p1 < (rom[23] = 10)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

mulmodp: ; multiplies t6, t8 -> t2 mod 2^127-1. uses t0, r1, r2, r3, r5, r6, r7, r8. returns via p2
; copy t6 to t0
	mov     r3, rom+21, ~~                     ; r3 = rom[21] = 6
	xor     r1, r1, r1                         ; r1 = 0 (offset, high bits)
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
mulmodp-copy:
	mpld    ~~, r2, r1                         ; load t0[r1,r2]
	add     r1, r1, r3                         ; go to t6
	mpld    ~~, r2, r1                         ; load t6[r1,r2]
	mov     t0, t6, ~~                         ; t0[r1,r2] = t6[r1,r2]
	ublk                                       ; unblock shift-resets
	add     r1, r1, rom+23                     ; go back to t0 (r1 += rom[23] = 10)
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, r1, flags                      ; r1 += carry
	jne     mulmodp-copy, r1, rom+16           ; if r1 != rom[16] = 2, loop
; zero out t2
mulmodp-zero:
	mpld    ~~, r2, r1                         ; load t2[r1,r2]
	xor     t2, t2, t2                         ; t2[r1,r2] = 0
	ublk                                       ; unblock shift-resets
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, r1, flags                      ; r1 += carry
	jne     mulmodp-zero, r1, rom+18           ; if r1 != rom[18] = 4, loop
; init main loop
	mov     r5, rom+22, ~~                     ; r5 = rom[22] = 8 (offset, high bits)
	xor     r6, r6, r6                         ; r6 = 0 (offset, low bits)
mulmodp-top:
	mpld    ~~, r6, r5                         ; load t8[r5,r6]
	mov     r7, t8, ~~                         ; r7 = t8[r5,r6]
	xor     r8, r8, r8                         ; r8 = 0
	ublk                                       ; unblock shift-resets
mulmodp-inner:
	ext6    flags, r7, r8                      ; flags is 6 iff r7[r8] is set
	jne     mulmodp-dbl, flags, rom+21         ; if flags != rom[21] = 6, skip to doubling
	mov     p1, rom+16, ~~                     ; p1 = rom[16] = 2
	jmp     addmodp                            ; call addmodp (t2 += t0)
addmodp<--2:
; double t0 (shift bits by 1)
mulmodp-dbl:
	xor     r1, r1, r1                         ; r1 = 0 (offset, high bits)
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
	ext6    r3, r2, r2                         ; r3 = 0
mulmodp-dblloop:
	mpld    ~~, r2, r1                         ; load t0[r1,r2]
	shl1    t0, t0, r3                         ; t0[r1,r2] = (t0[r1,r2] << 1) | r3
	ublk
	mov     r3, flags, ~~                      ; r3 = flags
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, r1, flags                      ; r1 += carry
	jne     mulmodp-dblloop, r1, rom+16        ; if r1 != rom[16] = 2, loop
	and     t0+31, t0+31, rom+17               ; t0 msb &= rom[17] = 7
	add     t0, t0, flags                      ; t0 += flags (1 iff msb was truncated)
	add1    r8, r8, ~~                         ; r8 += 1
	jne     mulmodp-inner, rom+18, r8          ; if r8 != rom[18] = 4, loop
	add1    r6, r6, ~~                         ; r6 += 1
	add     r5, r5, flags                      ; r5 += carry
	jne     mulmodp-top, rom+23, r5            ; if r5 != rom[23] = 10, loop
mulmodp-done:
; return based on p2
	je      mulmodp<--4, p2, rom+18            ; rom[18] = 4
	je      mulmodp<--7, p2, rom+17            ; rom[17] = 7
	je      mulmodp<--2, p2, rom+16            ; rom[16] = 2
	je      mulmodp<--10, p2, rom+23           ; rom[23] = 10
	je      mulmodp<--6, p2, rom+21            ; rom[21] = 6
	je      mulmodp<--15, p2, rom+19           ; rom[19] = 15
	je      mulmodp<--5, p2, rom+20            ; rom[20] = 5
	je      mulmodp<--14, p2, rom+14           ; rom[14] = 14
	je      mulmodp<--12, p2, rom+15           ; rom[15] = 12
	je      mulmodp<--8, p2, rom+22            ; rom[22] = 8
	je      mulmodp<--0, p2, rom+29            ; rom[29] = 0
	je      mulmodp<--3, p2, rom+24            ; rom[24] = 3
	jl      addmodp<--12, p2, rom+16           ; jump if p2 < (rom[16] = 2) (this is also mulmodp<--1)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

invmodp: ; invert t10 mod p -> t2. uses t0, t6, t8, r1, r2, r4, r5, r6, r7, r8, r9. only returns to one location (hopefully this doesnt change)
; copy t10 to t2
	mov     r1, rom+16, ~~                     ; r1 = rom[16] = 2 (offset, high bits)
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
invmodp-copy-init:
	mpld    ~~, r2, r1                         ; load t2[r1,r2]
	add     r1, r1, rom+22                     ; go to t10 (r1 += rom[22] = 8)
	mpld    ~~, r2, r1                         ; load t10[r1,r2]
	mov     t2, t10, ~~                        ; t2[r1,r2] = t10[r1,r2]
	ublk                                       ; unblock shift-resets
	add     r1, r1, rom+22                     ; go back to t2 (r1 += rom[22] = 8)
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, r1, flags                      ; r1 += carry
	jne     invmodp-copy-init, r1, rom+18      ; if r1 != rom[18] = 4, loop

	xor     r4, r4, r4                         ; r4 = 0
	mov     r9, rom+16, ~~                     ; r9 = rom[16] = 2
invmodp-looptop:
; copy t2 to t6, t8
	mov     r1, rom+16, ~~                     ; r1 = rom[16] = 2 (offset, high bits)
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
invmodp-copy1:
	mpld    ~~, r2, r1                         ; load t2[r1,r2]
	add     r1, r1, rom+18                     ; go to t6 (r1 += rom[18] = 4)
	mpld    ~~, r2, r1                         ; load t6[r1,r2]
	add2    r1, r1, ~~                         ; go to t8
	mpld    ~~, r2, r1                         ; load t8[r1,r2]
	mov     t6, t2, ~~                         ; t6[r1,r2] = t2[r1,r2]
	mov     t8, t2, ~~                         ; t8[r1,r2] = t2[r1,r2]
	ublk                                       ; unblock shift-resets
	add     r1, r1, rom+23                     ; go back to t2 (r1 += rom[23] = 10)
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, r1, flags                      ; r1 += carry
	jne     invmodp-copy1, r1, rom+18          ; if r1 != rom[18] = 4, loop

	mov     p2, rom+17, ~~                     ; p2 = rom[17] = 7
	jmp     mulmodp                            ; call mulmodp (t2 = t6 * t8)
mulmodp<--7:

; skip the multiplication on the second-to-last iteration
	jsl    mulmodp<--4, r4, r9                 ; jump if r4 is 7 and r9 is 14 (r4*16 + 19 = 126)

; copy t2 to t6, t10 to t8
	mov     r1, rom+16, ~~                     ; r1 = rom[16] = 2 (offset, high bits)
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
invmodp-copy2:
	mpld    ~~, r2, r1                         ; load t2[r1,r2]
	add     r1, r1, rom+18                     ; go to t6 (r1 += rom[18] = 4)
	mpld    ~~, r2, r1                         ; load t6[r1,r2]
	add2    r1, r1, ~~                         ; go to t8
	mpld    ~~, r2, r1                         ; load t8[r1,r2]
	add2    r1, r1, ~~                         ; go to t10
	mpld    ~~, r2, r1                         ; load t10[r1,r2]
	mov     t6, t2, ~~                         ; t6[r1,r2] = t2[r1,r2]
	mov     t8, t10, ~~                        ; t8[r1,r2] = t10[r1,r2]
	ublk                                       ; unblock shift-resets
	add     r1, r1, rom+22                     ; go back to t2 (r1 += rom[22] = 8)
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, r1, flags                      ; r1 += carry
	jne     invmodp-copy2, r1, rom+18          ; if r1 != rom[18] = 4, loop

	mov     p2, rom+18, ~~                     ; p2 = rom[18] = 4
	jmp     mulmodp                            ; call mulmodp (t2 = t6 * t8)
mulmodp<--4:
; one iteration does t2 = t2^2 * t10. doing this 126 times gives t2 = t10^(2^127-1).
; BUT on the second-to-last iteration we skip the *t10, so we get t10^(2^127-3) = t10^(-1)
	add1    r9, r9, ~~                         ; r9 += 1
	add     r4, r4, flags                      ; r4 += carry
	jle     invmodp-looptop, r4, rom+17        ; if r4 <= rom+17 = 7 (r4*16 + r9 <= 127), loop
	jmp     invmodp<--after                    ; return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

ecmul: ; R = P, Q, or (t12, 1), selected by r13 (0 vs >0, or 12). compute t12 * R -> (t2, 1) if r13 != 12, otherwise (puncture) * R -> (t2, 1).
; uses mem[0-127], t0, t4, t6, t8, t10, t14, r1-r12. returns via p3

; zero out mem[0-127], except: mem[0] = 1, mem[64] = 3, mem[96] = 1
	xor     r10, r10, r10                      ; r10 = 0 (offset, high bits)
	xor     r11, r11, r11                      ; r11 = 0 (offset, low bits)
ecmul-init:
	mld1    ~~, r11, r10                       ; load mem[r10,r11]
	xor     mem, mem, mem                      ; set mem[r10,r11] = 0
	jne     ecmul-skipset, r11, rom+29         ; skip Pset if r11 != rom[29] = 0
	ext6    flags, r10, r11                    ; set flags=6 iff r10 & 1
	jne     ecmul-skipset, flags, rom+21       ; skip Pset if flags != rom[29] = 0 (rom is at +29 not +21 because we havent unblocked)
	pset    mem, r10, r11                      ; set mem[r10,r11] (we can only get here if (r10*16 + r11) is a multiple of 32)
ecmul-skipset:
	add1    r11, r11, ~~                       ; r11 += 1
	add     r10, flags, r10                    ; r10 += carry
	ublk                                       ; unblock shift-resets
	and     r10, r10, rom+17                   ; r10 &= rom[17] = 7
	ext6    r1, flags, rom+29                  ; r1 is 6 iff (flags >> rom[29] = 0) & 1 iff r10 > 7
	jne     ecmul-init, r1, rom+21             ; if r1 isnt rom[21] = 6 (r10 <= 7), loop
	je      ecmul-skipsetQ, r13, r11           ; if r13 is 0, skip setQ
; copy rom[32-63] to mem[64-95]
	add2    r10, r10, ~~                       ; r10 = 2
ecmul-setQ:
	rld1    ~~, r11, r10                       ; load rom[r10,r11]
	add2    r10, r10, ~~                       ; r10 += 2
	mld1    ~~, r11, r10                       ; load mem[r10,r11]
	xor     mem, rom, mem                      ; mem[r10,r11] ^= rom[r10,r11]
	ublk                                       ; unblock shift-resets
	sub     r10, r10, rom+16                   ; reset r10 (subtract rom[16] = 2)
	add1    r11, r11, ~~                       ; r11 += 1
	add     r10, flags, r10                    ; r10 += carry
	jg      ecmul-setQ, rom+18, r10            ; if r10 < rom[18] = 4, loop
	and     r10, rom+23, r10                   ; r10 &= rom[23] = 10 (r10 = 0)

	jne     ecmul-skipsetQ, r13, rom+15        ; if r13 isnt rom[15] = 12, skip the next part
; copy t12 to mem[64-95]
	mov     r10, rom+18, ~~                    ; r10 = rom[18] = 4
ecmul-setQ2:
	mld1    ~~, r11, r10                       ; load mem[r10,r11]
	add     r10, r10, rom+22                   ; r10 += rom[22] = 8
	mpld    ~~, r11, r10                       ; load t12[r10,r11]
	mov     mem, t12, ~~                       ; mem[r10,r11] = t12[r10,r11]
	ublk                                       ; unblock shift-resets
	sub     r10, r10, rom+22                   ; reset r10 (subtract rom[22] = 8)
	add1    r11, r11, ~~                       ; r11 += 1
	add     r10, flags, r10                    ; r10 += carry
	jg      ecmul-setQ2, rom+21, r10           ; if r10 < rom[21] = 6, loop
	xor     r10, r10, r10                      ; r10 = 0
ecmul-skipsetQ:
	xor     r11, rom+15, r11                   ; r11 ^= rom[15] = 12 (offset, high bits)
	add1    r11, r11, ~~                       ; r11 = 13
	sub1    r10, r10, ~~                       ; r10 -= 1 (r10 = 15, offset, low bits)
ecmul-outer:
	mpld    ~~, r10, r11                       ; load t12[r11,r10]
	mov     r4, t12, ~~                        ; r4 = t12[r11,r10]
	ublk                                       ; unblock shift-resets
	sub     r1, rom+17, rom+18                 ; r1 = (rom[17] = 7) - (rom[18] = 4) = 3
	pset    r4, r1, r4                         ; bit reverse r4

	jne     ecmul-skippuncture, r13, rom+15    ; if r13 isnt rom[15] = 12, skip the next part
; puncture bits are the lsbs of rom[67,71,75,79], rom[83,87,91,95], ..., rom[291,295,299,303] (29 x 4 bits)
; 12*16      = 192 -> 67  =  4*16 + 3, +7, +11, +15
; 12*16 +  1 = 193 -> 83  =  5*16 + 3, +7, +11, +15
; 12*16 + 12 = 205 -> 259 = 16*16 + 3, +7, +11, +15
; 12*16 + 14 = 207 -> 291 = 18*16 + 3, +7, +11, +15
	xor     r4, r4, r4                         ; r4 = 0
	jne     ecmul-skippuncture, r11, r13       ; if r11 isnt 12, skip loading puncture bit
	jg      ecmul-skippuncture, r10, rom+14    ; if r10 > rom[14] = 14, skip loading puncture bit
	
	mov     r3, rom+18, ~~                     ; r3 = rom[18] = 4
	add     r2, r10, r3                        ; r2 = r10 + 4
	mov     r6, flags, ~~                      ; r6 = carry
	mov     r1, rom+24, ~~                     ; r1 = rom[24] = 3
	sub     r7, rom+17, rom+21                 ; r7 = (rom[17] = 7) - (rom[21] = 6) = 1
; set r4 = (rom[r2,r1], rom[r2,r1+4], rom[r2,r1+8], rom[r2,r1+12])
	rld2    ~~, r6, ~~                         ; load rom + 256 if r6 is set
	rld1    ~~, r1, r2                         ; load rom[r2,r1]
	and     r4, rom, r7                        ; r4 = rom & 1
	add     r1, r1, r3                         ; r1 += 4
	rld1    ~~, r1, r2                         ; load rom[r2,r1] (+4)
	and     r5, r7, rom                        ; r5 = rom & 1
	shl1    r4, r4, r5                         ; r4 = (r4 << 1) | r5
	add     r1, r1, r3                         ; r1 += 4
	ublk                                       ; unblock shift-resets
	je      nah, r10, rom+14                   ; if r10 = rom[14] = 14, skip next two bits
	rld2    ~~, r6, ~~                         ; load rom + 256 if r6 is set
	rld1    ~~, r1, r2                         ; load rom[r2,r1] (+8)
	and     r5, r7, rom                        ; r5 = rom & 1
	shl1    r4, r4, r5                         ; r4 = (r4 << 1) | r5
	add     r1, r1, r3                         ; r1 += 4
	rld1    ~~, r1, r2                         ; load rom[r2,r1] (+12)
	and     r5, r7, rom                        ; r5 = rom & 1
	shl1    r4, r4, r5                         ; r4 = (r4 << 1) | r5
	ublk                                       ; unblock shift-resets
	jmp     ecmul-skippuncture
nah:
	add     r4, r4, r4                         ; r4 *= 2
	add     r4, r4, r4                         ; r4 *= 2
ecmul-skippuncture:
	xor     r12, r12, r12                      ; r12 = 0 (bit-offset)
ecmul-inner:
; montgomery ladder on (mem[0-31], mem[32-63]), (mem[64-95], mem[96-127])
; copy mem[0-31] to t0, mem[32-63] to t2
	xor     r1, r1, r1                         ; r1 = 0 (offset, high bits)
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
ecmul-copy1:
	mld1    ~~, r2, r1                         ; load mem[r1,r2]
	mpld    ~~, r2, r1                         ; load t0[r1,r2]
	add2    r1, r1, ~~                         ; go to t2
	mpld    ~~, r2, r1                         ; load t2[r1,r2]
	mov     t0, mem, ~~                        ; t0[r1,r2] = mem[r1,r2]
	mov     t2, mem+32, ~~                     ; t2[r1,r2] = mem[r1,r2 + 32]
	ublk                                       ; unblock shift-resets
	sub     r1, r1, rom+16                     ; go back to t0 (subtract rom[16] = 2)
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, flags, r1                      ; r1 += carry
	jl      ecmul-copy1, r1, rom+16            ; if r1 < rom[16] = 2, loop
	mov     p1, rom+19, ~~                     ; p1 = rom[19] = 15
	jmp     addmodp                            ; call addmodp (t2 += t0)
addmodp<--15:
; now t2 stores Xn+Zn
; copy t2 to t6
	mov     r1, rom+16, ~~                     ; r1 = rom[16] = 2 (offset, high bits)
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
ecmul-copy2:
	mpld    ~~, r2, r1                         ; load t2[r1,r2]
	add     r1, r1, rom+18                     ; go to t6 (r1 += rom[18] = 4)
	mpld    ~~, r2, r1                         ; load t6[r1,r2]
	mov     t6, t2, ~~                         ; t6[r1,r2] = t2[r1,r2]
	ublk                                       ; unblock shift-resets
	add     r1, r1, rom+15                     ; go back to t2 (r1 += rom[15] = 12)
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, r1, flags                      ; r1 += carry
	jne     ecmul-copy2, r1, rom+18            ; if r1 != rom[18] = 4, loop
; copy -mem[32-63] to t2
	mov     r1, rom+16, ~~                     ; r1 = rom[16] = 2 (offset, high bits)
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
ecmul-copy3:
	mld1    ~~, r2, r1                         ; load mem[r1,r2]
	mpld    ~~, r2, r1                         ; load t2[r1,r2]
	xor     t2, mem, rom+19                    ; t2[r1,r2] = mem[r1,r2] ^ (rom[19] = 15)
	ublk                                       ; unblock shift-resets
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, flags, r1                      ; r1 += carry
	jl      ecmul-copy3, r1, rom+18            ; if r1 < rom[18] = 4, loop
	xor     t2+31, t2+31, rom+22               ; remove t2 msb (rom[22] = 8)
	mov     p1, rom+21, ~~                     ; p1 = rom[21] = 6
	jmp     addmodp                            ; call addmodp (t2 += t0)
addmodp<--6:
; now t2 stores Xn-Zn
; copy t2 to t10
	mov     r1, rom+16, ~~                     ; r1 = rom[16] = 2 (offset, high bits)
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
ecmul-copy4:
	mpld    ~~, r2, r1                         ; load t2[r1,r2]
	add     r1, r1, rom+22                     ; go to t10 (r1 += rom[22] = 8)
	mpld    ~~, r2, r1                         ; load t10[r1,r2]
	mov     t10, t2, ~~                        ; t10[r1,r2] = t2[r1,r2]
	ublk                                       ; unblock shift-resets
	add     r1, r1, rom+22                     ; go back to t2 (r1 += rom[22] = 8)
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, r1, flags                      ; r1 += carry
	jne     ecmul-copy4, r1, rom+18            ; if r1 != rom[18] = 4, loop

; copy mem[64-95] to t0, -mem[96-127] to t2
	xor     r1, r1, r1                         ; r1 = 0 (offset, high bits)
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
ecmul-copy5:
	mpld    ~~, r2, r1                         ; load t0[r1,r2]
	add2    r1, r1, ~~                         ; go to t2
	mpld    ~~, r2, r1                         ; load t2[r1,r2]
	add2    r1, r1, ~~                         ; r1 = 4
	mld1    ~~, r2, r1                         ; load mem[r1,r2]
	mov     t0, mem, ~~                        ; t0[r1,r2] = mem[r1,r2]
	xor     t2, mem+32, rom+19                 ; t2[r1,r2] = mem[r1,r2 + 32] ^ (rom[19] = 15)
	ublk                                       ; unblock shift-resets
	sub     r1, r1, rom+18                     ; go back to t0 (r1 -= rom[18] = 4)
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, flags, r1                      ; r1 += carry
	jl      ecmul-copy5, r1, rom+16            ; if r1 < rom[16] = 2, loop
	xor     t2+31, t2+31, rom+22               ; remove t2 msb (rom[22] = 8)
	mov     p1, rom+23, ~~                     ; p1 = rom[23] = 10
	jmp     addmodp                            ; call addmodp (t2 += t0)
addmodp<--10:
; now t2 stores Xm-Zm
; copy t2 to t8
	mov     r1, rom+16, ~~                     ; r1 = rom[16] = 2 (offset, high bits)
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
ecmul-copy6:
	mpld    ~~, r2, r1                         ; load t2[r1,r2]
	add     r1, r1, rom+21                     ; go to t8 (r1 += rom[21] = 6)
	mpld    ~~, r2, r1                         ; load t8[r1,r2]
	mov     t8, t2, ~~                         ; t8[r1,r2] = t2[r1,r2]
	ublk                                       ; unblock shift-resets
	add     r1, r1, rom+23                     ; go back to t2 (r1 += rom[23] = 10)
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, r1, flags                      ; r1 += carry
	jne     ecmul-copy6, r1, rom+18            ; if r1 != rom[18] = 4, loop

	mov     p2, rom+16, ~~                     ; p2 = rom[16] = 2
	jmp     mulmodp                            ; call mulmodp (t2 = t6 * t8)
mulmodp<--2:
; t2 is (Xm-Zm)(Xn+Zn)
; copy t2 to t14
	mov     r1, rom+16, ~~                     ; r1 = rom[16] = 2 (offset, high bits)
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
ecmul-copy7:
	mpld    ~~, r2, r1                         ; load t2[r1,r2]
	add     r1, r1, rom+15                     ; go to t14 (r1 += rom[15] = 12)
	mpld    ~~, r2, r1                         ; load t14[r1,r2]
	mov     t14, t2, ~~                        ; t14[r1,r2] = t2[r1,r2]
	ublk                                       ; unblock shift-resets
	add     r1, r1, rom+18                     ; go back to t2 (r1 += rom[18] = 4)
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, r1, flags                      ; r1 += carry
	jne     ecmul-copy7, r1, rom+18            ; if r1 != rom[18] = 4, loop

; copy mem[64-95] to t0, mem[96-127] to t2
	xor     r1, r1, r1                         ; r1 = 0 (offset, high bits)
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
ecmul-copy8:
	mpld    ~~, r2, r1                         ; load t0[r1,r2]
	add2    r1, r1, ~~                         ; go to t2
	mpld    ~~, r2, r1                         ; load t2[r1,r2]
	add2    r1, r1, ~~                         ; r1 = 4
	mld1    ~~, r2, r1                         ; load mem[r1,r2]
	mov     t0, mem, ~~                        ; t0[r1,r2] = mem[r1,r2]
	mov     t2, mem+32, ~~                     ; t2[r1,r2] = mem[r1,r2 + 32]
	ublk                                       ; unblock shift-resets
	add     r1, r1, rom+15                     ; go back to t0 (add rom[15] = 12)
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, flags, r1                      ; r1 += carry
	jl      ecmul-copy8, r1, rom+16            ; if r1 < rom[16] = 2, loop
	mov     p1, rom+22, ~~                     ; p1 = rom[22] = 8
	jmp     addmodp                            ; call addmodp (t2 += t0)
addmodp<--8:
; now t2 stores Xm+Zm
; copy t2 to t6, t10 to t8
	mov     r1, rom+16, ~~                     ; r1 = rom[16] = 2 (offset, high bits)
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
ecmul-copy9:
	mpld    ~~, r2, r1                         ; load t2[r1,r2]
	add     r1, r1, rom+18                     ; go to t6 (r1 += rom[18] = 4)
	mpld    ~~, r2, r1                         ; load t6[r1,r2]
	add2    r1, r1, ~~                         ; go to t8
	mpld    ~~, r2, r1                         ; load t8[r1,r2]
	add2    r1, r1, ~~                         ; go to t10
	mpld    ~~, r2, r1                         ; load t10[r1,r2]
	mov     t6, t2, ~~                         ; t6[r1,r2] = t2[r1,r2]
	mov     t8, t10, ~~                        ; t8[r1,r2] = t10[r1,r2]
	ublk                                       ; unblock shift-resets
	add     r1, r1, rom+22                     ; go back to t2 (r1 += rom[22] = 8)
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, r1, flags                      ; r1 += carry
	jne     ecmul-copy9, r1, rom+18            ; if r1 != rom[18] = 4, loop

	mov     p2, rom+23, ~~                     ; p2 = rom[23] = 10
	jmp     mulmodp                            ; call mulmodp (t2 = t6 * t8)
mulmodp<--10:
; t2 is (Xm+Zm)(Xn-Zn)
; copy t14 to t0, t2 to t10
	xor     r1, r1, r1                         ; r1 = 0 (offset, high bits)
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
ecmul-copy10:
	mpld    ~~, r2, r1                         ; load t0[r1,r2]
	add2    r1, r1, ~~                         ; go to t2
	mpld    ~~, r2, r1                         ; load t2[r1,r2]
	add     r1, r1, rom+22                     ; go to t10 (add rom[22] = 8)
	mpld    ~~, r2, r1                         ; load t10[r1,r2]
	add2    r1, r1, ~~                         ; go to t12
	add2    r1, r1, ~~                         ; go to t14
	mpld    ~~, r2, r1                         ; load t14[r1,r2]
	mov     t0, t14, ~~                        ; t0[r1,r2] = t14[r1,r2]
	mov     t10, t2, ~~                        ; t10[r1,r2] = t2[r1,r2]
	ublk                                       ; unblock shift-resets
	add1    r2, r2, ~~                         ; r2 += 1
	add2    r1, r1, ~~                         ; go back to t0
	add     r1, flags, r1                      ; r1 += carry
	jl      ecmul-copy10, r1, rom+16           ; if r1 < rom[16] = 2, loop
	mov     p1, rom+18, ~~                     ; p1 = rom[18] = 4
	jmp     addmodp                            ; call addmodp (t2 += t0)
addmodp<--4:
; t2 is (Xm-Zm)(Xn+Zn) + (Xm+Zm)(Xn-Zn)
; copy t2 to t6, t8
	mov     r1, rom+16, ~~                     ; r1 = rom[16] = 2 (offset, high bits)
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
ecmul-copy11:
	mpld    ~~, r2, r1                         ; load t2[r1,r2]
	add     r1, r1, rom+18                     ; go to t6 (r1 += rom[18] = 4)
	mpld    ~~, r2, r1                         ; load t6[r1,r2]
	add2    r1, r1, ~~                         ; go to t8
	mpld    ~~, r2, r1                         ; load t8[r1,r2]
	mov     t6, t2, ~~                         ; t6[r1,r2] = t2[r1,r2]
	mov     t8, t6, ~~                         ; t8[r1,r2] = t6[r1,r2]
	ublk                                       ; unblock shift-resets
	add     r1, r1, rom+23                     ; go back to t2 (r1 += rom[23] = 10)
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, r1, flags                      ; r1 += carry
	jne     ecmul-copy11, r1, rom+18           ; if r1 != rom[18] = 4, loop

	mov     p2, rom+21, ~~                     ; p2 = rom[21] = 6
	jmp     mulmodp                            ; call mulmodp (t2 = t6 * t8)
mulmodp<--6:
; t2 is ((Xm-Zm)(Xn+Zn) + (Xm+Zm)(Xn-Zn))^2
; copy t14 to t0, t2 to t4, -t10 to t2
	xor     r1, r1, r1                         ; r1 = 0 (offset, high bits)
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
ecmul-copy12:
	mpld    ~~, r2, r1                         ; load t0[r1,r2]
	add2    r1, r1, ~~                         ; go to t2
	mpld    ~~, r2, r1                         ; load t2[r1,r2]
	add2    r1, r1, ~~                         ; go to t4
	mpld    ~~, r2, r1                         ; load t4[r1,r2]
	pset    r1, r1, r1                         ; go to t10 (pset of 4,4 is 10; 5,5 is 11)
	mpld    ~~, r2, r1                         ; load t10[r1,r2]
	add     r1, r1, rom+18                     ; go back to t14 (r1 += rom[18] = 4)
	mpld    ~~, r2, r1                         ; load t14[r1,r2]
	mov     t0, t14, ~~                        ; t0[r1,r2] = t14[r1,r2]
	mov     t4, t2, ~~                         ; t4[r1,r2] = t2[r1,r2]
	xor     t2, t10, rom+3                     ; t2[r1,r2] = t10[r1,r2] ^ (rom[19] = 15)
	ublk                                       ; unblock shift-resets
	add1    r2, r2, ~~                         ; r2 += 1
	add2    r1, r1, ~~                         ; go back to t0
	add     r1, flags, r1                      ; r1 += carry
	jl      ecmul-copy12, r1, rom+16           ; if r1 < rom[16] = 2, loop
	mov     p1, rom+14, ~~                     ; p1 = rom[14] = 14
	and     t2+31, t2+31, rom+17               ; remove t2 msb (rom[17] = 7)
	jmp     addmodp                            ; call addmodp (t2 += t0)
addmodp<--14:
; t2 is (Xm-Zm)(Xn+Zn) - (Xm+Zm)(Xn-Zn)
; copy t2 to t6, t8
	mov     r1, rom+16, ~~                     ; r1 = rom[16] = 2 (offset, high bits)
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
ecmul-copy13:
	mpld    ~~, r2, r1                         ; load t2[r1,r2]
	add     r1, r1, rom+18                     ; go to t6 (r1 += rom[18] = 4)
	mpld    ~~, r2, r1                         ; load t6[r1,r2]
	add2    r1, r1, ~~                         ; go to t8
	mpld    ~~, r2, r1                         ; load t8[r1,r2]
	mov     t6, t2, ~~                         ; t6[r1,r2] = t2[r1,r2]
	mov     t8, t6, ~~                         ; t8[r1,r2] = t6[r1,r2]
	ublk                                       ; unblock shift-resets
	add     r1, r1, rom+23                     ; go back to t2 (r1 += rom[23] = 10)
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, r1, flags                      ; r1 += carry
	jne     ecmul-copy13, r1, rom+18           ; if r1 != rom[18] = 4, loop

	mov     p2, rom+19, ~~                     ; p2 = rom[19] = 15
	jmp     mulmodp                            ; call mulmodp (t2 = t6 * t8)
mulmodp<--15:
; t2 is ((Xm-Zm)(Xn+Zn) - (Xm+Zm)(Xn-Zn))^2
	je      ecmul-skipmulQx, r13, rom+29       ; if r13 = rom[29] = 0, skip mul by Qx
ecmul-mulQx:
; copy t2 to t8, rom[32-63] to t6
	sub     r6, r6, r6                         ; r6 = 0 (offset, high bits)
	xor     r7, r6, r6                         ; r7 = 0 (offset, low bits)
ecmul-copy13.5:
	add2    r6, r6, ~~                         ; go to t2
	mpld    ~~, r7, r6                         ; load t2[r6,r7]
	rld1    ~~, r7, r6                         ; load rom[r6,r7]
	add2    r6, r6, ~~                         ; go to t4
	add2    r6, r6, ~~                         ; go to t6
	mpld    ~~, r7, r6                         ; load t6[r6,r7]
	mov     t6, rom, ~~                        ; t6[r6,r7] = rom[r6,r7]
	add2    r6, r6, ~~                         ; go to t8
	mpld    ~~, r7, r6                         ; load t8[r6,r7]
	mov     t8, t2, ~~                         ; t8[r6,r7] = t2[r6,r7]
	ublk                                       ; unblock shift-resets
	add     r6, rom+22, r6                     ; reset r6 (r6 += rom[22] = 8)
	add1    r7, r7, ~~                         ; r7 += 1
	add     r6, r6, flags                      ; r6 += carry
	and     r2, rom+16, r6                     ; flags = (rom[16] = 2) > r6
	jne     ecmul-copy13.5, flags, rom+29      ; if flags != rom[29] = 0 (r6 < 2), loop
	add1    p2, r7, ~~                         ; p2 = 1
	xor     t6, t6, rom+24                     ; t6[0] ^= 3 (rom[32-63] stores Qx ^ 3)
	
	jne     ecmul-skippuncture2, r13, rom+15   ; if r13 isnt rom[15] = 12, skip the next part
; copy t12 to t6
	mov     r1, r13, ~~                        ; r1 = 12 (offset, high bits)
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
ecmul-copy13.75:
	mpld    ~~, r2, r1                         ; load t12[r1,r2]
	add     r1, rom+23, r1                     ; go to t6 (add rom[23] = 10)
	mpld    ~~, r2, r1                         ; load t6[r1,r2]
	mov     t6, t12, ~~                        ; t6[r1,r2] = t12[r1,r2]
	ublk                                       ; unblock shift-resets
	add     r1, r1, rom+21                     ; go back to t12 (r1 += rom[21] = 6)
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, r1, flags                      ; r1 += carry
	jne     ecmul-copy13.75, r1, rom+14        ; if r1 != rom[14] = 14, loop
ecmul-skippuncture2:
	jmp     mulmodp                            ; call mulmodp (t2 = t6 * t8)
ecmul-skipmulQx:
; copy t2 to t0
	xor     r1, r1, r1                         ; r1 = 0 (offset, high bits)
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
ecmul-copy14:
	mpld    ~~, r2, r1                         ; load t0[r1,r2]
	add2    r1, r1, ~~                         ; go to t2
	mpld    ~~, r2, r1                         ; load t2[r1,r2]
	mov     t0, t2, ~~                         ; t0[r1,r2] = t2[r1,r2]
	ublk                                       ; unblock shift-resets
	add     r1, r1, rom+14                     ; go back to t0 (r1 += rom[14] = 14)
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, r1, flags                      ; r1 += carry
	jne     ecmul-copy14, r1, rom+16           ; if r1 != rom[16] = 2, loop
	sub     p1, r1, r1                         ; p1 = 0
	jmp     addmodp                            ; call addmodp (t2 += t0)
addmodp<--0:
	mov     p1, rom+15, ~~                     ; p1 = rom[15] = 12
	jmp     addmodp                            ; call addmodp (t2 += t0)
addmodp<--12:
; t2 is [Px,Qx,t12][r13] * ((Xm-Zm)(Xn+Zn) - (Xm+Zm)(Xn-Zn))^2
	ext6    flags, r4, r12                     ; flags is 6 iff r4[r12] is set
	add     r1, flags, flags                   ; r1 is 12 iff r4[r12] is set
	add     r2, rom+18, r1                     ; r2 is 0 iff r4[r12] is set, else 4
; copy (t4, t2) to (mem[r2,0-31], mem[r2,32-63])
	xor     r1, flags, flags                   ; r1 = 0 (offset, low bits)
	mov     r3, rom+16, ~~                     ; r3 = rom[16] = 2 (offset, high bits)
ecmul-copy15:
	mld1    ~~, r1, r2                         ; load mem[r2,r1]
	mpld    ~~, r1, r3                         ; load t2[r3,r1]
	add2    r3, r3, ~~                         ; go to t4
	mpld    ~~, r1, r3                         ; load t4[r3,r1]
	mov     mem, t4, ~~                        ; mem[r2,r1] = t4[r3,r1]
	mov     mem+32, t2, ~~                     ; mem[r2,r1 + 32] = t2[r3,r1]
	ublk                                       ; unblock shift-resets
	sub     r3, r3, rom+16                     ; go back to t2 (subtract rom[16] = 2)
	add1    r1, r1, ~~                         ; r1 += 1
	addnf   r2, flags, r2                      ; r2 += carry
	add     r3, flags, r3                      ; r3 += carry
	jl      ecmul-copy15, r3, rom+18           ; if r3 < rom[18] = 4, loop
	sub     r2, rom+21, r2                     ; r2 = 6 - r2 (now 4 iff r4[r12] is set, else 0)
; copy (mem[r2,0-31], mem[r2,32-63]) to (t0, t2 and t4)
	xor     r1, r1, r1                         ; r1 = 0 (offset, low bits)
	xor     r3, r3, r3                         ; r3 = 0 (offset, high bits)
ecmul-copy16:
	mld1    ~~, r1, r2                         ; load mem[r2,r1]
	mpld    ~~, r1, r3                         ; load t0[r3,r1]
	add2    r3, r3, ~~                         ; go to t2
	mpld    ~~, r1, r3                         ; load t2[r3,r1]
	add2    r3, r3, ~~                         ; go to t4
	mpld    ~~, r1, r3                         ; load t4[r3,r1]
	mov     t0, mem, ~~                        ; t0[r3,r1] = mem[r2,r1]
	mov     t2, mem+32, ~~                     ; t2[r3,r1] = mem[r2,r1 + 32]
	mov     t4, mem, ~~                        ; t4[r3,r1] = mem[r2,r1 + 32]
	ublk                                       ; unblock shift-resets
	sub     r3, r3, rom+18                     ; go back to t0 (subtract rom[18] = 4)
	add1    r1, r1, ~~                         ; r1 += 1
	addnf   r2, flags, r2                      ; r2 += carry
	add     r3, flags, r3                      ; r3 += carry
	jl      ecmul-copy16, r3, rom+16           ; if r3 < rom[16] = 2, loop
	mov     p1, rom+20, ~~                     ; p1 = rom[20] = 5
	sub     p1, p1, rom+20                     ; p1 -= rom[20] (p1 = 0)
	add1    p1, p1, ~~                         ; p1 += 1 (p1 = 1)
	jmp     addmodp                            ; call addmodp (t2 += t0)
addmodp<--1:
; t2 is X + Z
; copy t2 to t6 and t8, -t4 to t2
	xor     r1, r1, r1                         ; r1 = 0 (offset, high bits)
	add2    r1, r1, ~~                         ; r1 = 2
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
ecmul-copy17:
	mpld    ~~, r2, r1                         ; load t2[r1,r2]
	add2    r1, r1, ~~                         ; go to t4
	mpld    ~~, r2, r1                         ; load t4[r1,r2]
	add2    r1, r1, ~~                         ; go to t6
	mpld    ~~, r2, r1                         ; load t6[r1,r2]
	add2    r1, r1, ~~                         ; go to t8
	mpld    ~~, r2, r1                         ; load t8[r1,r2]
	mov     t6, t2, ~~                         ; t6[r1,r2] = t2[r1,r2]
	mov     t8, t6, ~~                         ; t8[r1,r2] = t6[r1,r2]
	xor     t2, t4, rom+19                     ; t2[r1,r2] = t4[r1,r2] ^ (rom[19] = 15)
	ublk                                       ; unblock shift-resets
	add     r1, r1, rom+23                     ; go back to t2 (r1 += rom[23] = 10)
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, r1, flags                      ; r1 += carry
	jne     ecmul-copy17, r1, rom+18           ; if r1 != rom[18] = 4, loop
	and     t2+31, t2+31, rom+17               ; remove t2 msb (rom[17] = 7)
	mov     p1, rom+15, ~~                     ; p1 = rom[15] = 12
	xor     p1, rom+20, p1                     ; p1 ^= rom[20] = 5 (p1 = 9)
	jmp     addmodp                            ; call addmodp (t2 += t0)
addmodp<--9:
; t2 is X - Z
; copy t2 to t4
	mov     r1, rom+16, ~~                     ; r1 = rom[16] = 2 (offset, high bits)
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
ecmul-copy18:
	mpld    ~~, r2, r1                         ; load t2[r1,r2]
	add2    r1, r1, ~~                         ; go to t4
	mpld    ~~, r2, r1                         ; load t4[r1,r2]
	mov     t4, t2, ~~                         ; t4[r1,r2] = t2[r1,r2]
	ublk                                       ; unblock shift-resets
	add     r1, r1, rom+14                     ; go back to t2 (r1 += rom[14] = 14)
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, r1, flags                      ; r1 += carry
	jne     ecmul-copy18, r1, rom+18           ; if r1 != rom[18] = 4, loop
	
	mov     p2, rom+20, ~~                     ; p2 = rom[20] = 5
	jmp     mulmodp                            ; call mulmodp (t2 = t6 * t8)
mulmodp<--5:
; t2 is (X + Z)^2
; copy t4 to t6 and t8, t2 to t4
	mov     r1, rom+16, ~~                     ; r1 = rom[16] = 2 (offset, high bits)
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
ecmul-copy19:
	mpld    ~~, r2, r1                         ; load t2[r1,r2]
	add2    r1, r1, ~~                         ; go to t4
	mpld    ~~, r2, r1                         ; load t4[r1,r2]
	add2    r1, r1, ~~                         ; go to t6
	mpld    ~~, r2, r1                         ; load t6[r1,r2]
	add2    r1, r1, ~~                         ; go to t8
	mpld    ~~, r2, r1                         ; load t8[r1,r2]
	mov     t8, t4, ~~                         ; t8[r1,r2] = t4[r1,r2]
	mov     t6, t8, ~~                         ; t6[r1,r2] = t8[r1,r2]
	mov     t4, t2, ~~                         ; t4[r1,r2] = t2[r1,r2]
	ublk                                       ; unblock shift-resets
	sub     r1, r1, rom+21                     ; go back to t2 (r1 -= rom[21] = 6)
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, r1, flags                      ; r1 += carry
	jne     ecmul-copy19, r1, rom+18           ; if r1 != rom[18] = 4, loop

	mov     p2, rom+29, ~~                     ; p2 = rom[29] = 0
	jmp     mulmodp                            ; call mulmodp (t2 = t6 * t8)
mulmodp<--0:
; t2 is (X - Z)^2
; copy t2 to t6, t4 to t8
	mov     r1, rom+16, ~~                     ; r1 = rom[16] = 2 (offset, high bits)
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
ecmul-copy20:
	mpld    ~~, r2, r1                         ; load t2[r1,r2]
	add2    r1, r1, ~~                         ; go to t4
	mpld    ~~, r2, r1                         ; load t4[r1,r2]
	add2    r1, r1, ~~                         ; go to t6
	mpld    ~~, r2, r1                         ; load t6[r1,r2]
	mov     t6, t2, ~~                         ; t6[r1,r2] = t2[r1,r2]
	add2    r1, r1, ~~                         ; go to t8
	mpld    ~~, r2, r1                         ; load t8[r1,r2]
	mov     t8, t4, ~~                         ; t8[r1,r2] = t4[r1,r2]
	ublk                                       ; unblock shift-resets
	sub     r1, r1, rom+21                     ; go back to t2 (r1 -= rom[21] = 6)
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, r1, flags                      ; r1 += carry
	jne     ecmul-copy20, r1, rom+18           ; if r1 != rom[18] = 4, loop

	mov     p2, rom+14, ~~                     ; p2 = rom[14] = 14
	jmp     mulmodp                            ; call mulmodp (t2 = t6 * t8)
mulmodp<--14:
; t2 is (X - Z)^2(X + Z)^2
	ext6    flags, r4, r12                     ; flags is 6 iff r4[r12] is set
	and     r1, flags, rom+18                  ; r1 = flags & 4
; copy t2 to mem[r1,0-31]
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
	mov     r3, rom+16, ~~                     ; r3 = rom[16] = 2 (offset, high bits)
ecmul-copy21:
	mld1    ~~, r2, r1                         ; load mem[r1,r2]
	mpld    ~~, r2, r3                         ; load t2[r3,r2]
	mov     mem, t2, ~~                        ; mem[r1,r2] = t2[r3,r2]
	ublk                                       ; unblock shift-resets
	add1    r2, r2, ~~                         ; r2 += 1
	addnf   r1, flags, r1                      ; r1 += carry
	add     r3, flags, r3                      ; r3 += carry
	jl      ecmul-copy21, r3, rom+18           ; if r3 < rom[18] = 4, loop
; copy -t6 to t0, t8 to t2
	mov     r1, rom+29, ~~                     ; r1 = rom[29] = 0 (offset, high bits)
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
ecmul-copy22:
	mpld    ~~, r2, r1                         ; load t0[r1,r2]
	add2    r1, r1, ~~                         ; go to t2
	mpld    ~~, r2, r1                         ; load t2[r1,r2]
	add2    r1, r1, ~~                         ; go to t4
	add2    r1, r1, ~~                         ; go to t6
	mpld    ~~, r2, r1                         ; load t6[r1,r2]
	add2    r1, r1, ~~                         ; go to t8
	mpld    ~~, r2, r1                         ; load t8[r1,r2]
	mov     t2, t8, ~~                         ; t2[r1,r2] = t8[r1,r2]
	sub     t0, rom+19, t6                     ; t0[r1,r2] = (rom[19] = 15) - t6[r1,r2]
	ublk                                       ; unblock shift-resets
	xor     r1, r1, rom+22                     ; go back to t0 (r1 ^= rom[22] = 8)
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, r1, flags                      ; r1 += carry
	jne     ecmul-copy22, r1, rom+16           ; if r1 != rom[16] = 2, loop
	and     t0+31, t0+31, rom+17               ; remove t0 msb (rom[17] = 7)

	mov     p1, rom+24, ~~                     ; p1 = rom[24] = 3
	jmp     addmodp                            ; call addmodp (t2 += t0)
addmodp<--3:
; t2 is (X + Z)^2 - (X - Z)^2 = 4XZ
; copy t6 to t4, t2 to t8, write (A+2)/4 = 15602 = 0x3cf2 to t6
	mov     r1, rom+16, ~~                     ; r1 = rom[16] = 2 (offset, high bits)
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
ecmul-copy23:
	mpld    ~~, r2, r1                         ; load t2[r1,r2]
	add2    r1, r1, ~~                         ; go to t4
	mpld    ~~, r2, r1                         ; load t4[r1,r2]
	add2    r1, r1, ~~                         ; go to t6
	mpld    ~~, r2, r1                         ; load t6[r1,r2]
	mov     t4, t6, ~~                         ; t4[r1,r2] = t6[r1,r2]
	xor     t6, t6, t6                         ; t6[r1,r2] = 0
; load 0x9cf2 to t6, we'll subtract 0x6000 later
	jge     ecmul-skipconstant, r2, rom+18     ; if r2 >= rom[18] = 4, skip the next step
	add     r3, r1, rom+7                      ; r3 = r1 + (rom[23] = 10) (now either 0 or 1)
	jne     ecmul-skipconstant, t6, r3         ; if r3 != 0, (r1 != 6), skip the next step
	add     r5, r2, r2                         ; r5 = r2 + r2
	add2    r3, r3, ~~                         ; r3 = 2
	sub     r3, r3, r5                         ; r3 -= r5
	sub     t6, r3, r2                         ; t6 = r3 - r2 (equals [2, 15, 12, 9][r2])
ecmul-skipconstant:
	add2    r1, r1, ~~                         ; go to t8
	mpld    ~~, r2, r1                         ; load t8[r1,r2]
	mov     t8, t2, ~~                         ; t8[r1,r2] = t2[r1,r2]
	ublk                                       ; unblock shift-resets
	sub     r1, r1, rom+21                     ; go back to t2 (r1 -= rom[21] = 6)
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, r1, flags                      ; r1 += carry
	jne     ecmul-copy23, r1, rom+18           ; if r1 != rom[18] = 4, loop
	sub     t6+3, t6+3, rom+21                 ; fix t6[3] = 9 - (rom[21] = 6) = 3

	mov     p2, rom+15, ~~                     ; p2 = rom[15] = 12
	jmp     mulmodp                            ; call mulmodp (t2 = t6 * t8)
mulmodp<--12:
; t2 is (A+2)/4 * 4XZ
; copy t4 to t0
	xor     r1, p2, p2                         ; r1 = 0 (offset, high bits)
	xor     r2, p1, p1                         ; r2 = 0 (offset, low bits)
ecmul-copy24:
	mpld    ~~, r2, r1                         ; load t0[r1,r2]
	xor     r1, r1, rom+18                     ; go to t4 (r1 ^= rom[18] = 4)
	mpld    ~~, r2, r1                         ; load t4[r1,r2]
	mov     t0, t4, ~~                         ; t0[r1,r2] = t4[r1,r2]
	ublk                                       ; unblock shift-resets
	sub     r1, r1, rom+18                     ; go back to t0 (r1 -= rom[18] = 4)
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, r1, flags                      ; r1 += carry
	jne     ecmul-copy24, r1, rom+16           ; if r1 != rom[16] = 2, loop

	mov     p1, rom+17, ~~                     ; p1 = rom[17] = 7
	jmp     addmodp                            ; call addmodp (t2 += t0)
addmodp<--7:
; t2 is (X-Z)^2 + (A+2)/4 * 4XZ
; copy t2 to t6
	mov     r1, rom+16, ~~                     ; r1 = rom[16] = 2 (offset, high bits)
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
ecmul-copy25:
	mpld    ~~, r2, r1                         ; load t2[r1,r2]
	add     r1, r1, rom+18                     ; go to t6 (r1 += rom[18] = 4)
	mpld    ~~, r2, r1                         ; load t6[r1,r2]
	mov     t6, t2, ~~                         ; t6[r1,r2] = t2[r1,r2]
	ublk                                       ; unblock shift-resets
	add     r1, r1, rom+15                     ; go back to t2 (r1 += rom[15] = 12)
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, r1, flags                      ; r1 += carry
	jne     ecmul-copy25, r1, rom+18           ; if r1 != rom[18] = 4, loop

	mov     p2, rom+22, ~~                     ; p2 = rom[22] = 8
	jmp     mulmodp                            ; call mulmodp (t2 = t6 * t8)
mulmodp<--8:
; t2 is (4XZ)((X-Z)^2 + (A+2)/4 * 4XZ)
 	ext6    flags, r4, r12                     ; flags is 6 iff r4[r12] is set
	and     r1, flags, rom+18                  ; r1 = flags & 4
	add2    r1, r1, ~~                         ; r1 is 6 iff r4[r12] is set, else 2
; copy t2 to mem[r1,32-63]
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
	mov     r3, rom+16, ~~                     ; r3 = rom[16] = 2 (offset, high bits)
ecmul-copy26:
	mld1    ~~, r2, r1                         ; load mem[r1,r2]
	mpld    ~~, r2, r3                         ; load t2[r3,r2]
	mov     mem, t2, ~~                        ; mem[r1,r2] = t2[r3,r2]
	ublk                                       ; unblock shift-resets
	add1    r2, r2, ~~                         ; r2 += 1
	addnf   r1, flags, r1                      ; r1 += carry
	add     r3, flags, r3                      ; r3 += carry
	jl      ecmul-copy26, r3, rom+18           ; if r3 < rom[18] = 4, loop

; end inner loop body
	add1    r12, r12, ~~                       ; r12 += 1
	and     r1, r12, rom+24                    ; r1 = r12 & 3, flags = r12 > 3
	je      ecmul-inner, flags, rom+29         ; if flags is 0 (r12 < 4), loop
; end inner loop
	sub1    r10, r10, ~~                       ; r10 -= 1
	jne     ecmul-isnt15, r10, rom+19          ; if r10 isnt rom[19] = 15, skip the next instruction
	sub1    r11, r11, ~~                       ; r11 -= 1
ecmul-isnt15:
	jge     ecmul-outer, r11, rom+15           ; if r11 >= 12, loop
; end outer loop
; copy mem[32-63] to t10
	mov     r1, rom+16, ~~                     ; r1 = rom[16] = 2 (offset, high bits)
	xor     r2, r2, r2                         ; r2 = 0 (offset, low bits)
ecmul-copy27:
	mld1    ~~, r2, r1                         ; load mem[r1,r2]
	add     r1, r1, rom+22                     ; move to t10 (r1 += rom[22] = 8)
	mpld    ~~, r2, r1                         ; load t10[r1,r2]
	mov     t10, mem, ~~                       ; t10[r1,r2] = mem[r1,r2]
	ublk                                       ; unblock shift-resets
	and     r1, r1, rom+17                     ; reset r1 (r1 &= rom[17] = 7)
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, flags, r1                      ; r1 += carry
	jl      ecmul-copy27, r1, rom+18           ; if r1 < rom[18] = 4, loop
	jmp     invmodp                            ; call invmodp (t2 = t10^(-1))
invmodp<--after:
; copy t2 to t8, mem[0-31] to t6
	xor     r1, rom+4, rom+4                   ; r1 = 0 (offset, high bits)
	sub     r2, r9, r9                         ; r2 = 0 (offset, low bits)
ecmul-last-copy-i-swear:
	mld1    ~~, r2, r1                         ; load mem[r1,r2]
	add2    r1, r1, ~~                         ; move to t2
	mpld    ~~, r2, r1                         ; load t2[r1,r2]
	add     r1, r1, rom+18                     ; move to t6 (add rom[18] = 4)
	mpld    ~~, r2, r1                         ; load t6[r1,r2]
	mov     t6, mem, ~~                        ; t6[r1,r2] = mem[r1,r2]
	add2    r1, r1, ~~                         ; move to t8
	mpld    ~~, r2, r1                         ; load t8[r1,r2]
	mov     t8, t2, ~~                         ; t8[r1,r2] = t2[r1,r2]
	ublk                                       ; unblock shift-resets
	xor     r1, r1, rom+22                     ; reset r1 (r1 ^= rom[22] = 8)
	add1    r2, r2, ~~                         ; r2 += 1
	add     r1, flags, r1                      ; r1 += carry
	jl      ecmul-last-copy-i-swear, r1, rom+16; if r1 < rom[16] = 2, loop
	mov     p2, rom+24, ~~                     ; p2 = rom[24] = 3
	jmp     mulmodp                            ; call mulmodp (t2 = t6 * t8)
mulmodp<--3:
	je      ecmul<--12, r13, rom+15            ; jump if r13 = rom[15] = 12
	je      ecmul<--14, p3, rom+14             ; rom[14] = 14
	jge     ecmul<--11, p3, rom+22             ; rom[22] = 8
	jl      ecmul<--1, p3, rom+20              ; jump if p3 < (rom[20] = 5)
; return
	halt	fail
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;