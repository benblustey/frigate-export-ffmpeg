import os
import sys
import argparse
import subprocess
import requests
import json
import re
from datetime import datetime, timedelta

# DIR = "/mnt/nvr/frigate/cron_exports" ## not used
URL = "http://192.168.1.81:5000/api/events"
EVENTS_FILTER = "?camera=front_yard&labels=fireworks,explosion"

def epoch_convert(epoch_time):
    return datetime.fromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M:%S')

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process video clips")
    parser.add_argument("-t", action="store_true", help="Test run. Only outputs the txt files, but does not download the clips or start the FFMPEG process.")
    parser.add_argument("-d", type=str, help="Specify a date to process YYYY-MM-DD")
    parser.add_argument("-f", action="store_true", help="Force reprocess. This will remove the date folder")
    parser.add_argument("-s", type=str, help="Set a custom start time YYYY-MM-DD")
    parser.add_argument("-e", type=str, help="Set a custom end time YYYY-MM-DD")
    parser.add_argument("-o", type=str, help="Set and output directory other than default")
    # parser.add_argument("-c", action="store_true", help="Processes the current day up to current time")
    return parser.parse_args()

## CONVERTERS
def epoch_convert(epoch_time): ## 1728457200
    return datetime.fromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M:%S')
def yymmdd_convert(yymmdd): ## 2024-10-09
    return (datetime.strptime(yymmdd, '%Y-%m-%d')).timestamp()
def return_end_of_day(epoch_value): ## 1728457200
    date_obj = datetime.utcfromtimestamp(epoch_value)
    end_of_day = datetime.combine(date_obj, datetime.max.time()) - timedelta(microseconds=1)
    return int(end_of_day.timestamp())

def main():
    args = parse_arguments()

    current_time = int(datetime.now().timestamp())
    end_time = int((datetime.now().replace(hour=6, minute=0, second=0) + timedelta(days=1)).timestamp())
    start_time = int((datetime.now().replace(hour=6, minute=0, second=0) - timedelta(days=1)).timestamp())
    process_date = args.d
    provided_start = args.s
    provided_end = args.e
    output_directory = "./downloads"

    ## Process Start Time
    if args.s:
        print(provided_start)
        start_time = yymmdd_convert(provided_start)
    elif not process_date:
        yesterday = datetime.now() + timedelta(days=-1)
        start_time = int(yesterday.replace(hour=0, minute=0, second=0).timestamp())
    ## Process End Time
    if args.e: ## 2024-10-09
        print(provided_end)
        end_time = return_end_of_day(yymmdd_convert(provided_end))
    elif not process_date:
        yesterday = datetime.now() + timedelta(days=-1)
        end_time = int(yesterday.replace(hour=23, minute=59, second=59,microsecond=999999).timestamp())
    print("Start Time: ",start_time,"\nEnd Time: ",end_time)

    if process_date:
        start_time = yymmdd_convert(process_date)
        end_time = return_end_of_day(yymmdd_convert(process_date))

    if end_time < start_time:
        return("Dates don't work loser")

    if args.o:
        output_directory = args.o

    if os.path.exists(output_directory) and args.f:
        confirm = input(f"Are you sure you want to delete ./{output_directory} folder? This may include downloads that have not been processed.\n(y/n) ")
        if confirm.lower() == 'y':
            print(f"Removing directory ./{output_directory}")
            os.system(f"rm -rf ./{output_directory}")

    date_filter = f"&after={start_time}&before={end_time}"

    response = requests.get(f"{URL}{EVENTS_FILTER}{date_filter}")
    clips = json.loads(response.text)
    videos_processed = 0

    for clip in clips:
        clip_name = f"{clip['camera']}-{clip['id']}"
        clip_name_short = re.match(r'^[^.]+', clip_name)[0]
        if not os.path.exists(f"{output_directory}/{clip_name_short}.mp4"):
            print(clip['id'])
            if not args.t:
                clip_url = f"{URL}/{clip['id']}/clip.mp4"
                r = requests.get(clip_url)
                with open(f"{output_directory}/{clip_name_short}.mp4", 'wb') as f:
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
    else:
        print("NOTHING TO DO - Thanks for all the fish!")

if __name__ == "__main__":
    main()
