"""
Processor registry for managing available operations.
Follows Open/Closed Principle: New processors can be registered without modifying existing code.
"""

from typing import Dict, List, Type, Union

from .base import MediaProcessor, Downloader


class ProcessorRegistry:
    """Central registry for all media processors and downloaders."""

    def __init__(self):
        self._processors: Dict[str, MediaProcessor] = {}
        self._downloaders: Dict[str, Downloader] = {}

    def register_processor(self, key: str, processor: MediaProcessor) -> None:
        """Register a media processor."""
        self._processors[key] = processor

    def register_downloader(self, key: str, downloader: Downloader) -> None:
        """Register a downloader."""
        self._downloaders[key] = downloader

    def get_processor(self, key: str) -> MediaProcessor:
        """Get a processor by key."""
        if key not in self._processors:
            raise KeyError(
                f"Processor '{key}' not found. Available: {list(self._processors.keys())}"
            )
        return self._processors[key]

    def get_downloader(self, key: str) -> Downloader:
        """Get a downloader by key."""
        if key not in self._downloaders:
            raise KeyError(
                f"Downloader '{key}' not found. Available: {list(self._downloaders.keys())}"
            )
        return self._downloaders[key]

    def list_processors(self) -> Dict[str, MediaProcessor]:
        """List all registered processors."""
        return self._processors.copy()

    def list_downloaders(self) -> Dict[str, Downloader]:
        """List all registered downloaders."""
        return self._downloaders.copy()

    def list_all(self) -> Dict[str, Union[MediaProcessor, Downloader]]:
        """List all registered operations."""
        return {**self._processors, **self._downloaders}


def create_default_registry() -> ProcessorRegistry:
    """Create a registry with all default processors registered."""
    from .processors import (
        ImageCompressor,
        VideoCompressor,
        YouTubeVideoDownloader,
        YouTubeAudioDownloader,
    )

    registry = ProcessorRegistry()

    registry.register_processor("compress-images", ImageCompressor())
    registry.register_processor("compress-video", VideoCompressor())
    registry.register_downloader("youtube-video", YouTubeVideoDownloader())
    registry.register_downloader("youtube-audio", YouTubeAudioDownloader())

    return registry
