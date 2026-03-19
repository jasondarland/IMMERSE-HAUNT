from models.project import (
    AmbientLayer,
    Cue,
    DeploymentManifest,
    Device,
    HauntedProject,
    MediaAsset,
    Node,
    ProjectInfo,
    Room,
    RuntimeState,
    ScareEvent,
    Timeline,
    TimelineEvent,
    TimelineTrack,
    TriggerRule,
    Zone,
)


def build_sample_project() -> HauntedProject:
    rooms = [
        Room(name="Raven Gate Queue", type="Queue", theme="Victorian cemetery", x=40, y=50, width=220, height=100),
        Room(name="Whisper Hallway", type="Hallway", theme="Cracked plaster and whisper vents", x=310, y=45, width=260, height=90),
        Room(name="Seance Chamber", type="Scene Room", theme="Occult parlor", x=620, y=40, width=220, height=140),
        Room(name="Finale Crypt", type="Finale Room", theme="Collapsed crypt with projection tomb", x=620, y=230, width=260, height=150),
    ]

    zones = [
        Zone(name="Whisper Midpoint", room_id=rooms[1].id, type="Scare Zone", description="Mid-hall fog and whisper sting"),
        Zone(name="Seance Circle", room_id=rooms[2].id, type="Actor Zone", description="Actor-assisted blackout hit"),
        Zone(name="Crypt Launch", room_id=rooms[3].id, type="Finale Zone", description="Synchronized finale trigger"),
    ]

    nodes = [
        Node(name="Queue Audio Node", hostname="10.10.0.20", room_zone_assignment=rooms[0].name, type="IMMERSE Audio Node", online=True),
        Node(name="Hallway FX Node", hostname="10.10.0.31", room_zone_assignment=rooms[1].name, type="IMMERSE FX Node", online=True),
        Node(name="Finale Lighting Node", hostname="10.10.0.40", room_zone_assignment=rooms[3].name, type="IMMERSE Lighting Node", online=False),
    ]

    devices = [
        Device(name="Hallway Whisper Speakers", type="Audio Output", node_assignment=nodes[0].id, protocol="Dante", address="A1", room_zone_assignment=rooms[1].id),
        Device(name="Red Chase Fixtures", type="Lighting Fixture", node_assignment=nodes[2].id, protocol="DMX", address="Universe 2 / 001", room_zone_assignment=rooms[1].id),
        Device(name="Crypt Fog Burst", type="Fog Machine", node_assignment=nodes[1].id, protocol="Relay", address="R3", room_zone_assignment=rooms[3].id),
        Device(name="Actor GO Beacon", type="Actor Cue Indicator", node_assignment=nodes[1].id, protocol="GPIO", address="O5", room_zone_assignment=rooms[2].id),
        Device(name="Emergency Worklights", type="Worklights", node_assignment=nodes[2].id, protocol="Relay", address="R7", room_zone_assignment=rooms[3].id),
    ]

    cues = [
        Cue(name="Hall Whisper Sting", type="Audio Cue", target_devices=[devices[0].id], hold_duration=4.0, color="#4cc9f0"),
        Cue(name="Hall Red Chase", type="Lighting Cue", target_devices=[devices[1].id], hold_duration=8.0, color="#f8961e"),
        Cue(name="Fog Burst", type="Fog/Effect Cue", target_devices=[devices[2].id], hold_duration=1.5, cooldown_time=20.0, color="#f3722c"),
        Cue(name="Actor GO", type="Actor Cue", target_devices=[devices[3].id], hold_duration=2.0, color="#90be6d"),
        Cue(name="Emergency Worklights", type="Worklight Cue", target_devices=[devices[4].id], hold_duration=0.0, blocking=True, color="#f94144"),
    ]

    finale_timeline = Timeline(
        name="Finale Sequence",
        description="Entry-triggered synchronized crypt finale",
        duration=18.0,
        tracks=[
            TimelineTrack(name="Audio", type="Audio", events=[TimelineEvent(name="Whisper Sting", cue_id=cues[0].id, start=0.5, duration=4.0, color="#4cc9f0")]),
            TimelineTrack(name="Lighting", type="Lighting", events=[TimelineEvent(name="Red Chase", cue_id=cues[1].id, start=0.0, duration=8.0, color="#f8961e")]),
            TimelineTrack(name="FX", type="Fog", events=[TimelineEvent(name="Fog Hit", cue_id=cues[2].id, start=6.0, duration=1.5, color="#f3722c")]),
            TimelineTrack(name="Actor", type="Actor Cue", events=[TimelineEvent(name="GO Cue", cue_id=cues[3].id, start=5.0, duration=2.0, color="#90be6d")]),
        ],
    )

    trigger_rules = [
        TriggerRule(name="Hallway Beam Break", trigger_source="Beam Break", condition="Group enters Whisper Hallway", target_action="Start Cue", target_ref=cues[0].id, lockout_timer=20.0),
        TriggerRule(name="Finale Entry", trigger_source="Room Entry", condition="Group enters Finale Crypt", target_action="Start Timeline", target_ref=finale_timeline.id, lockout_timer=45.0),
        TriggerRule(name="Emergency Stop", trigger_source="E-Stop", condition="Any E-Stop Active", target_action="Enter Runtime State", target_ref="Emergency Stop", repeat_mode="Repeat"),
    ]

    scares = [
        ScareEvent(name="Whisper Midpoint Hit", scare_type="Environmental Scare", zone_room=zones[0].id, trigger_source="Beam Break 2", cue_stack=[cues[0].id, cues[1].id, cues[2].id], strike_cue=cues[2].id, cooldown_timer=20.0),
        ScareEvent(name="Seance Blackout Pop", scare_type="Actor-Assisted Scare", zone_room=zones[1].id, trigger_source="Actor Button", cue_stack=[cues[3].id], actor_participation=True, trigger_mode="Assisted", safety_notes="Actor clear zone before blackout"),
    ]

    ambient = [
        AmbientLayer(room_id=rooms[1].id, name="Whisper Loop", asset_ref="whispers_loop.wav", min_interval=5.0, max_interval=15.0, probability=0.8),
        AmbientLayer(room_id=rooms[3].id, name="Crypt Wind", asset_ref="crypt_wind.wav", min_interval=8.0, max_interval=18.0, probability=0.65),
    ]

    media = [
        MediaAsset(name="whispers_loop.wav", asset_type="Audio", path="media/whispers_loop.wav", label="Whisper Hall Bed"),
        MediaAsset(name="crypt_wind.wav", asset_type="Audio", path="media/crypt_wind.wav", label="Finale Wind Loop"),
        MediaAsset(name="crypt_projection.mov", asset_type="Video", path="media/crypt_projection.mov", label="Finale Projection"),
    ]

    states = [
        RuntimeState(name="Startup", scare_enabled=False, actor_cue_available=False, lighting_mode="Worklight"),
        RuntimeState(name="Active Show", scare_enabled=True, actor_cue_available=True, lighting_mode="Armed", transitions=["Hold", "Reset", "Emergency Stop"]),
        RuntimeState(name="Hold", scare_enabled=False, actor_cue_available=True, lighting_mode="Safe Blue", transitions=["Active Show", "Emergency Stop"]),
        RuntimeState(name="Emergency Stop", scare_enabled=False, actor_cue_available=False, lighting_mode="Worklight", audio_mode="Paging", notes="Disable scares, enable worklights, hold actors"),
    ]

    return HauntedProject(
        info=ProjectInfo(
            attraction_name="RAVEN HOLLOW HAUNT",
            show_id="RVN-HLH-001",
            version="1.0.0",
            operator_notes="Nightly reset after each group. Actor briefing at 18:30.",
            project_notes="Demonstrates ambient systems, hallway scare logic, finale sequence, and emergency handling.",
            estimated_walkthrough_minutes=14,
        ),
        rooms=rooms,
        zones=zones,
        nodes=nodes,
        devices=devices,
        cues=cues,
        timelines=[finale_timeline],
        trigger_rules=trigger_rules,
        scares=scares,
        ambient_layers=ambient,
        runtime_states=states,
        media_assets=media,
        deployment=DeploymentManifest(package_name="raven_hollow_haunt"),
    )
