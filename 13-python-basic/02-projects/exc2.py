print(f"########################## 1st exc ##########################\n")

employee = {
"name": "Tim",
"age": 30,
"birthday": "1990-03-10",
"job": "DevOps Engineer"
}

# Write a Python Script that:

# Updates the job to Software Engineer
# Removes the age key from the dictionary
# Loops through the dictionary and prints the key:value pairs one by one

employee["job"] = "Software Engineer"
del employee["age"]
for key, value in employee.items():
    print(f"{key}: {value}")

print(f"\n\n########################## 2nd exc ##########################\n")

dict_one = {'a': 100, 'b': 400} 
dict_two = {'x': 300, 'y': 200}
# Write a Python Script that:

# Merges these two Python dictionaries into 1 new dictionary.
# Sums up all the values in the new dictionary and prints it out
# Prints the max and minimum values of the dictionary
merged_dict = dict_one | dict_two

print(merged_dict)

total = 0
for i in merged_dict.values():
    num = int(i)
    total = total + num
    
print(f"\nsum of values= {total}")

print(f"\nMax value: {max(list(merged_dict.values()))}\nMin value: {min(list(merged_dict.values()))}")