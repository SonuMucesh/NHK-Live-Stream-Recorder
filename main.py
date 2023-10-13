import subprocess
import requests
import json
from datetime import datetime
import pytz
import time
import os

# Global variables
program_json = []
time_to_sleep_till_next_program = 0
programs_to_download = []
cached_schedule = []

# Constants
LOCAL_TIMEZONE = pytz.timezone("Europe/London")
EPG_URL = ""
LIVESTREAM_URL = ""
SERIES_IDS = []
RECORDING_PATH = ""


def get_epg_now():
    headers = {
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

    response = requests.get(EPG_URL, headers=headers)
    json_response = response.json()

    global cached_schedule
    cached_schedule = json_response["channel"]["item"]

    programs = [program for program in json_response["channel"]["item"] if program["seriesId"] in SERIES_IDS]

    if len(programs) == 0:
        print("No programs found from EPG")
        last_item_end_time = int(cached_schedule[-1]["endDate"]) // 1000
        last_item_end_time = datetime.utcfromtimestamp(last_item_end_time)\
            .replace(tzinfo=pytz.UTC).astimezone(LOCAL_TIMEZONE)
        current_time = datetime.now(LOCAL_TIMEZONE)
        global time_to_sleep_till_next_program
        time_to_sleep_till_next_program = int((last_item_end_time - current_time).total_seconds())
        print("Sleeping for: " + str(time_to_sleep_till_next_program) + " seconds then will call main() again"
              + " current time: " + str(current_time.strftime("%Y-%m-%d %H:%M:%S")) + " last item end time: " +
              str(last_item_end_time.strftime("%Y-%m-%d %H:%M:%S")) + "\n")
        time.sleep(time_to_sleep_till_next_program)
        main()
    else:
        print("Programs found from EPG")
        print("Programs list from EPG: " + str(len(programs)) + "and current time is: " +
              str(datetime.now(LOCAL_TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")) + "\n")
        for program in programs:
            store_programs_to_download(program)


def store_programs_to_download(program):
    print("Program: " + json.dumps(program))
    print("Storing program to download")
    print("appending program to programs_to_download")
    program_dict = {
        "title": program["title"],
        "subtitle": program["subtitle"],
        "start_time": program["pubDate"],
        "end_time": program["endDate"],
        "description": program["description"],
        "duration": None
    }
    programs_to_download.append(program_dict)
    print("Programs to download stored: " + str(len(programs_to_download)) + "\n")


def download_video(program):
    print("Downloading for: " + str(program["duration"]) + " seconds")
    time_to_download = int(program["duration"])
    currentYear = datetime.now().year
    currentDay = datetime.now().day

    filename = f"{program['title']} - {currentYear}x{currentDay}.mp4"
    if program["subtitle"] != "":
        filename = f"{program['title']} - {currentYear}x{currentDay} - {program['subtitle']}.mp4"
    output_file = os.path.join(RECORDING_PATH, filename)
    ffmpeg_command = [
        "ffmpeg",
        "-i", LIVESTREAM_URL,
        "-t", str(time_to_download),
        "-c", "copy",
        "-metadata", f"description={program['description']}",
        output_file
    ]

    process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               universal_newlines=True)

    for line in process.stdout:
        print(line, end="")

    # Wait for the process to finish
    process.wait()

    print("Download finished for: " + filename)
    programs_to_download.remove(program)
    print("Programs to download left: " + str(len(programs_to_download)) + "\n")


def use_config_to_set_variables():
    global LOCAL_TIMEZONE, RECORDING_PATH, SERIES_IDS, EPG_URL, LIVESTREAM_URL
    with open("config.json") as config_file:
        config = json.load(config_file)

    # Extract the parameters from the config
    local_timezone_config = config.get("local_timezone")
    recording_path_config = config.get("recording_path")
    series_ids_list_config = config.get("series_ids")
    epg_url_config = config.get("epg_url")
    livestream_url_config = config.get("livestream_url")

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

    print("LOCAL_TIMEZONE: " + str(LOCAL_TIMEZONE))
    print("RECORDING_PATH: " + str(RECORDING_PATH))
    print("SERIES_IDS: " + str(SERIES_IDS))
    print("EPG_URL: " + str(EPG_URL))
    print("LIVESTREAM_URL: " + str(LIVESTREAM_URL) + "\n")
    return True


def main():
    # Check if the config.json file exists and if it does, use it to set the variables
    if use_config_to_set_variables() is False:
        return False

    get_epg_now()
    for program in programs_to_download:
        # Convert the timestamp from milliseconds to seconds
        start_time_ms = program["start_time"]
        start_time_seconds = (int(start_time_ms) // 1000)

        end_time_ms = program["end_time"]
        end_time_seconds = (int(end_time_ms) // 1000)

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
            print(program["title"] + " starts at: " + str(start_time_local.strftime("%Y-%m-%d %H:%M:%S")) +
                  " and current time is: " + str(current_time.strftime("%Y-%m-%d %H:%M:%S") + " with duration: " +
                                                 str(program["duration"]) + " seconds"))
            print("Sleeping for: " + str(time_to_sleep_till_next_program) + " seconds" + "\n")
            time.sleep(time_to_sleep_till_next_program)
        if time_to_sleep_till_next_program < 0:
            print(program["title"] + " started at: " + str(start_time_local.strftime("%Y-%m-%d %H:%M:%S")) +
                  " and current time is: " + str(current_time.strftime("%Y-%m-%d %H:%M:%S") + " with duration: " +
                                                 str(program["duration"]) + " seconds"))
            print("Skipping program" + "\n")
            programs_to_download.remove(program)
            continue

        download_video(program)

    if len(programs_to_download) == 0:
        current_time = datetime.now(LOCAL_TIMEZONE)
        print("No more programs to download at the end of main() and current time is: " +
              str(current_time.strftime("%Y-%m-%d %H:%M:%S")))

        last_item_end_time = int(cached_schedule[-1]["endDate"]) // 1000
        last_item_end_time = datetime.utcfromtimestamp(last_item_end_time).replace(tzinfo=pytz.UTC).astimezone(LOCAL_TIMEZONE)
        current_time = datetime.now(LOCAL_TIMEZONE)

        # Check if the last item in the schedule has ended and if it hasn't, sleep until it has
        if last_item_end_time > current_time:
            global time_to_sleep_till_next_program
            time_to_sleep_till_next_program = int((last_item_end_time - current_time).total_seconds())
            print("Last item in the schedule has not ended yet with end time: " + str(last_item_end_time.strftime("%Y-%m-%d %H:%M:%S")) +
                  " and current time is: " + str(current_time.strftime("%Y-%m-%d %H:%M:%S")))
            print("Sleeping for: " + str(time_to_sleep_till_next_program) + " seconds and current time is: " +
                  str(current_time.strftime("%Y-%m-%d %H:%M:%S")) + "\n")
            time.sleep(time_to_sleep_till_next_program)
        main()


if __name__ == '__main__':
    main()
