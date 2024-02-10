from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QFormLayout, QLineEdit, QProgressBar, QPushButton, QMessageBox

from gui.KmerCountThread import KmerCountThread


class KmerCountWidget(QWidget):
    def __init__(self, parent_widget=None):
        super().__init__()
        self.thread = None
        self.parent_widget = parent_widget
        title_label = QLabel("Kmer Count")
        title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setSpacing(15)
        main_layout.addWidget(title_label)
        self.setLayout(main_layout)
        layout = QFormLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.csv_file_edit = QLineEdit()
        layout.addRow("Csv file*", self.csv_file_edit)
        self.kmer_size_edit = QLineEdit()
        layout.addRow("K*", self.kmer_size_edit)
        self.output_file_edit = QLineEdit()
        layout.addRow("Output file", self.output_file_edit)
        self.n_threads_edit = QLineEdit()
        self.n_threads_edit.setPlaceholderText("5")
        layout.addRow("Number of threads", self.n_threads_edit)
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
            csv_file = self.csv_file_edit.text()
            if not csv_file:
                raise ValueError("Csv file cannot be empty")
            kmer_size = self.kmer_size_edit.text()
            if not kmer_size:
                raise ValueError("K cannot be empty")
            self.progress_bar.show()
            self.progress_bar.setRange(0, 0)
            self.setWidgetEnabled(False)
            self.thread = KmerCountThread(
                csv_file,
                int(kmer_size),
                int(self.n_threads_edit.text()) if self.n_threads_edit.text() else 5,
                self.output_file_edit.text()
            )
            self.thread.finished.connect(self.on_kmer_count_finished)
            self.thread.start()
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))

    def on_kmer_count_finished(self):
        QMessageBox.information(self, "Success", "Kmer count completed successfully")
        self.progress_bar.hide()
        self.setWidgetEnabled(True)
        self.thread = None
        self.csv_file_edit.clear()
        self.kmer_size_edit.clear()
        self.n_threads_edit.clear()

    def setWidgetEnabled(self, enabled):
        self.csv_file_edit.setEnabled(enabled)
        self.kmer_size_edit.setEnabled(enabled)
        self.n_threads_edit.setEnabled(enabled)
        self.run_button.setEnabled(enabled)
        if self.parent_widget:
            for child_widget in self.parent_widget.findChildren(QPushButton):
                child_widget.setEnabled(enabled)
