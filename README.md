# IMMERSE Haunted Designer

IMMERSE Haunted Designer is a PySide6 desktop MVP for programming haunted attractions in the IMMERSE Show Systems ecosystem.

## Features

- Dark, production-minded desktop UI with sidebar navigation and inspector panels.
- Project-based haunted attraction editing for rooms, zones, devices, nodes, cues, trigger rules, scares, runtime states, and media assets.
- Basic map/layout editor with draggable room blocks.
- Timeline editor with tracks and event blocks.
- Save/load haunted attraction projects as JSON.
- Export structured deployment packages for the IMMERSE runtime stack.
- Includes a sample project: **RAVEN HOLLOW HAUNT**.

## Requirements

- Python 3.11+
- PySide6

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run

```bash
python -m app.main
```

## Project Structure

- `app/` – application bootstrap and main window.
- `models/` – data models and serialization.
- `services/` – project persistence, export builder, and mock runtime services.
- `widgets/` – reusable UI widgets such as editors, inspectors, tables, and navigation.
- `pages/` – primary product modules.
- `themes/` – dark stylesheet.
- `assets/sample_projects/` – bundled sample haunted attraction project.

## Export Output

The Deployment page exports a folder containing:

- `project.json`
- `manifest.json`
- `media/`
- `timelines/`
- `reports/validation.json`

## Notes

This MVP is structured to scale into a fuller commercial show-control environment. Hardware connectivity is represented by placeholders and mock services, while project modeling, editing, patching, sequencing, and package export are fully wired for extension.
