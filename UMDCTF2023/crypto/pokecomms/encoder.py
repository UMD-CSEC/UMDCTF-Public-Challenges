
plaintext = "UMDCTF{P1K4CHU_Once upon a time, there was a young boy named Ash who dreamed of becoming the world's greatest Pokemon trainer. He set out on a journey with his trusty Pokemon partner, Pikachu, a cute and powerful electric-type Pokemon. As Ash and Pikachu traveled through the regions, they encountered many challenges and made many friends. But they also faced their fair share of enemies, including the notorious Team Rocket, who were always trying to steal Pikachu. Despite the odds stacked against them, Ash and Pikachu never gave up. They trained hard and battled even harder, always looking for ways to improve their skills and strengthen their bond. And along the way, they learned valuable lessons about friendship, determination, and the power of believing in oneself. Eventually, Ash and Pikachu's hard work paid off. They defeated powerful opponents, earned badges from Gym Leaders, and even competed in the prestigious Pokemon League tournaments. But no matter how many victories they achieved, Ash and Pikachu never forgot where they came from or the importance of their friendship. In the end, Ash and Pikachu became a legendary team, admired by Pokemon trainers around the world. And although their journey may have had its ups and downs, they always knew that as long as they had each other, they could overcome any obstacle that stood in their way}".replace(" ","_")
output = ""

for c in plaintext:
	curr = bin(ord(c)).replace("0b", "")
	while len(curr) < 8:
		curr = "0" + curr
	for k in curr:
		if int(k) == 0:
			output += " CHU!"
		else:
			output += " PIKA"
	output += "\n"

print(output)
