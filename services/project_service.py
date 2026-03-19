from __future__ import annotations

from pathlib import Path
from models.project import HauntedProject
from models.sample_project import build_sample_project


class ProjectService:
    def __init__(self) -> None:
        self.current_path: Path | None = None

    def new_project(self) -> HauntedProject:
        self.current_path = None
        return HauntedProject()

    def load_project(self, path: str | Path) -> HauntedProject:
        path = Path(path)
        self.current_path = path
        return HauntedProject.load_json(path)

    def save_project(self, project: HauntedProject, path: str | Path | None = None) -> Path:
        if path is not None:
            self.current_path = Path(path)
        if self.current_path is None:
            raise ValueError("No save path selected")
        project.save_json(self.current_path)
        return self.current_path

    def save_sample_project(self, target_dir: str | Path) -> Path:
        target_dir = Path(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        sample_path = target_dir / "raven_hollow_haunt.json"
        build_sample_project().save_json(sample_path)
        return sample_path
