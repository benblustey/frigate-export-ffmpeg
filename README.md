# Frigate Export FFmpeg

A Python-based tool for downloading, processing, and managing video clips from a Frigate NVR system. This tool is specifically designed to handle video clips of explosions and fireworks events, with features for video processing, metadata analysis, and MongoDB storage.

## Project Overview

This project was developed to help document and provide evidence of excessive fireworks activity in a neighborhood. It automates the process of collecting, processing, and storing video evidence from a Frigate NVR system.

### Processing Pipeline
1. Check for Events in Frigate API
2. Download Video Events
3. Analyze Videos (Directory)
4. Upload JSON to MongoDB
5. Process Videos
6. Move original videos to cold storage
7. Sync processed videos to Cloudflare CDN

## Features

- Download video clips from Frigate NVR based on specific criteria (camera, labels, date range)
- Process videos with FFmpeg to:
  - Crop and scale videos
  - Apply blur effects
  - Extract and overlay timestamps
  - Generate and overlay soundwave visualizations
- Store metadata in MongoDB
- Flexible date range processing
- Test mode for dry runs
- Force reprocessing option
- Automatic file management (cold storage and CDN sync)

## Prerequisites

- Python 3.x
- FFmpeg
- MongoDB
- Frigate NVR instance
- Cloudflare account (for CDN sync)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd frigate-export-ffmpeg
```

2. Install required Python packages:
```bash
pip install -r requirements.txt
```

3. Copy the example environment file and configure it:
```bash
cp example.env .env
```

Edit the `.env` file with your specific configuration:
```
MONGODB_IP=localhost
MONGODB_PORT=27017
FRIGATE_SERVER="http://your-frigate-server:5000/api/events"
```

## Usage

### Downloading Clips

```bash
python download_frigate.py [options]
```

Options:
- `-t`: Test run (only outputs txt files, no downloads)
- `-d`: Specify date to process (YYYY-MM-DD)
- `-f`: Force reprocess (removes date folder)
- `-s`: Set custom start time (YYYY-MM-DD)
- `-e`: Set custom end time (YYYY-MM-DD)
- `-o`: Set custom output directory

### Processing Videos

```bash
python process_video.py [options]
```

Options:
- `-o`: Set custom output directory
- `-i`: Set custom input directory

### Analyzing Directory

```bash
python analyze_directory.py
```

### Uploading to MongoDB

```bash
python upload_mongodb.py
```

## Directory Structure

- `downloads/`: Raw downloaded video clips
- `completed/`: Processed video files
- `temp_processing/`: Temporary files during processing
- `non-readable/`: Failed or unprocessable files

## Technical Details

### Frigate API Integration

The system uses Frigate's HTTP API to fetch events based on specific criteria:
```
<URL|IP-frigate-server>?camera=<camera_name>&label=<label>&after=<start-timestamp>&before=<end-timestamp>
```

- Timestamps are in Linux EPOCH format
- Default processing window: 24 hours (06:00:00 to next day 06:00:00)
- Events are filtered by camera and label (e.g., explosions, fireworks)

### Event Data Structure

Example event object stored in MongoDB:
```json
{
  "length": 11.138,
  "src": "1725254411.mp4",
  "friendlyDate": "24-09-01--22-20-11",
  "epoch": 1725254411,
  "starred": false,
  "approved": false
}
```

### Video Processing

Each video undergoes the following processing:
1. Resize and crop
2. Apply blur effect (except timestamp)
3. Generate and overlay soundwave visualization
4. Output to processed directory

## Error Handling

- Logs are maintained in `process_video.log`
- Failed processing attempts are logged with timestamps
- Temporary files are automatically cleaned up

## Known Issues

- Mac compatibility issue with `date -d` flag (use `gdate` as workaround)

## Todo List

- [ ] Add unit tests
- [ ] Create example .env-config file
- [ ] Add video audio analysis for event type detection
- [ ] Complete file mover for originals and processed
- [ ] Add notifications (Notifiarr/Discord)
- [ ] Add progress graphic on waveform
- [ ] Improve error handling for FFmpeg processing
- [x] Remove hardcoded values
- [x] Add custom time range flag
- [x] Improve output logs
- [x] Add MariaDB integration
- [x] Create temp directory for cleanup
- [x] Implement filename cleaning

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Add your license information here]

```
Check for Events => Download Video Events => Analyze Videos (Directory) => Upload JSON to MongoDB => Process Videos
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
`download_frigate.py` uses the Frigate API to request json based on a specific date range (default to previous day), specified event types. The returned JSON is then used to download each clip into a directory.

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