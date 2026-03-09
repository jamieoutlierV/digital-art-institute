#!/usr/bin/env python3
"""
A(DAI) Concept Linker
=====================
Reads all processed signals from /signals/ and builds a
concept graph by finding co-occurrence and semantic relationships
across signals.

Writes: /graph-data.json — nodes and edges for the D3 force-directed graph

Architecture: Git-first. No Notion. No external database.
Everything is plain markdown files in the repo.

Usage:
    python concept_linker.py
    python concept_linker.py --dry-run
"""

import json
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

# ── Paths ─────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent.parent
PROCESSED_DIR = REPO_ROOT / "signals"
GRAPH_OUTPUT = REPO_ROOT / "graph-data.json"

# ── Parse frontmatter ──────────────────────────────────────────────────────────
def parse_frontmatter(content: str) -> dict:
    """Extract structured data from YAML frontmatter."""
    data = {
        "concepts": [],
        "practitioners": [],
        "scenes": [],
        "tendencies": [],
        "confidence": "medium",
        "provenance": {},
    }

    if not content.startswith("---"):
        return data

    parts = content.split("---", 2)
    if len(parts) < 3:
        return data

    current_key = None
    for line in parts[1].strip().splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        # List item
        if stripped.startswith("- ") and current_key:
            data[current_key].append(stripped[2:].strip())
            continue

        # Key: value
        if ":" in stripped and not stripped.startswith(" "):
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()

            if key in ("concepts", "practitioners", "scenes", "tendencies"):
                current_key = key
                data[key] = []
            elif key == "confidence":
                data["confidence"] = value
                current_key = None
            elif key == "provenance":
                current_key = "provenance"
            else:
                current_key = None

    return data

# ── Build graph ────────────────────────────────────────────────────────────────
def build_graph(dry_run: bool = False) -> dict:
    """
    Read all processed signals and build nodes + edges for D3 graph.

    Node types: concept, practitioner, scene, signal
    Edges: co-occurrence within the same signal
    """
    processed_files = [
        f for f in PROCESSED_DIR.glob("*.md")
        if "status: processed" in f.read_text(encoding="utf-8")
    ]

    if not processed_files:
        print("No processed signals found. Run signal_processor.py first.")
        return {"nodes": [], "edges": [], "meta": {}}

    print(f"Building graph from {len(processed_files)} processed signal(s)...\n")

    # Accumulate nodes and co-occurrences
    node_registry = {}        # id → node dict
    co_occurrences = defaultdict(int)  # (id_a, id_b) → count
    signal_nodes = []

    def node_id(node_type: str, name: str) -> str:
        return f"{node_type}:{name.lower().replace(' ', '-')}"

    def ensure_node(node_type: str, name: str, signal_count: int = 0):
        nid = node_id(node_type, name)
        if nid not in node_registry:
            node_registry[nid] = {
                "id": nid,
                "label": name,
                "type": node_type,
                "signal_count": 0,
                "confidence_scores": [],
            }
        node_registry[nid]["signal_count"] += 1
        return nid

    for signal_path in sorted(processed_files):
        content = signal_path.read_text(encoding="utf-8")
        data = parse_frontmatter(content)

        # Create signal node
        signal_nid = node_id("signal", signal_path.stem)
        node_registry[signal_nid] = {
            "id": signal_nid,
            "label": signal_path.stem,
            "type": "signal",
            "signal_count": 1,
            "confidence": data.get("confidence", "medium"),
        }
        signal_nodes.append(signal_nid)

        # Collect all entity IDs in this signal
        signal_entities = [signal_nid]

        for concept in data.get("concepts", []):
            nid = ensure_node("concept", concept)
            signal_entities.append(nid)

        for practitioner in data.get("practitioners", []):
            nid = ensure_node("practitioner", practitioner)
            signal_entities.append(nid)

        for scene in data.get("scenes", []):
            nid = ensure_node("scene", scene)
            signal_entities.append(nid)

        # Build co-occurrence edges (all pairs within this signal)
        for i, a in enumerate(signal_entities):
            for b in signal_entities[i + 1:]:
                if a != b:
                    key = tuple(sorted([a, b]))
                    co_occurrences[key] += 1

        print(f"  {signal_path.name}: "
              f"{len(data['concepts'])} concepts, "
              f"{len(data['practitioners'])} practitioners, "
              f"{len(data['scenes'])} scenes")

    # Build edges (co-occurrence weight ≥ 1)
    edges = []
    for (source, target), weight in co_occurrences.items():
        edges.append({
            "source": source,
            "target": target,
            "weight": weight,
        })

    # Sort nodes: concepts first, then practitioners, scenes, signals
    type_order = {"concept": 0, "practitioner": 1, "scene": 2, "signal": 3}
    nodes = sorted(
        node_registry.values(),
        key=lambda n: (type_order.get(n["type"], 9), n["label"])
    )

    graph = {
        "nodes": nodes,
        "edges": edges,
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "signal_count": len(processed_files),
            "node_count": len(nodes),
            "edge_count": len(edges),
        }
    }

    return graph

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="A(DAI) Concept Linker")
    parser.add_argument("--dry-run", action="store_true",
                        help="Build graph but don't write graph-data.json")
    args = parser.parse_args()

    graph = build_graph(dry_run=args.dry_run)

    if not graph["nodes"]:
        return

    meta = graph["meta"]
    print(f"\nGraph built:")
    print(f"  Nodes: {meta['node_count']}")
    print(f"  Edges: {meta['edge_count']}")
    print(f"  Signals: {meta['signal_count']}")

    if args.dry_run:
        print("\n[dry-run] graph-data.json not written.")
        return

    GRAPH_OUTPUT.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    print(f"\n✓ Written to {GRAPH_OUTPUT.relative_to(REPO_ROOT)}")
    print(f"  Feed this to the D3 force-directed graph on /")

if __name__ == "__main__":
    main()
