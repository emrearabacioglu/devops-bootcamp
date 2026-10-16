my_list = [1, 2, 2, 4, 4, 5, 6, 8, 10, 13, 22, 35, 52, 83]
# Write a program that prints out all the elements of the list that are higher than or equal to 10.
# Instead of printing the elements one by one, make a new list that has all the elements higher than or equal to 10 from this list in it and print out this new list.
# Ask the user for a number as input and print a list that contains only those elements from my_list that are higher than the number given by the user.
new_list = []
userinput = input("Enter a number: ")
num = int(userinput)

for i in my_list:
    if i >= num: 
        new_list.append(i)
        
print(f"List of numbers higer than or equal to {num}: {new_list}")