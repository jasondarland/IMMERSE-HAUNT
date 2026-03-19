from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsView, QHBoxLayout, QLabel, QListWidget, QPushButton, QSplitter, QVBoxLayout, QWidget

from map_editor.map_scene import MapScene
from models.project import ExperienceProject, LayoutItem
from widgets.property_editor import PropertyEditor


class MapPage(QWidget):
    def __init__(self, project_getter, on_changed):
        super().__init__()
        self.project_getter = project_getter
        self.on_changed = on_changed
        self.selected_item: LayoutItem | None = None
        layout = QVBoxLayout(self)
        title = QLabel("Layout / Map Designer")
        title.setObjectName("titleLabel")
        layout.addWidget(title)
        toolbar = QHBoxLayout()
        add_btn = QPushButton("Add Layout Block")
        add_btn.clicked.connect(self.add_item)
        toolbar.addWidget(add_btn)
        toolbar.addStretch(1)
        layout.addLayout(toolbar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.item_list = QListWidget()
        self.item_list.currentRowChanged.connect(self.select_item)
        self.scene = MapScene(self._item_moved)
        self.view = QGraphicsView(self.scene)
        self.inspector = PropertyEditor()
        splitter.addWidget(self.item_list)
        splitter.addWidget(self.view)
        splitter.addWidget(self.inspector)
        splitter.setSizes([180, 760, 300])
        layout.addWidget(splitter)

    def refresh(self, project: ExperienceProject) -> None:
        self.item_list.blockSignals(True)
        self.item_list.clear()
        for item in project.layout_items:
            self.item_list.addItem(f"{item.name} [{item.item_type}]")
        self.item_list.blockSignals(False)
        self.scene.load_items(project.layout_items)
        if project.layout_items:
            self.item_list.setCurrentRow(0)
        else:
            self.inspector.bind(None, self.on_changed)

    def add_item(self) -> None:
        project = self.project_getter()
        item = LayoutItem(name=f"Item {len(project.layout_items) + 1}", x=40 + len(project.layout_items) * 28, y=40 + len(project.layout_items) * 22)
        project.layout_items.append(item)
        self.on_changed()
        self.refresh(project)

    def select_item(self, row: int) -> None:
        project = self.project_getter()
        self.selected_item = project.layout_items[row] if 0 <= row < len(project.layout_items) else None
        self.inspector.bind(self.selected_item, self._changed)

    def _changed(self) -> None:
        self.on_changed()
        if self.selected_item is not None and self.item_list.currentItem() is not None:
            self.item_list.currentItem().setText(f"{self.selected_item.name} [{self.selected_item.item_type}]")
        self.scene.load_items(self.project_getter().layout_items)

    def _item_moved(self) -> None:
        self.on_changed()
        self.scene.load_items(self.project_getter().layout_items)
