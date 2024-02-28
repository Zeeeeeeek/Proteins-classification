import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QWidget, QFormLayout, QLineEdit, QCheckBox, QPushButton, QVBoxLayout, QMessageBox, \
    QProgressBar, QStyle, QFileDialog, QHBoxLayout

from gui.QueryThread import QueryThread


class QueryWidget(QWidget):
    def __init__(self, parent_widget=None):
        super().__init__()
        self.thread = None
        self.parent_widget = parent_widget
        title_label = QLabel("Query repeatsdb")
        title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setSpacing(15)
        main_layout.addWidget(title_label)
        layout = QFormLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Query
        self.classes_layout = QHBoxLayout()
        self.class_2 = QCheckBox("2")
        self.class_3 = QCheckBox("3")
        self.class_4 = QCheckBox("4")
        self.class_5 = QCheckBox("5")
        self.classes_layout.addWidget(self.class_2)
        self.classes_layout.addWidget(self.class_3)
        self.classes_layout.addWidget(self.class_4)
        self.classes_layout.addWidget(self.class_5)
        layout.addRow("Query classes", self.classes_layout)

        # Output file
        self.output_line_edit = QLineEdit()
        self.output_line_edit.setReadOnly(True)
        self.output_line_edit.setPlaceholderText("output")
        self.output_button = QPushButton()
        self.output_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
        self.output_button.clicked.connect(self.get_save_file_name)
        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_line_edit)
        output_layout.addWidget(self.output_button)
        output_layout.setStretch(0, 5)
        output_layout.setStretch(1, 1)
        layout.addRow("Output file name", output_layout)

        # Number of threads
        self.n_threads_line_edit = QLineEdit()
        self.n_threads_line_edit.setPlaceholderText("5")
        layout.addRow("Number of threads", self.n_threads_line_edit)

        # Merge regions
        self.merge_regions = QCheckBox()
        self.merge_regions.setChecked(True)
        layout.addRow("Merge regions", self.merge_regions)

        # Run button
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_button_clicked)

        main_layout.addLayout(layout)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.run_button)
        self.setLayout(main_layout)

    def checkbox_state_changed(self, state):
        if state == Qt.CheckState.Checked:
            selected_text = self.sender().text()
            print(f"Checkbox selezionata: {selected_text}")

    def run_button_clicked(self):
        try:
            classes = self.get_classes()
            print(classes)
            if not classes:
                raise ValueError("Query cannot be empty")
            self.progress_bar.show()
            self.progress_bar.setRange(0, 0)
            self.set_widget_enabled(False)
            self.thread = QueryThread(
                classes,
                self.output_line_edit.text() if self.output_line_edit.text() else "output",
                self.merge_regions.isChecked(),
                int(self.n_threads_line_edit.text()) if self.n_threads_line_edit.text() else 5
            )
            self.thread.finished.connect(self.on_query_finished)
            self.thread.error.connect(self.on_query_error)
            self.thread.start()
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))

    def on_query_end(self, title, message, success):
        if success:
            QMessageBox.information(self, title, message)
        else:
            QMessageBox.critical(self, title, message)
        self.progress_bar.hide()
        self.set_widget_enabled(True)
        self.thread = None
        self.class_2.setChecked(False)
        self.class_3.setChecked(False)
        self.class_4.setChecked(False)
        self.class_5.setChecked(False)
        self.output_line_edit.clear()
        self.n_threads_line_edit.clear()

    def on_query_error(self, message):
        self.on_query_end("Error", message, False)

    def on_query_finished(self):
        self.on_query_end("Success", "Query completed successfully", True)

    def set_widget_enabled(self, enabled: bool):
        self.class_2.setEnabled(enabled)
        self.class_3.setEnabled(enabled)
        self.class_4.setEnabled(enabled)
        self.class_5.setEnabled(enabled)
        self.output_line_edit.setEnabled(enabled)
        self.merge_regions.setEnabled(enabled)
        self.run_button.setEnabled(enabled)
        self.n_threads_line_edit.setEnabled(enabled)

        if self.parent_widget:
            for child_widget in self.parent_widget.findChildren(QPushButton):
                child_widget.setEnabled(enabled)

    def get_save_file_name(self):
        file_filter = 'Query file (*.csv)'
        response = QFileDialog.getSaveFileName(
            parent=self,
            caption='Select an output file',
            directory=os.getcwd(),
            filter=file_filter,
        )
        self.output_line_edit.setText(str(response[0]))

    def get_classes(self):
        result = []
        if self.class_2.isChecked():
            result.append('2')
        if self.class_3.isChecked():
            result.append('3')
        if self.class_4.isChecked():
            result.append('4')
        if self.class_5.isChecked():
            result.append('5')
        return result
