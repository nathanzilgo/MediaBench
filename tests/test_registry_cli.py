import unittest

from src.base import Downloader, MediaProcessor, MediaType, ProcessingResult
from src.main import MediaBenchCLI
from src.registry import ProcessorRegistry


class _DummyProcessor(MediaProcessor):
    @property
    def name(self) -> str:
        return "Dummy Processor"

    @property
    def media_type(self) -> MediaType:
        return MediaType.IMAGE

    def get_cli_args(self) -> dict:
        return {
            "input": {
                "flags": ["-i", "--input"],
                "type": str,
                "required": True,
                "help": "input",
            },
            "output": {
                "flags": ["-o", "--output"],
                "type": str,
                "required": True,
                "help": "output",
            },
        }

    def process(self, **kwargs) -> ProcessingResult:
        return ProcessingResult(
            success=True,
            message="ok",
            input_path=kwargs.get("input_folder"),
            output_path=kwargs.get("output_folder"),
        )


class _DummyDownloader(Downloader):
    @property
    def name(self) -> str:
        return "Dummy Downloader"

    @property
    def source(self) -> str:
        return "Dummy"

    def get_cli_args(self) -> dict:
        return {
            "url": {
                "flags": ["-u", "--url"],
                "type": str,
                "required": True,
                "help": "url",
            },
            "output": {
                "flags": ["-o", "--output"],
                "type": str,
                "required": True,
                "help": "output",
            },
        }

    def download(self, url: str, output_path: str, **kwargs) -> ProcessingResult:
        return ProcessingResult(
            success=True, message=f"downloaded {url}", output_path=output_path
        )


class TestProcessorRegistry(unittest.TestCase):
    def test_register_and_get_processor(self):
        reg = ProcessorRegistry()
        reg.register_processor("p", _DummyProcessor())
        self.assertEqual(reg.get_processor("p").name, "Dummy Processor")

    def test_register_and_get_downloader(self):
        reg = ProcessorRegistry()
        reg.register_downloader("d", _DummyDownloader())
        self.assertEqual(reg.get_downloader("d").name, "Dummy Downloader")

    def test_get_missing_raises(self):
        reg = ProcessorRegistry()
        with self.assertRaises(KeyError):
            reg.get_processor("missing")
        with self.assertRaises(KeyError):
            reg.get_downloader("missing")


class TestCLI(unittest.TestCase):
    def _make_cli(self) -> MediaBenchCLI:
        reg = ProcessorRegistry()
        reg.register_processor("compress-images", _DummyProcessor())
        reg.register_downloader("youtube-video", _DummyDownloader())
        return MediaBenchCLI(registry=reg)

    def test_cli_no_args_returns_0(self):
        cli = self._make_cli()
        rc = cli.run([])
        self.assertEqual(rc, 0)

    def test_cli_dispatch_processor_and_maps_kwargs(self):
        cli = self._make_cli()
        rc = cli.run(["compress-images", "-i", "in", "-o", "out"])
        self.assertEqual(rc, 0)

    def test_cli_dispatch_downloader_and_maps_kwargs(self):
        cli = self._make_cli()
        rc = cli.run(["youtube-video", "-u", "http://example", "-o", "./x"])
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
