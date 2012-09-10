# -*- coding:UTF-8 -*-
# Exo 6.1
mph = input("Saisir votre vitesse en miles/heure:")
mph = float(mph)
kph = mph * 1.609
mps = kph / 3.6
print(mph, "miles/heure font:")
print("  ", kph, "km/h")
print("  ", mps, "m/s")