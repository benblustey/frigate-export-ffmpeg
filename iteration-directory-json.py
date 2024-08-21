import os
import re
import json
import pytz
from datetime import datetime
import subprocess

def get_video_length(file_path):
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        return float(result.stdout)
    except ValueError:
        print(f"Could not retrieve video length for {file_path}")
        return 0

def process_mp4_files(base_path):
    la_timezone = pytz.timezone('America/Los_Angeles')
    json_output = {}
    eventClipData = []
    timeSlots = [0] * 24
    calendarEvents = []

    for root, _, files in sorted(os.walk(base_path)):
        directory_name = os.path.basename(root)
        if len(directory_name) == 10:
            calendarEvents.append({
                directory_name: len(files)
            })
            for f in sorted(files):
                if f.endswith('.mp4'):
                    print(f)
                    timestamp = int(re.search(r'\d+', f).group(0))
                    dt = datetime.fromtimestamp(timestamp, la_timezone)
                    file_name = dt.strftime('%y-%m-%d--%H-%M-%S.mp4')

                    date = dt.strftime('%Y-%m-%dT%H:%M:%S')
                    video_length = get_video_length(os.path.join(root, f))
                    
                    eventClipData.append({
                        'videoLength': video_length,
                        'fileName': file_name,
                        'date': date
                    })

                    # calendarEvents.directory_name += 1
                    eventhour = dt.hour
                    timeSlots[eventhour] += 1

    json_output['events'] = eventClipData
    json_output['timeSlots'] = timeSlots
    json_output['calendarEvents'] = calendarEvents
    return json_output

    return mp4_data

# Example usage
directory_path = './'
mp4_data = process_mp4_files(directory_path)

with open('mp4_data.json', 'w') as json_file:
    json.dump(mp4_data, json_file, indent=4)

