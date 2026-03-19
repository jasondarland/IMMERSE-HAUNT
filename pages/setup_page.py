from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from models.project import HauntedProject
from widgets.property_editor import PropertyEditor


class SetupPage(QWidget):
    def __init__(self, on_changed):
        super().__init__()
        self.on_changed = on_changed
        layout = QVBoxLayout(self)
        title = QLabel("Attraction Setup")
        title.setObjectName("titleLabel")
        self.editor = PropertyEditor()
        layout.addWidget(title)
        layout.addWidget(self.editor)

    def refresh(self, project: HauntedProject) -> None:
        self.editor.bind(project.info, self.on_changed)
