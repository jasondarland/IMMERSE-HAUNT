from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import uuid


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ProjectMetadata:
    project_name: str = "Untitled Experience"
    show_id: str = "IMD-001"
    version: str = "0.2.0"
    client_site: str = ""
    project_type: str = "General Attraction"
    operating_mode: str = "Programmed Experience"
    experience_duration_minutes: int = 15
    reset_behavior: str = "Manual or automatic reset"
    safety_defaults: str = "Safe outputs on fault, worklights available, emergency hold supported"
    notes: str = ""
    deployment_target: str = "IMMERSE Runtime"
    last_modified: str = field(default_factory=utc_now)
    enabled_modules: list[str] = field(default_factory=list)


@dataclass
class LayoutItem:
    id: str = field(default_factory=lambda: new_id("layout"))
    name: str = "New Layout Item"
    item_type: str = "Room"
    description: str = ""
    tags: list[str] = field(default_factory=list)
    default_state: str = "Default"
    linked_devices: list[str] = field(default_factory=list)
    linked_cues: list[str] = field(default_factory=list)
    notes: str = ""
    x: float = 40.0
    y: float = 40.0
    width: float = 220.0
    height: float = 120.0


@dataclass
class Device:
    id: str = field(default_factory=lambda: new_id("dev"))
    name: str = "New Device"
    device_type: str = "Lighting Fixture"
    category: str = "Lighting"
    node_assignment: str = ""
    protocol: str = "DMX"
    address: str = "1"
    location_assignment: str = ""
    tags: list[str] = field(default_factory=list)
    notes: str = ""
    enabled: bool = True


@dataclass
class Node:
    id: str = field(default_factory=lambda: new_id("node"))
    name: str = "New Node"
    hostname: str = "192.168.1.10"
    node_type: str = "IMMERSE GPIO Node"
    location_assignment: str = ""
    notes: str = ""
    online: bool = False
    io_summary: str = "8 in / 8 out"
    health_status: str = "Placeholder"


@dataclass
class Cue:
    id: str = field(default_factory=lambda: new_id("cue"))
    name: str = "New Cue"
    cue_type: str = "Audio Cue"
    description: str = ""
    targets: list[str] = field(default_factory=list)
    pre_delay: float = 0.0
    fade_time: float = 0.0
    hold_duration: float = 1.0
    follow_action: str = "None"
    retrigger_rules: str = "Respect cooldown"
    cooldown_time: float = 0.0
    priority: int = 50
    blocking: bool = False
    tags: list[str] = field(default_factory=list)
    notes: str = ""
    color: str = "#4cc9f0"


@dataclass
class TimelineEvent:
    id: str = field(default_factory=lambda: new_id("evt"))
    name: str = "Event"
    cue_id: str = ""
    start: float = 0.0
    duration: float = 1.0
    color: str = "#f8961e"
    marker_label: str = ""


@dataclass
class TimelineTrack:
    id: str = field(default_factory=lambda: new_id("track"))
    name: str = "Track"
    track_type: str = "Utility"
    events: list[TimelineEvent] = field(default_factory=list)


@dataclass
class Timeline:
    id: str = field(default_factory=lambda: new_id("timeline"))
    name: str = "Main Sequence"
    description: str = ""
    loop: bool = False
    duration: float = 30.0
    snap: float = 0.5
    markers: list[str] = field(default_factory=list)
    tracks: list[TimelineTrack] = field(default_factory=list)


@dataclass
class TriggerRule:
    id: str = field(default_factory=lambda: new_id("trig"))
    name: str = "New Trigger Rule"
    source: str = "Sensor"
    condition: str = "On Active"
    action: str = "Fire Cue"
    target_ref: str = ""
    delay: float = 0.0
    repeat_mode: str = "One Shot"
    armed: bool = True
    debounce: float = 0.2
    lockout_timer: float = 0.0
    dependency_conditions: list[str] = field(default_factory=list)
    fallback_action: str = ""


@dataclass
class RuntimeState:
    id: str = field(default_factory=lambda: new_id("state"))
    name: str = "Active Show"
    enabled_triggers: list[str] = field(default_factory=list)
    disabled_triggers: list[str] = field(default_factory=list)
    audio_mode: str = "Show"
    lighting_mode: str = "Programmed"
    cue_availability: str = "All"
    device_behavior: str = "Normal"
    transition_rules: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class MediaAsset:
    id: str = field(default_factory=lambda: new_id("media"))
    name: str = "Asset"
    asset_type: str = "Audio"
    path: str = ""
    label: str = ""
    metadata: str = ""
    notes: str = ""


@dataclass
class DeploymentManifest:
    target_runtime: str = "IMMERSE Runtime"
    export_version: str = "2.0"
    package_name: str = "untitled_package"
    generated_at: str = field(default_factory=utc_now)
    validation_warnings: list[str] = field(default_factory=list)
    supported_formats: list[str] = field(default_factory=lambda: ["folder", "zip", "future .immersepack"])


@dataclass
class ModuleConfig:
    name: str
    enabled: bool = True
    description: str = ""


