.text
.globl main
main: 
	la $t0, k
	li $t2, 0
	li $t3, 1024


xp:
	li $t1, <data>
	sw $t1, ($t0)
	addi $t0, $t0, 4
	addi $t2, $t2, 4
	blt $t2, $t3, xp

	jal ec
	jal clr
	jal clrs
	jal s
	jal clrk

	li $v0, 10
	syscall

ec:
	la $s5, k
	li $s6, 0
	li $s7, 1024

qk:
	sw $ra, ($sp)
	jal hurrrrr
	jal clr
	lw $ra, ($sp)
	li $t1, 0
	ori $t1, $v0, 0

	lw $t4, ($s5)
	xor $t4, $t4, $t1
	sw $t4, ($s5)

	addi $s5, $s5, 4
	addi $s6, $s6, 4
	blt $s6, $s7, qk

	jr $ra

s:
	sw $ra, ($sp)
	jal clr
	lw $ra, ($sp)

	li $t0, 1024
	li $t1, 0
	la $t2, k

p:
	lw $t3, ($t2)
	addi $t2, $t2, 4
	lw $t4, ($t2)
	addi $t2, $t2, 4

	addi $t1, $t1, 8


	li $t5, 4278190080
	and $s7, $t4, $t5
	srl $s7, $s7, 24

	li $t5, 16711680
	and $s6, $t4, $t5
	srl $s6, $s6, 16

	li $t5, 65280
	and $s5, $t4, $t5
	srl $s5, $s5, 8

	li $t5, 255
	and $s4, $t4, $t5
	srl $s4, $s4, 0


	li $t5, 4278190080
	and $s3, $t3, $t5
	srl $s3, $s3, 24

	li $t5, 16711680
	and $s2, $t3, $t5
	srl $s2, $s2, 16

	li $t5, 65280
	and $s1, $t3, $t5
	srl $s1, $s1, 8

	li $t5, 255
	and $s0, $t3, $t5
	srl $s0, $s0, 0



	li $t5, 128
	and $t6, $s7, $t5
	lb $t7, a
	andi $t7, $t7, 127
	or $t7, $t7, $t6
	sb $t7, a

	li $t5, 64
	and $t6, $s7, $t5
	sll $t6, $t6, 1
	lb $t7, b
	andi $t7, $t7, 127
	or $t7, $t7, $t6
	sb $t7, b 

	li $t5, 32
	and $t6, $s7, $t5
	sll $t6, $t6, 2
	lb $t7, c
	andi $t7, $t7, 127
	or $t7, $t7, $t6
	sb $t7, c

	li $t5, 16
	and $t6, $s7, $t5
	sll $t6, $t6, 3
	lb $t7, d
	andi $t7, $t7, 127
	or $t7, $t7, $t6
	sb $t7, d

	li $t5, 8
	and $t6, $s7, $t5
	sll $t6, $t6, 4
	lb $t7, e
	andi $t7, $t7, 127
	or $t7, $t7, $t6
	sb $t7, e

	li $t5, 4
	and $t6, $s7, $t5
	sll $t6, $t6, 5
	lb $t7, f
	andi $t7, $t7, 127
	or $t7, $t7, $t6
	sb $t7, f

	li $t5, 2
	and $t6, $s7, $t5
	sll $t6, $t6, 6
	lb $t7, g
	andi $t7, $t7, 127
	or $t7, $t7, $t6
	sb $t7, g

	li $t5, 1
	and $t6, $s7, $t5
	sll $t6, $t6, 7
	lb $t7, h
	andi $t7, $t7, 127
	or $t7, $t7, $t6
	sb $t7, h


	li $t5, 128
	and $t6, $s6, $t5
	srl $t6, $t6, 1
	lb $t7, a
	andi $t7, $t7, 191
	or $t7, $t7, $t6
	sb $t7, a

	li $t5, 64
	and $t6, $s6, $t5
	lb $t7, b
	andi $t7, $t7, 191
	or $t7, $t7, $t6
	sb $t7, b 

	li $t5, 32
	and $t6, $s6, $t5
	sll $t6, $t6, 1
	lb $t7, c
	andi $t7, $t7, 191
	or $t7, $t7, $t6
	sb $t7, c

	li $t5, 16
	and $t6, $s6, $t5
	sll $t6, $t6, 2
	lb $t7, d
	andi $t7, $t7, 191
	or $t7, $t7, $t6
	sb $t7, d

	li $t5, 8
	and $t6, $s6, $t5
	sll $t6, $t6, 3
	lb $t7, e
	andi $t7, $t7, 191
	or $t7, $t7, $t6
	sb $t7, e

	li $t5, 4
	and $t6, $s6, $t5
	sll $t6, $t6, 4
	lb $t7, f
	andi $t7, $t7, 191
	or $t7, $t7, $t6
	sb $t7, f

	li $t5, 2
	and $t6, $s6, $t5
	sll $t6, $t6, 5
	lb $t7, g
	andi $t7, $t7, 191
	or $t7, $t7, $t6
	sb $t7, g

	li $t5, 1
	and $t6, $s6, $t5
	sll $t6, $t6, 6
	lb $t7, h
	andi $t7, $t7, 191
	or $t7, $t7, $t6
	sb $t7, h


	li $t5, 128
	and $t6, $s5, $t5
	srl $t6, $t6, 2
	lb $t7, a
	andi $t7, $t7, 223
	or $t7, $t7, $t6
	sb $t7, a

	li $t5, 64
	and $t6, $s5, $t5
	srl $t6, $t6, 1
	lb $t7, b
	andi $t7, $t7, 223
	or $t7, $t7, $t6
	sb $t7, b 

	li $t5, 32
	and $t6, $s5, $t5
	lb $t7, c
	andi $t7, $t7, 223
	or $t7, $t7, $t6
	sb $t7, c

	li $t5, 16
	and $t6, $s5, $t5
	sll $t6, $t6, 1
	lb $t7, d
	andi $t7, $t7, 223
	or $t7, $t7, $t6
	sb $t7, d

	li $t5, 8
	and $t6, $s5, $t5
	sll $t6, $t6, 2
	lb $t7, e
	andi $t7, $t7, 223
	or $t7, $t7, $t6
	sb $t7, e

	li $t5, 4
	and $t6, $s5, $t5
	sll $t6, $t6, 3
	lb $t7, f
	andi $t7, $t7, 223
	or $t7, $t7, $t6
	sb $t7, f

	li $t5, 2
	and $t6, $s5, $t5
	sll $t6, $t6, 4
	lb $t7, g
	andi $t7, $t7, 223
	or $t7, $t7, $t6
	sb $t7, g

	li $t5, 1
	and $t6, $s5, $t5
	sll $t6, $t6, 5
	lb $t7, h
	andi $t7, $t7, 223
	or $t7, $t7, $t6
	sb $t7, h


	li $t5, 128
	and $t6, $s4, $t5
	srl $t6, $t6, 3
	lb $t7, a
	andi $t7, $t7, 239
	or $t7, $t7, $t6
	sb $t7, a

	li $t5, 64
	and $t6, $s4, $t5
	srl $t6, $t6, 2
	lb $t7, b
	andi $t7, $t7, 239
	or $t7, $t7, $t6
	sb $t7, b 

	li $t5, 32
	and $t6, $s4, $t5
	srl $t6, $t6, 1
	lb $t7, c
	andi $t7, $t7, 239
	or $t7, $t7, $t6
	sb $t7, c

	li $t5, 16
	and $t6, $s4, $t5
	lb $t7, d
	andi $t7, $t7, 239
	or $t7, $t7, $t6
	sb $t7, d

	li $t5, 8
	and $t6, $s4, $t5
	sll $t6, $t6, 1
	lb $t7, e
	andi $t7, $t7, 239
	or $t7, $t7, $t6
	sb $t7, e

	li $t5, 4
	and $t6, $s4, $t5
	sll $t6, $t6, 2
	lb $t7, f
	andi $t7, $t7, 239
	or $t7, $t7, $t6
	sb $t7, f

	li $t5, 2
	and $t6, $s4, $t5
	sll $t6, $t6, 3
	lb $t7, g
	andi $t7, $t7, 239
	or $t7, $t7, $t6
	sb $t7, g

	li $t5, 1
	and $t6, $s4, $t5
	sll $t6, $t6, 4
	lb $t7, h
	andi $t7, $t7, 239
	or $t7, $t7, $t6
	sb $t7, h


	li $t5, 128
	and $t6, $s3, $t5
	srl $t6, $t6, 4
	lb $t7, a
	andi $t7, $t7, 247
	or $t7, $t7, $t6
	sb $t7, a

	li $t5, 64
	and $t6, $s3, $t5
	srl $t6, $t6, 3
	lb $t7, b
	andi $t7, $t7, 247
	or $t7, $t7, $t6
	sb $t7, b 

	li $t5, 32
	and $t6, $s3, $t5
	srl $t6, $t6, 2
	lb $t7, c
	andi $t7, $t7, 247
	or $t7, $t7, $t6
	sb $t7, c

	li $t5, 16
	and $t6, $s3, $t5
	srl $t6, $t6, 1
	lb $t7, d
	andi $t7, $t7, 247
	or $t7, $t7, $t6
	sb $t7, d

	li $t5, 8
	and $t6, $s3, $t5
	lb $t7, e
	andi $t7, $t7, 247
	or $t7, $t7, $t6
	sb $t7, e

	li $t5, 4
	and $t6, $s3, $t5
	sll $t6, $t6, 1
	lb $t7, f
	andi $t7, $t7, 247
	or $t7, $t7, $t6
	sb $t7, f

	li $t5, 2
	and $t6, $s3, $t5
	sll $t6, $t6, 2
	lb $t7, g
	andi $t7, $t7, 247
	or $t7, $t7, $t6
	sb $t7, g

	li $t5, 1
	and $t6, $s3, $t5
	sll $t6, $t6, 3
	lb $t7, h
	andi $t7, $t7, 247
	or $t7, $t7, $t6
	sb $t7, h


	li $t5, 128
	and $t6, $s2, $t5
	srl $t6, $t6, 5
	lb $t7, a
	andi $t7, $t7, 251
	or $t7, $t7, $t6
	sb $t7, a

	li $t5, 64
	and $t6, $s2, $t5
	srl $t6, $t6, 4
	lb $t7, b
	andi $t7, $t7, 251
	or $t7, $t7, $t6
	sb $t7, b 

	li $t5, 32
	and $t6, $s2, $t5
	srl $t6, $t6, 3
	lb $t7, c
	andi $t7, $t7, 251
	or $t7, $t7, $t6
	sb $t7, c

	li $t5, 16
	and $t6, $s2, $t5
	srl $t6, $t6, 2
	lb $t7, d
	andi $t7, $t7, 251
	or $t7, $t7, $t6
	sb $t7, d

	li $t5, 8
	and $t6, $s2, $t5
	srl $t6, $t6, 1
	lb $t7, e
	andi $t7, $t7, 251
	or $t7, $t7, $t6
	sb $t7, e

	li $t5, 4
	and $t6, $s2, $t5
	lb $t7, f
	andi $t7, $t7, 251
	or $t7, $t7, $t6
	sb $t7, f

	li $t5, 2
	and $t6, $s2, $t5
	sll $t6, $t6, 1
	lb $t7, g
	andi $t7, $t7, 251
	or $t7, $t7, $t6
	sb $t7, g

	li $t5, 1
	and $t6, $s2, $t5
	sll $t6, $t6, 2
	lb $t7, h
	andi $t7, $t7, 251
	or $t7, $t7, $t6
	sb $t7, h


	li $t5, 128
	and $t6, $s1, $t5
	srl $t6, $t6, 6
	lb $t7, a
	andi $t7, $t7, 253
	or $t7, $t7, $t6
	sb $t7, a

	li $t5, 64
	and $t6, $s1, $t5
	srl $t6, $t6, 5
	lb $t7, b
	andi $t7, $t7, 253
	or $t7, $t7, $t6
	sb $t7, b 

	li $t5, 32
	and $t6, $s1, $t5
	srl $t6, $t6, 4
	lb $t7, c
	andi $t7, $t7, 253
	or $t7, $t7, $t6
	sb $t7, c

	li $t5, 16
	and $t6, $s1, $t5
	srl $t6, $t6, 3
	lb $t7, d
	andi $t7, $t7, 253
	or $t7, $t7, $t6
	sb $t7, d

	li $t5, 8
	and $t6, $s1, $t5
	srl $t6, $t6, 2
	lb $t7, e
	andi $t7, $t7, 253
	or $t7, $t7, $t6
	sb $t7, e

	li $t5, 4
	and $t6, $s1, $t5
	srl $t6, $t6, 1
	lb $t7, f
	andi $t7, $t7, 253
	or $t7, $t7, $t6
	sb $t7, f

	li $t5, 2
	and $t6, $s1, $t5
	lb $t7, g
	andi $t7, $t7, 253
	or $t7, $t7, $t6
	sb $t7, g

	li $t5, 1
	and $t6, $s1, $t5
	sll $t6, $t6, 1
	lb $t7, h
	andi $t7, $t7, 253
	or $t7, $t7, $t6
	sb $t7, h


	li $t5, 128
	and $t6, $s0, $t5
	srl $t6, $t6, 7
	lb $t7, a
	andi $t7, $t7, 254
	or $t7, $t7, $t6
	sb $t7, a

	li $t5, 64
	and $t6, $s0, $t5
	srl $t6, $t6, 6
	lb $t7, b
	andi $t7, $t7, 254
	or $t7, $t7, $t6
	sb $t7, b 

	li $t5, 32
	and $t6, $s0, $t5
	srl $t6, $t6, 5
	lb $t7, c
	andi $t7, $t7, 254
	or $t7, $t7, $t6
	sb $t7, c

	li $t5, 16
	and $t6, $s0, $t5
	srl $t6, $t6, 4
	lb $t7, d
	andi $t7, $t7, 254
	or $t7, $t7, $t6
	sb $t7, d

	li $t5, 8
	and $t6, $s0, $t5
	srl $t6, $t6, 3
	lb $t7, e
	andi $t7, $t7, 254
	or $t7, $t7, $t6
	sb $t7, e

	li $t5, 4
	and $t6, $s0, $t5
	srl $t6, $t6, 2
	lb $t7, f
	andi $t7, $t7, 254
	or $t7, $t7, $t6
	sb $t7, f

	li $t5, 2
	and $t6, $s0, $t5
	srl $t6, $t6, 1
	lb $t7, g
	andi $t7, $t7, 254
	or $t7, $t7, $t6
	sb $t7, g

	li $t5, 1
	and $t6, $s0, $t5
	lb $t7, h
	andi $t7, $t7, 254
	or $t7, $t7, $t6
	sb $t7, h

	li $t4, 0
	li $t3, 0

	lbu $t5, a
	or $t4, $t4, $t5
	sll $t4, $t4, 8

	lbu $t5, b
	or $t4, $t4, $t5
	sll $t4, $t4, 8

	lbu $t5, c
	or $t4, $t4, $t5
	sll $t4, $t4, 8

	lbu $t5, d
	or $t4, $t4, $t5

	lbu $t5, e
	or $t3, $t3, $t5
	sll $t3, $t3, 8

	lbu $t5, f
	or $t3, $t3, $t5
	sll $t3, $t3, 8

	lbu $t5, g
	or $t3, $t3, $t5
	sll $t3, $t3, 8

	lbu $t5, h
	or $t3, $t3, $t5

	sw $t4, -4($t2)
	sw $t3, -8($t2)

	blt $t1, $t0, p

	jr $ra

