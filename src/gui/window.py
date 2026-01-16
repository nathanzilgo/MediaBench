import sys
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QTextEdit,
    QLabel,
    QStatusBar,
)
from PyQt6.QtGui import QIcon, QFont

from .widgets import DynamicForm
from .workers import Worker
from ..registry import create_default_registry
from ..base import ProcessingResult


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.registry = create_default_registry()
        self.workers = []  # Keep references to running workers
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("MediaBench Native UI")
        self.resize(900, 700)

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main Layout
        layout = QVBoxLayout(central_widget)

        # Title
        title = QLabel("MediaBench")
        title_font = QFont("Arial", 20, QFont.Weight.Bold)
        title.setFont(title_font)
        layout.addWidget(title)

        # Tabs for each operation
        self.tabs = QTabWidget()
        self.init_tabs()
        layout.addWidget(self.tabs)

        # Log Output
        layout.addWidget(QLabel("Output Log:"))
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("font-family: monospace;")
        layout.addWidget(self.log_output)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def init_tabs(self):
        # Processors
        processors = self.registry.list_processors()
        for key, proc in processors.items():
            self.add_operation_tab(proc, f"🔨 {proc.name}")

        # Downloaders
        downloaders = self.registry.list_downloaders()
        for key, dl in downloaders.items():
            self.add_operation_tab(dl, f"⬇️ {dl.name}")

    def add_operation_tab(self, operation, title):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Description
        desc = QLabel(getattr(operation, "description", operation.name))
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(desc)

        # Dynamic Form
        form = DynamicForm(operation)
        form.run_requested.connect(
            lambda kwargs, op=operation: self.run_operation(op, kwargs)
        )
        layout.addWidget(form)

        self.tabs.addTab(tab, title)

    def run_operation(self, operation, kwargs):
        self.log(f"Starting {operation.name}...")
        self.status_bar.showMessage(f"Running {operation.name}...")

        # Argument Mapping (Logic adapted from src/main.py)
        # Map CLI arg names to method parameter names
        mapped_kwargs = kwargs.copy()
        arg_mapping = {}

        # Check command key to determine mapping
        # We need the key (e.g. 'compress-images') but we only have the operation object
        # We can deduce it or check operation type/name

        # Identify operation type by checking class name or attributes
        op_type = type(operation).__name__

        if op_type == "ImageCompressor":
            arg_mapping = {
                "input": "input_paths",
                "output": "output_folder",
            }
        elif op_type == "VideoCompressor":
            arg_mapping = {
                "input": "input_file",
                "output": "output_dir",
            }
        elif op_type in ["YouTubeVideoDownloader", "YouTubeAudioDownloader"]:
            arg_mapping = {"output": "output_path"}

        # Apply mapping
        final_kwargs = {}
        for key, value in mapped_kwargs.items():
            mapped_key = arg_mapping.get(key, key)
            final_kwargs[mapped_key] = value

        # Create Worker
        worker = Worker(operation, **final_kwargs)
        worker.finished.connect(self.on_process_finished)
        worker.error.connect(self.on_process_error)

        # Store worker to prevent garbage collection
        self.workers.append(worker)

        # Remove worker from list when done
        worker.finished.connect(lambda: self.cleanup_worker(worker))
        worker.error.connect(lambda: self.cleanup_worker(worker))

        worker.start()

    def on_process_finished(self, result: ProcessingResult):
        if result.success:
            self.log(f"✅ SUCCESS: {result.message}")
            if result.output_path:
                self.log(f"   Output saved to: {result.output_path}")
            if result.size_reduction_mb:
                self.log(f"   Size Reduced: {result.size_reduction_mb:.2f} MB")
        else:
            self.log(f"❌ FAILED: {result.message}")

        self.status_bar.showMessage("Ready")
        self.log("-" * 50)

    def on_process_error(self, error_msg):
        self.log(f"❌ CRITICAL ERROR: {error_msg}")
        self.status_bar.showMessage("Error occurred")
        self.log("-" * 50)

    def cleanup_worker(self, worker):
        if worker in self.workers:
            self.workers.remove(worker)

    def log(self, message):
        self.log_output.append(message)
        # Scroll to bottom
        cursor = self.log_output.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_output.setTextCursor(cursor)
