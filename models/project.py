from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import uuid


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ProjectInfo:
    attraction_name: str = "Untitled Attraction"
    show_id: str = "IMH-001"
    version: str = "0.1.0"
    operator_notes: str = ""
    attraction_type: str = "Walkthrough Haunted House"
    run_mode: str = "Continuous Flow"
    throughput_mode: str = "Timed Group Entry"
    group_size: int = 6
    estimated_walkthrough_minutes: int = 12
    reset_behavior: str = "Auto reset after zone clear"
    emergency_defaults: str = "Disable scares, worklights on, hold actors"
    last_modified: str = field(default_factory=utc_now)
    project_notes: str = ""


@dataclass
class Room:
    id: str = field(default_factory=lambda: _new_id("room"))
    name: str = "New Room"
    type: str = "Room"
    description: str = ""
    theme: str = ""
    default_ambient_state: str = "Ambient"
    entry_trigger: str = ""
    exit_trigger: str = ""
    panic_state: str = "Panic"
    maintenance_state: str = "Worklight"
    linked_devices: list[str] = field(default_factory=list)
    linked_cues: list[str] = field(default_factory=list)
    actor_notes: str = ""
    x: float = 40.0
    y: float = 40.0
    width: float = 220.0
    height: float = 120.0


@dataclass
class Zone:
    id: str = field(default_factory=lambda: _new_id("zone"))
    name: str = "New Zone"
    room_id: str = ""
    type: str = "Scare Zone"
    description: str = ""
    theme: str = ""
    ambient_state: str = "Ambient"
    notes: str = ""


@dataclass
class Device:
    id: str = field(default_factory=lambda: _new_id("dev"))
    name: str = "New Device"
    type: str = "Lighting Fixture"
    node_assignment: str = ""
    protocol: str = "DMX"
    address: str = "1"
    room_zone_assignment: str = ""
    tags: list[str] = field(default_factory=list)
    notes: str = ""
    enabled: bool = True


@dataclass
class Node:
    id: str = field(default_factory=lambda: _new_id("node"))
    name: str = "New Node"
    hostname: str = "192.168.1.10"
    room_zone_assignment: str = ""
    type: str = "IMMERSE GPIO Node"
    online: bool = False
    outputs: int = 8
    inputs: int = 8
    health_status: str = "Placeholder"
    notes: str = ""


@dataclass
class Cue:
    id: str = field(default_factory=lambda: _new_id("cue"))
    name: str = "New Cue"
    type: str = "Audio Cue"
    description: str = ""
    target_devices: list[str] = field(default_factory=list)
    pre_delay: float = 0.0
    fade_time: float = 0.0
    hold_duration: float = 1.0
    follow_action: str = "None"
    conditional_trigger: str = ""
    retrigger_rules: str = "Respect cooldown"
    cooldown_time: float = 5.0
    priority: int = 50
    blocking: bool = False
    tags: list[str] = field(default_factory=list)
    notes: str = ""
    color: str = "#4cc9f0"


@dataclass
class TimelineEvent:
    id: str = field(default_factory=lambda: _new_id("evt"))
    name: str = "Event"
    cue_id: str = ""
    start: float = 0.0
    duration: float = 1.0
    color: str = "#f8961e"


@dataclass
class TimelineTrack:
    id: str = field(default_factory=lambda: _new_id("track"))
    name: str = "Track"
    type: str = "Utility"
    events: list[TimelineEvent] = field(default_factory=list)


@dataclass
class Timeline:
    id: str = field(default_factory=lambda: _new_id("timeline"))
    name: str = "Main Sequence"
    description: str = ""
    loop: bool = False
    duration: float = 30.0
    tracks: list[TimelineTrack] = field(default_factory=list)


@dataclass
class TriggerRule:
    id: str = field(default_factory=lambda: _new_id("trig"))
    name: str = "New Trigger Rule"
    trigger_source: str = "Beam Break"
    condition: str = "On Trigger"
    target_action: str = "Fire Cue"
    target_ref: str = ""
    delay: float = 0.0
    repeat_mode: str = "One Shot"
    armed: bool = True
    debounce: float = 0.2
    lockout_timer: float = 10.0
    fallback_action: str = ""


@dataclass
class ScareEvent:
    id: str = field(default_factory=lambda: _new_id("scare"))
    name: str = "New Scare"
    scare_type: str = "Audio Sting"
    zone_room: str = ""
    trigger_source: str = ""
    cue_stack: list[str] = field(default_factory=list)
    pre_scare_ambient_state: str = "Ambient"
    strike_cue: str = ""
    post_scare_decay: float = 4.0
    cooldown_timer: float = 20.0
    reset_rules: str = "Auto re-arm when clear"
    actor_participation: bool = False
    trigger_mode: str = "Auto"
    intensity_rating: int = 5
    safety_notes: str = ""
    timing_notes: str = ""


