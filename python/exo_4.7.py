# -*- coding:UTF-8 -*-
# Afficher les 20 premiers termes de la table de mult de 7, avec une * pour les mult de 3

i=1
while i<=20 :
    print(i*7, end='')
    if (i*7)%3 == 0:
      print("*", end=' ')
    else :
      print("", end=' ')
    i += 1
print("")