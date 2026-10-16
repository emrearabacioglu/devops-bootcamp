# Write a program that:

# runs until the user guesses a number (hint: while loop)
# generates a random number between 1 and 9 (including 1 and 9)
# asks the user to guess the number
# then prints a message to the user, whether they guessed too low, too high
# if the user guesses the number right, print out YOU WON! and exit the program
# Hint: Use the built-in random module to generate random numbers https://docs.python.org/3/library/random.html

# Concepts covered: Built-In Module, User Input, Comparison Operator, While loop
import random
num = random.randint(1,100)

while True:
    guess = input("guess a number between 1 and 100: ")
    try:
        guess_num = int(guess)
    except ValueError:
        print("Enter a number")
        continue
    if guess_num < num:
        print("you guessed too low")
    elif guess_num > num :
        print("you guessed too high")
    else:
        print("you won!")
        break