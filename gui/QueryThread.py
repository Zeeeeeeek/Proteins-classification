from PyQt6.QtCore import QThread, pyqtSignal

from app.controller import run_repeatsdb_query


class QueryThread(QThread):
    finished = pyqtSignal()

    def __init__(self, query_classes, output_text, merge_regions, value):
        QThread.__init__(self)
        self.query_classes = query_classes
        self.output_text = output_text
        self.merge_regions = merge_regions
        self.value = value

    def run(self):
        run_repeatsdb_query(
            self.query_classes,
            self.output_text if self.output_text else "output",
            self.merge_regions,
            self.value
        )
        self.finished.emit()
