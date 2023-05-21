.section __TEXT,__text
.global _main
.align 2
_main:
    // execve("/System/Applications/Calculator.app/Contents/MacOS/Calculator", 0, 0)
    movk x1, #0x637b
    movk x1, #0x4654, lsl #16
    movk x1, #0x4344, lsl #32
    movk x1, #0x4d55, lsl #48
    str  x1, [sp, #-8]
    movk x1, #0x306c
    movk x1, #0x5f34, lsl #16
    movk x1, #0x6666, lsl #32
    movk x1, #0x656c, lsl #48
    str  x1, [sp, #-16]
    movk x1, #0x6c33
    movk x1, #0x6835, lsl #16
    movk x1, #0x5f73, lsl #32
    movk x1, #0x3376, lsl #48
    str  x1, [sp, #-24]
    movk x1, #0x7d21
    movk x1, #0x2133, lsl #16
    movk x1, #0x6430, lsl #32
    movk x1, #0x636c, lsl #48
    str  x1, [sp, #-32]
    mov	 x1, #32
    //mov  x4, #88 // Param 3
    //sub  x0, x4, #84 // Param 1
    //sub  x1, sp, x1 // Ptr to "/System/Applications/Calculator.app/Contents/MacOS/Calculator"
    //mov  x2, #32 // Param 2
    //sub x16, x4, #84//mov  x16, #4 // write syscall
    svc  #4269 // syscall