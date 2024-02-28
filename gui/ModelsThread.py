from PyQt6 import QtCore
from app.controller import run_models_on_kmers


class ModelsThread(QtCore.QThread):
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(str)

    def __init__(self, path, level, method, k, max_sample_size_per_level, random_state):
        QtCore.QThread.__init__(self)
        self.path = path
        self.level = level
        self.method = method
        self.max_sample_size_per_level = max_sample_size_per_level
        self.k = k
        self.random_state = random_state

    def run(self):
        try:
            run_models_on_kmers(
                self.path,
                self.level,
                self.method,
                self.max_sample_size_per_level,
                self.k,
                self.random_state
            )
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))
