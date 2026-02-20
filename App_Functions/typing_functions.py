#LOADING MODULES
# time: Used for delays and sleep functions
# sys: Used for system-specific parameters and functions (like exit)

import time
import sys



# Function for typewriter effect
# Prints text character by character with a delay to create a typewriter animation effect
def type_print(text, speed=0.03):
    for char in text:
        sys.stdout.write(char)  # Write one character at a time
        sys.stdout.flush()      # Force output to appear immediately
        time.sleep(speed)       # Wait a bit before next character
    print()  # new line after finishing

# Function for typewriter effect with input
# Displays text with typewriter effect, then gets user input
def type_input(text, speed=0.03):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    return input("")   # <- takes input right after typing
