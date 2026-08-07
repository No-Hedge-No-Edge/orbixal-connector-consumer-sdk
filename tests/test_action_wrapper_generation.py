from __future__ import annotations

import json
from pathlib import Path
import sys

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))
from scripts.generate_action_wrappers import render_action_wrappers


def test_generate_action_wrappers_from_manifest_schema(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "key": "sample_connector",
                "operations": [
                    {
                        "name": "search_items",
                        "kind": "query",
                        "input_schema": {
                            "type": "object",
                            "required": ["query"],
                            "properties": {
                                "query": {"type": "string"},
                                "limit": {"type": "integer"},
                            },
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    generated = render_action_wrappers([manifest_path])

    assert "class SampleConnectorSearchItems" in generated
    assert "query: str" in generated
    assert "limit: int | None = None" in generated
    assert 'payload["query"] = self.query' in generated
    assert 'if self.limit is not None:' in generated
