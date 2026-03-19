from __future__ import annotations

from models.project import (
    ActorStation,
    Cue,
    DeploymentManifest,
    Device,
    EventSequence,
    ExperienceProject,
    ExhibitInteraction,
    LayoutItem,
    MediaAsset,
    ModuleConfig,
    Node,
    ProjectMetadata,
    PuzzleDefinition,
    RuntimeState,
    ScareEvent,
    Timeline,
    TimelineEvent,
    TimelineTrack,
    TriggerRule,
)


PROJECT_TEMPLATES: dict[str, dict[str, object]] = {
    "Haunted House": {
        "modules": ["Haunt Module"],
        "operating_mode": "Continuous walk-through",
        "defaults": ["Active Show", "Reset", "Worklight", "Emergency Stop"],
    },
    "Escape Room": {
        "modules": ["Escape Module"],
        "operating_mode": "Session-based gameplay",
        "defaults": ["Startup", "Gameplay", "Hint Mode", "Reset"],
    },
    "Immersive Event": {
        "modules": ["Events Module"],
        "operating_mode": "Timed scenes",
        "defaults": ["Pre-Show", "Active Show", "Hold", "Shutdown"],
    },
    "Museum / Exhibit": {
        "modules": ["Museum Module"],
        "operating_mode": "Open/close daily cycle",
        "defaults": ["Attract", "Open", "Maintenance", "Closed"],
    },
    "General Attraction": {
        "modules": [],
        "operating_mode": "Programmed experience",
        "defaults": ["Startup", "Active Show", "Maintenance", "Shutdown"],
    },
    "Custom Experience": {
        "modules": [],
        "operating_mode": "Custom",
        "defaults": ["Startup", "Active Show"],
    },
}


def create_project_from_template(project_type: str, project_name: str = "Untitled Experience") -> ExperienceProject:
    template = PROJECT_TEMPLATES.get(project_type, PROJECT_TEMPLATES["General Attraction"])
    states = [RuntimeState(name=name) for name in template["defaults"]]
    modules = [ModuleConfig(name=name, description=f"Optional tools for {project_type.lower()} workflows") for name in template["modules"]]
    metadata = ProjectMetadata(project_name=project_name, project_type=project_type, operating_mode=str(template["operating_mode"]), enabled_modules=[m.name for m in modules])
    return ExperienceProject(metadata=metadata, runtime_states=states, modules=modules, deployment=DeploymentManifest(package_name=project_name.lower().replace(' ', '_')))


def build_sample_projects() -> dict[str, ExperienceProject]:
    return {
        "RAVEN HOLLOW HAUNT": _haunt_sample(),
        "LOCKDOWN CELLBLOCK 13": _escape_sample(),
        "THE VEIL: IMMERSIVE EXPERIENCE": _event_sample(),
        "DISCOVER EARTH EXHIBIT": _museum_sample(),
    }


