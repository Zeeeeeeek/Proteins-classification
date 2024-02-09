from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout


class KmerCountWidget(QWidget):
    def __init__(self):
        super().__init__()

        title_label = QLabel("Kmer Count")
        title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")


        layout = QVBoxLayout()
        layout.addWidget(title_label)

        self.setLayout(layout)
        self.hide()
