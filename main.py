import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QAction, QVBoxLayout, QWidget
from annotator import ZoomableAnnotationView
from config import IMAGE_FOLDER


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Coral Annotation Tool")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget and layout
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        # Pass layout to ZoomableAnnotationView
        self.viewer = ZoomableAnnotationView(layout)  # Pass the layout here
        layout.addWidget(self.viewer)  # Add the viewer to the layout

        # Set the central widget for the window
        self.setCentralWidget(central_widget)

        # Menu Actions
        open_action = QAction("Open Image", self)
        open_action.triggered.connect(self.open_image)

        save_action = QAction("Save Annotations", self)
        save_action.triggered.connect(self.viewer.save_annotations)

        # Menu Bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)

    def open_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Image", IMAGE_FOLDER, "Images (*.png *.jpg *.jpeg)"
        )
        if file_name:
            self.viewer.load_image(file_name)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
