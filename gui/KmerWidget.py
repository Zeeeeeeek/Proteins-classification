import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QFormLayout, QLineEdit, QProgressBar, QPushButton, \
    QMessageBox, QFileDialog, QStyle, QHBoxLayout

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

        # Csv file
        self.csv_file_edit = QLineEdit()
        self.csv_file_edit.setReadOnly(True)
        self.csv_file_button = QPushButton()
        self.csv_file_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
        self.csv_file_button.clicked.connect(self.get_file_name)
        csv_layout = QHBoxLayout()
        csv_layout.addWidget(self.csv_file_edit)
        csv_layout.addWidget(self.csv_file_button)
        csv_layout.setStretch(0, 5)
        csv_layout.setStretch(1, 1)
        layout.addRow("Csv file*", csv_layout)

        # Kmer size
        self.kmer_size_edit = QLineEdit()
        layout.addRow("K*", self.kmer_size_edit)

        # Output file
        self.output_file_edit = QLineEdit()
        self.output_file_edit.setReadOnly(True)
        self.output_file_button = QPushButton()
        self.output_file_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
        self.output_file_button.clicked.connect(self.get_save_file_name)
        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_file_edit)
        output_layout.addWidget(self.output_file_button)
        output_layout.setStretch(0, 5)
        output_layout.setStretch(1, 1)
        layout.addRow("Output file", output_layout)

        # Run button
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
            self.set_widget_enabled(False)
            self.thread = KmerCountThread(
                csv_file,
                int(kmer_size),
                self.output_file_edit.text()
            )
            self.thread.finished.connect(self.on_kmer_count_finished)
            self.thread.error.connect(self.on_kmer_count_error)
            self.thread.start()
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))

    def on_kmer_count_end(self, title, message, success):
        if success:
            QMessageBox.information(self, title, message)
        else:
            QMessageBox.critical(self, title, message)
        self.progress_bar.hide()
        self.set_widget_enabled(True)
        self.thread = None
        self.kmer_size_edit.clear()
        self.csv_file_edit.clear()
        self.output_file_edit.clear()

    def on_kmer_count_error(self, exc):
        self.on_kmer_count_end("Error", str(exc), False)

    def on_kmer_count_finished(self):
        self.on_kmer_count_end("Success", "Kmer count finished", True)

    def set_widget_enabled(self, enabled):
        self.csv_file_edit.setEnabled(enabled)
        self.output_file_edit.setEnabled(enabled)
        self.csv_file_button.setEnabled(enabled)
        self.kmer_size_edit.setEnabled(enabled)
        self.run_button.setEnabled(enabled)
        if self.parent_widget:
            for child_widget in self.parent_widget.findChildren(QPushButton):
                child_widget.setEnabled(enabled)

    def get_file_name(self):
        file_filter = 'Data File (*.csv)'
        response = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select a file',
            directory=os.getcwd(),
            filter=file_filter,
            initialFilter='Excel File (*.xlsx *.xls)'
        )
        self.csv_file_edit.setText(str(response[0]))

    def get_save_file_name(self):
        file_filter = 'Kmer file (*.csv)'
        response = QFileDialog.getSaveFileName(
            parent=self,
            caption='Select an output file',
            directory=os.getcwd(),
            filter=file_filter,
        )
        self.output_file_edit.setText(str(response[0]))
