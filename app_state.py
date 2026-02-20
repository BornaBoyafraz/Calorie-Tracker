import os
from App_Functions import typing_functions
user_name = typing_functions.type_input("Enter your first and last name: ").strip().lower().replace(" ", "_")
file_name = user_name + ".txt"  # Create filename from user name
foodData = 'foods.txt'

#DIR : director
userDataDIR = r'C:\Programming\Python\Calory Tracker\Users_Data'

def user_data_file_path(filename: str) -> str:
    return os.path.join(userDataDIR, filename)