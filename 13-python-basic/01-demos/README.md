# Module 13 – Programming with Python

## Contents

| # | Section | What's inside |
|---|---|---|
| 1 | Python Basics: Variables, Functions, Conditionals, Error Handling & Loops | Days-to-hours converter with input validation |
| 2 | Lists & Sets | Indexing, `append()`, `add()`, `remove()`, duplicates |
| 3 | Dictionaries | Converter extended with `days:unit` input stored in a dictionary |
| 4 | Modules | Own `helper.py` module, built-in modules |
| 5 | Write Countdown Application | Remaining hours to a deadline with `datetime` |
| 6 | Packages, PyPI & pip | Virtual environment, installing `openpyxl` and `requests` |
| 7 | Automation with Python | Process `inventory.xlsx` with `openpyxl` |
| 8 | Classes and Objects | `Userclass` and `Postclass`, creating objects |
| 9 | API Request to GitLab | List my public repos with `requests` (GitHub API) |

## Takeaways

- **Input validation:** wrap `int(...)` in `try/except` so a non-numeric value prints a message instead of crashing. Zero and negative numbers get their own `elif`/`else` message.
- **Parsing input:** `split(", ")` for several values, `split(":")` for `days:unit` or `goal:date`. `set()` drops duplicate values.
- **List vs set:** a list keeps duplicates and `remove()` deletes only the first match. A set holds unique values.
- **Own modules:** move functions into `helper.py` and use `from helper import validate_and_execute, user_input_message`. Pass values as parameters instead of reading globals.
- **Dates:** `datetime.strptime(deadline, "%d.%m.%Y")` turns a string into a date. Subtract `datetime.today()` and use `total_seconds() / 60 / 60` for hours.
- **Virtual environment:** `python3 -m venv .venv` + `source .venv/bin/activate`. `which python` shows the `.venv` interpreter, and `pip install` goes only into this project.
- **openpyxl:** `load_workbook()`, pick the sheet with `["Sheet1"]`, read with `cell(row, col).value`. Loop from row 2 to `max_row + 1` to skip the header. Write to `cell(...).value` and `save()` to a new file.
- **Classes:** `__init__(self, ...)` sets the attributes, methods change them (`change_job_title()`). Classes in separate files are imported like modules.
- **API calls:** `requests.get(url).json()` returns a list of dicts, so fields are read with `repo['name']`, `repo['html_url']`.

******

<details>
<summary>Python Basics: Variables, Functions, Conditionals, Error Handling & Loops</summary>
 <br />

### Validating User Input

#### Days-to-Hours Converter
Built a small CLI program that converts a number of days into hours. Covered variables, functions, user input, `if/elif/else`, `try/except`, `while` and `for` loops in one script.

* The program runs in a `while` loop until the user types `exit`.
* Multiple values can be entered at once, separated by commas; `set()` removes duplicates.
* Input is validated: zero, negative numbers and non-numeric values get their own message instead of crashing the program.

The script:
```python
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
```

</details>

******

<details>
<summary>Lists & Sets</summary>
 <br />

### Working with Lists and Sets

#### Lists
Accessed list elements by index and added new elements with `append()`.
```python
    my_list = ["january", "february", "march"]
    print(my_list[2])
    my_list.append("april")
    print(my_list)
```

#### Sets
Used sets for unique values: iterated over a set, added and removed elements. Compared with a list, which keeps duplicates.
```python
    my_set = {"Jan", "Feb", "Mar"}
    for element in my_set:
        print(element)

    my_set.add("Apr")
    my_set.remove("Jan")

    my_list = ["Jan", "Feb", "Mar", "Jan"]
    my_list.remove("Jan")    # removes only the first "Jan"
```

</details>

******

<details>
<summary>Dictionaries</summary>
 <br />

### Extending the Converter with a Dictionary

#### Days and Conversion Unit as Key-Value Pairs
Extended the converter to support two units (`hours`, `minutes`). The user enters `days:unit` (e.g. `10:minutes`); the input is split and stored in a dictionary, then passed to the conversion logic.

```python
    def days_to_units(num_of_days, conversion_unit):
        if conversion_unit == "hours":
            return f"{num_of_days} days are {num_of_days * 24} hours"
        elif conversion_unit == "minutes" :
            return f"{num_of_days} days are {num_of_days * 24 * 60} minutes"
        else:
            return "unit is not valid"

    ...

    user_input = ""
    while user_input != "exit":
        user_input = input("enter number of days and conversion unit\n")
        days_and_unit = user_input.split(":")
        days_and_unit_dictionary = {"days": days_and_unit[0], "unit": days_and_unit[1]}
        validate_and_execute()
```

</details>

******

