# -*- coding:UTF-8 -*-
n,g,t = 1,1,0
while n<65 :
    print(n, g)
    n,g,t = n+1, g*2, t+g
print("Total:", t)
