from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QWidget, QFormLayout, QLineEdit, QCheckBox, QPushButton, QVBoxLayout, QMessageBox, \
    QProgressBar


class QueryWidget(QWidget):
    def __init__(self, parent_widget=None):
        super().__init__()
        self.parent_widget = parent_widget
        title_label = QLabel("Query repeatsdb")
        title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setSpacing(15)
        main_layout.addWidget(title_label)
        layout = QFormLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.query_line_edit = QLineEdit()
        layout.addRow("Query*", self.query_line_edit)
        self.output_line_edit = QLineEdit()
        layout.addRow("Output file name", self.output_line_edit)
        self.merge_regions = QCheckBox()
        self.merge_regions.setChecked(True)
        layout.addRow("Merge regions", self.merge_regions)
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_button_clicked)
        main_layout.addLayout(layout)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.run_button)
        self.setLayout(main_layout)

    def run_button_clicked(self):
        try:
            query_text = self.query_line_edit.text()
            output_text = self.output_line_edit.text()
            merge_regions_checked = self.merge_regions.isChecked()
            if not query_text:
                raise ValueError("Query cannot be empty")
            self.progress_bar.show()
            self.progress_bar.setRange(0, 0)
            self.setWidgetEnabled(False)
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))

    def setWidgetEnabled(self, enabled: bool):
        self.query_line_edit.setEnabled(enabled)
        self.output_line_edit.setEnabled(enabled)
        self.merge_regions.setEnabled(enabled)
        self.run_button.setEnabled(enabled)

        if self.parent_widget:
            for child_widget in self.parent_widget.findChildren(QPushButton):
                child_widget.setEnabled(enabled)
