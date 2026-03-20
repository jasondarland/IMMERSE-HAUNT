from __future__ import annotations

from pathlib import Path
from typing import Callable

from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QColor, QBrush, QPen, QPixmap
from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsScene, QGraphicsSimpleTextItem, QGraphicsView

from models.project import LayoutCanvasSettings, LayoutItem


class LayoutRectItem(QGraphicsRectItem):
    def __init__(self, item_data: LayoutItem, on_move: Callable[[LayoutItem], None]) -> None:
        super().__init__(0, 0, item_data.width, item_data.height)
        self.item_data = item_data
        self.on_move = on_move
        self.label = QGraphicsSimpleTextItem(self)
        self.label.setBrush(QColor("#f2f6fb"))
        self.refresh_from_model()
        self.setFlags(
            QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

    def refresh_from_model(self) -> None:
        self.setPos(self.item_data.x, self.item_data.y)
        self.setRect(0, 0, self.item_data.width, self.item_data.height)
        self.label.setText(f"{self.item_data.name}\n{self.item_data.item_type}")
        self.label.setPos(10, 10)
        self._apply_style()

    def _apply_style(self) -> None:
        fill = QColor("#263747")
        outline = QColor("#4cc9f0") if self.isSelected() else QColor("#2c95c8")
        self.setBrush(QBrush(fill))
        self.setPen(QPen(outline, 3 if self.isSelected() else 2))

    def itemChange(self, change, value):  # type: ignore[override]
        if change == QGraphicsRectItem.GraphicsItemChange.ItemSelectedHasChanged:
            self._apply_style()
        return super().itemChange(change, value)

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        super().mouseReleaseEvent(event)
        pos = self.pos()
        self.item_data.x = pos.x()
        self.item_data.y = pos.y()
        self.on_move(self.item_data)


class MapScene(QGraphicsScene):
    def __init__(self, on_item_moved: Callable[[LayoutItem], None], on_selection_changed: Callable[[LayoutItem | None], None]) -> None:
        super().__init__()
        self.on_item_moved = on_item_moved
        self.on_selection_changed = on_selection_changed
        self.rect_items: dict[str, LayoutRectItem] = {}
        self.background_item: QGraphicsPixmapItem | None = None
        self.setSceneRect(QRectF(0, 0, 3200, 2200))
        self.setBackgroundBrush(QColor("#0d1117"))
        self.selectionChanged.connect(self._emit_selection)

    def load_project(self, layout_items: list[LayoutItem], canvas: LayoutCanvasSettings) -> None:
        self.clear()
        self.rect_items.clear()
        self.background_item = None
        self._load_background(canvas)
        for item in layout_items:
            rect_item = LayoutRectItem(item, self.on_item_moved)
            self.addItem(rect_item)
            self.rect_items[item.id] = rect_item

    def _load_background(self, canvas: LayoutCanvasSettings) -> None:
        if not canvas.background_image or not Path(canvas.background_image).exists():
            return
        pixmap = QPixmap(canvas.background_image)
        if pixmap.isNull():
            return
        if canvas.fit_background_to_canvas:
            pixmap = pixmap.scaled(2200, 1600, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.background_item = QGraphicsPixmapItem(pixmap)
        self.background_item.setOpacity(canvas.background_opacity)
        self.background_item.setVisible(canvas.background_visible)
        self.background_item.setZValue(-100)
        if canvas.background_locked:
            self.background_item.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.addItem(self.background_item)
        self.background_item.setPos(0, 0)

    def select_item(self, item_id: str | None) -> None:
        for rect_item in self.rect_items.values():
            rect_item.setSelected(False)
        if item_id and item_id in self.rect_items:
            self.rect_items[item_id].setSelected(True)

    def refresh_item(self, item: LayoutItem) -> None:
        rect_item = self.rect_items.get(item.id)
        if rect_item is not None:
            rect_item.refresh_from_model()

    def _emit_selection(self) -> None:
        selected = self.selectedItems()
        layout_item = selected[0].item_data if selected and isinstance(selected[0], LayoutRectItem) else None
        self.on_selection_changed(layout_item)


class MapView(QGraphicsView):
    zoom_changed = Signal(int)

    def __init__(self, scene: MapScene) -> None:
        super().__init__(scene)
        self._zoom_percent = 100
        self.setRenderHints(self.renderHints())
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)

    @property
    def zoom_percent(self) -> int:
        return self._zoom_percent

    def set_zoom_percent(self, percent: int) -> None:
        percent = max(25, min(400, percent))
        factor = percent / self._zoom_percent
        self.scale(factor, factor)
        self._zoom_percent = percent
        self.zoom_changed.emit(self._zoom_percent)

    def zoom_in(self) -> None:
        self.set_zoom_percent(self._zoom_percent + 10)

    def zoom_out(self) -> None:
        self.set_zoom_percent(self._zoom_percent - 10)

    def reset_zoom(self) -> None:
        self.resetTransform()
        self._zoom_percent = 100
        self.zoom_changed.emit(self._zoom_percent)

    def fit_scene(self) -> None:
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self._zoom_percent = 100
        self.zoom_changed.emit(self._zoom_percent)

    def wheelEvent(self, event) -> None:  # type: ignore[override]
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
            return
        super().wheelEvent(event)
