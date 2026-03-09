#!/usr/bin/env python3
"""
A(DAI) Signal Processor
=======================
Processes raw signals from /inbox/ using the Ralph pattern:
one Claude API call per signal, fresh context each time.

Extracts: concepts, practitioners, scenes, tendencies, CLA layers
Writes: structured markdown to /signals/ with W3C PROV provenance

Usage:
    python signal_processor.py
    python signal_processor.py --signal path/to/signal.md
    python signal_processor.py --dry-run

Architecture: Git-first. Reads from and writes to the local repo.
No Notion dependency. No database. Plain markdown files.

Ralph pattern: one Claude API call per signal, fresh context, no chaining.
"""

import os
import sys
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
import anthropic

# ── Paths ─────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent.parent
INBOX_DIR = REPO_ROOT / "inbox"
PROCESSED_DIR = REPO_ROOT / "signals"
SKILLS_DIR = REPO_ROOT / "skills"

# ── Claude model ───────────────────────────────────────────────────────────────
MODEL = "claude-opus-4-6"

# ── Load skills ────────────────────────────────────────────────────────────────
def load_skill(skill_name: str) -> str:
    """Load a skill file from /skills/ if it exists."""
    skill_path = SKILLS_DIR / f"{skill_name}.md"
    if skill_path.exists():
        return skill_path.read_text(encoding="utf-8")
    return ""

# ── CLA extraction prompt ──────────────────────────────────────────────────────
def build_extraction_prompt(signal_text: str) -> str:
    cla_skill = load_skill("cla-extraction")
    tendency_skill = load_skill("tendency-vocabulary")
    provenance_skill = load_skill("provenance-standards")

    return f"""You are A(DAI)'s signal processor. Extract structured intelligence from the signal below.

{f"## CLA Extraction Guide{chr(10)}{cla_skill}" if cla_skill else ""}

{f"## Tendency Vocabulary{chr(10)}{tendency_skill}" if tendency_skill else ""}

{f"## Provenance Standards{chr(10)}{provenance_skill}" if provenance_skill else ""}

## Signal to process

{signal_text}

---

Extract the following and return as JSON only — no preamble, no markdown fences:

{{
  "concepts": ["list of key concepts identified"],
  "practitioners": ["list of named practitioners or organisations"],
  "scenes": ["list of scenes, subcultures, or geographic contexts"],
  "tendencies": ["list of directional forces or tendencies observed"],
  "cla": {{
    "surface": "L1 — observable facts and events (1-3 sentences)",
    "systemic": "L2 — causes, structures, patterns (1-3 sentences)",
    "worldview": "L3 — discourse, values, assumptions (1-3 sentences)",
    "narrative": "L4 — deep metaphor, myth, cultural meaning (1-3 sentences)"
  }},
  "confidence": "high | medium | low | speculative",
  "summary": "One paragraph synthesising the signal's significance for the digital arts field"
}}
"""

