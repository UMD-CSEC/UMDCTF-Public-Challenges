UndergroundPathRoute7Copy_Object:
	db $a ; border block

	def_warp_events
	warp_event  3,  7, LAST_MAP, 6
	warp_event  4,  7, LAST_MAP, 6
	warp_event  4,  4, UNDERGROUND_PATH_WEST_EAST, 1

	def_bg_events

	def_object_events
	object_event  3,  2, SPRITE_GIRL, STAY, NONE, 1 ; person
	object_event  2,  4, SPRITE_MIDDLE_AGED_MAN, STAY, NONE, 2 ; person

	def_warps_to UNDERGROUND_PATH_ROUTE_7_COPY
