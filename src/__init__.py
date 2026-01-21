"""
MediaBench - A unified media processing toolkit.

SOLID Architecture:
- Single Responsibility: Each processor handles one type of media operation
- Open/Closed: New processors can be added via the registry without modifying existing code
- Liskov Substitution: All processors implement the same abstract interface
- Interface Segregation: Separate interfaces for processors vs downloaders
- Dependency Inversion: High-level modules depend on abstractions (base classes)
"""

from .base import MediaProcessor, Downloader, ProcessingResult, MediaType
from .registry import ProcessorRegistry, create_default_registry
from .main import main, MediaBenchCLI

from .processors import (
    ImageCompressor,
    VideoCompressor,
    YouTubeVideoDownloader,
    YouTubeAudioDownloader,
)

__all__ = [
    # Base classes
    "MediaProcessor",
    "Downloader",
    "ProcessingResult",
    "MediaType",
    # Registry
    "ProcessorRegistry",
    "create_default_registry",
    # CLI
    "main",
    "MediaBenchCLI",
    # Processors
    "ImageCompressor",
    "VideoCompressor",
    "YouTubeVideoDownloader",
    "YouTubeAudioDownloader",
]