# ── Parse frontmatter ──────────────────────────────────────────────────────────
def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML-style frontmatter from a markdown file."""
    frontmatter = {}
    body = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    key, _, value = line.partition(":")
                    frontmatter[key.strip()] = value.strip()
            body = parts[2].strip()

    return frontmatter, body

# ── Process a single signal ────────────────────────────────────────────────────
def process_signal(signal_path: Path, dry_run: bool = False) -> bool:
    """
    Process one signal file using the Ralph pattern.
    Returns True if successful.
    """
    print(f"Processing: {signal_path.name}")

    content = signal_path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(content)

    # Skip already processed
    if frontmatter.get("status") == "processed":
        print(f"  → Already processed, skipping.")
        return True

    if dry_run:
        print(f"  → [dry-run] Would process signal.")
        return True

    # ── Ralph pattern: one fresh API call per signal ───────────────────────────
    client = anthropic.Anthropic()

    prompt = build_extraction_prompt(body or content)

    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        raw_response = message.content[0].text.strip()
    except Exception as e:
        print(f"  ✗ Claude API error: {e}")
        return False

    # ── Parse JSON response ────────────────────────────────────────────────────
    try:
        # Strip markdown fences if present
        clean = re.sub(r"^```(?:json)?\n?", "", raw_response)
        clean = re.sub(r"\n?```$", "", clean)
        extracted = json.loads(clean)
    except json.JSONDecodeError as e:
        print(f"  ✗ JSON parse error: {e}")
        print(f"  Raw response: {raw_response[:200]}")
        return False

    # ── Build processed signal ─────────────────────────────────────────────────
    processed_at = datetime.now(timezone.utc).isoformat()
    signal_id = signal_path.stem

    # Preserve original provenance, add processing metadata
    provenance = {
        "contributor": frontmatter.get("saved_by", "unknown"),
        "contribution_date": frontmatter.get("saved_at", "unknown"),
        "contribution_method": frontmatter.get("contribution_method", "bookmark"),
        "confidence": extracted.get("confidence", "medium"),
        "lived_experience": frontmatter.get("lived_experience", "false") == "true",
        "consent": frontmatter.get("consent", "public"),
        "license": "CC-BY-SA",
        "processed_at": processed_at,
        "processor_version": "1.0.0",
        "model": MODEL,
    }

    output_lines = [
        "---",
        f"id: {signal_id}",
        f"status: processed",
        f"source_url: {frontmatter.get('source_url', '')}",
        f"title: {frontmatter.get('title', signal_id)}",
        f"processed_at: {processed_at}",
        "provenance:",
    ]
    for k, v in provenance.items():
        output_lines.append(f"  {k}: {v}")

    output_lines += [
        "concepts:",
    ]
    for c in extracted.get("concepts", []):
        output_lines.append(f"  - {c}")

    output_lines += ["practitioners:"]
    for p in extracted.get("practitioners", []):
        output_lines.append(f"  - {p}")

    output_lines += ["scenes:"]
    for s in extracted.get("scenes", []):
        output_lines.append(f"  - {s}")

    output_lines += ["tendencies:"]
    for t in extracted.get("tendencies", []):
        output_lines.append(f"  - {t}")

    output_lines += [
        "---",
        "",
        f"# {frontmatter.get('title', signal_id)}",
        "",
        f"> {extracted.get('summary', '')}",
        "",
        "## CLA Analysis",
        "",
        f"**L1 — Surface**: {extracted['cla'].get('surface', '')}",
        "",
        f"**L2 — Systemic**: {extracted['cla'].get('systemic', '')}",
        "",
        f"**L3 — Worldview**: {extracted['cla'].get('worldview', '')}",
        "",
        f"**L4 — Narrative**: {extracted['cla'].get('narrative', '')}",
        "",
        "## Original Signal",
        "",
        body or content,
    ]

    output = "\n".join(output_lines)

    # ── Write to /signals/ ─────────────────────────────────────────────────────
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PROCESSED_DIR / signal_path.name
    output_path.write_text(output, encoding="utf-8")

    # ── Mark inbox file as processed ──────────────────────────────────────────
    updated_content = re.sub(
        r"^status: raw", "status: processed", content, flags=re.MULTILINE
    )
    if "status:" not in content:
        updated_content = content.replace("---\n", f"---\nstatus: processed\n", 1)
    signal_path.write_text(updated_content, encoding="utf-8")

    print(f"  ✓ Written to {output_path.relative_to(REPO_ROOT)}")
    print(f"    Concepts: {len(extracted.get('concepts', []))} | "
          f"Practitioners: {len(extracted.get('practitioners', []))} | "
          f"Confidence: {extracted.get('confidence', '?')}")
    return True

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="A(DAI) Signal Processor (Ralph pattern)")
    parser.add_argument("--signal", help="Process a single signal file")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable not set.")
        sys.exit(1)

    if args.signal:
        signal_path = Path(args.signal)
        if not signal_path.exists():
            print(f"Error: {signal_path} not found.")
            sys.exit(1)
        process_signal(signal_path, dry_run=args.dry_run)
        return

    # Process all raw signals in inbox
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    raw_signals = [
        f for f in INBOX_DIR.glob("*.md")
        if "status: processed" not in f.read_text()
    ]

    if not raw_signals:
        print("No unprocessed signals in inbox.")
        return

    print(f"Found {len(raw_signals)} unprocessed signal(s).\n")
    success, failed = 0, 0

    for signal_path in sorted(raw_signals):
        if process_signal(signal_path, dry_run=args.dry_run):
            success += 1
        else:
            failed += 1
        print()

    print(f"Done. {success} processed, {failed} failed.")

if __name__ == "__main__":
    main()