def _haunt_sample() -> ExperienceProject:
    project = create_project_from_template("Haunted House", "RAVEN HOLLOW HAUNT")
    project.metadata.client_site = "Raven Hollow Park"
    project.metadata.notes = "Haunted attraction sample with scare events, actor support, and emergency operations."
    project.layout_items = [
        LayoutItem(name="Queue Gate", item_type="Queue Area", x=40, y=50, width=210, height=90),
        LayoutItem(name="Whisper Hallway", item_type="Hallway", x=280, y=50, width=280, height=90),
        LayoutItem(name="Seance Chamber", item_type="Scene", x=600, y=40, width=230, height=140),
        LayoutItem(name="Finale Crypt", item_type="Room", x=600, y=230, width=250, height=140),
    ]
    project.nodes = [
        Node(name="Hall FX Node", hostname="10.20.0.11", node_type="IMMERSE FX Node", location_assignment=project.layout_items[1].id, online=True),
        Node(name="Finale Lighting Node", hostname="10.20.0.21", node_type="IMMERSE Lighting Node", location_assignment=project.layout_items[3].id),
    ]
    project.devices = [
        Device(name="Whisper Speakers", device_type="Audio Output", category="Audio", node_assignment=project.nodes[0].id, protocol="Dante", address="A1", location_assignment=project.layout_items[1].id),
        Device(name="Crypt Fog Burst", device_type="Fog Machine", category="FX", node_assignment=project.nodes[0].id, protocol="Relay", address="R3", location_assignment=project.layout_items[3].id),
        Device(name="Actor Cue Beacon", device_type="Cue Light", category="Operator", node_assignment=project.nodes[0].id, protocol="GPIO", address="O5", location_assignment=project.layout_items[2].id),
    ]
    project.cues = [
        Cue(name="Whisper Sting", cue_type="Audio Cue", targets=[project.devices[0].id], hold_duration=4.0, color="#4cc9f0"),
        Cue(name="Fog Burst", cue_type="Effect Cue", targets=[project.devices[1].id], hold_duration=1.5, cooldown_time=20, color="#f3722c"),
        Cue(name="Actor GO", cue_type="Actor Cue", targets=[project.devices[2].id], hold_duration=2.0, color="#90be6d"),
    ]
    project.timelines = [
        Timeline(
            name="Finale Sequence",
            description="Room-entry finale sting",
            duration=18.0,
            markers=["Entry", "Hit", "Reset"],
            tracks=[
                TimelineTrack(name="Audio", track_type="Audio", events=[TimelineEvent(name="Whisper Sting", cue_id=project.cues[0].id, start=0.5, duration=4.0, color="#4cc9f0")]),
                TimelineTrack(name="FX", track_type="FX", events=[TimelineEvent(name="Fog Burst", cue_id=project.cues[1].id, start=6.0, duration=1.5, color="#f3722c")]),
            ],
        )
    ]
    project.trigger_rules = [
        TriggerRule(name="Hall Beam", source="Beam Break", condition="Guests enter hallway", action="Fire Cue", target_ref=project.cues[0].id, lockout_timer=20.0),
        TriggerRule(name="Finale Entry", source="Room Entry", condition="Guests enter crypt", action="Start Timeline", target_ref=project.timelines[0].id, lockout_timer=45.0),
    ]
    project.scare_events = [
        ScareEvent(name="Whisper Midpoint Hit", scare_type="Environmental Scare", location_ref=project.layout_items[1].id, trigger_source="Beam Break", cue_stack=[cue.id for cue in project.cues], actor_assignment="Seance Actor", safety_notes="Observe cooldown before re-arm."),
    ]
    project.actor_stations = [ActorStation(name="Seance Actor Station", location_ref=project.layout_items[2].id, cue_device=project.devices[2].id, trigger_binding="Manual GO")]
    project.media_assets = [MediaAsset(name="whisper_bed.wav", asset_type="Audio", path="media/whisper_bed.wav", label="Ambient whisper bed")]
    return project


def _escape_sample() -> ExperienceProject:
    project = create_project_from_template("Escape Room", "LOCKDOWN CELLBLOCK 13")
    project.metadata.client_site = "Cellblock Adventures"
    project.layout_items = [
        LayoutItem(name="Booking Area", item_type="Scene", x=40, y=60, width=220, height=110),
        LayoutItem(name="Cell Block", item_type="Room", x=300, y=60, width=260, height=130),
        LayoutItem(name="Control Booth", item_type="Operator Station", x=600, y=60, width=220, height=100),
    ]
    project.nodes = [Node(name="Game Master OCC", hostname="10.30.0.10", node_type="IMMERSE OCC Panel", location_assignment=project.layout_items[2].id, online=True)]
    project.devices = [
        Device(name="Door Maglock", device_type="Maglock", category="Access", node_assignment=project.nodes[0].id, protocol="Relay", address="R1", location_assignment=project.layout_items[1].id),
        Device(name="Hint Monitor", device_type="Video Display", category="Video", node_assignment=project.nodes[0].id, protocol="HDMI", address="Display 1", location_assignment=project.layout_items[0].id),
    ]
    project.cues = [
        Cue(name="Puzzle Solved", cue_type="Puzzle Cue", targets=[project.devices[0].id], hold_duration=0.0, color="#90be6d"),
        Cue(name="Hint Playback", cue_type="Video Cue", targets=[project.devices[1].id], hold_duration=10.0, color="#4cc9f0"),
    ]
    project.puzzle_definitions = [
        PuzzleDefinition(name="Keypad Override", state="Armed", success_condition="Correct code entered", hint_behavior="Auto hint after 5 minutes", reset_rule="Reset keypad and relock door"),
        PuzzleDefinition(name="Evidence Board", state="Idle", success_condition="All evidence tiles placed", dependencies=["Keypad Override"]),
    ]
    project.trigger_rules = [
        TriggerRule(name="Code Success", source="Keypad", condition="Valid code", action="Fire Cue", target_ref=project.cues[0].id),
        TriggerRule(name="Hint Request", source="GM Button", condition="Hint pressed", action="Fire Cue", target_ref=project.cues[1].id),
    ]
    project.timelines = [Timeline(name="Finale Escape", duration=20.0, tracks=[TimelineTrack(name="Reveal", track_type="Video")])]
    project.media_assets = [MediaAsset(name="intro_brief.mp4", asset_type="Video", path="media/intro_brief.mp4", label="Intro briefing")]
    return project


