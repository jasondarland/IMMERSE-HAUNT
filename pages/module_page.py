from __future__ import annotations

from models.project import ExperienceProject
from widgets.entity_page import EntityPage


class ModuleEntityPage(EntityPage):
    def __init__(self, title, collection_getter, create_factory, on_project_changed):
        super().__init__(title, collection_getter, create_factory, on_project_changed)

    def refresh(self, project: ExperienceProject | None = None) -> None:
        super().refresh()