hurrrrr:

	li $s0, 32
	li $s1, 0
	li $t8, 0

o:
	li $t0, 0
	li $t1, 0
	li $t2, 0
	li $t3, 0
	li $t4, 0
	li $t5, 0
	li $t6, 0
	li $t7, 0 

	srl $t8, $t8, 1
	lw $t0, st
	andi $t1, $t0, 1
	ori $t7, $t1, 0
	sll $t7, $t7, 31

	andi $t2, $t0, 2
	srl $t2, $t2, 1
	andi $t3, $t0, 32
	srl $t3, $t3, 5
	andi $t4, $t0, 256
	srl $t4, $t4, 8
	andi $t5, $t0, 4096
	srl $t5, $t5, 12
	andi $t6, $t0, 2147483648
	srl $t6, $t6, 31

	xor $t1, $t1, $t2
	xor $t1, $t1, $t3
	xor $t1, $t1, $t4
	xor $t1, $t1, $t5
	xor $t1, $t1, $t6

	srl $t0, $t0, 1
	sll $t1, $t1, 31
	or $t0, $t0, $t1
	or $t8, $t8, $t7


	addi $s1, $s1, 1
	sw $t0, st
	blt $s1, $s0, o

	addi $v0, $t8, 0
	jr $ra

clr:
	sb $zero, a
	sb $zero, b
	sb $zero, c
	sb $zero, d
	sb $zero, e
	sb $zero, f
	sb $zero, g
	sb $zero, h

	li $t0, 0
	li $t1, 0
	li $t2, 0
	li $t3, 0
	li $t4, 0
	li $t5, 0
	li $t6, 0
	li $t7, 0
	li $t8, 0
	li $t9, 0

	jr $ra

clrs:
	li $s0, 0
	li $s1, 0
	li $s2, 0
	li $s3, 0
	li $s4, 0
	li $s5, 0
	li $s6, 0
	li $s7, 0

	jr $ra

clrk:
	li $t0, 65535
	li $t1, 0
	la $t2, k
	li $t3, 1

l:
	sb $t3, ($t2)
	addi $t1, $t1, 1
	addi $t2, $t2, 1
	blt $t1, $t0, l

	jr $ra

.data
	a:  .byte 85
	b:  .byte 77
	c:  .byte 68
	d:  .byte 67
	e:  .byte 84
	f:  .byte 70
	g:  .byte 45
	h:  .byte 123
	a2: .byte 108
	b2: .byte 111
	c2: .byte 108
	d2: .byte 110
	e2: .byte 111
	f2: .byte 112
	g2: .byte 101
	h2: .byte 125
	st: .word 938214802

.align 2
	k:  .space 65536
