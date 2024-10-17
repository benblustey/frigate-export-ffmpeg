import argparse
import shutil
import sys
import os
import logging
import re
import ffmpeg
from datetime import datetime

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process Videos")
    parser.add_argument("-o", type=str, help="Set an output directory other than default")
    parser.add_argument("-i", type=str, help="Set an target directory other than downloads")
    # parser.add_argument("-t", action="store_true", help="Test run. Only analyzes the directory and out put")
    return parser.parse_args()

target_dir = './downloads'
output_dir = './completed'
temp_dir = './temp_processing'
ffmpeg_loglevel="quiet"

# Define the root directory videos are located
os.makedirs(output_dir, exist_ok=True)
os.makedirs(temp_dir, exist_ok=True)

# Input/Output file paths
temp_crop = os.path.join(temp_dir, 'temp_crop.mp4')
temp_blur = os.path.join(temp_dir, 'temp_blur.mp4')
temp_timestamp = os.path.join(temp_dir, 'temp_timestamp.mp4')
temp_soundwave_png = os.path.join(temp_dir, 'temp_overlay.png')


# Error handling function
logging.basicConfig(
  filename='process_video.log',
  level=logging.ERROR,
  format='%(asctime)s:%(levelname)s:%(message)s'
)

# Step 1: Crop and ScDale the Video
def crop_and_scale(input_video, temp_crop):
    try:
        original_video = ffmpeg.input(input_video)
        original_video.filter('crop', 1900, 800, 0, 0).filter('scale', 1140, 480).output(temp_crop, loglevel=ffmpeg_loglevel).run(overwrite_output=True)
        return temp_crop
    except ffmpeg.Error as e:
        logging.error(f"Error processing {input_video}: {e}")



# Step 2: Apply Blur and Extract Timestamp
def blur_and_extract_timestamp(temp_crop, temp_blur, temp_timestamp):
    try:
        temp_crop_import = ffmpeg.input(temp_crop)
        temp_crop_import.filter('boxblur', 15).output(temp_blur, loglevel=ffmpeg_loglevel).run(overwrite_output=True)
        temp_crop_import.crop(0, 0, 500, 60).output(temp_timestamp, loglevel=ffmpeg_loglevel).run(overwrite_output=True)
        return temp_blur, temp_timestamp
    except ffmpeg.Error as e:
        logging.error(f"Error processing {input_video}: {e}")


# Step 3: Combine Blurred Video with Timestamp
def combine_blur_and_timestamp(temp_blur, temp_timestamp):
    try:
        cropped_scaled_video = ffmpeg.input(temp_blur)
        timestamp_clip = ffmpeg.input(temp_timestamp)
        combined_video = ffmpeg.overlay(cropped_scaled_video, timestamp_clip, x=0, y=0)
        return combined_video
    except ffmpeg.Error as e:
        logging.error(f"Error combining cropped and timestamp: {e}")


# Step 4: Create Showwaves Image (Soundwave)
def create_soundwave_image(input_video, temp_soundwave_png):
    try:
        ffmpeg.input(input_video).filter('showwavespic', s='1140x160').output(temp_soundwave_png, vframes=1, format='image2', pix_fmt='rgb24', loglevel=ffmpeg_loglevel).run(overwrite_output=True)
        return temp_soundwave_png
    except ffmpeg.Error as e:
        logging.error(f"Error processing {input_video}: {e}")


# Step 5: Overlay Showwaves Image on Combined Video and Add Audio
def overlay_soundwave_and_audio(combined_video, overlay_png, input_video, output_path):
    try:
        final_video = ffmpeg.overlay(combined_video, ffmpeg.input(overlay_png), x=0, y=320)
        ffmpeg.output(final_video, ffmpeg.input(input_video).audio, output_path, vcodec='libx264', acodec='aac', loglevel=ffmpeg_loglevel).run(overwrite_output=True)
    except ffmpeg.Error as e:
        logging.error(f"Error processing {input_video}: {e}")


def cleanup_temp_files():
    # cleanup
    for filename in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)  # Delete file
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)  # Delete subdirectory recursively

def process_video(input_video, output_video):
    try:
        # Step-by-step processing
        if not crop_and_scale(input_video, temp_crop):
            return False
        if not blur_and_extract_timestamp(temp_crop, temp_blur, temp_timestamp):
            return False
        combined_ts_blur = combine_blur_and_timestamp(temp_blur, temp_timestamp)
        if not combined_ts_blur:
            return False
        if not create_soundwave_image(input_video, temp_soundwave_png):
            return False
        
        # Overlay PNG (soundwave) on top of the combined video and add audio
        overlay_soundwave_and_audio(combined_ts_blur, temp_soundwave_png, input_video, output_video)
        
        print(f'Processed {input_video} successfully.')
        return True
    except Exception as e:
        logging.error(f"Error processing {input_video}: {e}")
        return False

def main():
    args = parse_arguments()
    startTime = datetime.now()
    successes = 0

    # Iterate over all video files in the download directory
    for video_file in os.listdir(target_dir):
        if video_file.endswith('.mp4'):
            
            video_id = re.search(r'\d+', video_file).group(0)
            input_video = os.path.join(target_dir, video_file)
            output_video = os.path.join(output_dir, video_id+'.mp4')
            
            # Process each video, skip to next if any issue occurs
            if not process_video(input_video, output_video):
                print(f'\033[91mSkipping {video_file} due to an error. See the process_video.log\033[0m')
                continue
            successes += 1
            cleanup_temp_files()

    print('\033[32mProcessing completed.\033[0m')
    print(f'\033[33mCompleted {successes} files in:', datetime.now() - startTime,'\033[0m')

if __name__ == "__main__":
    main()