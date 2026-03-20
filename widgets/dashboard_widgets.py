from __future__ import annotations

from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget


class StatCard(QFrame):
    def __init__(self, label: str, value: str, accent: str = "#4cc9f0") -> None:
        super().__init__()
        self.setObjectName("panel")
        layout = QVBoxLayout(self)
        title = QLabel(label)
        title.setObjectName("sectionLabel")
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {accent};")
        layout.addWidget(title)
        layout.addWidget(self.value_label)


class DashboardGrid(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.layout = QGridLayout(self)
        self.cards: list[StatCard] = []

    def set_cards(self, cards: list[StatCard]) -> None:
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.cards = cards
        for index, card in enumerate(cards):
            self.layout.addWidget(card, index // 3, index % 3)
