from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from models.project import Cue, Device, HauntedProject, Node, RuntimeState, ScareEvent, TriggerRule, Zone
from models.sample_project import build_sample_project
from pages.dashboard_page import DashboardPage
from pages.deployment_page import DeploymentPage
from pages.map_page import MapPage
from pages.media_page import MediaPage
from pages.setup_page import SetupPage
from pages.timeline_page import TimelinePage
from services.export_service import ExportService
from services.project_service import ProjectService
from widgets.entity_page import EntityPage


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("IMMERSE Haunted Designer")
        self.resize(1560, 920)
        self.project_service = ProjectService()
        self.export_service = ExportService()
        # Boot with a realistic bundled project so the UI immediately demonstrates haunted-attraction workflows.
        self.project = build_sample_project()
        self.current_file: Path | None = None

        central = QWidget()
        root = QHBoxLayout(central)
        self.nav = QListWidget()
        self.nav.setMaximumWidth(220)
        self.nav.addItems(
            [
                "Dashboard",
                "Attraction Setup",
                "Map / Layout",
                "Zones",
                "Device Patch",
                "Nodes / Hardware",
                "Cue Builder",
                "Timeline / Sequence",
                "Trigger Logic",
                "Scare Programming",
                "Runtime States",
                "Media Library",
                "Deployment / Export",
            ]
        )
        self.stack = QStackedWidget()
        self.dashboard_page = DashboardPage()
        self.setup_page = SetupPage(self.on_project_changed)
        self.map_page = MapPage(lambda: self.project, self.on_project_changed)
        self.zone_page = EntityPage("Zones", lambda: self.project.zones, lambda: Zone(), self.on_project_changed)
        self.device_page = EntityPage("Device Patch", lambda: self.project.devices, lambda: Device(), self.on_project_changed)
        self.node_page = EntityPage("Nodes / Hardware", lambda: self.project.nodes, lambda: Node(), self.on_project_changed)
        self.cue_page = EntityPage("Cue Builder", lambda: self.project.cues, lambda: Cue(), self.on_project_changed)
        self.trigger_page = EntityPage("Trigger Logic", lambda: self.project.trigger_rules, lambda: TriggerRule(), self.on_project_changed)
        self.scare_page = EntityPage("Scare Programming", lambda: self.project.scares, lambda: ScareEvent(), self.on_project_changed)
        self.runtime_page = EntityPage("Runtime States", lambda: self.project.runtime_states, lambda: RuntimeState(), self.on_project_changed)
        self.timeline_page = TimelinePage(lambda: self.project, self.on_project_changed)
        self.media_page = MediaPage(lambda: self.project, self.on_project_changed)
        self.deployment_page = DeploymentPage(lambda: self.project)

        for page in [
            self.dashboard_page,
            self.setup_page,
            self.map_page,
            self.zone_page,
            self.device_page,
            self.node_page,
            self.cue_page,
            self.timeline_page,
            self.trigger_page,
            self.scare_page,
            self.runtime_page,
            self.media_page,
            self.deployment_page,
        ]:
            self.stack.addWidget(page)

        brand_panel = QVBoxLayout()
        brand = QLabel("IMMERSE\nHaunted Designer")
        brand.setObjectName("titleLabel")
        brand_panel.addWidget(brand)
        brand_panel.addWidget(self.nav)
        wrapper = QWidget()
        wrapper.setLayout(brand_panel)
        wrapper.setMaximumWidth(240)
        root.addWidget(wrapper)
        root.addWidget(self.stack, 1)
        self.setCentralWidget(central)

        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.nav.setCurrentRow(0)

        self._build_toolbar()
        self.setStatusBar(QStatusBar())
        self.refresh_all_pages()
        self.statusBar().showMessage("Loaded sample project: RAVEN HOLLOW HAUNT")

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Project")
        toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        for label, handler in [
            ("New", self.new_project),
            ("Open", self.open_project),
            ("Save", self.save_project),
            ("Save As", self.save_project_as),
            ("Load Sample", self.load_sample),
            ("Quick Export", self.quick_export),
        ]:
            btn = QPushButton(label)
            if label in {"Save", "Quick Export"}:
                btn.setObjectName("accentButton")
            btn.clicked.connect(handler)
            toolbar.addWidget(btn)

    def refresh_all_pages(self) -> None:
        self.dashboard_page.refresh(self.project)
        self.setup_page.refresh(self.project)
        self.map_page.refresh(self.project)
        self.zone_page.refresh()
        self.device_page.refresh()
        self.node_page.refresh()
        self.cue_page.refresh()
        self.timeline_page.refresh(self.project)
        self.trigger_page.refresh()
        self.scare_page.refresh()
        self.runtime_page.refresh()
        self.media_page.refresh(self.project)
        self.deployment_page.refresh(self.project)

    def on_project_changed(self) -> None:
        self.project.touch()
        self.refresh_all_pages()
        self.statusBar().showMessage(f"Project updated: {self.project.info.attraction_name}")

    def new_project(self) -> None:
        self.project = HauntedProject()
        self.current_file = None
        self.refresh_all_pages()
        self.statusBar().showMessage("Created new haunted attraction project")

    def load_sample(self) -> None:
        self.project = build_sample_project()
        self.current_file = None
        self.refresh_all_pages()
        self.statusBar().showMessage("Loaded sample project: RAVEN HOLLOW HAUNT")

    def open_project(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Haunted Project", str(Path.cwd()), "JSON Files (*.json)")
        if not file_name:
            return
        self.project = self.project_service.load_project(file_name)
        self.current_file = Path(file_name)
        self.refresh_all_pages()
        self.statusBar().showMessage(f"Opened {self.current_file.name}")

    def save_project(self) -> None:
        if self.current_file is None:
            self.save_project_as()
            return
        self.project_service.save_project(self.project, self.current_file)
        self.statusBar().showMessage(f"Saved {self.current_file.name}")

    def save_project_as(self) -> None:
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Haunted Project", str(Path.cwd() / "haunted_project.json"), "JSON Files (*.json)")
        if not file_name:
            return
        self.current_file = self.project_service.save_project(self.project, file_name)
        self.statusBar().showMessage(f"Saved {self.current_file.name}")

    def quick_export(self) -> None:
        output_dir = Path.cwd() / "build"
        package_dir = self.export_service.export_project(self.project, output_dir)
        QMessageBox.information(self, "Quick Export", f"Deployment package exported to:\n{package_dir}")
        self.statusBar().showMessage(f"Exported package to {package_dir}")


def launch() -> None:
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
