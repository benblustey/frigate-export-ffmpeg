import os
import sys
import argparse
import subprocess
import requests
import json
from datetime import datetime, timedelta

DIR = "/mnt/nvr/frigate/cron_exports"
URL = "http://192.168.1.81:5000/api/events"
EVENTS_FILTER = "?camera=front_yard&labels=fireworks,explosion"
OUTPUT_DIR = "./completed"

def epoch_convert(epoch_time):
    return datetime.fromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M:%S')

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process video clips")
    parser.add_argument("-d", type=str, help="Specify a date to process YYYY-MM-DD")
    parser.add_argument("-f", action="store_true", help="Force reprocess. This will remove the date folder")
    parser.add_argument("-c", action="store_true", help="Processes the current day up to current time")
    parser.add_argument("-t", action="store_true", help="Test run. Only outputs the txt files, but does not download the clips or start the FFMPEG process.")
    parser.add_argument("-s", type=str, help="Set a custom start time YYYY-MM-DD")
    parser.add_argument("-e", type=str, help="Set a custom end time YYYY-MM-DD")
    return parser.parse_args()

def main():
    args = parse_arguments()

    current_time = int(datetime.now().timestamp())
    end_time = int((datetime.now().replace(hour=6, minute=0, second=0) + timedelta(days=1)).timestamp())
    start_time = int((datetime.now().replace(hour=6, minute=0, second=0) - timedelta(days=1)).timestamp())
    process_date = args.d
    custom_start = args.s
    custom_end = args.e

    if process_date:
        print(f"Processing Date Provided {process_date}")
        start_time = int(datetime.strptime(f"{process_date} 06:00:00", "%Y-%m-%d %H:%M:%S").timestamp())
        end_time = int((datetime.strptime(f"{process_date} 06:00:00", "%Y-%m-%d %H:%M:%S") + timedelta(days=1)).timestamp())
    elif args.c:
        print("Processing Today starting at 06:00")
        start_time = int(datetime.now().replace(hour=6, minute=0, second=0).timestamp())
        end_time = current_time
    elif custom_start:
        print(f"Processing Custom Range {custom_start} - {custom_end}")
        start_time = int(datetime.strptime(f"{custom_start} 06:00:00", "%Y-%m-%d %H:%M:%S").timestamp())
        end_time = int((datetime.strptime(f"{custom_end} 06:00:00", "%Y-%m-%d %H:%M:%S") + timedelta(days=1)).timestamp())
    else:
        process_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    date_filter = f"&after={start_time}&before={end_time}"

    if os.path.exists(process_date) and args.f:
        confirm = input(f"Are you sure you want to delete ./{process_date} folder? (y/n) ")
        if confirm.lower() == 'y':
            print(f"Removing directory ./{process_date}")
            os.system(f"rm -rf ./{process_date}")
    elif not args.t:
        os.makedirs(process_date, exist_ok=True)
        print(f"Making directory {process_date}")

    print(f":: {URL}{EVENTS_FILTER}{date_filter}")

    response = requests.get(f"{URL}{EVENTS_FILTER}{date_filter}")
    clips = json.loads(response.text)
    videos_processed = 0

    for clip in clips:
        clip_name = f"{clip['camera']}-{clip['id']}"
        if not os.path.exists(f"{process_date}/{clip_name}.mp4"):
            print(clip['id'])
            if not args.t:
                clip_url = f"{URL}/{clip['id']}/clip.mp4"
                r = requests.get(clip_url)
                with open(f"{process_date}/{clip_name}.mp4", 'wb') as f:
                    f.write(r.content)
            videos_processed += 1
        elif args.t:
            print(clip['id'])
            videos_processed += 1
        else:
            print("File Already Exists")

    if args.t:
        print(f"Currrent_Time: {epoch_convert(current_time)}")
        print(f"Start_Time: {epoch_convert(start_time)}")
        print(f"End_Time: {epoch_convert(end_time)}")
        print(f"API_URL: {URL}{EVENTS_FILTER}&after={start_time}&before={end_time}")

    if videos_processed != 0 or args.f:
        print(f"Processed {videos_processed} Events for {process_date}")
        # if not args.t:
        #     print(f"Sending {process_date} to ffmpeg_process.sh")
        #     os.system(f"./ffmpeg_process.sh -d {process_date}")
    else:
        print("NOTHING TO DO - Thanks for all the fish!")

if __name__ == "__main__":
    main()
