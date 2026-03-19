from __future__ import annotations

from dataclasses import asdict
from typing import Any, Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from widgets.property_editor import PropertyEditor


class EntityPage(QWidget):
    def __init__(
        self,
        title: str,
        collection_getter: Callable[[], list[Any]],
        create_factory: Callable[[], Any],
        on_project_changed: Callable[[], None],
    ) -> None:
        super().__init__()
        self.collection_getter = collection_getter
        self.create_factory = create_factory
        self.on_project_changed = on_project_changed
        self.selected: Any | None = None

        root = QVBoxLayout(self)
        title_label = QLabel(title)
        title_label.setObjectName("titleLabel")
        root.addWidget(title_label)

        toolbar = QHBoxLayout()
        add_btn = QPushButton("Add")
        remove_btn = QPushButton("Delete")
        toolbar.addWidget(add_btn)
        toolbar.addWidget(remove_btn)
        toolbar.addStretch(1)
        root.addLayout(toolbar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.list_widget = QListWidget()
        self.list_widget.setMaximumWidth(220)
        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.inspector = PropertyEditor()
        splitter.addWidget(self.list_widget)
        splitter.addWidget(self.table)
        splitter.addWidget(self.inspector)
        splitter.setSizes([180, 500, 320])
        root.addWidget(splitter)

        add_btn.clicked.connect(self.add_item)
        remove_btn.clicked.connect(self.delete_item)
        self.list_widget.currentRowChanged.connect(self.select_row)

    def refresh(self) -> None:
        items = self.collection_getter()
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        for obj in items:
            QListWidgetItem(getattr(obj, "name", getattr(obj, "id", obj.__class__.__name__)), self.list_widget)
        self.list_widget.blockSignals(False)
        self._populate_table(items)
        if items:
            self.list_widget.setCurrentRow(0)
        else:
            self.selected = None
            self.inspector.bind(None, self.on_project_changed)

    def _populate_table(self, items: list[Any]) -> None:
        if not items:
            self.table.clear()
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return
        keys = list(asdict(items[0]).keys())[:6]
        self.table.setColumnCount(len(keys))
        self.table.setHorizontalHeaderLabels([k.replace("_", " ").title() for k in keys])
        self.table.setRowCount(len(items))
        for row, obj in enumerate(items):
            payload = asdict(obj)
            for col, key in enumerate(keys):
                value = payload[key]
                if isinstance(value, list):
                    text = ", ".join(str(v) for v in value)
                else:
                    text = str(value)
                self.table.setItem(row, col, QTableWidgetItem(text))
        self.table.resizeColumnsToContents()

    def add_item(self) -> None:
        obj = self.create_factory()
        self.collection_getter().append(obj)
        self.on_project_changed()
        self.refresh()
        self.list_widget.setCurrentRow(len(self.collection_getter()) - 1)

    def delete_item(self) -> None:
        row = self.list_widget.currentRow()
        items = self.collection_getter()
        if 0 <= row < len(items):
            items.pop(row)
            self.on_project_changed()
            self.refresh()

    def select_row(self, row: int) -> None:
        items = self.collection_getter()
        self.selected = items[row] if 0 <= row < len(items) else None
        self.inspector.bind(self.selected, self._changed)

    def _changed(self) -> None:
        self.on_project_changed()
        self._populate_table(self.collection_getter())
        row = self.list_widget.currentRow()
        if row >= 0 and self.selected is not None:
            self.list_widget.item(row).setText(getattr(self.selected, "name", getattr(self.selected, "id", "Item")))
