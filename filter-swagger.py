#!/usr/bin/env python3
"""
Filter swagger.json to only include partner-facing API endpoints.
Removes all admin, internal, and non-partner tags.

Usage:
  python3 filter-swagger.py input.json output.json
  python3 filter-swagger.py swagger.json swagger.json  (in-place)
"""

import json
import sys
import copy

# Tags to include in the public partner-facing API docs
KEEP_TAGS = {
    # Auth
    "Authentication",
    "Registration",
    "MFA",
    "Tokens",
    "Public",

    # Identity & KYC
    "KYC & Verification",
    "KYC Verification",
    "Verification",
    "Document Verification",

    # Organization & Users
    "Organizations",
    "Organizations - Settings",
    "Settings - Organization",
    "Settings - Preferences",
    "Organization Members & Invites",
    "Teams",
    "Users",
    "Users - Preferences",
    "Onboarding",
    "Invitations",
    "Access Control",

    # Claims & workflow
    "Claims",
    "Claims Portal",
    "Approvals",
    "Forensics",

    # Files & Evidence
    "Evidence",
    "Evidence - Public Upload",
    "Files",

    # Participants
    "Participants",

    # Voice
    "Voice Analysis & Intelligence",
    "Voice Calls",
    "Voice Interview",
    "Voice Question Bank",
    "Webhooks - VAPI",

    # Audit
    "Audit",
    "Audit Logs",
}

def filter_spec(data):
    filtered = copy.deepcopy(data)

    # 1. Filter paths — keep only operations that have at least one KEEP tag
    new_paths = {}
    for path, path_item in data.get("paths", {}).items():
        new_path_item = {}
        for method, operation in path_item.items():
            if not isinstance(operation, dict):
                # Keep non-operation fields like 'parameters', 'summary', etc.
                new_path_item[method] = operation
                continue
            op_tags = set(operation.get("tags", []))
            if op_tags & KEEP_TAGS:  # intersection — has at least one kept tag
                new_path_item[method] = operation
        if new_path_item:
            new_paths[path] = new_path_item

    filtered["paths"] = new_paths

    # 2. Filter the top-level 'tags' array
    if "tags" in filtered:
        filtered["tags"] = [
            t for t in filtered["tags"]
            if t.get("name") in KEEP_TAGS
        ]

    # 3. Collect all $ref values still used by the kept paths
    kept_spec_str = json.dumps({"paths": new_paths})
    used_refs = set()
    def collect_refs(obj):
        if isinstance(obj, dict):
            if "$ref" in obj:
                ref = obj["$ref"]
                # e.g. "#/components/schemas/CreateClaimDto"
                if ref.startswith("#/components/"):
                    parts = ref.split("/")
                    if len(parts) == 4:
                        used_refs.add((parts[2], parts[3]))
            for v in obj.values():
                collect_refs(v)
        elif isinstance(obj, list):
            for item in obj:
                collect_refs(item)

    collect_refs(new_paths)

    # Iteratively expand: some schemas reference other schemas
    components = data.get("components", {})
    all_component_sections = {k: v for k, v in components.items()}

    prev_size = -1
    while len(used_refs) != prev_size:
        prev_size = len(used_refs)
        for section, name in list(used_refs):
            obj = all_component_sections.get(section, {}).get(name)
            if obj:
                collect_refs(obj)

    # 4. Filter components to only include used refs
    if "components" in filtered:
        new_components = {}
        for section, section_items in components.items():
            if section == "securitySchemes":
                # Always keep security schemes
                new_components[section] = section_items
            elif isinstance(section_items, dict):
                kept = {
                    name: schema
                    for name, schema in section_items.items()
                    if (section, name) in used_refs
                }
                if kept:
                    new_components[section] = kept
            else:
                new_components[section] = section_items
        filtered["components"] = new_components

    return filtered

def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else "swagger.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "swagger.json"

    print(f"Reading: {input_file}")
    with open(input_file) as f:
        data = json.load(f)

    original_paths = len(data.get("paths", {}))
    original_schemas = len(data.get("components", {}).get("schemas", {}))

    filtered = filter_spec(data)

    kept_paths = len(filtered.get("paths", {}))
    kept_schemas = len(filtered.get("components", {}).get("schemas", {}))

    print(f"Paths:   {original_paths} → {kept_paths}  (removed {original_paths - kept_paths})")
    print(f"Schemas: {original_schemas} → {kept_schemas}  (removed {original_schemas - kept_schemas})")

    print(f"Writing: {output_file}")
    with open(output_file, "w") as f:
        json.dump(filtered, f, indent=2)

    print("Done.")

if __name__ == "__main__":
    main()
