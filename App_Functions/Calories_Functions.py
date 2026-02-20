#LOADING MODULES
# ast: Used to safely evaluate strings containing Python literals (like dictionaries)
# os: Used for file operations like checking if files exist and removing files
# time: Used for delays and sleep functions
# sys: Used for system-specific parameters and functions (like exit)
# typing_function: Used for self-made functions like "type_print" and " type_input"

import ast
import os
import time
import sys
from App_Functions import typing_functions

# navigating to the new path
sys.path.append("..")
import app_state
username = app_state.user_name
file_name = app_state.file_name
foodData = app_state.foodData
# Name of the food database file that stores meal names and their calorie values



# function to close the program
# Gracefully exits the program with a goodbye message
def closing_program():
    typing_functions.type_print("Exiting the program. Goodbye!")
    time.sleep(1)
    sys.exit()



# Functions for saving values to a file
# This function merges new data with existing data in the file
# If a key already exists, it gets replaced with the new value
# If a key doesn't exist, it gets added
def save_value(input_value, filename):
    # Parse the input_value (which is a dictionary string) back to a dictionary
    # input_value is a string like "{'key': 'value'}" that needs to be converted to a dict
    new_values = ast.literal_eval(input_value)
    
    # Try to load existing dictionary from file
    # If file exists, load it; if not, start with empty dictionary
    try:
        file_content = load_value(filename).strip()
        if file_content:
            existing_values = ast.literal_eval(file_content)  # Convert string to dictionary
        else:
            existing_values = {}  # Empty file means empty dictionary
    except (FileNotFoundError, ValueError, SyntaxError, OSError):
        # If file doesn't exist, is empty, or has invalid data, start with empty dictionary
        existing_values = {}
    
    # Update existing dictionary with new values (this replaces existing keys and adds new ones)
    # .update() merges new_values into existing_values, overwriting duplicates
    existing_values.update(new_values)
    
    # Save the updated dictionary back to the file
    with open(app_state.user_data_file_path(filename), 'w') as f:
        f.write(str(existing_values))  # Convert dictionary back to string for storage

# Functions for loading values from a file
# Reads the entire file content and returns it as a string
def load_value(filename):
    with open(app_state.user_data_file_path(filename), 'r') as f:
        read = f.read()
    return read

# Function to ask the user if they want to save the new data too
# After calculating calories, asks if user wants to save the remaining calories for later use
def ask_to_save_new_data_too(calories_left, day_type):
    continue_choice = typing_functions.type_input("Do you want to save the new data too? (yes/no): ").strip().lower()
    if continue_choice == "yes":
        # Load the user's data
        values = ast.literal_eval(load_value(file_name))
        # Save the calories left for tracking (so user can resume later)
        if day_type == "rest days":
            values["Calories Left Rest Day"] = calories_left
        elif day_type == "workout days":
            values["Calories Left Workout Day"] = calories_left
        save_value(str(values), file_name)
        typing_functions.type_print("Your data has been saved successfully.")
        return
    elif continue_choice == "no":
        return  # User doesn't want to save, just return
    else:
        typing_functions.type_print("Invalid choice. Please try again.")
        ask_to_save_new_data_too(calories_left, day_type)  # Recursively ask again


# Function to add a new meal that is not in the database to the database
# Adds a new meal entry to the foods.txt file in CSV format (name,calories)
def add_meal_to_database(foodData, meal_name=None, calories=None):
    # Use provided meal_name or ask for it
    # If meal_name is provided, format it; otherwise ask user
    if meal_name is None:
        meal_name = typing_functions.type_input("Enter the name of the meal you want to add: ").strip().lower().replace(" ", "_")
    else:
        # Format the provided meal_name (lowercase, spaces to underscores)
        meal_name = meal_name.strip().lower().replace(" ", "_")
    
    # Always ask for calories (since we need calories per 100g)
    # Display name with spaces for user-friendly output
    display_name = meal_name.replace("_", " ")
    calories = typing_functions.type_input(f"Enter the calories for {display_name} per 100g: ").strip()

    # Append the new meal to the food database file
    with open(foodData, 'a') as file:  # 'a' mode appends to end of file
        file.write(f"{meal_name},{calories}\n")  # Format: meal_name,calories
    
    # Return the calories that were added (as integer for calculations)
    return int(calories)


