from PyQt6.QtCore import QThread, pyqtSignal

from app.controller import run_kmer_count

class KmerCountThread(QThread):
    finished = pyqtSignal()

    def __init__(self, csv_file, kmer_size, value, output_file):
        QThread.__init__(self)
        self.csv_file = csv_file
        self.kmer_size = kmer_size
        self.value = value
        self.output_file = output_file

    def run(self):
        run_kmer_count(
            self.csv_file,
            self.kmer_size,
            self.output_file,
            self.value
        )
        self.finished.emit()
