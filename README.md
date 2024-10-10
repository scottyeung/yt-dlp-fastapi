# YouTube to MP3 Converter API

This FastAPI-based application allows users to convert YouTube videos to MP3 audio files. It provides a simple API for submitting YouTube URLs, checking conversion status, and retrieving download links for the converted audio files.

## Features

- Convert YouTube videos to MP3 format
- Asynchronous processing using Redis for task management
- File size limit of 1GB
- Maximum video duration of 2 hours
- Support for various audio qualities

## Prerequisites

- Python 3.7+
- Redis server
- FFmpeg

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/youtube-to-mp3-api.git
   cd youtube-to-mp3-api
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up Redis:
   - Install Redis on your system if not already installed
   - Ensure Redis is running on localhost:6379 or set the `REDIS_HOST` environment variable

4. Install FFmpeg:
   - Follow the installation instructions for your operating system: [FFmpeg Download](https://ffmpeg.org/download.html)

## Usage

1. Start the FastAPI server:
   ```
   uvicorn main:app --reload
   ```

2. The API will be available at `http://localhost:8000`

3. API Endpoints:
   - `POST /submit`: Submit a YouTube URL for conversion
   - `GET /status/{task_id}`: Check the status of a conversion task
   - `GET /download/{task_id}`: Get the download URL for a completed conversion

## API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Example Usage

1. Submit a video for conversion:
   ```
   curl -X POST "http://localhost:8000/submit" -H "Content-Type: application/json" -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
   ```

2. Check conversion status:
   ```
   curl "http://localhost:8000/status/{task_id}"
   ```

3. Get download URL:
   ```
   curl "http://localhost:8000/download/{task_id}"
   ```

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This tool is for personal use only. Please respect YouTube's terms of service and copyright laws when using this API.
