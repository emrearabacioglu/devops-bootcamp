# Write a function that accepts a list of dictionaries with employee age (see example list from Exercise 3) and prints out the name and age of the youngest employee.
# Write a function that accepts a string and calculates the number of upper case letters and lower case letters.
# Write a function that prints the even numbers from a provided list.
# For cleaner code, declare these functions in its own helper Module and use them in the main.py file

def find_youngest(employees):
    youngest_name = ""
    youngest_age = 1000
    
    for employee in employees:
        age = int(employee["age"])
        if age < youngest_age:
            youngest_age = age
            youngest_name = employee["name"]
    print(f"Youngest employee: {youngest_name}, age: {youngest_age}")
    
    
def calculate_letters(input_text):
    upper = 0
    lower = 0
    for letter in input_text:
        if letter.isupper():
            upper += 1
        elif letter.islower():
            lower += 1
            
    print(f"Upper case letters: {upper}\nLower case letters: {lower}")
    
def print_even(input_list):
    even_list = []
    for i in input_list:
        if i % 2 == 0:
            even_list.append(i)
    print(even_list)