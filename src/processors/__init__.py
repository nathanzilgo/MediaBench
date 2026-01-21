"""Media processors package."""

from .image import ImageCompressor
from .video import VideoCompressor
from .youtube import YouTubeVideoDownloader, YouTubeAudioDownloader

__all__ = [
    "ImageCompressor",
    "VideoCompressor",
    "YouTubeVideoDownloader",
    "YouTubeAudioDownloader",
]
