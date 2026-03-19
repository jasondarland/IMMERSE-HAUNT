# IMMERSE Designer

IMMERSE Designer is the unified flagship desktop authoring environment for the IMMERSE ecosystem.

It generalizes the earlier haunt-only tool into a single modular platform for programming and deploying:

- haunted houses
- escape rooms
- immersive walkthrough events
- museums and exhibits
- themed attractions, preshows, queues, and interactive environments

## MVP Highlights

- Unified `ExperienceProject` JSON model for layout, devices, nodes, cues, timelines, trigger logic, media, runtime states, and deployment data.
- Template-aware project creation for **Haunted House**, **Escape Room**, **Immersive Event**, **Museum / Exhibit**, **General Attraction**, and **Custom Experience**.
- Optional specialty module framework for haunt, escape, events, and museum workflows.
- Professional dark UI shell built with PySide6, including:
  - Dashboard
  - Project Setup
  - Layout / Map Designer
  - Devices / Patch
  - Nodes / Hardware
  - Cue Builder
  - Timeline / Sequence Editor
  - Trigger Logic
  - States / Modes
  - Media Library
  - Safety / Operations
  - Deployment / Export
- Drag-block layout editor and inspector-based data editing.
- Save/load project files as JSON.
- Structured folder or zip export packages.
- Backward migration support for older IMMERSE Haunted Designer JSON files.

## Sample Projects

The repository includes four sample projects demonstrating the unified architecture:

- `RAVEN HOLLOW HAUNT` – haunted house sample with scare logic and actor support
- `LOCKDOWN CELLBLOCK 13` – escape room sample with puzzle state definitions and hint logic
- `THE VEIL: IMMERSIVE EXPERIENCE` – event sample with scene sequencing and timed transitions
- `DISCOVER EARTH EXHIBIT` – museum sample with attract loops and occupancy-driven triggers

Saved JSON examples are written into `samples/`.

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

- `app/` – application bootstrap and main window shell
- `models/` – unified project model plus templates
- `services/` – persistence, export, migration, and mock runtime services
- `pages/` – major workflow pages
- `widgets/` – reusable editors and inspector widgets
- `timeline/` – timeline canvas widgets
- `map_editor/` – layout map graphics scene
- `samples/` – sample project JSON files
- `themes/` – dark premium IMMERSE stylesheet

## Export Output

Exports create a deployment package containing:

- `project.json`
- `manifest.json`
- `media/`
- `timelines/`
- `modules/`
- `reports/validation.json`

Folder and zip export are both supported in the MVP.

## Migration Note

When loading a legacy IMMERSE Haunted Designer file, the project service will automatically migrate it into the unified IMMERSE Designer schema when possible.
