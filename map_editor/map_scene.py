from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QBrush, QPen
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsScene

from models.project import LayoutItem


class LayoutRectItem(QGraphicsRectItem):
    def __init__(self, item_data: LayoutItem, on_move: Callable[[], None]) -> None:
        super().__init__(item_data.x, item_data.y, item_data.width, item_data.height)
        self.item_data = item_data
        self.on_move = on_move
        self.setBrush(QBrush(QColor("#1f2f3f")))
        self.setPen(QPen(QColor("#4cc9f0"), 2))
        self.setFlags(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable | QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable)
        self.setToolTip(f"{item_data.name} ({item_data.item_type})")

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        super().mouseReleaseEvent(event)
        rect = self.rect()
        pos = self.pos()
        self.item_data.x = rect.x() + pos.x()
        self.item_data.y = rect.y() + pos.y()
        self.on_move()


class MapScene(QGraphicsScene):
    def __init__(self, on_changed: Callable[[], None]) -> None:
        super().__init__()
        self.on_changed = on_changed
        self.setSceneRect(QRectF(0, 0, 1600, 900))
        self.setBackgroundBrush(QColor("#0d1117"))

    def load_items(self, layout_items: list[LayoutItem]) -> None:
        self.clear()
        for item in layout_items:
            rect_item = LayoutRectItem(item, self.on_changed)
            self.addItem(rect_item)
            text = self.addText(f"{item.name}\n{item.item_type}")
            text.setDefaultTextColor(QColor("#d7dde6"))
            text.setPos(item.x + 8, item.y + 8)
