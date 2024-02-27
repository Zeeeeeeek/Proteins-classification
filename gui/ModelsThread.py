from PyQt6 import QtCore
from app.controller import run_models_on_kmers


class ModelsThread(QtCore.QThread):
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(str)

    def __init__(self, path, level, method, max_sample_size_per_level):
        QtCore.QThread.__init__(self)
        self.path = path
        self.level = level
        self.method = method
        self.max_sample_size_per_level = max_sample_size_per_level

    def run(self):
        try:
            run_models_on_kmers(
                self.path,
                self.level,
                self.method,
                self.max_sample_size_per_level
            )
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()
