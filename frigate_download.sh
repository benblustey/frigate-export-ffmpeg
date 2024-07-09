#!/bin/bash

DIR="/mnt/nvr/frigate/cron_exports"
URL="http://192.168.1.81:5000/api/events"
EVENTS_FILTER="?camera=front_yard&label=explosion"
OUTPUT_DIR="./completed"

shopt -s expand_aliases
source ~/.zshrc
##
### Function to display usage information
#####
usage() {
    echo "-d    Specify a date to process YYYY-DD-MM"
    echo "-f    Force reprocess. This will remove the date folder"
    echo "-c    Processes the current day up to current time"
    echo "-t    Test run. Only outputs the txt files, but does not download the clips or start the FFMPEG process."
    echo "-s    Set a custom start time YYYY-DD-MM"
    echo "-e    Set a custom end time YYYY-DD-MM"
    exit 1
}
##
### Parse command line flag options
#####
while getopts ":fcts:e:d:" flag; do
  case $flag in
    d) PROCESS_DATE=$OPTARG
      if [[ ! $PROCESS_DATE =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
        echo "The date variable is not YYYY-MM-DD."
        exit 1
      fi
      ;;
    f) FORCE_PROCESS=true;;
    c) CURRENT_DAY=true;;
    t) TEST_RUN=true;;
    s) CUSTOM_START=$OPTARG
      if [[ ! $CUSTOM_START =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
        echo "The custom start date variable is not YYYY-MM-DD."
        exit 1
      fi
      ;;
    e) CUSTOM_END=$OPTARG
      if [[ ! $CUSTOM_END =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
        echo "The custom end date variable is not YYYY-MM-DD."
        exit 1
      fi
      ;;
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

if [ $TEST_RUN ]; then
  echo "Running in test mode..."
fi
##
### CONVERT EPOCH
### helper funtion for testing
#####
function epochConvert () {
  echo $(TZ="America/Los_Angeles" date -d @$(($1)) '+%F %H:%M:%S')
}

##
### CREATE START_TIME & END_TIME
#####
## VARIABLES
CURRENT_TIME=$(date +%s)
END_TIME=$(date -d "today 06:00:00" +%s)
START_TIME=$(date -d "yesterday 06:00:00" +%s)
PROCESS_EPOCH=$(date -d "$PROCESS_DATE" +%s)
#####
if [ ! -z "$PROCESS_DATE" ]; then
  echo "Processing Date Provided $PROCESS_DATE"
  # START_TIME=6:00am of provided date
  START_TIME=$(date -d "$PROCESS_DATE 06:00:00" +%s)
  # # END_TIME=6:00am of day after provided date
  END_TIME=$(date -d "$PROCESS_DATE + 1 day 06:00:00" +%s)
elif [ $CURRENT_DAY ]; then
  echo "Processing Today starting at 06:00"
  START_TIME=$(date -d "today 06:00:00" +%s)
  END_TIME=$CURRENT_TIME
elif [ $CUSTOM_START ]; then
  echo "Processing Custom Range $CUSTOM_START - $CUSTOM_END"
  START_TIME=$(date -d "$CUSTOM_START 06:00:00" +%s)
  END_TIME=$(date -d "$CUSTOM_END + 1 day 06:00:00" +%s)
else
  PROCESS_DATE=$(date -d "yesterday" +%F)
fi
#### Construct the date filter for the API call
DATEFILTER="&after=${START_TIME}&before=${END_TIME}"

if [[ -d $PROCESS_DATE ]] && [[ $FORCE_PROCESS ]]; then
  read -p "Are you sure you want to delete ./$PROCESS_DATE folder? (y/n)" -n 1 -r
  if [[ $REPLY =~ ^[Yy]$ ]]; then
      echo "Removing directory ./$PROCESS_DATE"
      rm -rf ./$PROCESS_DATE
  fi
elif [[ ! $TEST_RUN ]]; then
  # Now make a dir if it doesn't exist
  mkdir -p $PROCESS_DATE
  echo "Making directory $PROCESS_DATE"
fi
##
### Query Clips
#####
echo :: ${URL}${EVENTS_FILTER}${DATEFILTER}
for clip in $(curl ${URL}${EVENTS_FILTER}${DATEFILTER} 2> /dev/null | jq -r '.[] | .camera + "-" + .id') ; do
  if [[ ! -f "${PROCESS_DATE}/${clip}.mp4" ]]; then
    echo ${clip#*-}
    id=${clip#*-}
    if [ ! $TEST_RUN ]; then
      curl ${URL}/${id}/clip.mp4 -o "${PROCESS_DATE}/${clip}.mp4"
    fi
    ((VIDEOS_PROCESSED++))
  elif [ $TEST_RUN ]; then
    echo ${clip#*-}
    ((VIDEOS_PROCESSED++))
  else
    echo "File Already Exists"
  fi
done

##
#### TEST RUN VARIABLES
######
if [ $TEST_RUN ]; then
  echo Currrent_Time: $(epochConvert $CURRENT_TIME)
  echo Start_Time: $(epochConvert $START_TIME)
  echo End_Time:  $(epochConvert $END_TIME)
  echo API_URL: "${URL}${EVENTS_FILTER}&after=${START_TIME}&before=${END_TIME}"
fi
#####
# Let's GO!
# If no videos were downloaded, don't do anything
#####
echo ::: $FORCE_PROCESS
if [ $VIDEOS_PROCESSED -ne 0] || [ $FORCE_PROCESS ]; then
  echo "Processed ${VIDEOS_PROCESSED} Events for $PROCESS_DATE"
  # ## RUN THE FFMPEG CONCAT SCRIPT
  if [ ! $TEST_RUN ]; then
    echo "Sending ${PROCESS_DATE} to ffmpeg_process.sh"
    ./ffmpeg_process.sh -d ${PROCESS_DATE}
  fi
else
  echo "NOTHING TO DO - Thanks for all the fish!"
fi
