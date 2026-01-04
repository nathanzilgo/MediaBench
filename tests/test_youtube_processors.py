import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from src.processors.youtube import YouTubeAudioDownloader, YouTubeVideoDownloader


class _DummyStream:
    def __init__(self, payload: bytes = b"data"):
        self._payload = payload

    def download(self, output_path: str):
        os.makedirs(output_path, exist_ok=True)
        out_path = os.path.join(output_path, "downloaded.mp4")
        with open(out_path, "wb") as f:
            f.write(self._payload)
        return out_path


class _DummyStreams:
    def __init__(self, stream: _DummyStream):
        self._stream = stream

    def filter(self, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def desc(self):
        return self

    def first(self):
        return self._stream


class _DummyYouTube:
    def __init__(self, url: str, on_progress_callback=None):
        self.url = url
        self.title = "dummy"
        self.streams = _DummyStreams(_DummyStream())


class TestYouTubeDownloaders(unittest.TestCase):
    @patch("src.processors.youtube.YouTube", _DummyYouTube)
    def test_youtube_video_download_success(self):
        downloader = YouTubeVideoDownloader()
        with tempfile.TemporaryDirectory() as out_dir:
            result = downloader.download(
                url="https://example.com",
                output_path=out_dir,
                quality="720p",
            )
            self.assertTrue(result.success)
            self.assertTrue(result.output_path)
            self.assertTrue(os.path.exists(result.output_path))

    @patch("src.processors.youtube.YouTube", _DummyYouTube)
    def test_youtube_audio_download_success_without_wav(self):
        downloader = YouTubeAudioDownloader()
        with tempfile.TemporaryDirectory() as out_dir:
            result = downloader.download(
                url="https://example.com",
                output_path=out_dir,
                convert_wav=False,
            )
            self.assertTrue(result.success)
            self.assertTrue(os.path.exists(result.output_path))

    @patch("src.processors.youtube.YouTube", _DummyYouTube)
    def test_youtube_audio_download_success_with_wav(self):
        downloader = YouTubeAudioDownloader()
        with tempfile.TemporaryDirectory() as out_dir:
            with patch.object(downloader, "_convert_to_wav") as convert:
                wav_path = os.path.join(out_dir, "downloaded.wav")

                def _convert(inp):
                    with open(wav_path, "wb") as f:
                        f.write(b"wav")
                    return wav_path

                convert.side_effect = _convert

                result = downloader.download(
                    url="https://example.com",
                    output_path=out_dir,
                    convert_wav=True,
                )

                self.assertTrue(result.success)
                self.assertEqual(result.output_path, wav_path)
                self.assertTrue(os.path.exists(wav_path))


if __name__ == "__main__":
    unittest.main()
