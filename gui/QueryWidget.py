from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

class QueryWidget(QWidget):
    def __init__(self):
        super().__init__()

        title_label = QLabel("Query repeatsdb")
        title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout = QVBoxLayout()
        layout.addWidget(title_label)
        self.setLayout(layout)