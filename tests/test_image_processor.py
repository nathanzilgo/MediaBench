import os
import tempfile
import unittest

from PIL import Image

from src.processors.image import ImageCompressor


class TestImageCompressor(unittest.TestCase):
    def test_compress_images_in_folder_success(self):
        compressor = ImageCompressor()

        with tempfile.TemporaryDirectory() as input_dir, tempfile.TemporaryDirectory() as output_dir:
            img_path = os.path.join(input_dir, "test.jpg")
            img = Image.new("RGB", (32, 32), color=(255, 0, 0))
            img.save(img_path, quality=95)

            result = compressor.process(
                input_folder=input_dir,
                output_folder=output_dir,
                quality=50,
            )

            self.assertTrue(result.success)
            self.assertTrue(result.output_path)
            out_img = os.path.join(output_dir, "test.jpg")
            self.assertTrue(os.path.exists(out_img))
            self.assertIsNotNone(result.original_size)
            self.assertIsNotNone(result.processed_size)

    def test_compress_images_missing_input_folder(self):
        compressor = ImageCompressor()
        result = compressor.process(
            input_folder="/path/does/not/exist",
            output_folder="/tmp/out",
            quality=80,
        )
        self.assertFalse(result.success)


if __name__ == "__main__":
    unittest.main()
