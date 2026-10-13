from helper import validate_and_execute, user_input_message

user_input = ""
while user_input != "exit":
    user_input = input(user_input_message)
    days_and_unit = user_input.split(":")
    print(days_and_unit)
    days_and_unit_dictionary = {"days": days_and_unit[0], "unit": days_and_unit[1]}
    print(days_and_unit_dictionary)
    validate_and_execute()

# built-in modules
''' 
import math
import random -- for mathematical operations and random number generation
import datetime -- for date and time operations
import os -- for operating system related operations
import sys  -- for system-specific parameters and functions
import json -- for JSON data handling
import re -- for regular expressions
import csv -- for CSV file handling
import collections -- for specialized container datatypes
import itertools -- for creating iterators for efficient looping
import functools -- for higher-order functions and operations on callable objects
import subprocess -- for spawning new processes, connecting to their input/output/error pipes, and obtaining their
return codes. 
import threading -- for threading operations
import time -- for time-related functions
import logging -- for logging events for tracking and debugging purposes
'''