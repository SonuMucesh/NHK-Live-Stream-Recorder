# NHK Live Stream Recorder

The NHK Live Stream Recorder is a Python script that allows you to download videos from a live stream based on a configured schedule. 
It retrieves program information from the NHK World and uses FFmpeg to download the videos.

## Getting Started

These instructions will help you get the NHK Stream Downloader up and running on your local machine or in a Docker container.

### Prerequisites

- Python 3.9 or later
- FFmpeg
- Docker (optional)

### Installation

1. Clone this repository or download the source code.

```bash
git clone https://github.com/SonuMucesh/NHK-Live-Stream-Recorder.git
```

2. Install the Python dependencies by running the following command in the project directory:

```bash
pip install -r requirements.txt
```

3. Install FFmpeg. If you're using a Linux-based system, you can install it with the following command:

```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

### Configuration

1. Open the `config.json` file and configure the settings according to your needs. Modify the content of the file to:

```json
{
  "epg_url": "https://nwapi.nhk.jp/nhkworld/epg/v7b/world/now.json",
  "local_timezone": "Europe/London",
  "recording_path": "PATH/TO/RECORDINGS", 
  "program_ids": ["72hours","cycle","somewhere","japanrailway"],
  "livestream_url": "https://nhkwlive-ojp.akamaized.net/hls/live/2003459/nhkwlive-ojp-en/index.m3u8"
}
```

The Program IDS can be retrieved from this command:

```bash
curl --location 'https://nwapi.nhk.jp/nhkworld/epg/v7b/world/now.json'
```

Which returns the EPG in JSON format where `pgm_gr_id` is the Program ID:

```json
    "channel": {
        "item": [
            {
                "seriesId": "2093",
                "airingId": "048",
                "title": "Zero Waste Life",
                "description": "Nihei Toru sells restored old furniture; bringing out the hidden charm in pieces most would consider worthless. But instead of going for good-as-new, he strives to preserve their vintage feel.",
                "link": "/nhkworld/en/tv/zerowaste/20231013/2093048/",
                "pubDate": "1697201100000",
                "endDate": "1697202000000",
                "vodReserved": false,
                "jstrm": "1",
                "wstrm": "1",
                "subtitle": "Furniture: Shabby to Chic",
                "content": "In this era of cheap, mass-produced products, Nihei Toru sells restored old furniture at his shop in a verdant mountain village north of Tokyo. Pieces that were in bad condition are brought back from the dead. But rather than aiming for good-as-new, he strives to preserve their vintage feel. His passion even extends to his own home—once abandoned and decaying—now tastefully restored. To him, bringing out the hidden charm of such seemingly worthless things far more than just a job, it's a way of life.",
                "content_clean": "In this era of cheap, mass-produced products, Nihei Toru sells restored old furniture at his shop in a verdant mountain village north of Tokyo. Pieces that were in bad condition are brought back from the dead. But rather than aiming for good-as-new, he strives to preserve their vintage feel. His passion even extends to his own home—once abandoned and decaying—now tastefully restored. To him, bringing out the hidden charm of such seemingly worthless things far more than just a job, it's a way of life.",
                "pgm_gr_id": "zerowaste",
                "thumbnail": "/nhkworld/upld/thumbnails/en/tv/zerowaste/c63812fdd3e2abf089a5dd193fbb94b7_large.jpg",
                "thumbnail_s": "/nhkworld/upld/thumbnails/en/tv/zerowaste/c63812fdd3e2abf089a5dd193fbb94b7_small.jpg",
                "showlist": "1",
                "internal": "1",
                "genre": {
                    "TV": [
                        "20",
                        "18"
                    ],
                    "Top": "",
                    "LC": ""
                },
                "vod_id": "nw_vod_v_en_2093_048_20231013104500_01_1697177378",
                "vod_url": "/nhkworld/en/ondemand/video/2093048/",
                "analytics": "[nhkworld]simul;Zero Waste Life_Furniture: Shabby to Chic;w02,001;2093-048-2023;2023-10-13T21:45:00+09:00"
            },
        ]
    }
```

2. Save the `config.json` file with your changes.

### Usage

To run the NHK Stream Downloader, execute the following command:

```bash
python main.py
```

The script will retrieve the Electronic Program Guide (EPG) from the NHKニュース website and download the videos based on the configured schedule.

### Running with Docker

Alternatively, you can use Docker to run the NHK Stream Downloader. Make sure you have Docker installed on your machine.

1. Pull the Docker image from the [DockerHub repository](https://hub.docker.com/repository/docker/sonumucesh/nhk-record/general) or build it yourself:

```bash
docker build -t nhk-stream-dl .
```

```bash
docker pull sonumucesh/nhk-record
```

2. Start a Docker container using the following command:

```bash
docker run --name nhk-stream-dl -v /path/to/config.json:/app/config.json -v /path/to/recordings:/app/recordings sonumucesh/nhk-record
```

3. You can also run the container using docker-compose:

```bash
version: '3'
services:
  nhk-stream-dl:
    build:
      context: .
    environment:
      - CONFIG_PATH=/app/config.json
    volumes:
      - ./config.json:/app/config.json
      - ./recordings:/app/recordings
 ```

Make sure to replace `/path/to/config.json` and `/path/to/recordings` with the actual paths to your configuration file and desired output directory.

### Contributing

Contributions are welcome! If you find any issues or would like to suggest improvements, please open an issue or submit a pull request.

### License

This project is licensed under the [MIT License](LICENSE).