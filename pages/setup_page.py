from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from models.project import ExperienceProject
from widgets.property_editor import PropertyEditor


class SetupPage(QWidget):
    def __init__(self, on_changed):
        super().__init__()
        self.on_changed = on_changed
        layout = QVBoxLayout(self)
        title = QLabel("Project Setup")
        title.setObjectName("titleLabel")
        self.editor = PropertyEditor()
        layout.addWidget(title)
        layout.addWidget(self.editor)

    def refresh(self, project: ExperienceProject) -> None:
        self.editor.bind(project.metadata, self.on_changed)
