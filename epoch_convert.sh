#! /bin/bash

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


pst_time=$(TZ="America/Los_Angeles" date -d "@$timestamp" '+%Y-%m-%d %H:%M:%S')
