# Write a program that:

# accepts user's birthday as input
# and calculates how many days, hours and minutes are remaining till the birthday
# prints out the result as a message to the user

from datetime import datetime 
userinput = input("Enter your birthday(dd/mm): ")
day, month = userinput.split("/")
now = datetime.now()
next_birthday_date = datetime(now.year, int(month), int(day))

if next_birthday_date < now:
    next_birthday_date = next_birthday_date.replace(year=now.year + 1)

time_till = next_birthday_date - now

hours = time_till.seconds // 3600
minutes = (time_till.seconds % 3600) // 60

print(f"{time_till.days} days, {hours} hours and {minutes} minutes remaninig till your birthday")