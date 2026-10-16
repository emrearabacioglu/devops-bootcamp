employees = [{
"name": "Tina",
"age": 30,
"birthday": "1990-03-10",
"job": "DevOps Engineer",
"address": {
    "city": "New York",
    "country": "USA"
  }
},

{
"name": "Tim",
"age": 35,
"birthday": "1985-02-21",
"job": "Developer",
"address": {
    "city": "Sydney",
    "country": "Australia"
  }
}]
# Write a Python Program that:

# Prints out - the name, job and city of each employee using a loop. The program must work for any number of employees in the list, not just 2.
# Prints the country of the second employee in the list by accessing it directly without the loop.

for employee in employees:
    print(f"Name: {employee["name"]} \nJob: {employee["job"]}\nCity: {employee["address"]["city"]}\n")
    
print(f"{employees[1]["address"]["country"]}")