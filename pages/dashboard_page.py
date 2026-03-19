from __future__ import annotations

from PySide6.QtWidgets import QLabel, QPlainTextEdit, QVBoxLayout, QWidget

from models.project import ExperienceProject
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
        layout.addWidget(QLabel("Notes / Recent Changes"))
        layout.addWidget(self.notes)

    def refresh(self, project: ExperienceProject) -> None:
        self.summary.setText(
            f"{project.metadata.project_name}  •  {project.metadata.project_type}  •  Version {project.metadata.version}  •  Last modified {project.metadata.last_modified}"
        )
        health = self.runtime.node_health([node.name for node in project.nodes])
        online = len([item for item in health if item.status == "Healthy"])
        self.grid.set_cards(
            [
                StatCard("Layout Items", str(len(project.layout_items)), "#7ec8ff"),
                StatCard("Devices", str(len(project.devices)), "#4cc9f0"),
                StatCard("Cues", str(len(project.cues)), "#90be6d"),
                StatCard("Trigger Rules", str(len(project.trigger_rules)), "#f8961e"),
                StatCard("Modules", ", ".join(project.metadata.enabled_modules) or "Core Only", "#adb5bd"),
                StatCard("Healthy Nodes", f"{online}/{max(1, len(project.nodes))}", "#43aa8b"),
                StatCard("Warnings", str(len(project.deployment.validation_warnings)), "#f94144"),
                StatCard("Deployment", project.deployment.package_name, "#adb5bd"),
            ]
        )
        self.notes.setPlainText(project.metadata.notes)
