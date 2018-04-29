


hscan = [ '0.0000', '0.0625', '0.1250', '0.1875', '0.2500', '0.3125', '0.3750', '0.4375', '0.5000', '0.5625', '0.6250', '0.6875', '0.7500', '0.8125', '0.8750', '0.9375', '1.0000' ]
vscan = [ '0.0000', '0.1111', '0.2222', '0.3333', '0.4444', '0.5556', '0.6667', '0.7778', '0.8889', '1.0000' ]

index=0

print("// LED CONFIGURATION")
print("\"leds\" :")
print("[")

for y in range (0, 9):
	for x in range (0, 16):
		print(" {")
		print("  \"index\" : %d," % index)
		print("  \"hscan\" : { \"minimum\" : %s, \"maximum\" : %s }," % (hscan[x],hscan[x+1]) )
		print("  \"vscan\" : { \"minimum\" : %s, \"maximum\" : %s }" % (vscan[y],vscan[y+1]) )
		index=index+1
		if index<144 :
			print(" },")
			print("")
		else:
			print(" }")

print("],")


