from __future__ import annotations

from typing import Any

from models.project import (
    Cue,
    DeploymentManifest,
    Device,
    ExperienceProject,
    LayoutItem,
    ModuleConfig,
    Node,
    ProjectMetadata,
    RuntimeState,
    ScareEvent,
    TriggerRule,
)


class MigrationService:
    """Converts the original haunt-only schema into the unified IMMERSE Designer project model."""

    def can_migrate(self, payload: dict[str, Any]) -> bool:
        return "info" in payload or "rooms" in payload or "scares" in payload

    def migrate_haunt_project(self, payload: dict[str, Any]) -> ExperienceProject:
        info = payload.get("info", {})
        metadata = ProjectMetadata(
            project_name=info.get("attraction_name", "Migrated Haunted Project"),
            show_id=info.get("show_id", "IMD-MIGRATED"),
            version=info.get("version", "1.0.0"),
            project_type="Haunted House",
            operating_mode=info.get("run_mode", "Continuous walk-through"),
            experience_duration_minutes=info.get("estimated_walkthrough_minutes", 12),
            reset_behavior=info.get("reset_behavior", "Migrated from haunt project"),
            safety_defaults=info.get("emergency_defaults", "Migrated emergency defaults"),
            notes=info.get("project_notes", info.get("operator_notes", "Migrated from IMMERSE Haunted Designer")),
            enabled_modules=["Haunt Module"],
        )
        project = ExperienceProject(
            schema_version="2.0-migrated",
            metadata=metadata,
            deployment=DeploymentManifest(package_name=metadata.project_name.lower().replace(" ", "_")),
            modules=[ModuleConfig(name="Haunt Module", description="Migrated haunt-specific tools")],
        )
        project.layout_items = [
            LayoutItem(
                id=item.get("id", ""),
                name=item.get("name", "Room"),
                item_type=item.get("type", "Room"),
                description=item.get("description", ""),
                tags=[],
                default_state=item.get("default_ambient_state", "Ambient"),
                linked_devices=item.get("linked_devices", []),
                linked_cues=item.get("linked_cues", []),
                notes=item.get("actor_notes", ""),
                x=item.get("x", 40.0),
                y=item.get("y", 40.0),
                width=item.get("width", 220.0),
                height=item.get("height", 120.0),
            )
            for item in payload.get("rooms", [])
        ]
        project.devices = [
            Device(
                id=item.get("id", ""),
                name=item.get("name", "Device"),
                device_type=item.get("type", "Device"),
                category=item.get("type", "General"),
                node_assignment=item.get("node_assignment", ""),
                protocol=item.get("protocol", ""),
                address=item.get("address", ""),
                location_assignment=item.get("room_zone_assignment", ""),
                tags=item.get("tags", []),
                notes=item.get("notes", ""),
                enabled=item.get("enabled", True),
            )
            for item in payload.get("devices", [])
        ]
        project.nodes = [
            Node(
                id=item.get("id", ""),
                name=item.get("name", "Node"),
                hostname=item.get("hostname", ""),
                node_type=item.get("type", "Node"),
                location_assignment=item.get("room_zone_assignment", ""),
                notes=item.get("notes", ""),
                online=item.get("online", False),
                io_summary=f"{item.get('inputs', 0)} in / {item.get('outputs', 0)} out",
                health_status=item.get("health_status", "Placeholder"),
            )
            for item in payload.get("nodes", [])
        ]
        project.cues = [
            Cue(
                id=item.get("id", ""),
                name=item.get("name", "Cue"),
                cue_type=item.get("type", "Cue"),
                description=item.get("description", ""),
                targets=item.get("target_devices", []),
                pre_delay=item.get("pre_delay", 0.0),
                fade_time=item.get("fade_time", 0.0),
                hold_duration=item.get("hold_duration", 0.0),
                follow_action=item.get("follow_action", "None"),
                retrigger_rules=item.get("retrigger_rules", "Respect cooldown"),
                cooldown_time=item.get("cooldown_time", 0.0),
                priority=item.get("priority", 50),
                blocking=item.get("blocking", False),
                tags=item.get("tags", []),
                notes=item.get("notes", ""),
                color=item.get("color", "#4cc9f0"),
            )
            for item in payload.get("cues", [])
        ]
        project.trigger_rules = [
            TriggerRule(
                id=item.get("id", ""),
                name=item.get("name", "Trigger Rule"),
                source=item.get("trigger_source", "Trigger"),
                condition=item.get("condition", "On Active"),
                action=item.get("target_action", "Fire Cue"),
                target_ref=item.get("target_ref", ""),
                delay=item.get("delay", 0.0),
                repeat_mode=item.get("repeat_mode", "One Shot"),
                armed=item.get("armed", True),
                debounce=item.get("debounce", 0.2),
                lockout_timer=item.get("lockout_timer", 0.0),
                fallback_action=item.get("fallback_action", ""),
            )
            for item in payload.get("trigger_rules", [])
        ]
        project.runtime_states = [
            RuntimeState(
                id=item.get("id", ""),
                name=item.get("name", "State"),
                enabled_triggers=[],
                disabled_triggers=item.get("disabled_triggers", []),
                audio_mode=item.get("audio_mode", "Show"),
                lighting_mode=item.get("lighting_mode", "Programmed"),
                cue_availability="Limited" if not item.get("actor_cue_available", True) else "All",
                device_behavior="Scares enabled" if item.get("scare_enabled", True) else "Safe mode",
                transition_rules=item.get("transitions", []),
                notes=item.get("notes", ""),
            )
            for item in payload.get("runtime_states", [])
        ]
        project.scare_events = [
            ScareEvent(
                id=item.get("id", ""),
                name=item.get("name", "Scare"),
                scare_type=item.get("scare_type", "Scare"),
                location_ref=item.get("zone_room", ""),
                trigger_source=item.get("trigger_source", ""),
                cue_stack=item.get("cue_stack", []),
                cooldown_timer=item.get("cooldown_timer", 0.0),
                actor_assignment="Actor-assisted" if item.get("actor_participation") else "",
                intensity_rating=item.get("intensity_rating", 5),
                safety_notes=item.get("safety_notes", ""),
            )
            for item in payload.get("scares", [])
        ]
        return project
