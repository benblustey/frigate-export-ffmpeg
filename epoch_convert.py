import sys
import time
import argparse
from datetime import datetime

def convert_date(date_input):
    # Check if the input is an epoch (integer or string of digits)
    if isinstance(date_input, (int, float)) or (isinstance(date_input, str) and date_input.isdigit()):
        # Convert epoch to 'YYYY-MM-DD HH:MM:SS'
        epoch = int(date_input)
        converted_date = datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')
        print(f"Converted epoch to: {converted_date}")
    
    else:
        try:
            # Try to parse the date input as 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD'
            try:
                date_obj = datetime.strptime(date_input, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                date_obj = datetime.strptime(date_input, '%Y-%m-%d')

            # Convert parsed date to epoch
            epoch = int(time.mktime(date_obj.timetuple()))
            print(f"Converted date to epoch: {epoch}")
        
        except ValueError:
            print("Invalid date format. Please use 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS' for date strings.")

if len(sys.argv) > 1:
    userDate = sys.argv[1]
    convert_date(userDate)
else:
    print("No date provided.")

# # Example usage
# date_input_epoch = 1725254411
# date_input_ymd = "2024-09-01"
# date_input_ymdhms = "2024-09-01 22:20:11"