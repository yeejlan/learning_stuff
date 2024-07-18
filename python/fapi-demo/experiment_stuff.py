import arrow

now = arrow.now()

arrow_obj = arrow.Arrow(2023, 1, 1, 12, 0, 0)
arrow_obj = now
print(now)


datetime_obj = arrow_obj._datetime
a = arrow.Arrow.fromdatetime(datetime_obj)

print(datetime_obj)  
print(a)