def _event_sample() -> ExperienceProject:
    project = create_project_from_template("Immersive Event", "THE VEIL: IMMERSIVE EXPERIENCE")
    project.layout_items = [
        LayoutItem(name="Arrival Lounge", item_type="Queue Area", x=40, y=50, width=240, height=110),
        LayoutItem(name="Transition Corridor", item_type="Hallway", x=320, y=50, width=220, height=90),
        LayoutItem(name="Main Ritual Chamber", item_type="Scene", x=580, y=40, width=280, height=160),
    ]
    project.nodes = [Node(name="Scene Runtime Host", hostname="10.40.0.5", node_type="Central Runtime Host", location_assignment=project.layout_items[2].id, online=True)]
    project.devices = [
        Device(name="Ritual Projection", device_type="Projector", category="Video", node_assignment=project.nodes[0].id, protocol="Network", address="Proj-01", location_assignment=project.layout_items[2].id),
        Device(name="Staff Cue Panel", device_type="Status Indicator", category="Operator", node_assignment=project.nodes[0].id, protocol="GPIO", address="O2", location_assignment=project.layout_items[1].id),
    ]
    project.cues = [
        Cue(name="Scene Transition", cue_type="Global Cue", targets=[project.devices[0].id], hold_duration=12.0, color="#4cc9f0"),
        Cue(name="Staff Ready", cue_type="Actor Cue", targets=[project.devices[1].id], hold_duration=3.0, color="#90be6d"),
    ]
    project.event_sequences = [EventSequence(name="Opening Processional", scene_order=[item.id for item in project.layout_items], staff_cues=[project.cues[1].id], coordination_notes="Scene manager advances guests every 3 minutes.")]
    project.timelines = [Timeline(name="Opening Sequence", duration=24.0, tracks=[TimelineTrack(name="Video", track_type="Video", events=[TimelineEvent(name="Scene Transition", cue_id=project.cues[0].id, start=0.0, duration=12.0, color="#4cc9f0")])])]
    project.trigger_rules = [TriggerRule(name="Advance Guests", source="Timer", condition="Every 180 seconds", action="Start Sequence", target_ref=project.event_sequences[0].id)]
    return project


def _museum_sample() -> ExperienceProject:
    project = create_project_from_template("Museum / Exhibit", "DISCOVER EARTH EXHIBIT")
    project.layout_items = [
        LayoutItem(name="Entry Kiosk", item_type="Exhibit Area", x=40, y=60, width=220, height=120),
        LayoutItem(name="Volcano Interactive", item_type="Exhibit Area", x=300, y=60, width=240, height=120),
        LayoutItem(name="Planet Wall", item_type="Exhibit Area", x=580, y=60, width=260, height=120),
    ]
    project.nodes = [Node(name="Exhibit Media Node", hostname="10.50.0.15", node_type="IMMERSE Video Node", location_assignment=project.layout_items[0].id, online=True)]
    project.devices = [
        Device(name="Welcome Screen", device_type="Kiosk Interface", category="Interactive", node_assignment=project.nodes[0].id, protocol="HTML5", address="kiosk-1", location_assignment=project.layout_items[0].id),
        Device(name="Volcano Motion Sensor", device_type="PIR Sensor", category="Sensors", node_assignment=project.nodes[0].id, protocol="GPIO", address="I4", location_assignment=project.layout_items[1].id),
    ]
    project.cues = [
        Cue(name="Attract Loop", cue_type="Exhibit Cue", targets=[project.devices[0].id], hold_duration=30.0, color="#4cc9f0"),
        Cue(name="Volcano Trigger", cue_type="Video Cue", targets=[project.devices[0].id], hold_duration=20.0, color="#f8961e"),
    ]
    project.exhibit_interactions = [
        ExhibitInteraction(name="Volcano Activation", exhibit_area=project.layout_items[1].id, trigger_source=project.devices[1].id, media_action=project.cues[1].id, occupancy_behavior="Fire only when occupied", notes="Returns to attract loop after 20 seconds."),
    ]
    project.trigger_rules = [
        TriggerRule(name="Idle Attract", source="Timer", condition="No occupancy for 45 seconds", action="Fire Cue", target_ref=project.cues[0].id),
        TriggerRule(name="Occupancy Activation", source="PIR", condition="Motion detected", action="Fire Cue", target_ref=project.cues[1].id),
    ]
    project.media_assets = [MediaAsset(name="earth_overview.mp4", asset_type="Video", path="media/earth_overview.mp4", label="Earth overview loop")]
    return project
