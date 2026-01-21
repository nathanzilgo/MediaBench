import traceback
from PyQt6.QtCore import QThread, pyqtSignal


class Worker(QThread):
    """
    Worker thread to run media processing tasks in the background.
    """

    finished = pyqtSignal(object)  # Emits ProcessingResult
    error = pyqtSignal(str)
    progress = pyqtSignal(str)  # Emits status messages

    def __init__(self, operation, **kwargs):
        super().__init__()
        self.operation = operation
        self.kwargs = kwargs

    def run(self):
        try:
            # Check if operation is a processor or downloader
            # The 'process' vs 'download' method distinction needs to be handled
            if hasattr(self.operation, 'process'):
                result = self.operation.process(**self.kwargs)
            elif hasattr(self.operation, 'download'):
                # Downloaders usually require 'url' and 'output_path'
                # The kwargs should already contain mapped arguments from the form
                result = self.operation.download(**self.kwargs)
            else:
                raise ValueError(f"Unknown operation type: {type(self.operation)}")

            self.finished.emit(result)
        except Exception as e:
            self.error.emit(f"Error: {str(e)}\n{traceback.format_exc()}")
