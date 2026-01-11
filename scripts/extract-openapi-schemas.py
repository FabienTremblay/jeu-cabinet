#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict

DRAFT = "https://json-schema.org/draft/2020-12/schema"

COMMON_SCHEMAS = {"ValidationError", "HTTPValidationError"}

def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

def rewrite_refs(obj: Any, rewrite_fn) -> Any:
    if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
            if k == "$ref" and isinstance(v, str):
                new[k] = rewrite_fn(v)
            else:
                new[k] = rewrite_refs(v, rewrite_fn)
        return new
    if isinstance(obj, list):
        return [rewrite_refs(x, rewrite_fn) for x in obj]
    return obj

def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: extract-openapi-schemas.py <openapi.json> <service_name>", file=sys.stderr)
        return 2

    openapi_path = Path(sys.argv[1])
    service_name = sys.argv[2]

    spec = load_json(openapi_path)
    components = spec.get("components", {})
    schemas: Dict[str, Any] = components.get("schemas", {})

    if not schemas:
        print(f"Aucun components.schemas dans {openapi_path}", file=sys.stderr)
        return 1

    out_service_dir = Path("contrats/jsonschema/http") / service_name
    out_common_dir = Path("contrats/jsonschema/_common/http")

    def ref_rewrite(ref: str) -> str:
        # Convertit #/components/schemas/XYZ vers un fichier JSON Schema.
        m = re.fullmatch(r"#/components/schemas/([A-Za-z0-9_]+)", ref)
        if not m:
            return ref

        name = m.group(1)
        if name in COMMON_SCHEMAS:
            return f"../../_common/http/{name}.schema.json"
        return f"./{name}.schema.json"

    # 1) sortir les schémas communs
    for name in COMMON_SCHEMAS:
        if name in schemas:
            data = schemas[name]
            data = rewrite_refs(data, ref_rewrite)
            if isinstance(data, dict) and "$schema" not in data:
                data = {"$schema": DRAFT, **data}
            save_json(out_common_dir / f"{name}.schema.json", data)

    # 2) écrire un fichier par schéma de service
    for name, data in schemas.items():
        if name in COMMON_SCHEMAS:
            continue
        data = rewrite_refs(data, ref_rewrite)
        if isinstance(data, dict) and "$schema" not in data:
            data = {"$schema": DRAFT, **data}
        save_json(out_service_dir / f"{name}.schema.json", data)

    # 3) écrire un index (optionnel mais très utile)
    index = {
        "service": service_name,
        "source_openapi": str(openapi_path),
        "schemas": sorted([n for n in schemas.keys() if n not in COMMON_SCHEMAS]),
        "common": sorted([n for n in COMMON_SCHEMAS if n in schemas]),
    }
    save_json(out_service_dir / "_index.json", index)

    print(f"OK: {service_name} -> {out_service_dir} (+ common dans {out_common_dir})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

