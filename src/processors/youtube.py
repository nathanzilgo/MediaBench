"""
YouTube download processors.
Single Responsibility: Each class handles one type of download.
Open/Closed: New download types can be added without modifying existing code.
"""

import os
import subprocess
from typing import Optional

from pytube import YouTube
from pytube.cli import on_progress

from ..base import Downloader, ProcessingResult


class YouTubeVideoDownloader(Downloader):
    """Downloads videos from YouTube."""

    QUALITY_OPTIONS = ("144p", "240p", "360p", "480p", "720p", "1080p")

    @property
    def name(self) -> str:
        return "YouTube Video Downloader"

    @property
    def source(self) -> str:
        return "YouTube"

    def get_cli_args(self) -> dict:
        return {
            "url": {
                "flags": ["-u", "--url"],
                "type": str,
                "required": True,
                "help": "YouTube video URL",
            },
            "output": {
                "flags": ["-o", "--output"],
                "type": str,
                "required": True,
                "help": "Output directory path",
            },
            "quality": {
                "flags": ["-q", "--quality"],
                "type": str,
                "default": "720p",
                "choices": list(self.QUALITY_OPTIONS),
                "help": "Video quality (default: 720p)",
            },
        }

    def download(
        self,
        url: str,
        output_path: str,
        quality: str = "720p",
        **kwargs,
    ) -> ProcessingResult:
        """Download a video from YouTube."""
        os.makedirs(output_path, exist_ok=True)

        try:
            yt = YouTube(url, on_progress_callback=on_progress)
            stream = yt.streams.filter(
                progressive=True, file_extension="mp4", res=quality
            ).first()

            if not stream:
                stream = (
                    yt.streams.filter(progressive=True, file_extension="mp4")
                    .order_by("resolution")
                    .desc()
                    .first()
                )

            if not stream:
                return ProcessingResult(
                    success=False,
                    message=f"No suitable stream found for quality: {quality}",
                )

            downloaded_path = stream.download(output_path)

            return ProcessingResult(
                success=True,
                message=f"Video downloaded successfully: {yt.title}",
                output_path=downloaded_path,
                processed_size=os.path.getsize(downloaded_path),
            )
        except Exception as e:
            return ProcessingResult(
                success=False,
                message=f"Error downloading video: {e}",
            )


class YouTubeAudioDownloader(Downloader):
    """Downloads audio from YouTube and converts to WAV."""

    @property
    def name(self) -> str:
        return "YouTube Audio Downloader"

    @property
    def source(self) -> str:
        return "YouTube"

    def get_cli_args(self) -> dict:
        return {
            "url": {
                "flags": ["-u", "--url"],
                "type": str,
                "required": True,
                "help": "YouTube video URL",
            },
            "output": {
                "flags": ["-o", "--output"],
                "type": str,
                "default": "audio",
                "help": "Output directory path (default: audio)",
            },
            "convert_wav": {
                "flags": ["--wav"],
                "action": "store_true",
                "default": False,
                "help": "Convert to WAV format after download",
            },
        }

    def download(
        self,
        url: str,
        output_path: str = "audio",
        convert_wav: bool = False,
        **kwargs,
    ) -> ProcessingResult:
        """Download audio from YouTube."""
        os.makedirs(output_path, exist_ok=True)

        try:
            yt = YouTube(url, on_progress_callback=on_progress)
            stream = yt.streams.filter(only_audio=True).first()

            if not stream:
                return ProcessingResult(
                    success=False,
                    message="No audio stream found.",
                )

            downloaded_path = stream.download(output_path=output_path)

            if convert_wav:
                wav_path = self._convert_to_wav(downloaded_path)
                return ProcessingResult(
                    success=True,
                    message=f"Audio downloaded and converted: {yt.title}",
                    output_path=wav_path,
                    processed_size=os.path.getsize(wav_path),
                )

            return ProcessingResult(
                success=True,
                message=f"Audio downloaded successfully: {yt.title}",
                output_path=downloaded_path,
                processed_size=os.path.getsize(downloaded_path),
            )
        except Exception as e:
            return ProcessingResult(
                success=False,
                message=f"Error downloading audio: {e}",
            )

    def _convert_to_wav(self, input_file: str) -> str:
        """Convert audio file to WAV format using ffmpeg."""
        output_file = os.path.splitext(input_file)[0] + ".wav"
        command = [
            "ffmpeg",
            "-i",
            input_file,
            "-ab",
            "160k",
            "-ac",
            "2",
            "-ar",
            "44100",
            "-vn",
            output_file,
        ]
        subprocess.run(command, check=True)
        return output_file