@dataclass
class AmbientLayer:
    id: str = field(default_factory=lambda: _new_id("amb"))
    room_id: str = ""
    name: str = "Ambient Layer"
    asset_ref: str = ""
    min_interval: float = 3.0
    max_interval: float = 12.0
    probability: float = 0.6
    notes: str = ""


@dataclass
class RuntimeState:
    id: str = field(default_factory=lambda: _new_id("state"))
    name: str = "Open"
    active_devices: list[str] = field(default_factory=list)
    disabled_triggers: list[str] = field(default_factory=list)
    audio_mode: str = "Show"
    lighting_mode: str = "Armed"
    scare_enabled: bool = True
    actor_cue_available: bool = True
    transitions: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class ActorStation:
    id: str = field(default_factory=lambda: _new_id("actor"))
    name: str = "Actor Station"
    zone_room: str = ""
    cue_light_device: str = ""
    local_trigger: str = ""
    hold_indicator: str = ""
    reset_indicator: str = ""
    notes: str = ""


@dataclass
class MediaAsset:
    id: str = field(default_factory=lambda: _new_id("media"))
    name: str = "Asset"
    asset_type: str = "Audio"
    path: str = ""
    label: str = ""
    notes: str = ""


@dataclass
class DeploymentManifest:
    target_runtime: str = "IMMERSE Runtime"
    export_version: str = "1.0"
    package_name: str = "untitled_package"
    generated_at: str = field(default_factory=utc_now)
    validation_warnings: list[str] = field(default_factory=list)


@dataclass
class HauntedProject:
    info: ProjectInfo = field(default_factory=ProjectInfo)
    rooms: list[Room] = field(default_factory=list)
    zones: list[Zone] = field(default_factory=list)
    devices: list[Device] = field(default_factory=list)
    nodes: list[Node] = field(default_factory=list)
    cues: list[Cue] = field(default_factory=list)
    timelines: list[Timeline] = field(default_factory=list)
    trigger_rules: list[TriggerRule] = field(default_factory=list)
    scares: list[ScareEvent] = field(default_factory=list)
    ambient_layers: list[AmbientLayer] = field(default_factory=list)
    runtime_states: list[RuntimeState] = field(default_factory=list)
    actor_stations: list[ActorStation] = field(default_factory=list)
    media_assets: list[MediaAsset] = field(default_factory=list)
    deployment: DeploymentManifest = field(default_factory=DeploymentManifest)

    def touch(self) -> None:
        self.info.last_modified = utc_now()

    def to_dict(self) -> dict[str, Any]:
        self.touch()
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "HauntedProject":
        def build(dataclass_type, source):
            return dataclass_type(**source)

        info = build(ProjectInfo, payload.get("info", {}))
        deployment = build(DeploymentManifest, payload.get("deployment", {}))
        timelines = []
        for tl in payload.get("timelines", []):
            tracks = []
            for tr in tl.get("tracks", []):
                events = [build(TimelineEvent, evt) for evt in tr.get("events", [])]
                tracks.append(TimelineTrack(events=events, **{k: v for k, v in tr.items() if k != "events"}))
            timelines.append(Timeline(tracks=tracks, **{k: v for k, v in tl.items() if k != "tracks"}))
        return cls(
            info=info,
            rooms=[build(Room, item) for item in payload.get("rooms", [])],
            zones=[build(Zone, item) for item in payload.get("zones", [])],
            devices=[build(Device, item) for item in payload.get("devices", [])],
            nodes=[build(Node, item) for item in payload.get("nodes", [])],
            cues=[build(Cue, item) for item in payload.get("cues", [])],
            timelines=timelines,
            trigger_rules=[build(TriggerRule, item) for item in payload.get("trigger_rules", [])],
            scares=[build(ScareEvent, item) for item in payload.get("scares", [])],
            ambient_layers=[build(AmbientLayer, item) for item in payload.get("ambient_layers", [])],
            runtime_states=[build(RuntimeState, item) for item in payload.get("runtime_states", [])],
            actor_stations=[build(ActorStation, item) for item in payload.get("actor_stations", [])],
            media_assets=[build(MediaAsset, item) for item in payload.get("media_assets", [])],
            deployment=deployment,
        )

    def save_json(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load_json(cls, path: str | Path) -> "HauntedProject":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
