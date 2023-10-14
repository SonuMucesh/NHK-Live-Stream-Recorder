# NHK Live Stream Recorder

The NHK Live Stream Recorder is a Python script that allows you to download videos from the live stream based on a configured schedule. 
It retrieves program information from NHK World and uses FFmpeg to download the videos. 
It also supports integration with Sonarr to download only the episodes that are missing.

## Getting Started

These instructions will help you get the NHK Live Stream Recorder up and running on your local machine or in a Docker container.

### Prerequisites

- Python 3.9 or later
- FFmpeg
- Docker (optional)
- Sonarr (optional)

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
  "recording_path": "/app/recordings",
  "ffmpeg_log_path": "/app/logs/ffmpeg.log",
  "series_ids": ["2090"], --> This is the series ID 
  "livestream_url": "https://nhkwlive-ojp.akamaized.net/hls/live/2003459/nhkwlive-ojp-en/index.m3u8",
  "sonarr_integration": "True", --> This is the Sonarr integration, if you want to use it, set it to True
  "sonarr_url": "YOUR_SONARR_URL", 
  "sonarr_api_key": "YOUR_SONARR_API_KEY", --> You can find your Sonarr API key in Settings > General
  "series_ids_mapping": [
     --> This mapping allows us to compare episodes on Sonarr and EPG you can use this or series_ids or both.
         However only series_ids_mapping will work with Sonarr integration
    {
      "nhk_series_id": "4026", --> This is the NHK Series ID From the EPG same as the one above
      "tv_db_id": "323119" --> This is the TVDB Series ID From Sonarr
    },
    {
      "nhk_series_id": "2066",
      "tv_db_id": "329370"
    },
    {
      "nhk_series_id": "4017",
      "tv_db_id": "338223"
    }
  ]
}
```

The Series IDs can be retrieved from this command:

```bash
curl --location 'https://nwapi.nhk.jp/nhkworld/epg/v7b/world/now.json'
```

Which returns the EPG in JSON format where `seriesId` is the Series ID:

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

The script will retrieve the Electronic Program Guide (EPG) from the NHK World and download the videos based on the configured schedule.

### Running with Docker

Alternatively, you can use Docker to run the NHK Stream Downloader. Make sure you have Docker installed on your machine.

1. Pull the Docker image from the [DockerHub repository](https://hub.docker.com/repository/docker/sonumucesh/nhk-record/general) or build it yourself:

```bash
docker build -t nhk-stream-dl .
```

```bash
docker pull sonumucesh/nhk-record:latest
```

2. Start a Docker container using the following command:

```bash
docker run -d \
  --name nhk-stream-dl \
  -v /path/to/config.json:/app/config.json \
  -v /path/to/recordings:/app/recordings \
  -v /path/to/logs:/app/logs \
  -e CONFIG_PATH=/app/config.json \
  sonumucesh/nhk-record:latest
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
      - ./logs:/app/logs
 ```

Make sure to replace `/path/to/config.json` and `/path/to/recordings` with the actual paths to your configuration file and desired output directory.

### Contributing

Contributions are welcome! If you find any issues or would like to suggest improvements, please open an issue or submit a pull request.

### License

This project is licensed under the [MIT License](LICENSE).
