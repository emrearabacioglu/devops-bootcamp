# Write a program that:

# reads file "employees.xlsx"  with the following information/
# columns: "name", "years of experience", "job title", "date of birth"

# creates a new spreadsheet file "employees_sorted.xlsx" with following info/
# columns: "name", "years of experience", where the years of experience is sorted in descending order: so the employee name with the most experience in years is on top.

import openpyxl

employees_file = openpyxl.load_workbook("employees.xlsx")
employee_list = employees_file["Sheet1"]
employees = []

for employee_row in range(2, employee_list.max_row + 1):
    name = employee_list.cell(employee_row, 1).value
    years = employee_list.cell(employee_row, 2).value
    
    dictionary = {
        "Name": name,
        "Experience": years
    }
    
    employees.append(dictionary)
    
employees_sorted = sorted(employees, key=lambda employee: employee["Experience"], reverse=True)


wb = openpyxl.Workbook()
ws = wb.active
ws.append(["Name", "Years of experience"])

for employee in employees_sorted:
    ws.append([employee["Name"], employee["Experience"]])
    
wb.save("sorted_by_experience.xlsx")