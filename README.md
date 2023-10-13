# NHK World Video Downloader

This script allows you to download shows from NHK World based on the current schedule obtained from their EPG (Electronic Program Guide) API.

## Prerequisites

- Python 3.7 or above
- FFmpeg installed and accessible from the command line
- Docker (optional, if using the Docker setup)

## Getting Started

1. Clone the repository or download the script file.

2. Install the required Python packages by running the following command:

3. Set the environment variables:

- `RECORDING_PATH`: Specify the path where downloaded videos will be saved.
- `PROGRAM_IDS`: Provide a comma-separated list of program IDs to download.

  Example:
  ```
  export RECORDING_PATH=/path/to/output
  export PROGRAM_IDS=id1,id2,id3
  ```

4. Run the script:

```bash
python nhk_video_downloader.py
```

The script will fetch the current schedule from the NHK EPG API and download the specified programs.

## Docker Setup (Alternative)

If you prefer using Docker, follow these steps:

1. Build the Docker image:

````bash
docker build -t nhk-video-downloader .
```

2. Run the Docker container, passing the environment variables:

````bash
docker run -e RECORDING_PATH=/path/to/output -e PROGRAM_IDS=id1,id2,id3 nhk-video-downloader
```

The script will be executed inside the Docker container, and the videos will be downloaded to the specified path.

## Configuration

Instead of setting the environment variables directly, you can also provide a configuration file (`config.json`) with the following structure:

```json
{
"recording_path": "/path/to/output",
"program_ids": ["id1", "id2", "id3"]
}
```

To use the configuration file, set the `CONFIG_PATH` environment variable to the file's location:

```bash
export CONFIG_PATH=/path/to/config.json
```

## Contributing

Contributions to this project are welcome! If you encounter any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
```

Feel free to customize this README file to fit your specific project and provide any additional information that might be useful for users.