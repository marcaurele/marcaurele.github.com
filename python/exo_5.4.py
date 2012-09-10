# -*- coding:UTF-8 -*-

interest_rate = 0.043 # 4.3%
amount = 100
year = 20
i=0
while i<year :
  amount += amount * interest_rate
  i += 1
  print("End of year ", i, ":", amount)
