# Use an official Python runtime as the base image
FROM python:3.9-slim-buster

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python script to the container
COPY main.py .

# Run the Python script when the container starts
CMD ["python", "-u", "main.py"]