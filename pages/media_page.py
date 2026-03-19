from __future__ import annotations

from models.project import ExperienceProject, MediaAsset
from widgets.entity_page import EntityPage


class MediaPage(EntityPage):
    def __init__(self, project_getter, on_project_changed):
        super().__init__(
            "Media Library",
            collection_getter=lambda: project_getter().media_assets,
            create_factory=lambda: MediaAsset(name="New Media Asset", asset_type="Audio", path="media/new_asset.wav", label="New Asset"),
            on_project_changed=on_project_changed,
        )

    def refresh(self, project: ExperienceProject) -> None:
        super().refresh()
