from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsView, QHBoxLayout, QLabel, QListWidget, QPushButton, QSplitter, QVBoxLayout, QWidget

from map_editor.map_scene import MapScene
from models.project import HauntedProject, Room
from widgets.property_editor import PropertyEditor


class MapPage(QWidget):
    def __init__(self, project_getter, on_changed):
        super().__init__()
        self.project_getter = project_getter
        self.on_changed = on_changed
        self.selected_room: Room | None = None

        layout = QVBoxLayout(self)
        title = QLabel("Map / Layout Designer")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        toolbar = QHBoxLayout()
        add_room = QPushButton("Add Room Block")
        add_room.clicked.connect(self.add_room)
        toolbar.addWidget(add_room)
        toolbar.addStretch(1)
        layout.addLayout(toolbar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.room_list = QListWidget()
        self.room_list.currentRowChanged.connect(self.select_room)
        self.scene = MapScene(self._room_moved)
        self.view = QGraphicsView(self.scene)
        self.inspector = PropertyEditor()
        splitter.addWidget(self.room_list)
        splitter.addWidget(self.view)
        splitter.addWidget(self.inspector)
        splitter.setSizes([180, 720, 300])
        layout.addWidget(splitter)

    def refresh(self, project: HauntedProject) -> None:
        self.room_list.blockSignals(True)
        self.room_list.clear()
        for room in project.rooms:
            self.room_list.addItem(room.name)
        self.room_list.blockSignals(False)
        self.scene.load_rooms(project.rooms)
        if project.rooms:
            self.room_list.setCurrentRow(0)
        else:
            self.inspector.bind(None, self.on_changed)

    def add_room(self) -> None:
        project = self.project_getter()
        room = Room(name=f"Room {len(project.rooms) + 1}", x=40 + len(project.rooms) * 30, y=40 + len(project.rooms) * 25)
        project.rooms.append(room)
        self.on_changed()
        self.refresh(project)

    def select_room(self, row: int) -> None:
        project = self.project_getter()
        self.selected_room = project.rooms[row] if 0 <= row < len(project.rooms) else None
        self.inspector.bind(self.selected_room, self._changed)

    def _changed(self) -> None:
        self.on_changed()
        if self.selected_room is not None and self.room_list.currentItem() is not None:
            self.room_list.currentItem().setText(self.selected_room.name)
        self.scene.load_rooms(self.project_getter().rooms)

    def _room_moved(self) -> None:
        self.on_changed()
        self.scene.load_rooms(self.project_getter().rooms)
