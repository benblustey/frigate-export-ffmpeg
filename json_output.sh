#!/bin/bash

input_file="$1"

if [[ -z "$input_file" ]]; then
  echo "Usage: $0 <input_json_file>"
  exit 1
fi

newVideo=$(cat $input_file)

# # The playlist file
playlist_file="playlist.json"
# Function to create a new playlist file with the initial object
create_playlist() {
  echo "[$newVideo]" > "$playlist_file"
}
# Check if the playlist file exists
if [[ ! -f "$playlist_file" ]]; then
  create_playlist
else
  # Read the current content of the playlist file
  current_content=$(cat "$playlist_file")
  # Insert the new object as the first object in the playlist
  updated_content=$(echo "$current_content" | jq --argjson newObject "$newVideo" '. | [$newObject] + .')
  # Write the updated content back to the playlist file
  echo "$updated_content" > "$playlist_file"
fi

