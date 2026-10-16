# Write a simple calculator program that:

# takes user input of 2 numbers and operation to execute
# handles the following operations: plus, minus, multiply, divide
# does proper user validation and give feedback: only numbers allowed
# Keeps the Calculator program running until the user types “exit”
# Keeps track of how many calculations the user has taken, and when the user exits the calculator program, prints out the number of calculations the user did
# Concepts covered: working with different data types, conditionals, type conversion, user input, user input validation
count = 0
while True:
    user_input = input("enter the operation(ex:2 + 2): ")
    if user_input == "q" :
        print(f"Count of calculations: {count}")
        break
    
    input_list = user_input.split()
    if len(input_list) != 3:
        print("wrong format.")
        continue
    try:
        num1 = float(input_list[0])
        num2 = float(input_list[2])
    except ValueError:
        print("Invalid input, enter numbers")
        continue
    
    if input_list[1] == "+":
        ans = num1 + num2
    elif input_list[1] == "-":
        ans = num1 - num2
    elif input_list[1] == "*":
        ans = num1 * num2
    elif input_list[1] == "/":
        if num2 == 0:
            print("cannot divide by 0")
            continue
        ans = num1 / num2
    else:
        print("Invalid operator, use + - * /")
        continue
    count += 1
    print(f"Result: {ans}")