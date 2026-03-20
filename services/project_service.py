from __future__ import annotations

from pathlib import Path
import json

from models.project import ExperienceProject
from models.templates import build_sample_projects, create_project_from_template
from services.migration_service import MigrationService


class ProjectService:
    def __init__(self) -> None:
        self.current_path: Path | None = None
        self.migration = MigrationService()

    def new_project(self, project_type: str = "General Attraction", project_name: str = "Untitled Experience") -> ExperienceProject:
        self.current_path = None
        return create_project_from_template(project_type, project_name)

    def load_project(self, path: str | Path) -> ExperienceProject:
        path = Path(path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        project = self.migration.migrate_haunt_project(payload) if self.migration.can_migrate(payload) and "metadata" not in payload else ExperienceProject.from_dict(payload)
        self.current_path = path
        return project

    def save_project(self, project: ExperienceProject, path: str | Path | None = None) -> Path:
        if path is not None:
            self.current_path = Path(path)
        if self.current_path is None:
            raise ValueError("No save path selected")
        project.save_json(self.current_path)
        return self.current_path

    def sample_projects(self) -> dict[str, ExperienceProject]:
        return build_sample_projects()
