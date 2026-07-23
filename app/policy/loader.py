from __future__ import annotations

import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.core.config import settings


@dataclass
class Rule:
    id: str
    condition: dict[str, Any]
    decision: str
    reason: str


@dataclass
class PolicyPack:
    name: str
    version: str
    rules: list[Rule] = field(default_factory=list)


def load_all_policies(policies_dir: str | None = None) -> list[PolicyPack]:
    dir_path = Path(policies_dir or settings.POLICIES_DIR)
    packs: list[PolicyPack] = []

    for yaml_file in sorted(dir_path.glob("*.yaml")):
        with yaml_file.open() as f:
            data = yaml.safe_load(f) or {}

        raw_rules = data.get("rules") or []
        rules = [
            Rule(
                id=r["id"],
                condition=r.get("condition", {}),
                decision=r["decision"],
                reason=r.get("reason", ""),
            )
            for r in raw_rules
        ]

        packs.append(PolicyPack(
            name=data.get("name", yaml_file.stem),
            version=str(data.get("version", "unknown")),
            rules=rules,
        ))

    return packs