<details>
<summary>Modules</summary>
 <br />

### Splitting the Code into Modules

#### Own Module
Moved the functions and the input message into `helper.py` and imported them into the main script. `validate_and_execute()` now gets the dictionary as a parameter instead of reading a global variable.

`helper.py`:
```python
    def days_to_units(num_of_days, conversion_unit):
        ...

    def validate_and_execute(days_and_unit_dictionary):
        try:
            user_input_number = int(days_and_unit_dictionary["days"])
            ...

    user_input_message = "enter number of days and conversion unit\n"
```

`modules.py`:
```python
    from helper import validate_and_execute, user_input_message

    user_input = ""
    while user_input != "exit":
        user_input = input(user_input_message)
        days_and_unit = user_input.split(":")
        days_and_unit_dictionary = {"days": days_and_unit[0], "unit": days_and_unit[1]}
        validate_and_execute(days_and_unit_dictionary)
```

#### Built-in Modules
Python ships with modules that only need an `import`, e.g. `datetime`, `os`, `sys`, `json`, `re`, `csv`, `subprocess`, `logging`, `time`. `datetime` is used in the Countdown App below.

</details>

******

<details>
<summary>Demo Project: Write Countdown Application</summary>
 <br />

### Demo Executed: Countdown App

#### Goal and Deadline Calculation
The user enters a goal and a deadline as `goal:dd.mm.yyyy`. The deadline string is converted to a `datetime` object with `strptime()`, and the remaining time is calculated from today's date.

```python
    from datetime import datetime

    user_input = input("Enter your goal with a deadline seperated by colon:\n")
    input_list = user_input.split(":")

    goal = input_list[0]
    deadline = input_list[1]

    deadline_date = datetime.strptime(deadline, "%d.%m.%Y")
    today_date = datetime.today()
    time_till = deadline_date - today_date

    hours_till = int(time_till.total_seconds() / 60 / 60)
    print(f"Time remaining for deadline: {hours_till} hours!")
```

#### Execution
Ran the script with a goal and a deadline:
```bash
    (.venv) root@PC:~/modules/python-basic# /root/modules/python-basic/.venv/bin/python /root/modules/python-basic/countdown.py
    Enter your goal with a deadline seperated by colon:
    complete bootcamp:05.11.2026
    Time remaining for deadline: 725 hours!
```

</details>

******

<details>
<summary>Packages, PyPI & pip</summary>
 <br />

### Project Environment and External Packages

#### Virtual Environment
Created an isolated Python environment for the module in WSL, so packages are installed only for this project and not into the system Python.
```bash
    root@PC:~/modules/python-basic# python3 -m venv .venv
    root@PC:~/modules/python-basic# source .venv/bin/activate
    (.venv) root@PC:~/modules/python-basic# which python
    /root/modules/python-basic/.venv/bin/python
```

#### Installing Packages from PyPI
Installed the external packages used in the demo projects with `pip`:
```bash
    (.venv) root@PC:~/modules/python-basic# pip install openpyxl
    (.venv) root@PC:~/modules/python-basic# pip install requests
```

</details>

******

<details>
<summary>Demo Project: Automation with Python</summary>
 <br />

### Demo Executed: Spreadsheet Automation with openpyxl

#### Inventory Processing
The script reads `inventory.xlsx` (columns: Product No, Inventory, Price, Supplier), goes through every row once and:

* counts products per supplier,
* calculates the total inventory value per supplier,
* lists products with less than 10 items in stock,
* writes the inventory value of each product into column 5 and saves the result as a new file (`inventory_with_total_value.xlsx`).

`xlsxautomation.py`:
```python
    import openpyxl

    inv_file = openpyxl.load_workbook("inventory.xlsx")
    product_list = inv_file["Sheet1"]

    products_per_supplier = {}
    total_value_per_supplier = {}
    products_under_10_inv = {}

    for product_row in range(2, product_list.max_row + 1):
        supplier_name = product_list.cell(product_row, 4).value
        inventory = product_list.cell(product_row, 2).value
        price = product_list.cell(product_row, 3).value
        product_num = product_list.cell(product_row, 1).value
        inventory_price = product_list.cell(product_row, 5)

        # product count per supplier
        if supplier_name in products_per_supplier:
            current_num_products = products_per_supplier.get(supplier_name)
            products_per_supplier[supplier_name] = current_num_products +1
        else:
            print("adding a new supplier")
            products_per_supplier[supplier_name] = 1

        # total inventory value per supplier
        if supplier_name in total_value_per_supplier:
            current_total_value = total_value_per_supplier.get(supplier_name)
            total_value_per_supplier[supplier_name] = current_total_value + inventory * price
        else :
            total_value_per_supplier[supplier_name] = inventory * price

        # products under 10 in inventory
        if inventory < 10 :
            products_under_10_inv[int(product_num)] = int(inventory)

        # add value for total inventory price
        inventory_price.value = inventory * price

    print(products_per_supplier)
    print(total_value_per_supplier)
    print(products_under_10_inv)

    inv_file.save("inventory_with_total_value.xlsx")
```

