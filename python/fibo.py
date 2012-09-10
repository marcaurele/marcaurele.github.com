# -*- coding:UTF-8 -*-
# First try for the Fibonacci suite, é
a, b, c = 1, 1, 1
while c<5000:
    print(c, ":", b, type(b))
    a, b, c = b, a+b, c+1
