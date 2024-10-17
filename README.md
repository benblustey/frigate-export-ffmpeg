# frigate-export-ffmpeg

## Overview
A collection of python scripts to GET videos from a frigate API endpoint, analyze the `.mp4` files quickly, push JSON data into a mongoDB, and process the videos using FFMPEG.

This library is designed to work independently from user interaction and executed via cron.

```
Check for Events => Download Video Events => Analyze Videos => Upload JSON to MongoDB => Process Videos
```

Once the data is uploaded and the video files are completed, the original video files are sent to cold storage on the local array, while the processed videos are moved to a directory that eventually gets synced with Cloudflare CDN.

### Frigate API Use
[Frigate](https://frigate.video/) has the option to track many types of [objects](https://docs.frigate.video/configuration/objects/). Those events are available via the HTTP API and can be polled using by passing multiple parameters.

For example:
```
<URL|IP-frigate-server>?camera=<camera_name>&label=<label>&after=<start-timestamp>&before=<end-timestamp>
```

`start-timestamp` and `end-timestamp` are in linux EPOCH time. Using the (EpochConverter)[https://www.epochconverter.com/] helped with learning and targeting different time periods. For my usecase, when processing a date (eg: June 25), videos are pulled from `June 25 06:00:00` to `June 26 06:00:00`.

All videos are concatnated, cropped and blurred for anonymity except for timestamp, and overlayed with a waveform png.

## My Use Case
There have been a rediculous amount of fireworks with our neighborhood that start around may and go through the summer. The community has been complaining, but no one was able to provide any substantial evidence on the sheer amount of fireworks. I decided to learn bash scripting and create theses scripts to automate the pulls and creation of videos and automatically post them to a website. I'll most likely convert this into python, but wanted a challenge.

## Script Descriptions
`frigate_download.py` uses the Frigate API to request json based on a specific date range (default to previous day), specified event types. The returned JSON is then used to download each clip into a directory.

`analyze_directory.py` Iterates over any files with the `.mp4` file extension in the download or target_dir. Each event is analyzed for specific attributes and appended to the json file `events_data.json`.

**Event Object Example**
```JSON
{
  "length": 11.138,
  "src": "1725254411.mp4",
  "friendlyDate": "24-09-01--22-20-11",
  "epoch": 1725254411,
  "starred": false,
  "approved": false
}
```

`upload_mongodb.py` Receives the `events_data.json` from the analyze directory process. Since the name of the event is the epoch date, this is used as the UUID for the MongoDB ID. Event event is checked if exists and if does not, the event is inserted.

`process_video.py` Iterates over the `.mp4` files in the download directory and processes each file. Eacch file is resized, cropped, blurred, overlayed, soundwave image generated, then output to a new directory.

## Todos
- [ ] add unit tests
- [ ] create an example .env-config file to set those values.
- [ ] add video audio anylize for event type to determin number of events withing clips
- [ ] finish file mover for originals and processed
- [ ] add notification, eg: Notifiarr or Discord
- [ ] add a progress graphic on top of waveform
- [ ] change flow for process to upload mongo in case of ffmpeg errors
- [x] remove hard coded values for `DIR`, `URL`, `EVENTS_FILTER`, and `OUTPUT_DIR`.
- [x] add custom time range flag and value
- [x] add better output logs
- [x] include functionality to post json for clip details to MariaDB
  - [x] move the content of the txt file to the json output
- [x] create a temp directory for easy file cleanup
- [x] regex `r'^[^.]+'` to clean the '107442-km3lt1' from end of clip names

## Known Issues
* Mac doesn't like the `date -d` flag, most likely an issue with the intial bash prompt at the top. Local solution was to use `gdate`.