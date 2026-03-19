from __future__ import annotations

from PySide6.QtWidgets import QLabel, QPlainTextEdit, QVBoxLayout, QWidget

from models.project import HauntedProject
from services.mock_runtime import MockRuntimeService
from widgets.dashboard_widgets import DashboardGrid, StatCard


class DashboardPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.runtime = MockRuntimeService()
        layout = QVBoxLayout(self)
        self.title = QLabel("Dashboard")
        self.title.setObjectName("titleLabel")
        self.summary = QLabel()
        self.grid = DashboardGrid()
        self.notes = QPlainTextEdit()
        self.notes.setReadOnly(True)
        self.notes.setMaximumHeight(140)
        layout.addWidget(self.title)
        layout.addWidget(self.summary)
        layout.addWidget(self.grid)
        layout.addWidget(QLabel("Project Notes"))
        layout.addWidget(self.notes)

    def refresh(self, project: HauntedProject) -> None:
        self.summary.setText(
            f"{project.info.attraction_name}  •  Show ID {project.info.show_id}  •  Version {project.info.version}  •  Last modified {project.info.last_modified}"
        )
        warnings = len([w for w in [*project.deployment.validation_warnings] if w])
        health = self.runtime.node_health([node.name for node in project.nodes])
        online = len([item for item in health if item.status == "Healthy"])
        self.grid.set_cards(
            [
                StatCard("Rooms / Scenes", str(len(project.rooms)), "#7ec8ff"),
                StatCard("Devices", str(len(project.devices)), "#4cc9f0"),
                StatCard("Trigger Rules", str(len(project.trigger_rules)), "#f8961e"),
                StatCard("Scares", str(len(project.scares)), "#f3722c"),
                StatCard("Runtime States", str(len(project.runtime_states)), "#90be6d"),
                StatCard("Healthy Nodes", f"{online}/{max(1, len(project.nodes))}", "#43aa8b"),
                StatCard("Warnings", str(warnings), "#f94144"),
                StatCard("Deployment Package", project.deployment.package_name, "#adb5bd"),
            ]
        )
        self.notes.setPlainText(project.info.project_notes or project.info.operator_notes)
