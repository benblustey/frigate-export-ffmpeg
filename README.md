# Frigate Export FFmpeg

A Python application that downloads and processes video clips from a Frigate NVR server. The application can be run either directly with Python or using Docker.

## Features

- Downloads video clips from Frigate NVR based on specified criteria
- Processes downloaded videos using FFmpeg
- Supports scheduled execution via cron
- MongoDB integration for data storage
- Configurable video processing options

## Prerequisites

- Python 3.9 or higher
- FFmpeg installed on your system
- MongoDB (if using database features)
- Docker (optional, for containerized deployment)

## Installation

### Python Installation

1. Clone the repository:
```bash
git clone https://github.com/benblustey/frigate-export-ffmpeg.git
cd frigate-export-ffmpeg
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Docker Installation

No additional installation steps required. Docker will handle all dependencies.

## Configuration

Create a `.env` file in the project root with the following variables:

```env
# Required
FRIGATE_SERVER=http://your-frigate-server:5000/api/events

# Optional
CRON_SCHEDULE=0 * * * *  # Default: Run every hour
DOWNLOADS_DIR=./downloads  # Default: ./downloads
PROCESS_VIDEO=false  # Default: false
```

## Usage

### Running with Python

1. Basic usage:
```bash
python main.py
```

2. Running download_frigate.py directly with options:
```bash
python download_frigate.py [options]
```

Available options:
- `-t`: Test run (only outputs txt files, no downloads)
- `-d YYYY-MM-DD`: Process specific date
- `-f`: Force reprocess (removes date folder)
- `-s YYYY-MM-DD`: Set custom start time
- `-e YYYY-MM-DD`: Set custom end time
- `-o PATH`: Set custom output directory
- `-p`: Enable video processing

Example:
```bash
python download_frigate.py -d 2024-03-20 -p
```

### Running with Docker

1. Build and start the container:
```bash
docker-compose up -d
```

2. View logs:
```bash
docker-compose logs -f
```

3. Stop the container:
```bash
docker-compose down
```

### Environment Variables

The following environment variables can be configured:

| Variable | Description | Default |
|----------|-------------|---------|
| FRIGATE_SERVER | Frigate NVR API endpoint | Required |
| CRON_SCHEDULE | Cron schedule for automated runs | 0 * * * * |
| DOWNLOADS_DIR | Directory for downloaded videos | ./downloads |
| PROCESS_VIDEO | Enable video processing | false |

## Directory Structure

```
frigate-export-ffmpeg/
├── main.py              # Main entry point
├── download_frigate.py  # Download script
├── analyze_directory.py # Directory analysis
├── upload_mongodb.py    # MongoDB upload
├── process_video.py     # Video processing
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── docker-compose.yaml # Docker Compose configuration
└── downloads/          # Downloaded videos directory
```

## Logging

Logs are written to both:
- Console output
- `frigate_export.log` file

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## Todos

** Add Attributes About Event **
- [ ] Include the `label:<camera_name>` for adding multiple sources
- [ ] Include the `data.score` to allow wider range of downloads with manual or future inteligent analyzing

## License

This project is licensed under the MIT License - see the LICENSE file for details.
