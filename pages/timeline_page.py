from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QListWidget, QPushButton, QSplitter, QVBoxLayout, QWidget

from models.project import HauntedProject, Timeline, TimelineTrack
from timeline.timeline_widget import TimelineView
from widgets.property_editor import PropertyEditor


class TimelinePage(QWidget):
    def __init__(self, project_getter, on_changed):
        super().__init__()
        self.project_getter = project_getter
        self.on_changed = on_changed
        self.selected: Timeline | None = None
        layout = QVBoxLayout(self)
        title = QLabel("Timeline / Sequence Editor")
        title.setObjectName("titleLabel")
        layout.addWidget(title)
        tools = QHBoxLayout()
        add_btn = QPushButton("Add Timeline")
        add_track_btn = QPushButton("Add Track")
        add_btn.clicked.connect(self.add_timeline)
        add_track_btn.clicked.connect(self.add_track)
        tools.addWidget(add_btn)
        tools.addWidget(add_track_btn)
        tools.addStretch(1)
        layout.addLayout(tools)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self.select_timeline)
        self.timeline_view = TimelineView()
        self.inspector = PropertyEditor()
        splitter.addWidget(self.list_widget)
        splitter.addWidget(self.timeline_view)
        splitter.addWidget(self.inspector)
        splitter.setSizes([180, 760, 280])
        layout.addWidget(splitter)

    def refresh(self, project: HauntedProject) -> None:
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        for timeline in project.timelines:
            self.list_widget.addItem(timeline.name)
        self.list_widget.blockSignals(False)
        if project.timelines:
            self.list_widget.setCurrentRow(0)
        else:
            self.timeline_view.load_timeline(None)
            self.inspector.bind(None, self.on_changed)

    def add_timeline(self) -> None:
        project = self.project_getter()
        project.timelines.append(Timeline(name=f"Timeline {len(project.timelines) + 1}", tracks=[TimelineTrack(name="Track 1")]))
        self.on_changed()
        self.refresh(project)

    def add_track(self) -> None:
        if self.selected is not None:
            self.selected.tracks.append(TimelineTrack(name=f"Track {len(self.selected.tracks) + 1}"))
            self.on_changed()
            self.timeline_view.load_timeline(self.selected)

    def select_timeline(self, row: int) -> None:
        project = self.project_getter()
        self.selected = project.timelines[row] if 0 <= row < len(project.timelines) else None
        self.timeline_view.load_timeline(self.selected)
        self.inspector.bind(self.selected, self._changed)

    def _changed(self) -> None:
        self.on_changed()
        if self.selected is not None and self.list_widget.currentItem() is not None:
            self.list_widget.currentItem().setText(self.selected.name)
            self.timeline_view.load_timeline(self.selected)
