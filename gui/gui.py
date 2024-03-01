from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QStackedWidget, QToolBar, QGridLayout, QToolButton

from gui.KmerWidget import KmerCountWidget
from gui.ModelsWidget import ModelsWidget
from gui.QueryWidget import QueryWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.kmer_widget = KmerCountWidget(self)
        self.query_widget = QueryWidget(self)
        self.models_widget = ModelsWidget(self)

        # Toolbar
        self.toolbar = QToolBar()
        self.kmer_button = QToolButton()
        self.kmer_button.setText("Kmer")
        self.kmer_button.setCheckable(True)
        self.kmer_button.setAutoExclusive(True)
        self.kmer_button.clicked.connect(self.show_kmer_widget)
        self.query_button = QToolButton()
        self.query_button.setText("Query")
        self.query_button.setCheckable(True)
        self.query_button.setChecked(True)
        self.query_button.setAutoExclusive(True)
        self.query_button.clicked.connect(self.show_query_widget)
        self.models_button = QToolButton()
        self.models_button.setText("Models")
        self.models_button.setCheckable(True)
        self.models_button.setAutoExclusive(True)
        self.models_button.clicked.connect(self.show_models_widget)
        self.toolbar.addWidget(self.query_button)
        self.toolbar.addWidget(self.kmer_button)
        self.toolbar.addWidget(self.models_button)

        # Stacked widget
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.query_widget)
        self.stacked_widget.addWidget(self.kmer_widget)
        self.stacked_widget.addWidget(self.models_widget)

        # Grid layout
        layout = QGridLayout()
        layout.addWidget(self.toolbar, 1, 1)
        layout.addWidget(self.stacked_widget, 2, 1)

        # Central widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.setWindowTitle("Protein Classifier")
        self.setFixedSize(400, 350)

    def show_kmer_widget(self):
        self.stacked_widget.setCurrentIndex(1)
        self.setFixedSize(400, 350)

    def show_query_widget(self):
        self.stacked_widget.setCurrentIndex(0)
        self.setFixedSize(400, 350)

    def show_models_widget(self):
        self.stacked_widget.setCurrentIndex(2)
        self.setFixedSize(400, 450)

    def set_enabled_toolbar(self, enabled):
        self.query_button.setEnabled(enabled)
        self.kmer_button.setEnabled(enabled)
        self.models_button.setEnabled(enabled)


def run():
    app = QApplication([])

    window = MainWindow()
    window.show()

    app.exec()
