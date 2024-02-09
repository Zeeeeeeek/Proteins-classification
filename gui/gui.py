from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QStackedWidget, \
    QHBoxLayout, QSpacerItem, QSizePolicy

from KmerWidget import KmerCountWidget
from QueryWidget import QueryWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        title_label = QLabel("Classifier")
        title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        subtitle_label = QLabel("Select an option")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        subtitle_label.setStyleSheet("font-size: 18px;")

        self.kmer_widget = KmerCountWidget()
        self.query_widget = QueryWidget()

        self.kmer_button = QPushButton("Kmer")
        self.kmer_button.clicked.connect(self.show_kmer_widget)
        self.query_button = QPushButton("Query")
        self.query_button.clicked.connect(self.show_query_widget)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.query_widget)
        self.stacked_widget.addWidget(self.kmer_widget)

        button_layout = QHBoxLayout()

        left_spacer = QSpacerItem(10, 1)
        button_layout.addItem(left_spacer)

        button_layout.addWidget(self.query_button)

        button_layout.addSpacing(10)

        button_layout.addWidget(self.kmer_button)

        right_spacer = QSpacerItem(10, 1)
        button_layout.addItem(right_spacer)

        layout = QVBoxLayout()
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addLayout(button_layout)
        layout.addWidget(self.stacked_widget)

        self.central_widget = QWidget()
        self.central_widget.setLayout(layout)

        self.setCentralWidget(self.central_widget)
        self.setWindowTitle("Protein Classifier")
        self.setFixedSize(400, 450)

    def show_kmer_widget(self):
        self.stacked_widget.setCurrentIndex(1)

    def show_query_widget(self):
        self.stacked_widget.setCurrentIndex(0)


if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.show()

    app.exec()
