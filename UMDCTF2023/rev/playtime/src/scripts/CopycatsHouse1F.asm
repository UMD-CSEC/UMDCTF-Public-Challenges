CopycatsHouse1F_Script:
	jp EnableAutoTextBoxDrawing

CopycatsHouse1F_TextPointers:
	dw CopycatsHouse1FText1
	dw CopycatsHouse1FText2
	dw CopycatsHouse1FText3

CopycatsHouse1FText1:
	text_far _CopycatsHouse1FText1
	text_end

CopycatsHouse1FText2:
	text_far _CopycatsHouse1FText2
	text_end

CopycatsHouse1FText3:
	text_far _CopycatsHouse1FText3
	text_asm
	ld a, CHANSEY
	call PlayCry
	jp TextScriptEnd
