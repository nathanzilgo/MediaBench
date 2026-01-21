# MediaBench

A unified media processing toolkit for image compression, video compression, and YouTube downloads.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Show all available commands
python -m src.main

# Compress images in a folder
python -m src.main compress-images -i ./photos -o ./compressed -q 80

# Compress a video file
python -m src.main compress-video -i video.mp4 -o ./output -b 1500

# Download video from YouTube
python -m src.main youtube-video -u "https://youtube.com/watch?v=..." -o ./videos -q 720p

# Download audio from YouTube (with optional WAV conversion)
python -m src.main youtube-audio -u "https://youtube.com/watch?v=..." -o ./audio --wav
```

## Commands

| Command | Description |
|---------|-------------|
| `compress-images` | Recursively compress images (JPG, JPEG, PNG) in a folder |
| `compress-video` | Compress video files (MP4, AVI, MOV) with configurable bitrate |
| `youtube-video` | Download videos from YouTube in various qualities |
| `youtube-audio` | Download audio from YouTube with optional WAV conversion |

## Project Structure

```
src/
├── __init__.py           # Package exports
├── base.py               # Abstract base classes
├── registry.py           # Processor registry
├── main.py               # Unified CLI entry point
└── processors/
    ├── __init__.py
    ├── image.py          # Image compression
    ├── video.py          # Video compression
    └── youtube.py        # YouTube downloaders
```

## Architecture

Built following **SOLID principles**:

- **Single Responsibility**: Each processor handles one media type
- **Open/Closed**: New processors can be added via the registry without modifying existing code
- **Liskov Substitution**: All processors implement the same abstract interface
- **Interface Segregation**: Separate interfaces for processors vs downloaders
- **Dependency Inversion**: High-level CLI depends on abstractions

## Programmatic Usage

```python
from src import ImageCompressor, VideoCompressor, YouTubeVideoDownloader

# Compress images
compressor = ImageCompressor()
result = compressor.process(input_folder="./photos", output_folder="./out", quality=80)
print(f"Size reduction: {result.size_reduction_mb:.2f} MB")

# Compress video
video = VideoCompressor()
result = video.process(input_file="video.mp4", output_dir="./out", bitrate=1500)

# Download from YouTube
downloader = YouTubeVideoDownloader()
result = downloader.download(url="https://...", output_path="./videos", quality="720p")
```

## Dependencies

- **Pillow**: Image processing
- **MoviePy**: Video processing
- **pytube**: YouTube downloads
- **tqdm**: Progress bars
- **ffmpeg**: Audio conversion (system dependency)