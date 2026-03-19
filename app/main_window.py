from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
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

from models.project import (
    ActorStation,
    Cue,
    Device,
    EventSequence,
    ExhibitInteraction,
    ExperienceProject,
    LayoutItem,
    MediaAsset,
    Node,
    PuzzleDefinition,
    RuntimeState,
    ScareEvent,
    TriggerRule,
)
from models.templates import PROJECT_TEMPLATES
from pages.dashboard_page import DashboardPage
from pages.deployment_page import DeploymentPage
from pages.map_page import MapPage
from pages.media_page import MediaPage
from pages.module_page import ModuleEntityPage
from pages.setup_page import SetupPage
from pages.timeline_page import TimelinePage
from services.export_service import ExportService
from services.project_service import ProjectService
from widgets.entity_page import EntityPage


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("IMMERSE Designer")
        self.resize(1600, 940)
        self.project_service = ProjectService()
        self.export_service = ExportService()
        self.sample_projects = self.project_service.sample_projects()
        self.project = ExperienceProject.from_dict(self.sample_projects["RAVEN HOLLOW HAUNT"].to_dict())
        self.current_file: Path | None = None
        self.page_factories: dict[str, QWidget] = {}

        central = QWidget()
        root = QHBoxLayout(central)
        nav_wrapper = QVBoxLayout()
        brand = QLabel("IMMERSE\nDesigner")
        brand.setObjectName("titleLabel")
        self.nav = QListWidget()
        self.nav.setMaximumWidth(240)
        nav_wrapper.addWidget(brand)
        nav_wrapper.addWidget(self.nav)
        nav_widget = QWidget()
        nav_widget.setLayout(nav_wrapper)
        nav_widget.setMaximumWidth(250)

        self.stack = QStackedWidget()
        root.addWidget(nav_widget)
        root.addWidget(self.stack, 1)
        self.setCentralWidget(central)

        self.dashboard_page = DashboardPage()
        self.setup_page = SetupPage(self.on_project_changed)
        self.map_page = MapPage(lambda: self.project, self.on_project_changed)
        self.layout_page = EntityPage("Zones / Scenes", lambda: self.project.layout_items, lambda: LayoutItem(item_type="Zone"), self.on_project_changed)
        self.device_page = EntityPage("Devices / Patch", lambda: self.project.devices, lambda: Device(), self.on_project_changed)
        self.node_page = EntityPage("Nodes / Hardware", lambda: self.project.nodes, lambda: Node(), self.on_project_changed)
        self.cue_page = EntityPage("Cue Builder", lambda: self.project.cues, lambda: Cue(), self.on_project_changed)
        self.timeline_page = TimelinePage(lambda: self.project, self.on_project_changed)
        self.trigger_page = EntityPage("Trigger Logic", lambda: self.project.trigger_rules, lambda: TriggerRule(), self.on_project_changed)
        self.state_page = EntityPage("States / Modes", lambda: self.project.runtime_states, lambda: RuntimeState(), self.on_project_changed)
        self.media_page = MediaPage(lambda: self.project, self.on_project_changed)
        self.operations_page = EntityPage("Safety / Operations", lambda: self.project.runtime_states, lambda: RuntimeState(name="Maintenance"), self.on_project_changed)
        self.deployment_page = DeploymentPage(lambda: self.project)
        self.haunt_page = ModuleEntityPage("Haunt Module", lambda: self.project.scare_events, lambda: ScareEvent(), self.on_project_changed)
        self.escape_page = ModuleEntityPage("Escape Module", lambda: self.project.puzzle_definitions, lambda: PuzzleDefinition(), self.on_project_changed)
        self.event_page = ModuleEntityPage("Events Module", lambda: self.project.event_sequences, lambda: EventSequence(), self.on_project_changed)
        self.museum_page = ModuleEntityPage("Museum Module", lambda: self.project.exhibit_interactions, lambda: ExhibitInteraction(), self.on_project_changed)
        self.actor_page = ModuleEntityPage("Actor / Operator Stations", lambda: self.project.actor_stations, lambda: ActorStation(), self.on_project_changed)

        self.pages = {
            "Dashboard": self.dashboard_page,
            "Project Setup": self.setup_page,
            "Layout / Map": self.map_page,
            "Zones / Scenes": self.layout_page,
            "Devices / Patch": self.device_page,
            "Nodes / Hardware": self.node_page,
            "Cue Builder": self.cue_page,
            "Timeline / Sequence": self.timeline_page,
            "Trigger Logic": self.trigger_page,
            "States / Modes": self.state_page,
            "Media Library": self.media_page,
            "Safety / Operations": self.operations_page,
            "Actor / Operator Stations": self.actor_page,
            "Deployment / Export": self.deployment_page,
            "Haunt Module": self.haunt_page,
            "Escape Module": self.escape_page,
            "Events Module": self.event_page,
            "Museum Module": self.museum_page,
        }
        for page in self.pages.values():
            self.stack.addWidget(page)

        self.nav.currentRowChanged.connect(self._navigate)
        self._build_toolbar()
        self.setStatusBar(QStatusBar())
        self.refresh_navigation()
        self.refresh_all_pages()
        self.statusBar().showMessage(f"Loaded sample project: {self.project.metadata.project_name}")

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Project")
        toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        for label, handler in [
            ("New Project", self.new_project),
            ("Open", self.open_project),
            ("Save", self.save_project),
            ("Save As", self.save_project_as),
            ("Load Sample", self.load_sample),
            ("Quick Export", self.quick_export),
        ]:
            button = QPushButton(label)
            if label in {"Save", "Quick Export"}:
                button.setObjectName("accentButton")
            button.clicked.connect(handler)
            toolbar.addWidget(button)

    def current_page_name(self) -> str:
        item = self.nav.currentItem()
        return item.text() if item is not None else "Dashboard"

    def refresh_navigation(self, keep_page: str | None = None) -> None:
        base_items = [
            "Dashboard",
            "Project Setup",
            "Layout / Map",
            "Zones / Scenes",
            "Devices / Patch",
            "Nodes / Hardware",
            "Cue Builder",
            "Timeline / Sequence",
            "Trigger Logic",
            "States / Modes",
            "Media Library",
            "Safety / Operations",
            "Actor / Operator Stations",
            "Deployment / Export",
        ]
        nav_items = base_items + self.project.metadata.enabled_modules
        self.nav.blockSignals(True)
        self.nav.clear()
        self.nav.addItems(nav_items)
        self.nav.blockSignals(False)
        target_page = keep_page if keep_page in nav_items else "Dashboard"
        self.nav.setCurrentRow(nav_items.index(target_page))

    def _navigate(self, row: int) -> None:
        item = self.nav.item(row)
        if item is None:
            return
        page_name = item.text()
        page = self.pages[page_name]
        self.stack.setCurrentWidget(page)

    def refresh_all_pages(self) -> None:
        self.dashboard_page.refresh(self.project)
        self.setup_page.refresh(self.project)
        self.map_page.refresh(self.project)
        self.layout_page.refresh()
        self.device_page.refresh()
        self.node_page.refresh()
        self.cue_page.refresh()
        self.timeline_page.refresh(self.project)
        self.trigger_page.refresh()
        self.state_page.refresh()
        self.media_page.refresh(self.project)
        self.operations_page.refresh()
        self.actor_page.refresh(self.project)
        self.deployment_page.refresh(self.project)
        self.haunt_page.refresh(self.project)
        self.escape_page.refresh(self.project)
        self.event_page.refresh(self.project)
        self.museum_page.refresh(self.project)

    def on_project_changed(self) -> None:
        page_name = self.current_page_name()
        self.project.touch()
        self.project.deployment.package_name = self.project.metadata.project_name.lower().replace(" ", "_")
        self.refresh_navigation(keep_page=page_name)
        self.refresh_all_pages()
        self._restore_page(page_name)
        self.statusBar().showMessage(f"Project updated: {self.project.metadata.project_name}")

    def _restore_page(self, page_name: str) -> None:
        items = [self.nav.item(index).text() for index in range(self.nav.count())]
        if page_name in items:
            self.nav.setCurrentRow(items.index(page_name))

    def new_project(self) -> None:
        project_type, ok = QInputDialog.getItem(self, "New Project", "Project Type", list(PROJECT_TEMPLATES.keys()), 4, False)
        if not ok:
            return
        project_name, ok = QInputDialog.getText(self, "New Project", "Project Name", text="Untitled Experience")
        if not ok:
            return
        self.project = self.project_service.new_project(project_type, project_name or "Untitled Experience")
        self.current_file = None
        self.refresh_navigation(keep_page="Project Setup")
        self.refresh_all_pages()
        self.statusBar().showMessage(f"Created new {project_type} project")

    def load_sample(self) -> None:
        sample_name, ok = QInputDialog.getItem(self, "Load Sample Project", "Sample", list(self.sample_projects.keys()), 0, False)
        if not ok:
            return
        self.project = ExperienceProject.from_dict(self.sample_projects[sample_name].to_dict())
        self.current_file = None
        self.refresh_navigation(keep_page="Dashboard")
        self.refresh_all_pages()
        self.statusBar().showMessage(f"Loaded sample project: {sample_name}")

    def open_project(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(self, "Open IMMERSE Designer Project", str(Path.cwd()), "JSON Files (*.json)")
        if not file_name:
            return
        self.project = self.project_service.load_project(file_name)
        self.current_file = Path(file_name)
        self.refresh_navigation(keep_page="Dashboard")
        self.refresh_all_pages()
        self.statusBar().showMessage(f"Opened {self.current_file.name}")

    def save_project(self) -> None:
        if self.current_file is None:
            self.save_project_as()
            return
        self.project_service.save_project(self.project, self.current_file)
        self.statusBar().showMessage(f"Saved {self.current_file.name}")

    def save_project_as(self) -> None:
        file_name, _ = QFileDialog.getSaveFileName(self, "Save IMMERSE Designer Project", str(Path.cwd() / "experience_project.json"), "JSON Files (*.json)")
        if not file_name:
            return
        self.current_file = self.project_service.save_project(self.project, file_name)
        self.statusBar().showMessage(f"Saved {self.current_file.name}")

    def quick_export(self) -> None:
        export_dir = Path.cwd() / "build"
        path = self.export_service.export_project(self.project, export_dir)
        QMessageBox.information(self, "Quick Export", f"Project exported to:\n{path}")
        self.statusBar().showMessage(f"Exported package to {path}")
