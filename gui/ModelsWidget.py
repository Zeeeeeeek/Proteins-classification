import os
import sys

from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QPushButton

from gui.ModelsThread import ModelsThread


class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        if self:
            self.textWritten.emit(str(text))


class ModelsWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ModelsWidget, self).__init__(parent)
        self.parent = parent
        self.textEdit = QtWidgets.QTextEdit()
        self.textEdit.setReadOnly(True)

        # Title
        title_label = QtWidgets.QLabel("Models")
        title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        # Form layout
        form_layout = QtWidgets.QFormLayout()

        # Csv file
        self.csv_file_edit = QtWidgets.QLineEdit()
        self.csv_file_edit.setReadOnly(True)
        self.csv_file_button = QtWidgets.QPushButton()
        self.csv_file_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DirIcon))
        self.csv_file_button.clicked.connect(self.get_file_name)
        csv_layout = QtWidgets.QHBoxLayout()
        csv_layout.addWidget(self.csv_file_edit)
        csv_layout.addWidget(self.csv_file_button)
        csv_layout.setStretch(0, 5)
        csv_layout.setStretch(1, 1)
        form_layout.addRow("Csv file*", csv_layout)

        # Level
        self.level_menu = QtWidgets.QComboBox()
        self.level_menu.addItems(["Class", "Topology", "Fold", "Clan", "Class_topology",
                                  "Class_topology_fold", "Class_topology_fold_clan"])
        form_layout.addRow("Level*", self.level_menu)

        # Method
        self.method_menu = QtWidgets.QComboBox()
        self.method_menu.addItems(["Classifiers", "Clustering"])
        form_layout.addRow("Method*", self.method_menu)

        # Max samples per level
        self.max_samples_edit = QtWidgets.QLineEdit()
        self.max_samples_edit.setPlaceholderText("5")
        form_layout.addRow("Max samples per level", self.max_samples_edit)

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        button = QtWidgets.QPushButton("Start")
        button.clicked.connect(self.run)
        layout.addWidget(title_label)
        layout.addLayout(form_layout)
        layout.addWidget(button)
        layout.addWidget(self.textEdit)
        self.thread = None

    def run(self):
        try:
            sys.stdout = EmittingStream()
            sys.stdout.textWritten.connect(self.normal_output_written)
            csv_file = self.csv_file_edit.text()
            if not csv_file:
                raise ValueError("Error: csv file is required.")
            self.textEdit.clear()
            self.thread = ModelsThread(
                csv_file,
                self.level_menu.currentText().lower(),
                self.method_menu.currentText().lower(),
                int(self.max_samples_edit.text()) if self.max_samples_edit.text() else 5
            )
            self.set_widget_enabled(False)
            self.thread.finished.connect(self.on_models_finished)
            self.thread.error.connect(self.on_models_error)
            self.thread.start()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def on_models_finished(self):
        self.set_widget_enabled(True)
        self.thread = None
        sys.stdout = sys.__stdout__
        QMessageBox.information(self, "Success", "Models completed successfully")

    def on_models_error(self, exc):
        self.set_widget_enabled(True)
        self.thread = None
        sys.stdout = sys.__stdout__
        QMessageBox.critical(self, "Error", exc)

    def set_widget_enabled(self, enabled):
        self.csv_file_button.setEnabled(enabled)
        self.level_menu.setEnabled(enabled)
        self.method_menu.setEnabled(enabled)
        self.max_samples_edit.setEnabled(enabled)
        if self.parent:
            for child_widget in self.parent.findChildren(QPushButton):
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

    def normal_output_written(self, text):
        cursor = self.textEdit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)
        cursor.insertText(text)
        self.textEdit.setTextCursor(cursor)
        self.textEdit.ensureCursorVisible()
