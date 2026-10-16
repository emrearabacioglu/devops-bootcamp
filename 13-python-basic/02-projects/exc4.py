# Write a function that accepts a list of dictionaries with employee age (see example list from Exercise 3) and prints out the name and age of the youngest employee.
# Write a function that accepts a string and calculates the number of upper case letters and lower case letters.
# Write a function that prints the even numbers from a provided list.
# For cleaner code, declare these functions in its own helper Module and use them in the main.py file

import exc4helper
    

employees = [
    {
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
    },
    {
        "name": "Lisa",
        "age": 28,
        "birthday": "1992-01-15",
        "job": "QA Engineer",
        "address": {
            "city": "Berlin",
            "country": "Germany"
        }
    },
    {
        "name": "Mark",
        "age": 42,
        "birthday": "1978-04-02",
        "job": "Cloud Architect",
        "address": {
            "city": "Toronto",
            "country": "Canada"
        }
    },
    {
        "name": "Sara",
        "age": 25,
        "birthday": "1995-02-28",
        "job": "Data Analyst",
        "address": {
            "city": "London",
            "country": "UK"
        }
    }
]

exc4helper.find_youngest(employees)


exc4helper.calculate_letters("AAAAAAAAAAAAAAAAAAAAAasdaspdiukasdoiashudasiodKUHPIHUOIUYUFG")

exc4helper.print_even([1,2,3,4,5,6,7,8,9,10])