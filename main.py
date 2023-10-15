import subprocess
import requests
import json
from datetime import datetime
import pytz
import time
import os
from pyarr import SonarrAPI
from fuzzywuzzy import fuzz

# Global variables
time_to_sleep_till_next_program = 0
programs_to_download = []
cached_schedule = []

# Constants
LOCAL_TIMEZONE = pytz.timezone("Europe/London")
EPG_URL = ""
LIVESTREAM_URL = ""
SERIES_IDS = []
RECORDING_PATH = ""
SONARR_URL = ""
SONARR_API_KEY = ""
SONARR_INTEGRATION = ""
SERIES_IDS_MAPPING = {}
FFMPEG_LOG_PATH = ""
FUZZY_MATCH_RATIO = 85
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0',
    'Accept': '*/*',
    'Accept-Language': 'en-GB,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www3.nhk.or.jp/',
    'Origin': 'https://www3.nhk.or.jp',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site'
}


def get_epg_now():
    """
    Get the current EPG and store the programs that match the series IDs in the global variable `programs_to_download`.
    If no programs are found, sleep until the next program starts.
    """
    response = requests.get(EPG_URL, headers=HEADERS)
    epg_json_response = response.json()

    global cached_schedule
    cached_schedule = epg_json_response["channel"]["item"]

    programs = [
        program for program in epg_json_response["channel"]["item"]
        if program["seriesId"] in SERIES_IDS_MAPPING.keys() or program["seriesId"] in SERIES_IDS
    ]

    if len(programs) == 0:
        print("No programs found from EPG")

        last_item_end_time = int(cached_schedule[-1]["endDate"]) // 1000
        last_item_end_time = (
            datetime.utcfromtimestamp(last_item_end_time)
            .replace(tzinfo=pytz.UTC)
            .astimezone(LOCAL_TIMEZONE)
        )

        current_time = datetime.now(LOCAL_TIMEZONE)

        global time_to_sleep_till_next_program
        time_to_sleep_till_next_program = int((last_item_end_time - current_time).total_seconds())

        print(
            f"Sleeping for: {time_to_sleep_till_next_program} seconds, then will call main() again."
            f" Current time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}, last item end time: "
            f"{last_item_end_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

        time.sleep(time_to_sleep_till_next_program)
        main()
    else:
        print(
            f"Programs list from EPG: {len(programs)} and current time is: "
            f"{datetime.now(LOCAL_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

        for program in programs:
            if SONARR_INTEGRATION and program["seriesId"] in SERIES_IDS_MAPPING.keys():
                sonarr(program)
            else:
                store_programs_to_download(program)


def store_programs_to_download(program, sonarr_episode_name=None):
    """
    Store the program to download in the global variable `programs_to_download`.
    """
    print(f"Program: {json.dumps(program)}")
    print("Storing program to download")
    print("Appending program to programs_to_download")

    program_dict = {
        "title": program["title"],
        "subtitle": program["subtitle"],
        "start_time": program["pubDate"],
        "end_time": program["endDate"],
        "description": program["description"],
        "duration": None,
        "sonarr_episode_name": sonarr_episode_name
    }

    # Check if the program is already in the list
    if program_dict not in programs_to_download:
        programs_to_download.append(program_dict)

    print(f"Programs to download stored: {len(programs_to_download)}\n")


def download_video(program):
    """
    Download the video for the given program from the livestream.
    """
    print(f"Downloading for: {program['duration']} seconds")
    time_to_download = int(program["duration"])
    current_year = datetime.now().year
    current_day = datetime.now().day

    if program["sonarr_episode_name"] is not None:
        filename = f"{program['sonarr_episode_name']}.mp4"
    elif program["subtitle"] != "":
        filename = f"{program['title']} - {current_year}x{current_day} - {program['subtitle']}.mp4"
    else:
        filename = f"{program['title']} - {current_year}x{current_day}.mp4"

    output_file = os.path.join(RECORDING_PATH, filename)
    ffmpeg_command = [
        "ffmpeg",
        "-i", LIVESTREAM_URL,
        "-t", str(time_to_download),
        "-c", "copy",
        "-metadata", f"description={program['description']}",
        output_file
    ]

    process = subprocess.Popen(
        ffmpeg_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )

    with open(FFMPEG_LOG_PATH, "a+") as file:
        for line in process.stdout:
            file.write(line)

    process.wait()

    print(f"Download finished for: {filename}")
    programs_to_download.remove(program)
    print(f"Programs to download left: {len(programs_to_download)}\n")


def sonarr(program):
    """
    Check if the program is available on Sonarr and store the program to download with the correct episode name.
    """
    epg_program_sub_title = program["subtitle"]
    epg_air_date = program["pubDate"]
    nhk_series_id = program["seriesId"]

    tv_db_series_id = SERIES_IDS_MAPPING[nhk_series_id]

    start_time_seconds = int(epg_air_date) // 1000
    start_time_utc = datetime.utcfromtimestamp(start_time_seconds).replace(tzinfo=pytz.UTC).date()

    sonarrApi = SonarrAPI(SONARR_URL, SONARR_API_KEY)

    series = SonarrAPI.get_series(self=sonarrApi, id_=tv_db_series_id, tvdb=True)[-1]
    series_id = SonarrAPI.get_series(self=sonarrApi, id_=tv_db_series_id, tvdb=True)[-1]['id']
    episodes = SonarrAPI.get_episode(self=sonarrApi, id_=series_id, series=True)

    for episode in episodes:
        sonarr_date = None
        try:
            sonarr_date = datetime.strptime(episode.get('airDateUtc', ''), '%Y-%m-%dT%H:%M:%S%z').astimezone(
                pytz.UTC).date()
        except Exception as e:
            pass

        episode_info = {
            'epg_program_sub_title': epg_program_sub_title,
            'epg_air_date': epg_air_date,
            'epg_converted_air_date': start_time_utc,
            'sonarr_episode_title': episode['title'],
            'sonarr_air_date': episode.get('airDateUtc', ''),
            'converted_sonarr_air_date': sonarr_date
        }

        if (sonarr_date is not None and sonarr_date == start_time_utc) \
                or fuzzy_match(program, episode) > FUZZY_MATCH_RATIO:
            print_sonarr_and_epg_episode_info(**episode_info)
            episode_title = check_if_duplicate(series, episode)
            if episode_title:
                store_programs_to_download(program, episode_title)
            elif episode_title is not False:
                store_programs_to_download(program)


def print_sonarr_and_epg_episode_info(epg_program_sub_title, epg_air_date, epg_converted_air_date, sonarr_episode_title,
                                      sonarr_air_date, converted_sonarr_air_date, fuzzy_match_ratio=None):
    """
    Print the episode information from Sonarr and the EPG.
    """
    print("Program from EPG:")
    print(f"title: {epg_program_sub_title}")
    print(f"with non-converted air date: {epg_air_date}")

    if epg_converted_air_date is not None:
        print(f"with converted air date: {epg_converted_air_date.strftime('%Y-%m-%d')}\n")
    else:
        print(f"Cant convert air date: {epg_air_date}\n")

    print("Program from Sonarr:")
    print(f"title: {sonarr_episode_title}")
    print(f"non-converted air date: {sonarr_air_date}")

    if converted_sonarr_air_date is not None:
        print(f"converted air date: {converted_sonarr_air_date.strftime('%Y-%m-%d')}\n")
    else:
        print(f"Cant convert air date: {sonarr_air_date}\n")

    if fuzzy_match_ratio is not None:
        print(
            f"Fuzzy ratio between names: {fuzzy_match_ratio} where threshold "
            f"for FUZZY_MATCH_RATIO is: {FUZZY_MATCH_RATIO}\n"
        )


def fuzzy_match(program, episode):
    title_ratio = fuzz.ratio(program['subtitle'], episode['title'])
    return title_ratio


def check_if_duplicate(series, episode):
    """
    Check if the episode has already been downloaded.
    If it hasn't, return the episode title.
    """
    if episode['hasFile']:
        print("The episode has already been downloaded.")
        print(f"Episode from Sonarr: {episode}\n")
        return False
    else:
        print("The episode has not been downloaded.")
        episode_title = f"{series['title']} - {episode['seasonNumber']}x{episode['episodeNumber']} - {episode['title']}"
        print(f"Episode title: {episode_title}\n")
        return episode_title


def use_config_to_set_variables():
    """
    Use the `config.json` file to set the global variables.
    """
    global LOCAL_TIMEZONE, RECORDING_PATH, SERIES_IDS, EPG_URL, LIVESTREAM_URL, SONARR_INTEGRATION, \
        SONARR_URL, SONARR_API_KEY, SERIES_IDS_MAPPING, FFMPEG_LOG_PATH, FUZZY_MATCH_RATIO
    with open("config.json") as config_file:
        config = json.load(config_file)

    # Extract the parameters from the config
    local_timezone_config = config.get("local_timezone")
    recording_path_config = config.get("recording_path")
    series_ids_list_config = config.get("series_ids")
    epg_url_config = config.get("epg_url")
    livestream_url_config = config.get("livestream_url")
    sonarr_integration_config = config.get("sonarr_integration")
    sonarr_url_config = config.get("sonarr_url")
    sonarr_api_key_config = config.get("sonarr_api_key")
    series_ids_mapping_config = config.get("series_ids_mapping")
    ffmpeg_log_path_config = config.get("ffmpeg_log_path")
    fuzzy_match_ratio_config = config.get("fuzzy_match_ratio")

    # Set the global variables
    if local_timezone_config is not None:
        LOCAL_TIMEZONE = pytz.timezone(local_timezone_config)
    else:
        print("No local_timezone found in config.json, using Europe/London")

    if recording_path_config is not None:
        RECORDING_PATH = recording_path_config
    else:
        print("No output_path found in config.json, using recordings")
        RECORDING_PATH = os.path.join(os.getcwd(), "recordings")

    if ffmpeg_log_path_config is not None:
        FFMPEG_LOG_PATH = ffmpeg_log_path_config
    else:
        print("No ffmpeg_log_path found in config.json, using ffmpeg.log")
        FFMPEG_LOG_PATH = os.path.join(os.getcwd(), "ffmpeg.log")

    if series_ids_list_config is not None:
        SERIES_IDS = series_ids_list_config
    else:
        print("No series_ids found in config.json, using empty list")
        SERIES_IDS = []

    if epg_url_config is not None:
        EPG_URL = epg_url_config
    else:
        print("No epg_url found in config.json, so the program will not be able to get the EPG")
        return False

    if livestream_url_config is not None:
        LIVESTREAM_URL = livestream_url_config
    else:
        print("No livestream_url found in config.json, so the program will not be able to get the livestream")
        return False

    if sonarr_integration_config is not None:
        SONARR_INTEGRATION = bool(sonarr_integration_config)
        if SONARR_URL is None or SONARR_API_KEY is None:
            print("No sonarr_url or sonarr_api_key found in config.json, so the program will not be able to use Sonarr")
            SONARR_INTEGRATION = False
        else:
            SONARR_URL = sonarr_url_config
            SONARR_API_KEY = sonarr_api_key_config
    else:
        print("No sonarr_integration found in config.json, so the program will not be able to use Sonarr")
        SONARR_INTEGRATION = False

    if series_ids_mapping_config is not None:
        for series_id_mapping in series_ids_mapping_config:
            SERIES_IDS_MAPPING[series_id_mapping['nhk_series_id']] = series_id_mapping['tv_db_id']
    else:
        if SONARR_INTEGRATION:
            print("No series_ids_mapping found in config.json, so the program will not be able to use Sonarr")
            SONARR_INTEGRATION = False

    if fuzzy_match_ratio_config is not None:
        FUZZY_MATCH_RATIO = int(fuzzy_match_ratio_config)
    else:
        print("No fuzzy_match_ratio found in config.json, using 85")
        FUZZY_MATCH_RATIO = 85

    print(f"LOCAL_TIMEZONE: {LOCAL_TIMEZONE}")
    print(f"RECORDING_PATH: {RECORDING_PATH}")
    print(f"FFMPEG_LOG_PATH: {FFMPEG_LOG_PATH}")
    print(f"SERIES_IDS: {SERIES_IDS}")
    print(f"EPG_URL: {EPG_URL}")
    print(f"LIVESTREAM_URL: {LIVESTREAM_URL}")
    print(f"SONARR_INTEGRATION: {SONARR_INTEGRATION}")
    print(f"SONARR_URL: {SONARR_URL}")
    print("SONARR_API_KEY: REDACTED")
    print(f"SERIES_IDS_MAPPING: {SERIES_IDS_MAPPING}\n")
    return True


def main():
    """
    The main function that runs the program.
    """
    # Check if the config.json file exists and if it does, use it to set the variables
    if use_config_to_set_variables() is False:
        return False

    get_epg_now()

    for program in programs_to_download:
        # Convert the timestamp from milliseconds to seconds
        start_time_ms = program["start_time"]
        start_time_seconds = int(start_time_ms) // 1000

        end_time_ms = program["end_time"]
        end_time_seconds = int(end_time_ms) // 1000

        # Convert the start_time_seconds to datetime object in UTC timezone
        start_time_utc = datetime.utcfromtimestamp(start_time_seconds).replace(tzinfo=pytz.UTC)
        end_time_utc = datetime.utcfromtimestamp(end_time_seconds).replace(tzinfo=pytz.UTC)

        # Get the current time
        current_time = datetime.now(LOCAL_TIMEZONE)

        # Convert the start_time_utc to datetime object in your local timezone
        start_time_local = start_time_utc.astimezone(LOCAL_TIMEZONE)
        end_time_local = end_time_utc.astimezone(LOCAL_TIMEZONE)

        # Calculate the time difference between the adjusted start time and the current time
        global time_to_sleep_till_next_program
        time_to_sleep_till_next_program = int((start_time_local - current_time).total_seconds())

        program["start_time"] = start_time_local
        program["end_time"] = end_time_local
        program["duration"] = int((end_time_local - start_time_local).total_seconds())

        if time_to_sleep_till_next_program > 0:
            print(f"{program['title']} starts at: {start_time_local.strftime('%Y-%m-%d %H:%M:%S')} "
                  f"and current time is: {current_time.strftime('%Y-%m-%d %H:%M:%S')} with duration: "
                  f"{program['duration']} seconds")
            print(f"Sleeping for: {time_to_sleep_till_next_program} seconds\n")
            time.sleep(time_to_sleep_till_next_program)

        if time_to_sleep_till_next_program < 0:
            print(f"{program['title']} started at: {start_time_local.strftime('%Y-%m-%d %H:%M:%S')} "
                  f"and current time is: {current_time.strftime('%Y-%m-%d %H:%M:%S')} with duration: "
                  f"{program['duration']} seconds")
            print("Skipping program\n")
            programs_to_download.remove(program)
            continue

        download_video(program)

    if len(programs_to_download) == 0:
        current_time = datetime.now(LOCAL_TIMEZONE)
        print(f"No more programs to download at the end of main() and current time is: "
              f"{current_time.strftime('%Y-%m-%d %H:%M:%S')}")

        last_item_end_time = int(cached_schedule[-1]["endDate"]) // 1000
        last_item_end_time = datetime.utcfromtimestamp(last_item_end_time).replace(tzinfo=pytz.UTC).astimezone(
            LOCAL_TIMEZONE)
        current_time = datetime.now(LOCAL_TIMEZONE)

        # Check if the last item in the schedule has ended and if it hasn't, sleep until it has
        if last_item_end_time > current_time:
            time_to_sleep_till_next_program = int((last_item_end_time - current_time).total_seconds())
            print("Last item in the schedule has not ended yet with end time: " +
                  f"{last_item_end_time.strftime('%Y-%m-%d %H:%M:%S')} and current time is: "
                  f"{current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Sleeping for: {time_to_sleep_till_next_program} seconds and current time is: "
                  f"{current_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            time.sleep(time_to_sleep_till_next_program)

        main()


if __name__ == '__main__':
    main()
