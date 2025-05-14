from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QInputDialog, QGraphicsPolygonItem, QGraphicsTextItem, QPushButton, QVBoxLayout
from PyQt5.QtGui import QPixmap, QPen, QColor, QPolygonF, QBrush, QPainter
from PyQt5.QtCore import Qt, QPointF, QRectF
import os

from config import OUTPUT_FOLDER
from data_handler import save_annotations


class ZoomableAnnotationView(QGraphicsView):
    def __init__(self, layout):
        super().__init__()
        self.setRenderHints(self.renderHints() | QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self.image_item = None
        self.current_points = []
        self.polygon_items = []

        self.scale_factor = 1.15

        # Store the layout and add buttons
        self.layout = layout
        self.add_buttons()

    def add_buttons(self):
        """Add control buttons to the layout."""
        # Clear All Annotations Button
        self.clear_button = QPushButton("Clear All Annotations")
        self.clear_button.clicked.connect(self.clear_annotations)
        self.layout.addWidget(self.clear_button)

        # Undo Last Annotation Button
        self.undo_button = QPushButton("Undo Last Annotation")
        self.undo_button.clicked.connect(self.undo_last_annotation)
        self.layout.addWidget(self.undo_button)

        # Zoom In/Out Buttons
        self.zoom_in_button = QPushButton("Zoom In")
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.layout.addWidget(self.zoom_in_button)

        self.zoom_out_button = QPushButton("Zoom Out")
        self.zoom_out_button.clicked.connect(self.zoom_out)
        self.layout.addWidget(self.zoom_out_button)

        # Save Annotations Button
        self.save_button = QPushButton("Save Annotations")
        self.save_button.clicked.connect(self.save_annotations)
        self.layout.addWidget(self.save_button)

        # Open Image Button
        self.open_button = QPushButton("Open Image")
        self.open_button.clicked.connect(self.open_image)
        self.layout.addWidget(self.open_button)

    def load_image(self, path):
        self.image_path = path
        self.scene.clear()
        self.current_points = []
        self.polygon_items = []

        pixmap = QPixmap(path)
        self.image_item = self.scene.addPixmap(pixmap)
        self.setSceneRect(QRectF(pixmap.rect()))

    def wheelEvent(self, event):
        zoom_in = event.angleDelta().y() > 0
        factor = self.scale_factor if zoom_in else 1 / self.scale_factor
        self.scale(factor, factor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            self.current_points.append(scene_pos)
            if len(self.current_points) > 1:
                self.draw_preview_line()
        elif event.button() == Qt.RightButton and len(self.current_points) >= 3:
            label, ok = QInputDialog.getText(
                self, "Label TAU", "Enter TAU label:")
            if ok and label:
                self.finalize_polygon(label)
        else:
            super().mousePressEvent(event)

    def draw_preview_line(self):
        if len(self.current_points) < 2:
            return
        last = self.current_points[-2]
        current = self.current_points[-1]
        line = self.scene.addLine(
            last.x(), last.y(), current.x(), current.y(), QPen(Qt.green, 2))
        self.polygon_items.append(line)

    def finalize_polygon(self, label):
        polygon = QPolygonF(self.current_points)
        poly_item = QGraphicsPolygonItem(polygon)
        poly_item.setPen(QPen(Qt.red, 2))
        poly_item.setBrush(QBrush(QColor(255, 0, 0, 40)))
        self.scene.addItem(poly_item)

        # Add label
        label_item = QGraphicsTextItem(label)
        label_item.setPos(polygon.boundingRect().topLeft())
        self.scene.addItem(label_item)

        # Store for saving
        self.polygon_items.append((polygon, label))

        # Reset current drawing
        self.current_points = []

    def clear_annotations(self):
        """Clear all annotations and reset the drawing area."""
        self.scene.clear()
        self.current_points = []
        self.polygon_items = []
        # Reload the image to reset everything
        self.load_image(self.image_path)

    def undo_last_annotation(self):
        """Undo the last drawn annotation."""
        if self.polygon_items:
            last_item = self.polygon_items.pop()
            if isinstance(last_item, QGraphicsPolygonItem):
                self.scene.removeItem(last_item)
            elif isinstance(last_item, QGraphicsLineItem):
                self.scene.removeItem(last_item)
            self.current_points.pop()

    def zoom_in(self):
        self.scale(self.scale_factor, self.scale_factor)

    def zoom_out(self):
        self.scale(1 / self.scale_factor, 1 / self.scale_factor)

    def save_annotations(self):
        """Save the annotations to a JSON file."""
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Annotations", "", "JSON Files (*.json)")
        if file_name:
            annotations = []
            for item in self.polygon_items:
                if isinstance(item, tuple):
                    poly, label = item
                    coords = [(point.x(), point.y()) for point in poly]
                    annotations.append({"label": label, "points": coords})
            save_annotations(file_name, annotations)

    def open_image(self):
        """Open an image using a file dialog."""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Images (*.png *.jpg *.bmp)")
        if file_name:
            self.load_image(file_name)
