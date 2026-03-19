from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QLabel, QMessageBox, QPushButton, QPlainTextEdit, QVBoxLayout, QWidget

from models.project import HauntedProject
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
        export_btn = QPushButton("Export Deployment Package")
        export_btn.clicked.connect(self.export_package)
        layout.addWidget(title)
        layout.addWidget(self.summary)
        layout.addWidget(export_btn)
        layout.addWidget(self.log)

    def refresh(self, project: HauntedProject) -> None:
        self.summary.setText(
            f"Target Runtime: {project.deployment.target_runtime}  •  Package: {project.deployment.package_name}  •  Export Version: {project.deployment.export_version}"
        )
        self.log.setPlainText("Ready to build structured deployment package for IMMERSE Runtime.")

    def export_package(self) -> None:
        project = self.project_getter()
        target = QFileDialog.getExistingDirectory(self, "Select Export Directory", str(Path.cwd()))
        if not target:
            return
        package_dir = self.export_service.export_project(project, target)
        self.log.setPlainText(f"Exported package to:\n{package_dir}")
        QMessageBox.information(self, "Export Complete", f"Deployment package created at:\n{package_dir}")
