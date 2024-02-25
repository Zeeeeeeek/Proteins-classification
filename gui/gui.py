from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QStackedWidget, \
    QHBoxLayout, QSpacerItem

from gui.KmerWidget import KmerCountWidget
from gui.QueryWidget import QueryWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.kmer_widget = KmerCountWidget(self)
        self.query_widget = QueryWidget(self)

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
        layout.addLayout(button_layout)
        layout.addWidget(self.stacked_widget)

        self.central_widget = QWidget()
        self.central_widget.setLayout(layout)

        self.setCentralWidget(self.central_widget)
        self.setWindowTitle("Protein Classifier")
        self.setFixedSize(400, 350)

    def show_kmer_widget(self):
        self.stacked_widget.setCurrentIndex(1)

    def show_query_widget(self):
        self.stacked_widget.setCurrentIndex(0)


def run():
    app = QApplication([])

    window = MainWindow()
    window.show()

    app.exec()


if __name__ == "__main__":
    run()
