import json
import os
import re
import shutil
import subprocess
import pytz
from datetime import datetime

# Define the root directory where the yyyy-mm-dd folders are located
target_dir = './'

# Define the directory where all .mp4 files will be moved
combined_dir = os.path.join(target_dir, 'combined')

# Ensure the 'combined' directory exists
if not os.path.exists(combined_dir):
    os.makedirs(combined_dir)

# Regex pattern for yyyy-mm-dd directory format
date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
la_timezone = pytz.timezone('America/Los_Angeles')
global errors

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

def iterrate_dir(root_dir):
  # setup JSON object
  # eventClipData = {}
  
  # SUCCESS
  eventClipData = []
  # LOGS
  processOutput = {}
  errorTotals = 0
  errorFiles = []
  successTotal = 0

  # Iterate over all items in the root directory
  for item in os.listdir(root_dir):
    item_path = os.path.join(root_dir, item)
    
    # Check if the item is a directory and matches the yyyy-mm-dd pattern
    if os.path.isdir(item_path) and date_pattern.match(item):
      # Iterate over files in the date directory
      for file_name in os.listdir(item_path):
        if file_name.endswith('.mp4'):
          
          # get timestamp int
          timestamp = re.search(r'\d+', file_name).group(0)
          
          # create file name
          new_file_name = timestamp + '.mp4'

          dt = datetime.fromtimestamp(int(timestamp), la_timezone)
          friendly_date = dt.strftime('%y-%m-%d--%H-%M-%S')

          # Source file path to move
          source_file = os.path.join(item_path, file_name)

          # CHAT Example
          # Destination file path
          destination_file = os.path.join(combined_dir, new_file_name)

          # Skip if the file already exists
          if os.path.isfile(destination_file):
              print("Skipping, file already exists:", destination_file)
              continue  # Continue to the next file

          # Get video length and check for ffmpeg errors
          video_length = get_video_length(source_file)
          if not video_length:
              print('Error processesing',source_file)
              errorFiles.append({'source_file': source_file})
              errorTotals += 1
              continue  # Continue to the next file

          # Move the .mp4 file to the 'combined' directory
          shutil.copyfile(source_file, destination_file)
          print(f"Moved: {source_file} -> {destination_file}")
          successTotal += 1
          # Append event data
          eventClipData.append({
              'length': video_length,         # 11.138
              'src': new_file_name,           # 1725254411.mp4
              'friendlyDate': friendly_date,  # 24-09-01--22-20-11
              'epoch': timestamp,             # 1725254411
              'starred': False                # default value
          })

  # Construct the Output JSON
  processOutput['errorTotals'] = errorTotals
  processOutput['errorFiles'] = errorFiles
  processOutput['successTotal'] = successTotal
  
  with open('process_output.json', 'w') as json_file:
      json.dump(processOutput, json_file, indent=4)

  with open('events_data.json', 'w') as json_file:
      json.dump(eventClipData, json_file, indent=4)

iterrate_dir(target_dir)
print("All .mp4 files have been moved to the 'combined' directory.")

