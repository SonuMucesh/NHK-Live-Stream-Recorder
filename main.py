import subprocess
import requests
import json
from datetime import datetime
import pytz
import time
import os

# Global variables
local_timezone = ""
program_json = []
time_to_sleep_till_next_program = 0
programs_to_download = []
cached_schedule = []
url = ""

# Constants
URL = "https://nwapi.nhk.jp/nhkworld/epg/v7b/world/now.json"
PROGRAM_IDS = []


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

    response = requests.get(URL, headers=headers)
    json_response = response.json()

    global cached_schedule
    cached_schedule = json_response["channel"]["item"]

    programs = [program for program in json_response["channel"]["item"] if program["pgm_gr_id"] in PROGRAM_IDS]

    if len(programs) == 0:
        print("No programs found from EPG")
        last_item_end_time = int(cached_schedule[-1]["endDate"]) // 1000
        last_item_end_time = datetime.utcfromtimestamp(last_item_end_time).astimezone(local_timezone)
        current_time = datetime.now(local_timezone)
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
              str(datetime.now(local_timezone).strftime("%Y-%m-%d %H:%M:%S")) + "\n")
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
    output_path = os.environ.get("RECORDING_PATH")
    output_file = os.path.join(output_path, filename)
    ffmpeg_command = [
        "ffmpeg",
        "-i", "https://nhkwlive-ojp.akamaized.net/hls/live/2003459/nhkwlive-ojp-en/index.m3u8",
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


def main():
    global local_timezone, output_path, PROGRAM_IDS, url
    local_timezone = os.environ.get("LOCAL_TIMEZONE")
    output_path = os.environ.get("RECORDING_PATH", "asjdnasjdn")
    program_ids_list = os.environ.get("PROGRAM_IDS", "cycle,newsline,")

    if not local_timezone:
        print("Local timezone not specified in the environment variable LOCAL_TIMEZONE.")
        print("Using Europe/London as default timezone.")
        local_timezone = pytz.timezone("Europe/London")

    if not output_path:
        print("Output path not specified in the environment variable OUTPUT_PATH.")
        return

    if program_ids_list:
        PROGRAM_IDS = program_ids_list.split(",")
    else:
        print("Program IDs not specified in the environment variable PROGRAM_IDS.")
        return


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
        current_time = datetime.now(local_timezone)

        # Convert the start_time_utc to datetime object in your local timezone
        start_time_local = start_time_utc.astimezone(local_timezone)
        end_time_local = end_time_utc.astimezone(local_timezone)

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
        current_time = datetime.now(local_timezone)
        print("No more programs to download at the end of main() and current time is: " +
              str(current_time.strftime("%Y-%m-%d %H:%M:%S") + "\n"))
        main()


if __name__ == '__main__':
    main()
