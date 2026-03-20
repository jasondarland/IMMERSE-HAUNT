from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QFileDialog

from models.project import ExperienceProject, MediaAsset
from widgets.entity_page import EntityPage


class MediaPage(EntityPage):
    def __init__(self, project_getter, on_project_changed):
        self.project_getter = project_getter
        super().__init__(
            "Media Library",
            collection_getter=lambda: project_getter().media_assets,
            create_factory=lambda: MediaAsset(name="New Media Asset", asset_type="Audio", path="media/new_asset.wav", label="New Asset"),
            on_project_changed=on_project_changed,
        )

    def refresh(self, project: ExperienceProject) -> None:
        super().refresh()

    def add_item(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Import Media", "", "Media Files (*.wav *.mp3 *.mp4 *.mov *.png *.jpg *.jpeg)")
        if not path:
            super().add_item()
            return
        asset_type = "Audio"
        suffix = Path(path).suffix.lower()
        if suffix in {".mp4", ".mov"}:
            asset_type = "Video"
        elif suffix in {".png", ".jpg", ".jpeg"}:
            asset_type = "Image"
        asset = MediaAsset(name=Path(path).name, asset_type=asset_type, path=path, label=Path(path).stem)
        self.collection_getter().append(asset)
        self.selected = asset
        self.on_project_changed()
        self.refresh(self.project_getter())
