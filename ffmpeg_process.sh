#!/bin/bash
baseURL="/videos"

##
### Function to display usage information
#####
usage() {
    echo "-d    Specify a date to process YYYY-DD-MM"
    echo "-t    Test run. Only outputs the txt files, but does not download the clips or start the FFMPEG process."
    echo "-f    Force reprocess. This will remove the date folder"
    exit 1
}
##
### Parse command line flag options
#####
while getopts ":fcts:e:d::" flag; do
  case $flag in
    d) PROCESS_DATE=$OPTARG
      if [[ ! $PROCESS_DATE =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
        echo "The date variable is not YYYY-MM-DD."
        exit 1
      fi
      ;;
    t) TEST_RUN=true;;
    f) FORCE_PROCESS=true;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done
if [ -z $PROCESS_DATE ]; then
  echo "Need a date to process..."
  echo "Use the -d flag to pass YYYY-MM-DD"
  exit
fi
if [ $TEST_RUN ]; then
  echo "Running in test mode..."
fi

## Clean the process text file
# > "$PROCESS_DATE.txt"
> "video_output.json"

## Iterate over the .mp4 files in the PROCESS_DATE directory
for filename in $(find ./$PROCESS_DATE -name "*.mp4" -maxdepth 1 -type f | sort -n ); do
  #### output time stamps and video name
  if [[ $filename =~ ([0-9]+)\.[0-9]+ ]]; then
    timestamp=${BASH_REMATCH[1]}
    if [ $TEST_RUN ]; then
      echo "Extracted Unix Timestamp: $timestamp from $filename"
    fi
  else
    echo "No valid timestamp found in the filename."
    exit 1
  fi
  # Convert the Unix Timestamp to PST
  pst_time=$(TZ="America/Los_Angeles" date -d "@$timestamp" '+%Y-%m-%d %H:%M:%S')
  # Output file name and timestamp
  echo file \'$filename\' $pst_time >> "$PROCESS_DATE.txt"
  ((NUMBEREVENTS++))
done

## Print some text
if [ $TEST_RUN ]; then
  echo "Number of events: $NUMBEREVENTS"
  echo "Contents of $PROCESS_DATE.txt"
  cat $PROCESS_DATE.txt
  exit
fi
if ! test -f ./$PROCESS_DATE.txt; then
  echo The $PROCESS_DATE.txt file does not exists. Exiting now ....
  exit
elif [ -s file ]; then
  echo The $PROCESS_DATE.txt file is empty. Exiting now ....
  exit
else
  echo Everything good, processing
fi

## DO FFMPEG STUFF HERE
ffmpeg -y -f concat -safe 0 -i "$PROCESS_DATE.txt" -c copy "${PROCESS_DATE}_concat.mp4"

## Crop video to hide location
ffmpeg -y -i "${PROCESS_DATE}_concat.mp4" \
  -vf "crop=2100:700:0:0" "${PROCESS_DATE}_cropped.mp4"

## Create the blur overlay
ffmpeg -y -i "${PROCESS_DATE}_cropped.mp4" \
  -filter_complex "[0:v]avgblur=20[bg];[0:v]crop=800:80:0:0[fg];[bg][fg]overlay=10:30;" \
  -c:a copy -movflags +faststart "${PROCESS_DATE}_post.mp4"

## Generate the soundwave from the post prod video
ffmpeg -y -i ${PROCESS_DATE}_post.mp4 -filter_complex \
  "color=c=black[color]; \
  aformat=channel_layouts=mono,showwavespic=s=2100x200:colors=red[wave]; \
  [color][wave]scale2ref[bg][fg]; \
  [bg][fg]overlay=format=auto" \
  -frames:v 1 ${PROCESS_DATE}_overlay.png

## Add the overlay to the video and export final mp4
ffmpeg -y -i ${PROCESS_DATE}_post.mp4 -i ${PROCESS_DATE}_overlay.png \
  -filter_complex [0]overlay=x=0:y=500[out] -map [out] -map 0:a? "${PROCESS_DATE}.mp4" \

## Create preview icon
ffmpeg -i "${PROCESS_DATE}.mp4" -ss 00:00:01.000 -vframes 1 "${PROCESS_DATE}.png"

## Generate JSON for video player
ffprobe_output=$(ffprobe -v quiet -print_format json -show_format -show_streams "${PROCESS_DATE}.mp4")
# $ffprobe_output >> "ffmpeg_output.json"
duration=$(echo "$ffprobe_output" | jq -r '.format.duration')
echo "{\"filename\":\"$(basename "$PROCESS_DATE")\",\
  \"title\": \"$PROCESS_DATE\", \"duration\":\"$(gdate -d@$duration -u +%M:%S)\", \
  \"url\": \"${baseURL}/${PROCESS_DATE}.mp4\", \"thumbnail\": \
  \"$baseURL/$PROCESS_DATE.png\"}" \
  >> "video_output.json"

## move the needed files
mkdir -p completed
mv "${PROCESS_DATE}.mp4" "$PROCESS_DATE.txt" "$PROCESS_DATE.png" ./completed

## remove the files not needed
rm ${PROCESS_DATE}_cropped.mp4 \
   ${PROCESS_DATE}_concat.mp4 \
   ${PROCESS_DATE}_post.mp4 \
   ${PROCESS_DATE}_overlay.png

echo "Video Compiled: $PROCESS_DATE.mp4"

if [ ! $TEST_RUN ]; then
  ./update_playlist.sh "video_output.json"
fi
