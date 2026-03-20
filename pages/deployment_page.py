from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QLabel, QMessageBox, QPushButton, QPlainTextEdit, QVBoxLayout, QWidget

from models.project import ExperienceProject
from services.export_service import ExportService


class DeploymentPage(QWidget):
    def __init__(self, project_getter):
        super().__init__()
        self.project_getter = project_getter
        self.export_service = ExportService()
        layout = QVBoxLayout(self)
        title = QLabel("Deployment / Export")
        title.setObjectName("titleLabel")
        self.summary = QLabel()
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        export_folder = QPushButton("Export Folder Package")
        export_zip = QPushButton("Export Zip Package")
        export_folder.clicked.connect(lambda: self.export_package(False))
        export_zip.clicked.connect(lambda: self.export_package(True))
        layout.addWidget(title)
        layout.addWidget(self.summary)
        layout.addWidget(export_folder)
        layout.addWidget(export_zip)
        layout.addWidget(self.log)

    def refresh(self, project: ExperienceProject) -> None:
        self.summary.setText(
            f"Runtime: {project.deployment.target_runtime}  •  Package: {project.deployment.package_name}  •  Formats: {', '.join(project.deployment.supported_formats)}"
        )
        self.log.setPlainText("Validate and export the current IMMERSE Designer project for deployment.")

    def export_package(self, as_zip: bool) -> None:
        project = self.project_getter()
        target = QFileDialog.getExistingDirectory(self, "Select Export Directory", str(Path.cwd()))
        if not target:
            return
        export_path = self.export_service.export_project(project, target, as_zip=as_zip)
        self.log.setPlainText(f"Exported package to:\n{export_path}")
        QMessageBox.information(self, "Export Complete", f"Deployment package created at:\n{export_path}")
