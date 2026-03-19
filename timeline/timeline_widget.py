from __future__ import annotations

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QBrush, QPen
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsScene, QGraphicsView

from models.project import Timeline


class TimelineView(QGraphicsView):
    def __init__(self) -> None:
        self.scene = QGraphicsScene()
        super().__init__(self.scene)
        self.setSceneRect(QRectF(0, 0, 1400, 700))
        self.setBackgroundBrush(QColor("#0f141a"))

    def load_timeline(self, timeline: Timeline | None) -> None:
        self.scene.clear()
        if timeline is None:
            return
        row_height = 72
        pixels_per_second = 40
        total_height = max(300, len(timeline.tracks) * row_height + 40)
        for i in range(int(timeline.duration) + 1):
            self.scene.addLine(i * pixels_per_second + 120, 0, i * pixels_per_second + 120, total_height, QPen(QColor("#22313f")))
            label = self.scene.addText(str(i))
            label.setDefaultTextColor(QColor("#7ec8ff"))
            label.setPos(i * pixels_per_second + 122, 0)
        for index, marker in enumerate(timeline.markers):
            marker_text = self.scene.addText(f"◆ {marker}")
            marker_text.setDefaultTextColor(QColor("#f8961e"))
            marker_text.setPos(120 + index * 120, 18)
        for row, track in enumerate(timeline.tracks):
            y = 40 + row * row_height
            name = self.scene.addText(track.name)
            name.setDefaultTextColor(QColor("#d7dde6"))
            name.setPos(8, y)
            self.scene.addLine(0, y + 22, 1400, y + 22, QPen(QColor("#22313f")))
            for event in track.events:
                rect = QGraphicsRectItem(event.start * pixels_per_second + 120, y, max(32, event.duration * pixels_per_second), 26)
                rect.setBrush(QBrush(QColor(event.color)))
                rect.setPen(QPen(QColor("#d7dde6"), 1))
                rect.setToolTip(event.name)
                self.scene.addItem(rect)
                label = self.scene.addText(event.name)
                label.setDefaultTextColor(QColor("#11161d"))
                label.setPos(event.start * pixels_per_second + 125, y + 2)
