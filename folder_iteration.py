import os
import json
from datetime import datetime
import pytz
import re

def iterate_directories(base_path):
    result = []
    monthtimeslots = [0] * 24

    for directory_name in sorted(os.listdir(base_path)):
        directory_path = os.path.join(base_path, directory_name)

        if os.path.isdir(directory_path) and len(directory_name) == 10:
            # print(directory_name)
            try:
                # Check if directory name is in the format 'YYYY-MM-DD'
                year, month, day = map(int, directory_name.split('-'))
            except ValueError:
                continue

            daytimeslots = [0] * 24
            # print(type(daytimeslots))
            mp4_files = []
            # iterate over the files
            for f in sorted(os.listdir(directory_path)):
                if f.endswith('.mp4'):
                # Regex to match the timestamp
                    timestamp = int(re.search(r'(\d+)', f).group(0))
                    # # Los Angeles timezone
                    la_timezone = pytz.timezone('America/Los_Angeles')
                    eventhour = datetime.fromtimestamp(timestamp, la_timezone).hour
                    mp4_files.append(f)
                    # increase the current value by 1
                    daytimeslots[eventhour] += 1
                    monthtimeslots[eventhour] += 1
            # print(daytimeslots)
            directory_info = {
                'date': directory_name,
                'total': len(mp4_files),
                'files': mp4_files,
                'times': daytimeslots
            }
            # print("daytimeslots",daytimeslots)
            result.append(directory_info)
    print('TimeSlots',monthtimeslots)
    return result

base_directory = '/Users/bsteyaert/Documents/development/frigate-export-ffmpeg/'
data = iterate_directories(base_directory)

with open('output.json', 'w') as json_file:
    json.dump(data, json_file, indent=4)