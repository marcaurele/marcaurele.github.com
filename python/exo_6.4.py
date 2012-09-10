# -*- coding:UTF-8 -*-

inp = input("Veuillez entrer une valeur : ")
resu = []
while len(inp) > 0 :
  resu.append(inp)
  inp = input("Veuillez entrer une valeur : ")
print(resu)