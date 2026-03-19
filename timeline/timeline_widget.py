from __future__ import annotations

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QBrush, QPen
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsScene, QGraphicsView

from models.project import Timeline


class TimelineView(QGraphicsView):
    def __init__(self) -> None:
        self.scene = QGraphicsScene()
        super().__init__(self.scene)
        self.setSceneRect(QRectF(0, 0, 1200, 600))
        self.setBackgroundBrush(QColor("#0f141a"))

    def load_timeline(self, timeline: Timeline | None) -> None:
        self.scene.clear()
        if timeline is None:
            return
        row_height = 70
        pixels_per_second = 40
        for i in range(int(timeline.duration) + 1):
            line = self.scene.addLine(i * pixels_per_second, 0, i * pixels_per_second, max(300, len(timeline.tracks) * row_height), QPen(QColor("#22313f")))
            if i < timeline.duration:
                label = self.scene.addText(str(i))
                label.setDefaultTextColor(QColor("#7ec8ff"))
                label.setPos(i * pixels_per_second + 2, 0)
        for row, track in enumerate(timeline.tracks):
            y = 30 + row * row_height
            name = self.scene.addText(track.name)
            name.setDefaultTextColor(QColor("#d7dde6"))
            name.setPos(4, y)
            self.scene.addLine(0, y + 22, 1200, y + 22, QPen(QColor("#22313f")))
            for event in track.events:
                rect = QGraphicsRectItem(event.start * pixels_per_second + 120, y, max(30, event.duration * pixels_per_second), 26)
                rect.setBrush(QBrush(QColor(event.color)))
                rect.setPen(QPen(QColor("#d7dde6"), 1))
                rect.setToolTip(event.name)
                self.scene.addItem(rect)
                label = self.scene.addText(event.name)
                label.setDefaultTextColor(QColor("#11161d"))
                label.setPos(event.start * pixels_per_second + 125, y + 2)