# Function to calculate remaining calories after a meal
# Searches for a meal in the database and returns its calories
# If meal not found, adds it to database and returns the calories
def meal_calculator(foodData, meal_name, calories_left):
    # Format the meal name for searching (lowercase, spaces to underscores)
    meal_name = meal_name.strip().lower().replace(" ", "_")

    # Search through the food database file
    with open(foodData, 'r') as file:
        for line in file:
            line = line.strip()

            if not line:
                continue # skip empty lines
            
            # Split the line into food name and calories
            # Format in file is: meal_name,calories
            try:
                name, Cal = line.split(",", 1)  # Split on first comma only (in case meal name has commas)
                name = name.strip().lower()  # Format for comparison
                Cal = Cal.strip()
            except ValueError:
                continue  # Skip invalid lines (lines without comma)

            # Check if this is the meal we're looking for
            if meal_name == name:
                nice_meal = meal_name.replace("_", " ")  # Format for display
                meal_name = meal_name.strip().lower().replace("_", " ")
                typing_functions.type_print(f"{meal_name} has {Cal} calories per 100g.")

                return int(Cal) #Return just the meal calories

    # Meal not found in database
    nice_meal = meal_name.replace("_", " ") 
    typing_functions.type_print(f"Sorry, we couldn't find {nice_meal} in the database.")
    typing_functions.type_print("Let's add it to the database.")
    # Add meal to database and get the calories that were added
    meal_calories = add_meal_to_database(foodData, nice_meal, calories_left)
    typing_functions.type_print(f"{nice_meal} has been added to the database with {meal_calories} calories per 100g.")
    # Return the calories so the calculation can continue
    return meal_calories


