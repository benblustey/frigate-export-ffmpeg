import os
import argparse
import subprocess
import requests
import json
import re
from datetime import datetime, timedelta

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
    parser.add_argument("-p", "--process-video", action="store_true", help="Run the process_video.py script after download")
    return parser.parse_args()

def yymmdd_convert(yymmdd):
    return (datetime.strptime(yymmdd, '%Y-%m-%d')).timestamp()

def return_end_of_day(epoch_value):
    date_obj = datetime.utcfromtimestamp(epoch_value)
    end_of_day = datetime.combine(date_obj, datetime.max.time()) - timedelta(microseconds=1)
    return int(end_of_day.timestamp())

def process_downloads(process_video=False):
    print("Files downloaded. Proceeding with the next tasks...")
    try:
        subprocess.run(['python', 'analyze_directory.py'], check=True)
        subprocess.run(['python', 'upload_mongodb.py'], check=True)
        if process_video:
            subprocess.run(['python', 'process_video.py'], check=True)
        print("All tasks completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing script: {e}")

def main():
    args = parse_arguments()

    current_time = int(datetime.now().timestamp())
    end_time = int((datetime.now().replace(hour=6, minute=0, second=0) + timedelta(days=1)).timestamp())
    start_time = int((datetime.now().replace(hour=6, minute=0, second=0) - timedelta(days=1)).timestamp())
    process_date = args.d
    provided_start = args.s
    provided_end = args.e
    downloads_directory = os.getenv('DOWNLOADS_DIR', './downloads')
    
    try:
        os.makedirs(downloads_directory)
    except FileExistsError:
        pass

    if args.s:
        print(provided_start)
        start_time = yymmdd_convert(provided_start)
    elif not process_date:
        yesterday = datetime.now() + timedelta(days=-1)
        start_time = int(yesterday.replace(hour=0, minute=0, second=0).timestamp())
    
    if args.e:
        print(provided_end)
        end_time = return_end_of_day(yymmdd_convert(provided_end))
    elif not process_date:
        yesterday = datetime.now() + timedelta(days=-1)
        end_time = int(yesterday.replace(hour=23, minute=59, second=59,microsecond=999999).timestamp())
    
    # print("Start Time: ",start_time,"\nEnd Time: ",end_time)
    
    if process_date:
        start_time = yymmdd_convert(process_date)
        end_time = return_end_of_day(yymmdd_convert(process_date))
    
    if end_time < start_time:
        return("Dates don't work.")

    if args.o:
        downloads_directory = args.o

    if os.path.exists(downloads_directory) and args.f:
        confirm = input(f"Are you sure you want to delete ./{downloads_directory} folder? This may include downloads that have not been processed.\n(y/n) ")
        if confirm.lower() == 'y':
            print(f"Removing directory ./{downloads_directory}")
            os.system(f"rm -rf ./{downloads_directory}")

    frigate_server = os.getenv('FRIGATE_SERVER')
    events_filter = "?camera=front_yard&labels=explosion&fireworks"
    # date_filter = f"&after={start_time}&before={end_time}"
    request_url = (f"{frigate_server}{events_filter}")
    
    print("Request URL: ",request_url)
    response = requests.get(request_url)
    clips = json.loads(response.text)
    videos_processed = 0

    for clip in clips:
        clip_name = f"{clip['camera']}-{clip['id']}"
        clip_name_short = re.match(r'^[^.]+', clip_name)[0]
        if not os.path.exists(f"{downloads_directory}/{clip_name_short}.mp4"):
            print(clip['id'])
            if not args.t:
                clip_url = f"{frigate_server}/{clip['id']}/clip.mp4"
                print(clip_url)
                r = requests.get(clip_url)
                with open(f"{downloads_directory}/{clip_name_short}.mp4", 'wb') as f:
                    f.write(r.content)
            videos_processed += 1
        elif args.t:
            print(clip['id'])
            videos_processed += 1
        # else:
        #     print("File Already Exists")

    if args.t:
        print(f"Current_Time: {epoch_convert(current_time)}")
        print(f"Start_Time: {epoch_convert(start_time)}")
        print(f"End_Time: {epoch_convert(end_time)}")
        print(f"API_URL: {frigate_server}{events_filter}&after={start_time}&before={end_time}")

    if videos_processed != 0 or args.f:
        print(f"Processed {videos_processed} Events for {process_date}")
        process_downloads(args.process_video)
    else:
        print("NOTHING TO DO - Thanks for all the fish!")

if __name__ == "__main__":
    main()
