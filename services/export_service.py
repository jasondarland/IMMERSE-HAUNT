from __future__ import annotations

from pathlib import Path
import json
import shutil
import zipfile

from models.project import ExperienceProject, utc_now


class ExportService:
    def export_project(self, project: ExperienceProject, output_dir: str | Path, as_zip: bool = False) -> Path:
        output_dir = Path(output_dir)
        package_dir = output_dir / project.deployment.package_name
        if package_dir.exists():
            shutil.rmtree(package_dir)
        for folder in ["media", "timelines", "reports", "modules"]:
            (package_dir / folder).mkdir(parents=True, exist_ok=True)

        project.touch()
        warnings = self.validate(project)
        project.deployment.validation_warnings = warnings
        manifest = {
            "project_name": project.metadata.project_name,
            "project_type": project.metadata.project_type,
            "show_id": project.metadata.show_id,
            "generated_at": utc_now(),
            "target_runtime": project.deployment.target_runtime,
            "enabled_modules": project.metadata.enabled_modules,
            "formats": project.deployment.supported_formats,
        }
        validation = {
            "warnings": warnings,
            "layout_count": len(project.layout_items),
            "device_count": len(project.devices),
            "node_count": len(project.nodes),
            "cue_count": len(project.cues),
        }
        (package_dir / "project.json").write_text(json.dumps(project.to_dict(), indent=2), encoding="utf-8")
        (package_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        (package_dir / "reports" / "validation.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
        for timeline in project.timelines:
            (package_dir / "timelines" / f"{timeline.name.lower().replace(' ', '_')}.json").write_text(json.dumps({"name": timeline.name, "duration": timeline.duration, "markers": timeline.markers}, indent=2), encoding="utf-8")
        for module_name in project.metadata.enabled_modules:
            (package_dir / "modules" / f"{module_name.lower().replace(' ', '_')}.json").write_text(json.dumps({"module": module_name, "enabled": True}, indent=2), encoding="utf-8")
        for asset in project.media_assets:
            (package_dir / "media" / Path(asset.path).name).write_text(f"placeholder for {asset.name}\n", encoding="utf-8")
        if as_zip:
            zip_path = output_dir / f"{project.deployment.package_name}.zip"
            if zip_path.exists():
                zip_path.unlink()
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for file_path in package_dir.rglob("*"):
                    if file_path.is_file():
                        zf.write(file_path, file_path.relative_to(package_dir.parent))
            return zip_path
        return package_dir

    def validate(self, project: ExperienceProject) -> list[str]:
        warnings: list[str] = []
        if not project.layout_items:
            warnings.append("Project has no layout items defined.")
        if not project.runtime_states:
            warnings.append("Project has no runtime states defined.")
        unpatched = [device.name for device in project.devices if not device.node_assignment]
        if unpatched:
            warnings.append(f"Devices without node assignment: {', '.join(unpatched)}")
        if project.metadata.project_type == "Escape Room" and not project.puzzle_definitions:
            warnings.append("Escape Room project has no puzzle definitions.")
        if project.metadata.project_type == "Museum / Exhibit" and not project.exhibit_interactions:
            warnings.append("Museum / Exhibit project has no exhibit interactions.")
        return warnings
