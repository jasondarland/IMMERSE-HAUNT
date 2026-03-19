from __future__ import annotations

from models.project import ExperienceProject
from models.templates import build_sample_projects


def build_sample_project() -> ExperienceProject:
    return build_sample_projects()["RAVEN HOLLOW HAUNT"]
