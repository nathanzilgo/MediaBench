"""
Abstract base classes for media processing operations.
Follows Interface Segregation and Dependency Inversion principles.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class MediaType(Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"


@dataclass
class ProcessingResult:
    """Result of a media processing operation."""

    success: bool
    message: str
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    original_size: Optional[int] = None
    processed_size: Optional[int] = None

    @property
    def size_reduction_mb(self) -> Optional[float]:
        if self.original_size and self.processed_size:
            return (self.original_size - self.processed_size) / (1024 * 1024)
        return None


class MediaProcessor(ABC):
    """Abstract base class for all media processors."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the processor."""
        pass

    @property
    @abstractmethod
    def media_type(self) -> MediaType:
        """Type of media this processor handles."""
        pass

    @abstractmethod
    def process(self, **kwargs) -> ProcessingResult:
        """Execute the processing operation."""
        pass

    @abstractmethod
    def get_cli_args(self) -> dict:
        """Return CLI argument definitions for this processor."""
        pass


class Downloader(ABC):
    """Abstract base class for media downloaders."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the downloader."""
        pass

    @property
    @abstractmethod
    def source(self) -> str:
        """Source platform name."""
        pass

    @abstractmethod
    def download(self, url: str, output_path: str, **kwargs) -> ProcessingResult:
        """Download media from the source."""
        pass

    @abstractmethod
    def get_cli_args(self) -> dict:
        """Return CLI argument definitions for this downloader."""
        pass
