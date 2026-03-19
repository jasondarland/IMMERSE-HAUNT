from __future__ import annotations

from dataclasses import dataclass
from random import choice


@dataclass
class RuntimeHealth:
    node_name: str
    status: str
    cpu_load: int
    network_latency_ms: int


class MockRuntimeService:
    def node_health(self, node_names: list[str]) -> list[RuntimeHealth]:
        statuses = ["Healthy", "Warning", "Placeholder"]
        return [
            RuntimeHealth(node_name=name, status=choice(statuses), cpu_load=choice([18, 24, 31, 47]), network_latency_ms=choice([3, 6, 12, 18]))
            for name in node_names
        ]
