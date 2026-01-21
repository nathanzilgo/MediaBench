"""
Video compression processor.
Single Responsibility: Only handles video compression logic.
"""

import os
from typing import Optional

from moviepy.editor import VideoFileClip

from ..base import MediaProcessor, MediaType, ProcessingResult


class VideoCompressor(MediaProcessor):
    """Compresses video files with configurable bitrate."""

    SUPPORTED_EXTENSIONS = (".mp4", ".avi", ".mov")

    @property
    def name(self) -> str:
        return "Video Compressor"

    @property
    def media_type(self) -> MediaType:
        return MediaType.VIDEO

    def get_cli_args(self) -> dict:
        return {
            "input": {
                "flags": ["-i", "--input"],
                "type": str,
                "required": True,
                "help": "Path to the input video file",
            },
            "output": {
                "flags": ["-o", "--output"],
                "type": str,
                "required": True,
                "help": "Path to the output directory",
            },
            "bitrate": {
                "flags": ["-b", "--bitrate"],
                "type": int,
                "default": 1000,
                "help": "Compression bitrate in kbps (default: 1000)",
            },
            "preset": {
                "flags": ["-p", "--preset"],
                "type": str,
                "default": "medium",
                "help": "Compression preset (ultrafast, fast, medium, slow, veryslow)",
            },
            "threads": {
                "flags": ["-t", "--threads"],
                "type": int,
                "default": 4,
                "help": "Number of threads for compression",
            },
        }

    def process(
        self,
        input_file: str,
        output_dir: str,
        bitrate: int = 1000,
        preset: str = "medium",
        threads: int = 4,
        **kwargs,
    ) -> ProcessingResult:
        """Compress a video file."""
        if not os.path.exists(input_file):
            return ProcessingResult(
                success=False,
                message=f"Input file {input_file} does not exist.",
            )

        if not input_file.lower().endswith(self.SUPPORTED_EXTENSIONS):
            return ProcessingResult(
                success=False,
                message=f"Unsupported file format. Supported: {self.SUPPORTED_EXTENSIONS}",
            )

        os.makedirs(output_dir, exist_ok=True)
        original_size = os.path.getsize(input_file)

        try:
            input_filename = os.path.basename(input_file)
            name, _ = os.path.splitext(input_filename)
            output_path = os.path.join(output_dir, f"{name}_compressed.mp4")

            video_clip = VideoFileClip(input_file)
            video_clip.write_videofile(
                output_path,
                codec="libx264",
                preset=preset,
                bitrate=f"{bitrate}k",
                audio_codec="aac",
                threads=threads,
            )
            video_clip.close()

            processed_size = os.path.getsize(output_path)

            return ProcessingResult(
                success=True,
                message="Video compression completed successfully.",
                input_path=input_file,
                output_path=output_path,
                original_size=original_size,
                processed_size=processed_size,
            )
        except Exception as e:
            return ProcessingResult(
                success=False,
                message=f"Error compressing video: {e}",
            )
