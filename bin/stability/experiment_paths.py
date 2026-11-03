"""Resolve pre-split paths without rewriting historical run records."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MIGRATION = json.loads((ROOT / 'migration.json').read_text())
ORIGINAL_ROOT = MIGRATION['original_root']


def relocate(value):
    if isinstance(value, str):
        if value == ORIGINAL_ROOT or value.startswith(ORIGINAL_ROOT + '/'):
            return str(ROOT) + value[len(ORIGINAL_ROOT):]
        return value
    if isinstance(value, list):
        return [relocate(item) for item in value]
    if isinstance(value, dict):
        return {key: relocate(item) for key, item in value.items()}
    return value
