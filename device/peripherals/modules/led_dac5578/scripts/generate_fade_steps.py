increment = 1
values = []
value = 0
while value < 100:
    values.append(value)
    value = int(increment ** 1.6)
    increment += 1
values.append(100)
print(values)
print(list(reversed(values)))
