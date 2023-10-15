# NHK Live Stream Recorder

The NHK Live Stream Recorder is a Python script that allows you to download videos from the live stream based on a configured schedule. 
It retrieves program information from NHK World and uses FFmpeg to download the shows. 
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

Adjust the following settings based on your preferences:

```properties
epg_url:The URL of the NHK World EPG. You can find it by running the specified command.
local_timezone: The timezone of your location.
recording_path: The directory path where the recordings will be saved.
ffmpeg_log_path: The directory path where the FFmpeg logs will be saved.
series_ids: The series IDs of the programs you want to record (more information below).
livestream_url: The URL of the NHK World livestream.
sonarr_integration: Set this to true if you want to use Sonarr integration.
sonarr_url: The URL of your Sonarr instance.
sonarr_api_key: The API key of your Sonarr instance.
fuzzy_match_ratio: The fuzzy match ratio for the Sonarr integration. Adjust this number to balance accuracy and strictness of the match.
series_ids_mapping: The mapping between the NHK World series IDs and the Sonarr series IDs (more information below). \
  This mapping allows comparison of episodes on Sonarr and EPG. You can use series_ids_mapping or series_ids or both. \
  However, only series_ids_mapping will work with Sonarr integration.
```
Here is an example of the configuration file that I use:
```json
{
  "epg_url": "https://nwapi.nhk.jp/nhkworld/epg/v7b/world/now.json",
  "local_timezone": "Europe/London",
  "recording_path": "/app/recordings",
  "ffmpeg_log_path": "/app/logs/ffmpeg.log",
  "series_ids": ["2090"],
  "livestream_url": "https://nhkwlive-ojp.akamaized.net/hls/live/2003459/nhkwlive-ojp-en/index.m3u8",
  "sonarr_integration": true, 
  "sonarr_url": "YOUR_SONARR_URL", 
  "sonarr_api_key": "YOUR_SONARR_API_KEY",
  "fuzzy_match_ratio": 85,
  "series_ids_mapping": [
    {
      "nhk_series_id": "4026", 
      "tv_db_id": "323119"
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


The Series IDs can be retrieved from this command if you want to get it from the EPG:

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

Another way to get the `Series ID` is to go to the program page on NHK World and then get the name of the show to use in the request below:

```bash
curl --location 'https://www3.nhk.or.jp/nhkworld/data/en/tv/program/{YOUR-PROGRAM}.json'
```

For example the page for `Somewhere Street` is [https://www3.nhk.or.jp/nhkworld/en/tv/somewhere/](https://www3.nhk.or.jp/nhkworld/en/tv/somewhere/)
use the `somewhere` bit of the URL to get the Series ID:
```bash
curl --location 'https://www3.nhk.or.jp/nhkworld/data/en/tv/program/somewhere.json'
```

this returns this where the `id` is the Series ID:
```json
{
  "id": "4017",
  "lang": "en",
  "title": "Somewhere Street",
  "description": "A unique walking-eye view of cities around the globe! Chat to the locals and enjoy encounters that only strolling the streets can bring.",
  "broadcastDay": "Sunday (UTC)",
  "created_at": "Fri, 16 Feb 2018 21:44:19 +0900",
  "updated_at": "Wed, 19 Jul 2023 15:59:51 +0900",
  "public_at": 1518785059000,
  "program_slag": "somewhere"
}
```

2. Save the `config.json` file with your changes.

### Usage

To run the NHK Stream Downloader, execute the following command where the config file is located:

```bash
python main.py
```

The script will retrieve the Electronic Program Guide (EPG) from the NHK World and download the programs based on the configured schedule.

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

Make sure to replace `/path/to/config.json`, `/path/to/recordings` and `./logs`with the actual paths to your configuration file and desired output directory.

### Contributing

Contributions are welcome! If you find any issues or would like to suggest improvements, please open an issue or submit a pull request.

### License

This project is licensed under the [MIT License](LICENSE).