#### Execution
Output: product count per supplier, total value per supplier, and products under 10 in stock (product no: count):
```bash
    (.venv) root@PC:~/modules/python-basic# /root/modules/python-basic/.venv/bin/python /root/modules/python-basic/xlsxautomation.py
    adding a new supplier
    adding a new supplier
    adding a new supplier
    {'AAA Company': 43, 'BBB Company': 17, 'CCC Company': 14}
    {'AAA Company': 10969059.95, 'BBB Company': 2375499.47, 'CCC Company': 8114363.62}
    {25: 7, 30: 6, 74: 2}
```

</details>

******

<details>
<summary>Classes and Objects</summary>
 <br />

### Object-Oriented Programming with Classes

#### User and Post Classes
Created two classes in separate files and used them from a main script:

* `Userclass` – attributes: email, name, password, job title; methods to change password / job title and print user info
* `Postclass` – a post with message and author

`Userclass`:
```python
    class Userclass :

        def __init__(self, email, name, password, current_job_title):
            self.email = email
            self.name = name
            self.password = password
            self.current_job_title = current_job_title

        def change_password(self, new_password):
            self.password = new_password

        def change_job_title(self, new_job_title):
            self.current_job_title = new_job_title

        def get_user_info(self):
            print(f"User {self.name} is currently works as {self.current_job_title}. \nYou can contact them at {self.email}")
```

`Postclass`:
```python
    class Postclass:

        def __init__(self, message, author):
            self.message = message
            self.author = author

        def get_post_info(self):
            print(f"Post: {self.message} written by {self.author}")
```

#### Creating Objects
Main script: created two users and a post, and changed one user's job title:
```python
    from userclass import Userclass
    from postclass import Postclass

    app_user_emre = Userclass("ee@aa.com", "Emre Arabacioglu", "pwd", "unemployed")
    app_user_emre.get_user_info()
    app_user_emre.change_job_title("DevOPS Engineer")
    app_user_emre.get_user_info()

    app_user_akif = Userclass("aa@aa.com", "Akif Arabacioglu", "pwd", "Engineer")
    app_user_akif.get_user_info()

    new_post = Postclass("on a secret mission today", app_user_akif.name)
    new_post.get_post_info()
```

</details>

******

<details>
<summary>Demo Project: API Request to GitLab</summary>
 <br />

### Demo Executed: Listing Public Repositories via the GitHub API

I used the GitHub API instead of GitLab.

#### API Request with requests
Sent a GET request to the GitHub REST API, parsed the JSON response and printed the name and URL of every public repository of my user.

```python
    import requests

    response = requests.get("https://api.github.com/users/emrearabacioglu/repos")
    my_repos = response.json()

    for repo in my_repos:
        print(f"Repository Name: {repo['name']}\nRepository Url: {repo['html_url']}\n")
```

#### Execution
Output lists every public repo with its URL:
```bash
    (.venv) root@PC:~/modules/python-basic# /root/modules/python-basic/.venv/bin/python /root/modules/python-basic/apirequest.py
    Repository Name: aws-exercises
    Repository Url: https://github.com/emrearabacioglu/aws-exercises

    Repository Name: cloud-exercises
    Repository Url: https://github.com/emrearabacioglu/cloud-exercises

    Repository Name: devops-bootcamp
    Repository Url: https://github.com/emrearabacioglu/devops-bootcamp

    Repository Name: devops-case
    Repository Url: https://github.com/emrearabacioglu/devops-case

    Repository Name: docker-exercises
    Repository Url: https://github.com/emrearabacioglu/docker-exercises

    Repository Name: java-app-chart
    Repository Url: https://github.com/emrearabacioglu/java-app-chart

    Repository Name: java-maven-app
    Repository Url: https://github.com/emrearabacioglu/java-maven-app

    Repository Name: java-terraform
    Repository Url: https://github.com/emrearabacioglu/java-terraform

    Repository Name: jenkins-exercises
    Repository Url: https://github.com/emrearabacioglu/jenkins-exercises

    Repository Name: jenkins-shared-library
    Repository Url: https://github.com/emrearabacioglu/jenkins-shared-library

    Repository Name: js-app
    Repository Url: https://github.com/emrearabacioglu/js-app

    Repository Name: terraform
    Repository Url: https://github.com/emrearabacioglu/terraform
```

</details>

******
