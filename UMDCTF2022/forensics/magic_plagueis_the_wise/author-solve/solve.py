#!/usr/bin/env python3

import shutil
import codecs

i = 1
while i <= 4464:
	with open(str(i), 'rb') as magic_file:
		original_data = magic_file.read(1)

	print(original_data.decode("utf-8"), end = "")

	i = i + 1
