import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from src.processors.video import VideoCompressor


class TestVideoCompressor(unittest.TestCase):
    def test_rejects_missing_input_file(self):
        compressor = VideoCompressor()
        result = compressor.process(input_file="/nope.mp4", output_dir="/tmp")
        self.assertFalse(result.success)

    def test_rejects_unsupported_extension(self):
        compressor = VideoCompressor()
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "video.txt")
            with open(path, "wb") as f:
                f.write(b"x")
            result = compressor.process(input_file=path, output_dir=tmp)
            self.assertFalse(result.success)

    @patch("src.processors.video.VideoFileClip")
    def test_compress_success_with_mocked_moviepy(self, video_file_clip):
        compressor = VideoCompressor()

        with tempfile.TemporaryDirectory() as tmp:
            input_path = os.path.join(tmp, "video.mp4")
            with open(input_path, "wb") as f:
                f.write(b"0" * 1024)

            mock_clip = MagicMock()

            def _write_videofile(out_path, **kwargs):
                with open(out_path, "wb") as out:
                    out.write(b"1" * 512)

            mock_clip.write_videofile.side_effect = _write_videofile
            video_file_clip.return_value = mock_clip

            result = compressor.process(
                input_file=input_path,
                output_dir=tmp,
                bitrate=500,
                preset="medium",
                threads=1,
            )

            self.assertTrue(result.success)
            self.assertTrue(result.output_path)
            self.assertTrue(os.path.exists(result.output_path))
            self.assertEqual(result.original_size, 1024)
            self.assertEqual(result.processed_size, 512)
            mock_clip.close.assert_called()


if __name__ == "__main__":
    unittest.main()
