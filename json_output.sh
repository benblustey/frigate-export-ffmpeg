#!/bin/bash

input_file="$1"
PROCESS_DATE="2024-06-30"
baseURL="/videos"

if [[ -z "$input_file" ]]; then
  echo "Usage: $0 <input_video_file>"
  exit 1
fi
> "ffprobe_output.json"
> "video_output.json"

## Generate JSON for video player
ffprobe_output=$(ffprobe -v quiet -print_format json -show_format -show_streams "$input_file")
duration=$(echo "$ffprobe_output" | jq -r '.format.duration')
# DURATION=$(date -d@$duration -u +%M:%S)
echo "{\"filename\":\"$(basename "$input_file")\",\
  \"title\": \"$PROCESS_DATE\", \"duration\":\"$(date -d@$duration -u +%M:%S)\", \
  \"url\": \"${baseURL}/${PROCESS_DATE}.mp4\", \"thumbnail\": \
  \"$baseURL/$PROCESS_DATE.png\"}" \
  >> "video_output.json"
