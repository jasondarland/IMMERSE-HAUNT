from __future__ import annotations

from pathlib import Path
import json
import shutil

from models.project import HauntedProject, utc_now


class ExportService:
    def export_project(self, project: HauntedProject, output_dir: str | Path) -> Path:
        output_dir = Path(output_dir)
        package_dir = output_dir / project.deployment.package_name
        if package_dir.exists():
            shutil.rmtree(package_dir)
        (package_dir / "media").mkdir(parents=True, exist_ok=True)
        (package_dir / "timelines").mkdir(parents=True, exist_ok=True)
        (package_dir / "reports").mkdir(parents=True, exist_ok=True)

        project.touch()
        # Keep the export structure explicit so IMMERSE Runtime packaging can evolve without rewriting the editor.
        manifest = {
            "attraction_name": project.info.attraction_name,
            "show_id": project.info.show_id,
            "generated_at": utc_now(),
            "target_runtime": project.deployment.target_runtime,
            "timelines": [t.name for t in project.timelines],
            "runtime_states": [s.name for s in project.runtime_states],
        }
        validation = {
            "warnings": self.validate(project),
            "device_count": len(project.devices),
            "node_count": len(project.nodes),
            "cue_count": len(project.cues),
        }

        (package_dir / "project.json").write_text(json.dumps(project.to_dict(), indent=2), encoding="utf-8")
        (package_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        (package_dir / "reports" / "validation.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
        for timeline in project.timelines:
            (package_dir / "timelines" / f"{timeline.name.lower().replace(' ', '_')}.json").write_text(
                json.dumps({"name": timeline.name, "duration": timeline.duration, "tracks": [track.name for track in timeline.tracks]}, indent=2),
                encoding="utf-8",
            )
        for asset in project.media_assets:
            asset_stub = package_dir / "media" / Path(asset.path).name
            asset_stub.write_text(f"placeholder for {asset.name}\n", encoding="utf-8")
        return package_dir

    def validate(self, project: HauntedProject) -> list[str]:
        warnings: list[str] = []
        if not project.rooms:
            warnings.append("Project has no rooms defined.")
        if not project.runtime_states:
            warnings.append("Project has no runtime states defined.")
        orphan_devices = [device.name for device in project.devices if not device.node_assignment]
        if orphan_devices:
            warnings.append(f"Devices without node assignment: {', '.join(orphan_devices)}")
        return warnings
