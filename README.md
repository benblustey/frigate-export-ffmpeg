# frigate-export-ffmpeg

## Overview
A collection of bash scripts use to GET videos from frigate and process using FFMPEG.

[Frigate](https://frigate.video/) has the option to track many types of [objects](https://docs.frigate.video/configuration/objects/). Those events are available via the HTTP API and can be polled using by passing multiple parameters.

For example:
```
<URL|IP-frigate-server>?camera=<camera_name>&label=<label>&after=<start-timestamp>&before=<end-timestamp>
```

`start-timestamp` and `end-timestamp` are in linux EPOCH time. Using the (EpochConverter)[https://www.epochconverter.com/] helped with learning and targeting different time periods. For my usecase, when processing a date (eg: June 25), videos are pulled from `June 25 06:00:00` to `June 26 06:00:00`.

All videos are concatnated, cropped and blurred for anonymity except for timestamp, and overlayed with a waveform png.

## My Use Case
There have been a rediculous amount of fireworks with our neighborhood that start around may and go through the summer. Since the community has been complaining, but no one was able to provide any substantial evidence on the sear amount of fireworks. I decided to learn bash scripting and create theses scripts to automate the pulls and creation of videos and automatically post them to a website. I'll most likely convert this into python, but wanted a challenge.

## Use
Update the URL, Events Filter, and associated directories within the `frigate_download.sh` to fit your use case.

## Ecpected Outcome
`frigate_download.sh` uses the Frigate API to GET a specific date range and event types and downloads each clip into a date named directory. When completed, the processed date is passed to `ffmpeg_process.sh`

`ffmpeg_process.sh` is the beast:
* iterates over the newly created directory
* generates a txt file including the video names and timestamp
* ffmpeg then 


## Todos
- [ ] remove hard coded values for `DIR`, `URL`, `EVENTS_FILTER`, and `OUTPUT_DIR`.
- [ ] add custom time range flag and value
- [ ] create an example .env-config file to set those values.
- [ ] add better output logs
- [ ] add video audio anylize for event type to determin number of events withing clips
- [ ] add a progress graphic on top of waveform
- [ ] include functionality to post json for clip details to MariaDB
  - [ ] move the content of the txt file to the json output
- [ ] create a temp directory for easy file cleanup

## Known Issues
* Mac doesn't like the `date -d` flag, most likely an issue with the intial bash prompt at the top. Local solution was to use `gdate`.