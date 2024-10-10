import os
import re
import shutil

# Define the root directory where the yyyy-mm-dd folders are located
target_dir = './'

# Define the directory where all .mp4 files will be moved
combined_dir = os.path.join(target_dir, 'combined')

# Ensure the 'combined' directory exists
if not os.path.exists(combined_dir):
    os.makedirs(combined_dir)

# Regex pattern for yyyy-mm-dd directory format
date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')

def iterrate_dir(root_dir):
  # Iterate over all items in the root directory
  for item in os.listdir(root_dir):
    item_path = os.path.join(root_dir, item)
    
    # Check if the item is a directory and matches the yyyy-mm-dd pattern
    if os.path.isdir(item_path) and date_pattern.match(item):
      # Iterate over files in the date directory
      for file_name in os.listdir(item_path):
        if file_name.endswith('.mp4'):
          # get timestamp int
          # timestamp = re.search(r'\d+', file_name).group(0)
          # # create file name
          # new_file_name = timestamp + '.mp4'
          # Source file path to move
          source_file = os.path.join(item_path, file_name)
          # Destination file path
          destination_file = os.path.join(combined_dir, file_name)
          # Move the .mp4 file to the 'combined' directory
          shutil.copyfile(source_file, destination_file)
          print(f"Moved: {source_file} -> {destination_file}")

events_data = iterrate_dir(target_dir)
print("All .mp4 files have been moved to the 'combined' directory.")

