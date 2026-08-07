"""Generate typed connector action wrappers from published manifest snapshots."""

from __future__ import annotations

import argparse
import json
import keyword
from pathlib import Path
from textwrap import dedent
from typing import Any


SDK_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = SDK_ROOT / "src" / "connector_consumer_sdk" / "first_party_actions.py"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest-root",
        action="append",
        default=[],
        help="Root containing */*/manifest.json files, such as first-party dist/.",
    )
    parser.add_argument(
        "--manifest",
        action="append",
        default=[],
        help="Specific manifest.json path. Can be repeated.",
    )
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()
    manifests = _discover_manifests(roots=args.manifest_root, paths=args.manifest)
    if not manifests:
        raise SystemExit("No manifests found.")
    content = render_action_wrappers(manifests)
    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    print(f"Generated {output} from {len(manifests)} manifests.")


def render_action_wrappers(manifest_paths: list[Path]) -> str:
    classes: list[str] = []
    exported_names: list[str] = []
    for manifest_path in sorted(manifest_paths):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        connector_key = str(manifest["key"])
        operations = manifest.get("operations") or []
        for operation in operations:
            if not isinstance(operation, dict):
                continue
            class_name = _class_name(connector_key, str(operation["name"]))
            exported_names.append(class_name)
            classes.append(_render_action_class(class_name=class_name, operation=operation))
    all_names = ", ".join(repr(name) for name in sorted(exported_names))
    body = "\n\n\n".join(classes)
    return (
        dedent(
            f'''
            """Generated typed action wrappers from connector manifests. Do not edit by hand."""

            from __future__ import annotations

            from dataclasses import dataclass
            from typing import Any, Literal


            __all__ = [{all_names}]
            '''
        ).strip()
        + "\n\n\n"
        + body
        + "\n"
    )


def _render_action_class(*, class_name: str, operation: dict[str, Any]) -> str:
    operation_name = str(operation["name"])
    operation_kind = str(operation["kind"])
    schema = operation.get("input_schema")
    properties = schema.get("properties", {}) if isinstance(schema, dict) else {}
    required = schema.get("required", []) if isinstance(schema, dict) else []
    required_names = [name for name in required if name in properties]
    optional_names = [name for name in properties if name not in required_names]
    fields: list[str] = []
    param_names: list[tuple[str, str, bool]] = []
    for name in required_names:
        py_name = _python_name(name)
        fields.append(f"    {py_name}: {_python_type(properties[name])}")
        param_names.append((name, py_name, True))
    for name in optional_names:
        py_name = _python_name(name)
        fields.append(f"    {py_name}: {_python_type(properties[name])} | None = None")
        param_names.append((name, py_name, False))
    fields.extend(
        [
            f'    name: str = "{operation_name}"',
            f'    operation: Literal["{operation_kind}"] = "{operation_kind}"',
        ]
    )
    lines = ["@dataclass(frozen=True, slots=True)", f"class {class_name}:", *fields, ""]
    lines.extend(["    def params(self) -> dict[str, object]:", "        payload: dict[str, object] = {}"])
    for original_name, py_name, is_required in param_names:
        if is_required:
            lines.append(f'        payload["{original_name}"] = self.{py_name}')
        else:
            lines.append(f"        if self.{py_name} is not None:")
            lines.append(f'            payload["{original_name}"] = self.{py_name}')
    lines.append("        return payload")
    return "\n".join(lines)


def _discover_manifests(*, roots: list[str], paths: list[str]) -> list[Path]:
    manifests = [Path(path).expanduser().resolve() for path in paths]
    for root in roots:
        root_path = Path(root).expanduser().resolve()
        manifests.extend(root_path.glob("*/*/manifest.json"))
        manifests.extend(root_path.glob("*/manifest.json"))
    return sorted({path for path in manifests if path.is_file()})


def _class_name(connector_key: str, operation_name: str) -> str:
    return "".join(_pascal_parts(connector_key) + _pascal_parts(operation_name))


def _pascal_parts(value: str) -> list[str]:
    return [part[:1].upper() + part[1:] for part in value.replace("-", "_").split("_") if part]


def _python_name(value: str) -> str:
    cleaned = value.replace("-", "_")
    if keyword.iskeyword(cleaned):
        return f"{cleaned}_"
    return cleaned


def _python_type(schema: dict[str, Any]) -> str:
    schema_type = schema.get("type")
    if schema_type == "string":
        return "str"
    if schema_type == "integer":
        return "int"
    if schema_type == "number":
        return "float"
    if schema_type == "boolean":
        return "bool"
    if schema_type == "array":
        return "list[object]"
    if schema_type == "object":
        return "dict[str, Any]"
    return "object"


if __name__ == "__main__":
    main()
