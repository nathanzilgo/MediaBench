"""
Image compression processor.
Single Responsibility: Only handles image compression logic.
"""

import os
import shutil
from typing import Optional

from PIL import Image
from tqdm import tqdm

from ..base import MediaProcessor, MediaType, ProcessingResult


class ImageCompressor(MediaProcessor):
    """Compresses images in a folder with configurable quality."""

    SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png")

    @property
    def name(self) -> str:
        return "Image Compressor"

    @property
    def media_type(self) -> MediaType:
        return MediaType.IMAGE

    def get_cli_args(self) -> dict:
        return {
            "input": {
                "flags": ["-i", "--input"],
                "type": str,
                "nargs": "+",
                "required": True,
                "help": "Path(s) to input image files or folders",
            },
            "output": {
                "flags": ["-o", "--output"],
                "type": str,
                "required": True,
                "help": "Path to the output folder for compressed images",
            },
            "quality": {
                "flags": ["-q", "--quality"],
                "type": int,
                "default": 85,
                "help": "Quality level of the compressed images (0-100)",
            },
        }

    def process(
        self,
        input_paths: List[str],
        output_folder: str,
        quality: int = 85,
        **kwargs,
    ) -> ProcessingResult:
        """Compress images from input paths and save to output_folder."""
        # Handle case where single string is passed (e.g. from direct call)
        if isinstance(input_paths, str):
            input_paths = [input_paths]

        os.makedirs(output_folder, exist_ok=True)

        # Calculate total original size
        original_size = 0
        for path in input_paths:
            if os.path.isfile(path):
                original_size += os.path.getsize(path)
            elif os.path.isdir(path):
                original_size += self._calculate_folder_size(path)

        try:
            for path in input_paths:
                if os.path.isfile(path):
                    if path.lower().endswith(self.SUPPORTED_EXTENSIONS):
                        print(f"Compressing {os.path.basename(path)}.")
                        output_path = os.path.join(
                            output_folder, os.path.basename(path)
                        )
                        self._compress_single_image(path, output_path, quality)
                elif os.path.isdir(path):
                    self._compress_folder(path, output_folder, quality)
                else:
                    print(f"Path not found: {path}")

            processed_size = self._calculate_folder_size(output_folder)

            return ProcessingResult(
                success=True,
                message="Image compression completed successfully.",
                input_path=", ".join(input_paths),
                output_path=output_folder,
                original_size=original_size,
                processed_size=processed_size,
            )
        except Exception as e:
            return ProcessingResult(
                success=False,
                message=f"Error during compression: {e}",
            )

    def _compress_folder(
        self, input_folder: str, output_folder: str, quality: int
    ) -> None:
        """Recursively compress images in a folder."""
        for root, _, files in tqdm(
            os.walk(input_folder),
            total=len(os.listdir(input_folder)),
            desc="Compressing images recursively",
        ):
            print(f"Compressing images in {root}.")
            for filename in files:
                print(f"Compressing {filename}.")
                input_path = os.path.join(root, filename)
                output_path = os.path.join(
                    output_folder, os.path.relpath(input_path, input_folder)
                )
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                if filename.lower().endswith(self.SUPPORTED_EXTENSIONS):
                    self._compress_single_image(input_path, output_path, quality)
                else:
                    print(f"{filename} is not an image file. Skipping...")
                    shutil.copy2(input_path, output_path)

    def _compress_single_image(
        self, input_path: str, output_path: str, quality: int
    ) -> None:
        """Compress a single image file."""
        try:
            img = Image.open(input_path)
            img.save(output_path, quality=quality)
        except Exception as e:
            print(f"Error compressing image {input_path}: {e}")

    @staticmethod
    def _calculate_folder_size(folder: str) -> int:
        """Calculate total size of all files in a folder recursively."""
        total_size = 0
        for root, _, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
        return total_size