class UserRequest():
    #changing the information for the user
    # Allows user to update their name, rest day calories, or workout day calories
    def changing_info(filename):
        global user_name, file_name  # Need to modify global variables
        #loading the values (just to verify file exists)
        load_value(file_name)
        typing_functions.type_print("Let's change your info...")
        time.sleep(1)

        # Asking what the user wants to change
        changeChoice = int(typing_functions.type_input("What do you want to change?\n 1. Your Name\n 2. Rest Day Calories\n 3. Workout Day Calories\n Your choice (1/2/3): "))
        # Changing the chosen info
        if changeChoice == 1:
            # Change user name - requires creating new file and deleting old one
            new_name = typing_functions.type_input("Enter your new name: ").strip().lower().replace(" ", "_")
            values = ast.literal_eval(load_value(file_name))
            values["user_name"] = new_name
            save_value(str(values), new_name + ".txt")  # Save to new filename
            os.remove(file_name)  # Delete old file
            user_name = new_name  # Update the global variable
            file_name = user_name + ".txt"  # Update the file_name variable
            typing_functions.type_print("Your name has been changed successfully.")
        elif changeChoice == 2:
            # Update rest day calorie goal
            new_rest_day_calories = int(typing_functions.type_input("Enter your new rest day calories: "))
            values = ast.literal_eval(load_value(file_name))
            values["Rest Day Calories"] = new_rest_day_calories
            save_value(str(values), file_name)
            typing_functions.type_print("Your rest day calories have been changed successfully.")
        elif changeChoice == 3:
            # Update workout day calorie goal
            new_workout_day_calories = int(typing_functions.type_input("Enter your new workout day calories: "))
            values = ast.literal_eval(load_value(file_name))
            values["Workout Day Calories"] = new_workout_day_calories
            save_value(str(values), file_name)
            typing_functions.type_print("Your workout day calories have been changed successfully.")
        else:
            typing_functions.type_print("Invalid choice. Please try again.")
            UserRequest.changing_info()  # Recursively call to try again
        
        UserRequest.User_Choice()  # Return to main menu

    # Function to calculate calories
    # Main function for calculating remaining calories and meal tracking
    def calculate_calories():
        typing_functions.type_print("ALRIGHT!Let's calculate your calories...")
        time.sleep(1)
        caloriesTaken = int(typing_functions.type_input("How many calories have you taken until now?: "))

        #asking for the info we need
        # User chooses whether to calculate for rest days or workout days
        goalForDay = typing_functions.type_input("Do you want to know your calories for rest days or workout days?(rest day/workout): ").strip().lower()

        #the user wants the goal for rest days
        if goalForDay == "rest days" or goalForDay == "rest day":
            # Load the user's rest day calorie goal from their file
            restDayCalories = ast.literal_eval(load_value(file_name))["Rest Day Calories"]
            time.sleep(1)
            # Calculate how many calories are left
            caloriesLeftForRestDay = restDayCalories - caloriesTaken

            # Check if user exceeded, reached, or has calories left
            if caloriesLeftForRestDay < 0:
                # User ate more than their goal
                typing_functions.type_print("You have exceeded your calorie limit for rest days.")
                typing_functions.type_print(f"You have exceeded by {-caloriesLeftForRestDay} calories.")
            elif caloriesLeftForRestDay == 0:
                # User exactly reached their goal
                typing_functions.type_print("You have reached your calorie limit for rest days.")
                typing_functions.type_print("You have 0 calories left.")
            else:
                # User still has calories left - check if there's saved progress
                #checking if there is a saved data for the rest days
                values = ast.literal_eval(load_value(file_name))
                if "Calories Left Rest Day" in values and values["Calories Left Rest Day"] is not None:
                    # Found saved data - ask if user wants to use it
                    newChoice = typing_functions.type_input("We found a saved data for your rest days. Do you want to use it? (yes/no): ").strip().lower()
                    if newChoice == "yes":
                        # Use saved calories left instead of calculated
                        caloriesLeftForRestDay = int(values["Calories Left Rest Day"])
                    elif newChoice == "no":
                        # Use the newly calculated calories
                        typing_functions.type_print("Okay, We will use the calculated data for your rest days.")
                        pass
                    else:
                        typing_functions.type_print("Invalid choice. Please try again.")
                        UserRequest.calculate_calories()  # Start over
                        return
                
                #continue to calculate the calories
                # Now ask about a meal to calculate remaining calories after eating
                typing_functions.type_print(f"You have {caloriesLeftForRestDay} calories left for your rest days.")
                mealName = typing_functions.type_input("Enter the name of your meal: ").strip().lower()
                typing_functions.type_print("Calculating calories for your meal...")
                time.sleep(2)

                # Subtracting the meal calories from the remaining calories
                meal_cal = meal_calculator(foodData, mealName, caloriesLeftForRestDay)  # Get meal calories from database
                caloriesLeftForRestDay -= int(meal_cal)  # Subtract meal calories from remaining
                typing_functions.type_print(f"After eating {mealName}, you have {caloriesLeftForRestDay} calories left for your rest days.")
                ask_to_save_new_data_too(caloriesLeftForRestDay, "rest days")  # Ask if user wants to save this

        #the user wants the goal for workout days
        # Same logic as rest days but for workout day calorie goals
        elif goalForDay == "workout" or goalForDay == "workout days" or goalForDay == "workout day":
            # Load the user's workout day calorie goal from their file
            workoutDayCalories = ast.literal_eval(load_value(file_name))["Workout Day Calories"]
            time.sleep(1)
            # Calculate how many calories are left
            caloriesLeftForWorkoutDay = workoutDayCalories - caloriesTaken
            
            # Check if user exceeded, reached, or has calories left
            if caloriesLeftForWorkoutDay < 0:
                # User ate more than their goal
                typing_functions.type_print("You have exceeded your calorie limit for workout days.")
                typing_functions.type_print(f"You have exceeded by {-caloriesLeftForWorkoutDay} calories.")
            elif caloriesLeftForWorkoutDay == 0:
                # User exactly reached their goal
                typing_functions.type_print("You have reached your calorie limit for workout days.")
                typing_functions.type_print("You have 0 calories left.")
            else:
                # User still has calories left - check if there's saved progress
                #checking if there is a saved data for the workout days
                values = ast.literal_eval(load_value(file_name))
                if "Calories Left Workout Day" in values and values["Calories Left Workout Day"] is not None:
                    # Found saved data - ask if user wants to use it
                    newChoice = typing_functions.type_input("We found a saved data for your workout days. Do you want to use it? (yes/no): ").strip().lower()
                    if newChoice == "yes":
                        # Use saved calories left instead of calculated
                        caloriesLeftForWorkoutDay = int(values["Calories Left Workout Day"])
                    elif newChoice == "no":
                        # Use the newly calculated calories
                        typing_functions.type_print("Okay, We will use the calculated data for your workout days.")
                        pass
                    else:
                        typing_functions.type_print("Invalid choice. Please try again.")
                        UserRequest.calculate_calories()  # Start over
                        return
                
                #continue to calculate the calories
                # Now ask about a meal to calculate remaining calories after eating
                typing_functions.type_print(f"You have {caloriesLeftForWorkoutDay} calories left for your workout days.")
                mealName = typing_functions.type_input("Enter the name of your meal: ").strip().lower()
                typing_functions.type_print("Calculating calories for your meal...")
                time.sleep(2)
                
                # Subtracting the meal calories from the remaining calories
                meal_cal = meal_calculator(foodData, mealName, caloriesLeftForWorkoutDay)  # Get meal calories from database
                caloriesLeftForWorkoutDay -= int(meal_cal)  # Subtract meal calories from remaining
                typing_functions.type_print(f"After eating {mealName}, you have {caloriesLeftForWorkoutDay} calories left for your workout days.")
                ask_to_save_new_data_too(caloriesLeftForWorkoutDay, "workout days")  # Ask if user wants to save this
        
        else:
            # User entered invalid choice for day type
            typing_functions.type_print("Invalid choice. Please try again.")
            UserRequest.calculate_calories()  # Start over
        UserRequest.User_Choice()  # Return to main menu

    # Function to ask for users choice
    # Main menu that displays options and handles user selection
    def User_Choice():

        while True:  # Keep showing menu until user exits

            try:
                #asking the user what the user wants to do
                # Display menu and get user's choice
                userChoice = int(typing_functions.type_input("Please choose from the menue below:\n"
                                            "1. Calculate calories for me\n" \
                                            "2. Change my info\n" \
                                            "3. Exit the program \n" \
                                            "Your choice (1/2/3): "
                                            ))
                
                #user wants to calculate the calories
                if userChoice == 1:
                    UserRequest.calculate_calories()  # Go to calorie calculation
                    return  # Return to menu after calculation
                
                #user wants to change the info
                elif userChoice == 2:
                    UserRequest.changing_info(filename=file_name)  # Go to info change menu
                    return  # Return to menu after changing info
                
                #user wants to exit the program
                elif userChoice == 3:
                    closing_program()  # Exit the program
                    return
                
                #invalid choice (number not 1, 2, or 3)
                else:
                    typing_functions.type_print("Invalid choice. Please try again.")
                
            except ValueError:    
                #invalid choice (user entered non-number)
                typing_functions.type_print("Invalid choice. Please try again.")


