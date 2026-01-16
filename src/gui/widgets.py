from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QFileDialog,
    QFormLayout,
    QComboBox,
    QCheckBox,
)
from PyQt6.QtCore import pyqtSignal


class DynamicForm(QWidget):
    """
    A dynamic form that generates input fields based on CLI arguments configuration.
    """

    run_requested = pyqtSignal(dict)  # Emits the collected arguments

    def __init__(self, operation, parent=None):
        super().__init__(parent)
        self.operation = operation
        self.fields = {}  # Map arg_name -> widget
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        cli_args = self.operation.get_cli_args()

        # Sort args to put required ones first, but standard dict order is usually fine
        for arg_name, config in cli_args.items():
            self._add_field(form_layout, arg_name, config)

        layout.addLayout(form_layout)

        # Add Run button
        self.run_btn = QPushButton(f"Run {self.operation.name}")
        self.run_btn.clicked.connect(self.collect_and_emit)
        layout.addWidget(self.run_btn)

        layout.addStretch()

    def _add_field(self, layout, arg_name, config):
        """Creates a widget based on the argument configuration."""
        help_text = config.get("help", "")
        default = config.get("default")
        arg_type = config.get("type")

        # Determine widget type
        widget = None

        # Check for specific naming conventions to determine file/folder pickers
        # This is a heuristic based on the existing codebase conventions
        is_path = (
            "path" in arg_name
            or "folder" in arg_name
            or "file" in arg_name
            or "output" in arg_name
            or "input" in arg_name
        )

        if config.get("choices"):
            widget = QComboBox()
            widget.addItems([str(c) for c in config["choices"]])
            if default:
                index = widget.findText(str(default))
                if index >= 0:
                    widget.setCurrentIndex(index)

        elif is_path:
            # Determine if it should be a folder or file selector
            is_folder_selector = (
                "folder" in arg_name or "dir" in arg_name or "output" in arg_name
            )
            is_multi_file = False

            # Special case for Image Compressor input which expects files (multi)
            if (
                getattr(self.operation, "name", "") == "Image Compressor"
                and arg_name == "input"
            ):
                is_folder_selector = False
                is_multi_file = True

            widget = PathSelector(
                mode="folder" if is_folder_selector else "file",
                save_mode="output" in arg_name,
                multi_file=is_multi_file,
            )
            if default:
                widget.set_path(str(default))

        elif arg_type is int:
            widget = QSpinBox()
            widget.setRange(0, 10000)  # Arbitrary large range
            if "quality" in arg_name:
                widget.setRange(0, 100)
            if default is not None:
                widget.setValue(default)

        elif arg_type is bool or config.get("action") in ["store_true", "store_false"]:
            widget = QCheckBox()
            if default:
                widget.setChecked(True)

        else:
            # Default to text input
            widget = QLineEdit()
            if default is not None:
                widget.setText(str(default))

            # Special case for URL
            if "url" in arg_name:
                widget.setPlaceholderText("https://...")

        # Add tooltip
        widget.setToolTip(help_text)

        self.fields[arg_name] = widget

        # Format label: "Input Folder:" or "Quality (0-100):"
        label_text = arg_name.replace("_", " ").title()
        if config.get("required", False):
            label_text += " *"

        layout.addRow(label_text, widget)

    def collect_and_emit(self):
        """Collects values from widgets and emits them."""
        kwargs = {}
        for name, widget in self.fields.items():
            value = None
            if isinstance(widget, PathSelector):
                value = widget.path()
                # Split paths if this is the multi-file input
                if (
                    getattr(self.operation, "name", "") == "Image Compressor"
                    and name == "input"
                    and ";" in value
                ):
                    value = value.split(";")
                # Ensure it's a list for Image Compressor even if single file
                elif (
                    getattr(self.operation, "name", "") == "Image Compressor"
                    and name == "input"
                    and value
                ):
                    value = [value]
            elif isinstance(widget, QSpinBox):
                value = widget.value()
            elif isinstance(widget, QCheckBox):
                value = widget.isChecked()
            elif isinstance(widget, QComboBox):
                value = widget.currentText()
            elif isinstance(widget, QLineEdit):
                value = widget.text()

            # Simple validation for required fields
            # In a real app, we'd do better validation
            config = self.operation.get_cli_args().get(name, {})
            if (
                config.get("required")
                and not value
                and not isinstance(value, bool)
                and value != 0
            ):
                # We could show an alert here, but for now we'll let the processor handle missing args or fail
                pass

            kwargs[name] = value

        self.run_requested.emit(kwargs)


class PathSelector(QWidget):
    """Composite widget for selecting a file or folder path."""

    def __init__(self, mode="file", save_mode=False, parent=None):
        super().__init__(parent)
        self.mode = mode  # 'file' or 'folder'
        self.save_mode = save_mode

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.line_edit = QLineEdit()
        self.btn = QPushButton("Browse...")
        self.btn.clicked.connect(self.browse)

        layout.addWidget(self.line_edit)
        layout.addWidget(self.btn)

    def browse(self):
        path = ""
        if self.mode == "folder":
            path = QFileDialog.getExistingDirectory(self, "Select Directory")
        else:
            if self.save_mode:
                path, _ = QFileDialog.getSaveFileName(self, "Save File")
            else:
                path, _ = QFileDialog.getOpenFileName(self, "Open File")

        if path:
            self.line_edit.setText(path)

    def path(self):
        return self.line_edit.text()

    def set_path(self, path):
        self.line_edit.setText(path)
