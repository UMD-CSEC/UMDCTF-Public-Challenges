SafariZoneSecretHouse_Object:
	db $17 ; border block

	def_warp_events
	warp_event  2,  7, SAFARI_ZONE_WEST, 7
	warp_event  3,  7, SAFARI_ZONE_WEST, 7

	def_bg_events

	def_object_events
	object_event  3,  3, SPRITE_FISHING_GURU, STAY, DOWN, 1 ; person

	def_warps_to SAFARI_ZONE_SECRET_HOUSE
