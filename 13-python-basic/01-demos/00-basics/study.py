calculation_to_units = 24
name_of_unit = "hours"


def days_to_units(num_of_days):
    return f"{num_of_days} days are {num_of_days * calculation_to_units} {name_of_unit}"


def validate_and_execute():
    try:
        user_input_number = int(num_of_days_element)
        
        
        if user_input_number > 0 :
            calculated_value = days_to_units(user_input_number)
            print(calculated_value)
        elif user_input_number == 0 :
            print("you entered zero, no conversion!\n")
        else:
            print("you entered a negative number, no conversion!\n")
    except: 
        print("your input is not a valid number!\n")



user_input = ""
while user_input != "exit":
    user_input = input("enter number of days seperated with comma and program will convert it to hours:\n")
    list_of_days = user_input.split(", ")
    
    for num_of_days_element in set(list_of_days):
        validate_and_execute()


