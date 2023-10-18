# NHK Live Stream Recorder

The NHK Live Stream Recorder, a Python script, enables you to schedule and download videos from live streams. It fetches program details from NHK World and leverages FFmpeg for the actual downloading of shows. Additionally, it offers Sonarr integration, allowing for selective downloading of only the missing episodes.

## Getting Started

Follow these guidelines to successfully set up the NHK Live Stream Recorder either on your local machine or within a Docker container.

### Prerequisites

- Python 3.9 or later
- FFmpeg
- Docker (optional)
- Sonarr (optional) -- This can be enabled in the `config.json` file. Please note there are certain conditions associated with its use, detailed in the Important Notes! section.

### Installation

1. Obtain the repository by either cloning it or downloading the source code.

```bash
git clone https://github.com/SonuMucesh/NHK-Live-Stream-Recorder.git
```

2. Navigate to the project directory and install the necessary Python dependencies with the following command:

```bash
pip install -r requirements.txt
```

3. FFmpeg is required for the script to function. If you're on a Linux-based system, you can install it using the commands below:

```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

### Configuration

1. Modify the config.json file according to your preferences:

- `epg_url`: The URL of the NHK World EPG. You can find it by running the specified command.
- `local_timezone`: The timezone of your location.
- `recording_path`: The directory path where the recordings will be saved.
- `ffmpeg_log_path`: The directory path where the FFmpeg logs will be saved.
- `series_ids`: The series IDs of the programs you want to record (more information below).
- `livestream_url`: The URL of the NHK World livestream.
- `sonarr_integration`: Set this to true if you want to use Sonarr integration.
- `sonarr_url`: The URL of your Sonarr instance.
- `sonarr_api_key`: The API key of your Sonarr instance.
- `fuzzy_match_ratio`: The fuzzy match ratio for the Sonarr integration. Adjust this number to balance accuracy and strictness of the match.
- `series_ids_mapping`: The mapping between the NHK World series IDs and the Sonarr series IDs. This mapping allows comparison of episodes on Sonarr and EPG. You can use `series_ids_mapping` or `series_ids` or both. However, only `series_ids_mapping` will work with Sonarr integration.

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

<details>
  <summary>Click to expand the response</summary>
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
</details>
&nbsp;

Alternatively, you can obtain the `Series ID` by visiting the program page on NHK World and extracting the show's name to use in the following request:

```bash
curl --location `'https://www3.nhk.or.jp/nhkworld/data/en/tv/program/{YOUR-PROGRAM}.json'`
```

For instance, if you visit the Somewhere Street page at `https://www3.nhk.or.jp/nhkworld/en/tv/somewhere/`, you can use the somewhere segment of the URL to fetch the `Series ID`:
```bash
curl --location 'https://www3.nhk.or.jp/nhkworld/data/en/tv/program/somewhere.json'
```

The response will be a JSON object where the id field is the `Series ID`:
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

To initiate the NHK Stream Downloader, navigate to the directory containing the config file and run the following command:

```bash
python main.py
```

Upon execution, the script fetches the Electronic Program Guide (EPG) from NHK World and proceeds to download programs according to the schedule specified in the configuration.

### Running with Docker

As an alternative, Docker can be used to run the NHK Stream Downloader. Ensure Docker is installed on your machine before proceeding.

1. Pull the Docker image from the [DockerHub repository](https://hub.docker.com/repository/docker/sonumucesh/nhk-record/general) or build it yourself:

```bash
docker build -t nhk-stream-dl .
```

or

```bash
docker pull sonumucesh/nhk-record:latest
```

2. Launch a Docker container with the following command:

```bash
docker run -d \
  --name nhk-stream-dl \
  -v /path/to/config.json:/app/config.json \
  -v /path/to/recordings:/app/recordings \
  -v /path/to/logs:/app/logs \
  -e CONFIG_PATH=/app/config.json \
  sonumucesh/nhk-record:latest
```

3. Alternatively, the container can be run using `docker-compose`:

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

## Important Notes

1. Sonarr uses TVDB for metadata. If the data on TVDB is incorrect, the program might not be labeled correctly in Sonarr. Please ensure the data on TheTVDB is accurate for the best results i.e if you know an episode is going to air and it's not on TVDB then add it there.

2. To check if the airing episode on NHK and the episode on Sonarr are the same, we use two methods for comparison:

   - First, we check if the episode air date is the same on both platforms.
   - As a fallback, we check if the title of the episode matches the subtitle on NHK.

   However, sometimes the NHK API doesn't provide a subtitle, so the comparison relies solely on the air dates. If both checks fail, we still download the episode as a precaution to avoid losing any content.

3. While there is no definitive NHK API available, making the process more challenging, the script has been tested and reliably matches episodes in Sonarr and NHK for several shows. For example, it has been successfully used with `"Somewhere Street"`, `"Document 72 Hours"`, and `"Cycle Around Japan"`. However, your experience may vary depending on the specific shows and episodes you are trying to match.

In the near future, we plan to update this comparison method to make it more reliable. Please stay tuned for updates.

## Disclaimer
Please note that this script is provided for educational and informational purposes only. It is intended to demonstrate the capabilities of Python and Docker in automating tasks such as downloading and scheduling. It is not intended to infringe upon any rights of NHK World or any other third party. Users are responsible for ensuring that their use of this script complies with all local, national, and international laws and regulations. The creators and contributors of this script are not responsible for any misuse or any consequences thereof.

### Contributing

Contributions are welcome! If you find any issues or would like to suggest improvements, please open an issue or submit a pull request.

### License

This project is licensed under the [MIT License](LICENSE).
