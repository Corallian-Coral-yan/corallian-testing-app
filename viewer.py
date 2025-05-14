from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


class ImageViewer(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)

        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

    def load_image(self, image_path):
        pixmap = QPixmap(image_path)
        self.pixmap_item.setPixmap(pixmap)
        self.setSceneRect(pixmap.rect())

    def wheelEvent(self, event):
        zoom_in = event.angleDelta().y() > 0
        scale_factor = 1.25 if zoom_in else 0.8
        self.scale(scale_factor, scale_factor)
