import json
import os
import re
import shutil
import subprocess
import pytz
import argparse
from datetime import datetime

def parse_arguments():
    parser = argparse.ArgumentParser(description="Analyze directory")
    parser.add_argument("-o", type=str, help="Set and output directory other than default")
    return parser.parse_args()

# Define the root directory videos are located
target_dir = './downloads'

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
  # SUCCESS
  eventClipData = []
  # LOGS
  processOutput = {}
  errorTotals = 0
  errorFiles = []
  successTotal = 0
  la_timezone = pytz.timezone('America/Los_Angeles')
  # Iterate over all items in the root directory
  for item in os.listdir(root_dir):
    if item.endswith('.mp4'):
      item_path = os.path.join(root_dir, item)
      timestamp = re.search(r'\d+', item).group(0)
      video_length = get_video_length(item_path)
      dt = datetime.fromtimestamp(int(timestamp), la_timezone)
      friendly_date = dt.strftime('%y-%m-%d--%H-%M-%S')

      if not video_length:
          print('Error processesing',item_path)
          errorFiles.append({'item_path': item_path})
          errorTotals += 1
          continue  # Continue to the next file
      
      successTotal += 1
      # Append event data
      eventClipData.append({
          'length': video_length,         # 11.138
          'src': item,                    # 1725254411.mp4
          'friendlyDate': friendly_date,  # 24-09-01--22-20-11
          'epoch': int(timestamp),        # 1725254411
          'starred': False,               # default value
          'approved': False               # default value
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
