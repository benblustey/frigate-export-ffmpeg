import json
import os
import re
import subprocess
import ffmpeg
import pytz
import argparse
from datetime import datetime

def parse_arguments():
    parser = argparse.ArgumentParser(description="Analyze directory")
    parser.add_argument("-o", type=str, help="Set and output directory other than default")
    return parser.parse_args()

# Define the root directory videos are located
target_dir = '/Volumes/frigate_final_data'

def get_video_length(file_path):
    try:
        probe = ffmpeg.probe(file_path)
        video_stream = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
        duration = float(video_stream['duration'])
        return float(duration)
    except Exception as e:
        print(f"Could not retrieve video length for {file_path}: {e}")
        return 0

def iterate_dir(root_dir, output_dir=None):
    # If no output directory is specified, use the root directory
    if output_dir is None:
        output_dir = root_dir

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
            iso_date = dt.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
            formatted_date = dt.strftime('%d %b %Y %H:%M:%S')

        if not video_length:
            print('Error processing',item_path)
            errorFiles.append({'item_path': item_path})
            errorTotals += 1
            continue  # Continue to the next file
        
        successTotal += 1
        # Append event data
        eventClipData.append({
            'length': video_length,          # 11.138
            'src': item,                     # 1725254411.mp4
            'eventDate': iso_date,           # 2025-01-02T12:00:00.000+00:00
            'formattedDate': formatted_date, # 3 Jan 2025 12:00:00
            'epoch': int(timestamp),         # 1725254411
            'starred': False,                # default value
            'approved': False                # default value
        })

    # Construct the Output JSON
    processOutput['errorTotals'] = errorTotals
    processOutput['errorFiles'] = errorFiles
    processOutput['successTotal'] = successTotal
    
    with open(os.path.join(output_dir, 'process_output.json'), 'w') as json_file:
        json.dump(processOutput, json_file, indent=4)

    with open(os.path.join(output_dir, 'events_data.json'), 'w') as json_file:
        json.dump(eventClipData, json_file, indent=4)

if __name__ == '__main__':
    args = parse_arguments()
    if args.o:
        target_dir = args.o
    iterate_dir(target_dir, output_dir='.')
