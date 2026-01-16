#!/usr/bin/env python3
"""
MediaBench - Unified CLI for media processing operations.

This module provides a single entry point to access all media processing
functionality including image compression, video compression, and YouTube downloads.

Usage:
    python -m src.main <command> [options]

Commands:
    compress-images  - Compress images in a folder
    compress-video   - Compress a video file
    youtube-video    - Download video from YouTube
    youtube-audio    - Download audio from YouTube

Examples:
    python -m src.main compress-images -i ./photos -o ./compressed -q 80
    python -m src.main compress-video -i video.mp4 -o ./output -b 1500
    python -m src.main youtube-video -u "https://youtube.com/watch?v=..." -o ./videos
    python -m src.main youtube-audio -u "https://youtube.com/watch?v=..." --wav
"""
import argparse
import sys
from typing import Optional

from .base import MediaProcessor, Downloader, ProcessingResult
from .registry import create_default_registry, ProcessorRegistry


class MediaBenchCLI:
    """Command-line interface for MediaBench operations."""

    def __init__(self, registry: Optional[ProcessorRegistry] = None):
        self.registry = registry or create_default_registry()

    def create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser with all subcommands."""
        parser = argparse.ArgumentParser(
            prog="mediabench",
            description="MediaBench - Unified media processing toolkit",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        subparsers = parser.add_subparsers(
            dest="command",
            title="commands",
            description="Available operations",
            help="Use '<command> --help' for more information",
        )

        # Add processor subcommands
        for key, processor in self.registry.list_processors().items():
            self._add_subparser(subparsers, key, processor)

        # Add downloader subcommands
        for key, downloader in self.registry.list_downloaders().items():
            self._add_subparser(subparsers, key, downloader)

        return parser

    def _add_subparser(
        self,
        subparsers,
        key: str,
        operation,
    ) -> None:
        """Add a subparser for a processor or downloader."""
        subparser = subparsers.add_parser(
            key,
            help=operation.name,
            description=operation.name,
        )

        cli_args = operation.get_cli_args()
        for arg_name, arg_config in cli_args.items():
            flags = arg_config.pop("flags")
            subparser.add_argument(*flags, **arg_config)
            arg_config["flags"] = flags  # Restore for potential reuse

    def run(self, args: Optional[list] = None) -> int:
        """Run the CLI with given arguments."""
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)

        if not parsed_args.command:
            parser.print_help()
            print("\n" + "=" * 60)
            self._print_available_operations()
            return 0

        return self._execute_command(parsed_args)

    def _execute_command(self, args: argparse.Namespace) -> int:
        """Execute the selected command."""
        command = args.command
        kwargs = {k: v for k, v in vars(args).items() if k != "command"}

        # Map CLI arg names to method parameter names
        arg_mapping = {
            "input": "input_paths" if "compress-images" in command else "input_file",
            "output": "output_folder" if "compress-images" in command else "output_dir",
        }

        # Special handling for downloaders
        if command in ["youtube-video", "youtube-audio"]:
            arg_mapping = {"output": "output_path"}

        mapped_kwargs = {}
        for key, value in kwargs.items():
            mapped_key = arg_mapping.get(key, key)
            mapped_kwargs[mapped_key] = value

        try:
            # Try processor first, then downloader
            try:
                operation = self.registry.get_processor(command)
                result = operation.process(**mapped_kwargs)
            except KeyError:
                operation = self.registry.get_downloader(command)
                result = operation.download(**mapped_kwargs)

            self._print_result(result)
            return 0 if result.success else 1

        except Exception as e:
            print(f"\n❌ Error: {e}")
            return 1

    def _print_result(self, result: ProcessingResult) -> None:
        """Print the processing result."""
        print("\n" + "=" * 60)
        if result.success:
            print(f"✅ {result.message}")
        else:
            print(f"❌ {result.message}")

        if result.output_path:
            print(f"📁 Output: {result.output_path}")

        if result.size_reduction_mb is not None:
            print(f"📉 Size reduction: {result.size_reduction_mb:.2f} MB")

        print("=" * 60)

    def _print_available_operations(self) -> None:
        """Print all available operations."""
        print("\n📋 Available Operations:\n")

        processors = self.registry.list_processors()
        if processors:
            print("  Processors:")
            for key, proc in processors.items():
                print(f"    • {key}: {proc.name} ({proc.media_type.value})")

        downloaders = self.registry.list_downloaders()
        if downloaders:
            print("\n  Downloaders:")
            for key, dl in downloaders.items():
                print(f"    • {key}: {dl.name} (source: {dl.source})")

        print()


def main(args: Optional[list] = None) -> int:
    """Main entry point for the CLI."""
    cli = MediaBenchCLI()
    return cli.run(args)


if __name__ == "__main__":
    sys.exit(main())
