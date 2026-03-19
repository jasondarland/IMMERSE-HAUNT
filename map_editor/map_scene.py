from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QBrush, QPen
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsScene

from models.project import Room


class RoomRectItem(QGraphicsRectItem):
    def __init__(self, room: Room, on_move: Callable[[], None]) -> None:
        super().__init__(room.x, room.y, room.width, room.height)
        self.room = room
        self.on_move = on_move
        self.setBrush(QBrush(QColor("#1f2f3f")))
        self.setPen(QPen(QColor("#4cc9f0"), 2))
        self.setFlags(
            QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable
        )
        self.setToolTip(room.name)

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        super().mouseReleaseEvent(event)
        rect = self.rect()
        pos = self.pos()
        self.room.x = rect.x() + pos.x()
        self.room.y = rect.y() + pos.y()
        self.on_move()


class MapScene(QGraphicsScene):
    def __init__(self, on_changed: Callable[[], None]) -> None:
        super().__init__()
        self.on_changed = on_changed
        self.setSceneRect(QRectF(0, 0, 1400, 900))
        self.setBackgroundBrush(QColor("#0d1117"))

    def load_rooms(self, rooms: list[Room]) -> None:
        self.clear()
        for room in rooms:
            item = RoomRectItem(room, self.on_changed)
            self.addItem(item)
            text = self.addText(room.name)
            text.setDefaultTextColor(QColor("#d7dde6"))
            text.setPos(room.x + 8, room.y + 8)

    def mouseDoubleClickEvent(self, event) -> None:  # type: ignore[override]
        super().mouseDoubleClickEvent(event)
        self.on_changed()
