from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QInputDialog, QGraphicsPolygonItem, QGraphicsTextItem
from PyQt5.QtGui import QPixmap, QPen, QColor, QPolygonF, QBrush, QPainter
from PyQt5.QtCore import Qt, QPointF, QRectF
import os

from config import OUTPUT_FOLDER
from data_handler import save_annotations


class ZoomableAnnotationView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setRenderHints(self.renderHints() | QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self.image_item = None
        self.current_points = []
        self.polygon_items = []

        self.scale_factor = 1.15

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

    def save_annotations(self):
        if not self.image_path:
            return

        base = os.path.basename(self.image_path)
        name, _ = os.path.splitext(base)

        annotations = []
        for item in self.polygon_items:
            if isinstance(item, tuple):
                poly, label = item
                coords = [(point.x(), point.y()) for point in poly]
                annotations.append({"label": label, "points": coords})

        out_path = os.path.join(OUTPUT_FOLDER, f"{name}_annotations.json")
        save_annotations(out_path, annotations)
