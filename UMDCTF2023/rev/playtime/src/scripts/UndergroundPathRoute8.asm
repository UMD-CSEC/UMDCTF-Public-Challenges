UndergroundPathRoute8_Script:
	ld a, ROUTE_8
	ld [wLastMap], a
	jp EnableAutoTextBoxDrawing

UndergroundPathRoute8_TextPointers:
	dw UndergroundPathEntranceRoute8Text1

UndergroundPathEntranceRoute8Text1:
	text_far _UndergroundPathEntRoute8Text1
	text_end