@dataclass
class ScareEvent:
    id: str = field(default_factory=lambda: new_id("scare"))
    name: str = "New Scare"
    scare_type: str = "Audio Sting"
    location_ref: str = ""
    trigger_source: str = ""
    cue_stack: list[str] = field(default_factory=list)
    cooldown_timer: float = 20.0
    actor_assignment: str = ""
    intensity_rating: int = 5
    safety_notes: str = ""


@dataclass
class PuzzleDefinition:
    id: str = field(default_factory=lambda: new_id("puzzle"))
    name: str = "New Puzzle"
    state: str = "Idle"
    success_condition: str = ""
    fail_condition: str = ""
    hint_behavior: str = "Manual hint"
    reset_rule: str = "Manual reset"
    dependencies: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class ActorStation:
    id: str = field(default_factory=lambda: new_id("actor"))
    name: str = "Actor / Operator Station"
    location_ref: str = ""
    cue_device: str = ""
    trigger_binding: str = ""
    notes: str = ""


@dataclass
class ExhibitInteraction:
    id: str = field(default_factory=lambda: new_id("exhibit"))
    name: str = "New Exhibit Interaction"
    exhibit_area: str = ""
    trigger_source: str = ""
    media_action: str = ""
    occupancy_behavior: str = "Idle attract"
    notes: str = ""


@dataclass
class EventSequence:
    id: str = field(default_factory=lambda: new_id("event"))
    name: str = "New Event Sequence"
    scene_order: list[str] = field(default_factory=list)
    coordination_notes: str = ""
    staff_cues: list[str] = field(default_factory=list)


@dataclass
class ExperienceProject:
    schema_version: str = "2.0"
    metadata: ProjectMetadata = field(default_factory=ProjectMetadata)
    layout_items: list[LayoutItem] = field(default_factory=list)
    devices: list[Device] = field(default_factory=list)
    nodes: list[Node] = field(default_factory=list)
    cues: list[Cue] = field(default_factory=list)
    timelines: list[Timeline] = field(default_factory=list)
    trigger_rules: list[TriggerRule] = field(default_factory=list)
    runtime_states: list[RuntimeState] = field(default_factory=list)
    media_assets: list[MediaAsset] = field(default_factory=list)
    deployment: DeploymentManifest = field(default_factory=DeploymentManifest)
    modules: list[ModuleConfig] = field(default_factory=list)
    scare_events: list[ScareEvent] = field(default_factory=list)
    puzzle_definitions: list[PuzzleDefinition] = field(default_factory=list)
    actor_stations: list[ActorStation] = field(default_factory=list)
    exhibit_interactions: list[ExhibitInteraction] = field(default_factory=list)
    event_sequences: list[EventSequence] = field(default_factory=list)

    def touch(self) -> None:
        self.metadata.last_modified = utc_now()

    def to_dict(self) -> dict[str, Any]:
        self.touch()
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ExperienceProject":
        def build(dc, source: dict[str, Any]) -> Any:
            return dc(**source)

        timelines: list[Timeline] = []
        for timeline_payload in payload.get("timelines", []):
            tracks = []
            for track_payload in timeline_payload.get("tracks", []):
                events = [build(TimelineEvent, event_payload) for event_payload in track_payload.get("events", [])]
                tracks.append(TimelineTrack(events=events, **{k: v for k, v in track_payload.items() if k != "events"}))
            timelines.append(Timeline(tracks=tracks, **{k: v for k, v in timeline_payload.items() if k != "tracks"}))

        metadata_payload = payload.get("metadata") or payload.get("info") or {}
        return cls(
            schema_version=payload.get("schema_version", "2.0"),
            metadata=build(ProjectMetadata, metadata_payload),
            layout_items=[build(LayoutItem, item) for item in payload.get("layout_items", payload.get("rooms", []))],
            devices=[build(Device, item) for item in payload.get("devices", [])],
            nodes=[build(Node, item) for item in payload.get("nodes", [])],
            cues=[build(Cue, item) for item in payload.get("cues", [])],
            timelines=timelines,
            trigger_rules=[build(TriggerRule, item) for item in payload.get("trigger_rules", [])],
            runtime_states=[build(RuntimeState, item) for item in payload.get("runtime_states", [])],
            media_assets=[build(MediaAsset, item) for item in payload.get("media_assets", [])],
            deployment=build(DeploymentManifest, payload.get("deployment", {})),
            modules=[build(ModuleConfig, item) for item in payload.get("modules", [])],
            scare_events=[build(ScareEvent, item) for item in payload.get("scare_events", payload.get("scares", []))],
            puzzle_definitions=[build(PuzzleDefinition, item) for item in payload.get("puzzle_definitions", [])],
            actor_stations=[build(ActorStation, item) for item in payload.get("actor_stations", [])],
            exhibit_interactions=[build(ExhibitInteraction, item) for item in payload.get("exhibit_interactions", [])],
            event_sequences=[build(EventSequence, item) for item in payload.get("event_sequences", [])],
        )

    def save_json(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load_json(cls, path: str | Path) -> "ExperienceProject":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
