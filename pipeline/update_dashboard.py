#!/usr/bin/env python3
"""
A(DAI) Dashboard Updater
========================
Reads processed signals and graph-data.json from the repo
and writes a human-readable status dashboard to /dashboard.md

Architecture: Git-first. No Notion. No external database.
Reads from /signals/ and /graph-data.json.
Writes to /dashboard.md (committed to repo, readable on GitHub).

Usage:
    python update_dashboard.py
    python update_dashboard.py --output path/to/dashboard.md
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

# ── Paths ─────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent.parent
PROCESSED_DIR = REPO_ROOT / "signals"
INBOX_DIR = REPO_ROOT / "inbox"
GRAPH_DATA = REPO_ROOT / "graph-data.json"
DASHBOARD_OUTPUT = REPO_ROOT / "dashboard.md"

# ── Parse frontmatter ──────────────────────────────────────────────────────────
def parse_frontmatter(content: str) -> dict:
    data = {
        "concepts": [],
        "practitioners": [],
        "scenes": [],
        "tendencies": [],
        "confidence": "medium",
        "title": "Untitled",
        "processed_at": "",
        "provenance": {},
    }

    if not content.startswith("---"):
        return data

    parts = content.split("---", 2)
    if len(parts) < 3:
        return data

    current_list_key = None
    for line in parts[1].strip().splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.startswith("- ") and current_list_key:
            data[current_list_key].append(stripped[2:].strip())
            continue

        if ":" in stripped and not stripped.startswith(" "):
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()
            if key in ("concepts", "practitioners", "scenes", "tendencies"):
                current_list_key = key
                data[key] = []
            elif key in ("confidence", "title", "processed_at"):
                data[key] = value
                current_list_key = None
            else:
                current_list_key = None

    return data

# ── Collect signal stats ───────────────────────────────────────────────────────
def collect_stats() -> dict:
    processed_files = [
        f for f in PROCESSED_DIR.glob("*.md")
        if "status: processed" in f.read_text(encoding="utf-8")
    ]
    inbox_files = list(INBOX_DIR.glob("*.md"))

    all_concepts = Counter()
    all_practitioners = Counter()
    all_scenes = Counter()
    all_tendencies = Counter()
    confidence_dist = Counter()
    recent_signals = []

    for f in sorted(processed_files, reverse=True):
        content = f.read_text(encoding="utf-8")
        data = parse_frontmatter(content)

        for c in data["concepts"]:
            all_concepts[c] += 1
        for p in data["practitioners"]:
            all_practitioners[p] += 1
        for s in data["scenes"]:
            all_scenes[s] += 1
        for t in data["tendencies"]:
            all_tendencies[t] += 1

        confidence_dist[data["confidence"]] += 1

        recent_signals.append({
            "title": data["title"],
            "processed_at": data["processed_at"],
            "confidence": data["confidence"],
            "concept_count": len(data["concepts"]),
        })

    # Count unprocessed inbox
    unprocessed = 0
    for f in inbox_files:
        content = f.read_text(encoding="utf-8")
        if "status: processed" not in content:
            unprocessed += 1

    # Load graph stats
    graph_stats = {"node_count": 0, "edge_count": 0, "generated_at": ""}
    if GRAPH_DATA.exists():
        try:
            graph = json.loads(GRAPH_DATA.read_text(encoding="utf-8"))
            meta = graph.get("meta", {})
            graph_stats = {
                "node_count": meta.get("node_count", len(graph.get("nodes", []))),
                "edge_count": meta.get("edge_count", len(graph.get("edges", []))),
                "generated_at": meta.get("generated_at", ""),
            }
        except json.JSONDecodeError:
            pass

    return {
        "processed_count": len(processed_files),
        "unprocessed_count": unprocessed,
        "total_inbox": len(inbox_files),
        "top_concepts": all_concepts.most_common(15),
        "top_practitioners": all_practitioners.most_common(10),
        "top_scenes": all_scenes.most_common(10),
        "top_tendencies": all_tendencies.most_common(10),
        "confidence_dist": dict(confidence_dist),
        "recent_signals": recent_signals[:10],
        "graph": graph_stats,
    }

# ── Format dashboard markdown ──────────────────────────────────────────────────
def format_dashboard(stats: dict) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# A(DAI) — Field Intelligence Dashboard",
        f"*Last updated: {now}*",
        "",
        "---",
        "",
        "## Signal Pipeline",
        "",
        f"| Metric | Count |",
        f"|---|---|",
        f"| Processed signals | {stats['processed_count']} |",
        f"| Awaiting processing | {stats['unprocessed_count']} |",
        f"| Total in inbox | {stats['total_inbox']} |",
        f"| Graph nodes | {stats['graph']['node_count']} |",
        f"| Graph edges | {stats['graph']['edge_count']} |",
        "",
    ]

    if stats["graph"]["generated_at"]:
        lines.append(f"*Graph last generated: {stats['graph']['generated_at']}*")
        lines.append("")

    # Confidence distribution
    if stats["confidence_dist"]:
        lines += [
            "## Confidence Distribution",
            "",
        ]
        for level in ["high", "medium", "low", "speculative"]:
            count = stats["confidence_dist"].get(level, 0)
            bar = "█" * count
            lines.append(f"- **{level}**: {bar} {count}")
        lines.append("")

    # Top concepts
    if stats["top_concepts"]:
        lines += [
            "## Top Concepts",
            "",
            "| Concept | Signals |",
            "|---|---|",
        ]
        for concept, count in stats["top_concepts"]:
            lines.append(f"| {concept} | {count} |")
        lines.append("")

    # Top practitioners
    if stats["top_practitioners"]:
        lines += [
            "## Top Practitioners & Organisations",
            "",
            "| Name | Signals |",
            "|---|---|",
        ]
        for name, count in stats["top_practitioners"]:
            lines.append(f"| {name} | {count} |")
        lines.append("")

    # Top scenes
    if stats["top_scenes"]:
        lines += [
            "## Scenes",
            "",
            "| Scene | Signals |",
            "|---|---|",
        ]
        for scene, count in stats["top_scenes"]:
            lines.append(f"| {scene} | {count} |")
        lines.append("")

    # Top tendencies
    if stats["top_tendencies"]:
        lines += [
            "## Tendencies",
            "",
        ]
        for tendency, count in stats["top_tendencies"]:
            lines.append(f"- {tendency} ({count})")
        lines.append("")

    # Recent signals
    if stats["recent_signals"]:
        lines += [
            "## Recently Processed Signals",
            "",
            "| Signal | Processed | Confidence | Concepts |",
            "|---|---|---|---|",
        ]
        for sig in stats["recent_signals"]:
            date = sig["processed_at"][:10] if sig["processed_at"] else "—"
            lines.append(
                f"| {sig['title']} | {date} | {sig['confidence']} | {sig['concept_count']} |"
            )
        lines.append("")

    lines += [
        "---",
        "",
        "*Generated by `pipeline/update_dashboard.py` · "
        "Source: [github.com/jbADAI/digital-arts-institute](https://github.com/jbADAI/digital-arts-institute)*",
    ]

    return "\n".join(lines)

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="A(DAI) Dashboard Updater")
    parser.add_argument("--output", help="Output path (default: /dashboard.md)")
    args = parser.parse_args()

    output_path = Path(args.output) if args.output else DASHBOARD_OUTPUT

    stats = collect_stats()
    dashboard = format_dashboard(stats)

    output_path.write_text(dashboard, encoding="utf-8")
    print(f"✓ Dashboard written to {output_path}")
    print(f"  {stats['processed_count']} signals · "
          f"{stats['graph']['node_count']} nodes · "
          f"{stats['graph']['edge_count']} edges")

if __name__ == "__main__":
    main()
