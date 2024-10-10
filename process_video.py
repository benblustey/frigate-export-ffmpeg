import argparse
import shutil
import sys
import os
import re
import logging
import ffmpeg
from time import time

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process Videos")
    parser.add_argument("-o", type=str, help="Set an output directory other than default")
    parser.add_argument("-i", type=str, help="Set an target directory other than downloads")
    # parser.add_argument("-t", action="store_true", help="Test run. Only analyzes the directory and out put")
    return parser.parse_args()

logging.basicConfig(
  filename='process_video.log',
  level=logging.ERROR,
  format='%(asctime)s:%(levelname)s:%(message)s'
)

def main():
    args = parse_arguments()
    # Define the root directory videos are located
    target_dir = './downloads'
    output_dir = './completed'
    temp_dir = './temp_processing'
    ffmpeg_loglevel="quiet"

    try:
      os.makedirs(output_dir)
    except FileExistsError:
      pass

    try:
      os.makedirs(temp_dir)
    except FileExistsError:
      pass

    try:
      os.makedirs(output_dir)
    except FileExistsError:
      pass

    for item in os.listdir(target_dir):

        video_id = re.search(r'\d+', item).group(0)
        item_path = os.path.join(target_dir, item)

        temp_crop = os.path.join(temp_dir, video_id+'_cropped.mp4')
        temp_blurred = os.path.join(temp_dir, video_id+'_blurred.mp4')
        temp_soundwave = os.path.join(temp_dir, video_id+'_overlay.png')
        final_output_file = os.path.join(output_dir, video_id+'.mp4')
        final_preview = os.path.join(output_dir, video_id+'.png')

        try:
            ffmpeg.input(item_path).output(temp_crop, vf=f'crop=2100:700:0:0', loglevel=ffmpeg_loglevel).run(overwrite_output=True)
            
            # Apply boxblur to the entire video
            blurred_video = ffmpeg.input(temp_crop).filter('boxblur', 20)
            # Crop a section from the original video
            cropped_video = ffmpeg.input(temp_crop).crop(0, 0, 800, 80)
            # Overlay the cropped video on top of the blurred video
            ffmpeg.overlay(blurred_video, cropped_video, x=10, y=30).output(temp_blurred, loglevel=ffmpeg_loglevel).run(overwrite_output=True)
            
            # Create a sound wave image with a black background
            ffmpeg.input(temp_crop).filter('showwavespic', s='2100x200').output(temp_soundwave, vframes=1, format='image2', pix_fmt='rgb24', loglevel=ffmpeg_loglevel).run(overwrite_output=True)
            
            # Add the overlay to the video and export final mp4
            ffmpeg.filter([ffmpeg.input(temp_blurred), ffmpeg.input(temp_soundwave)], 'overlay', 0, 500).output(final_output_file, loglevel=ffmpeg_loglevel).run(overwrite_output=True)

            # Create icon for video
            ffmpeg.input(final_output_file, ss=0).output(final_preview, vframes=1, loglevel=ffmpeg_loglevel).run(overwrite_output=True)

            print(f"Successfully processed {final_output_file}")

        except ffmpeg.Error as e:
            logging.error(f"Error occurred: {e.stderr}")

    # cleanup
    try:
        shutil.rmtree(temp_dir)
        print('Deleted the temp_dir')
    except FileNotFoundError:
        pass

if __name__ == "__main__":
    main()
