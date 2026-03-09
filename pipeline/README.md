# A(DAI) Signal Pipeline

Three scripts. No Notion. Everything in the repo.

```
inbox/               ← raw signals land here
signals/             ← processed signals (after pipeline runs)
graph-data.json      ← feeds the / graph page
dashboard.md         ← human-readable status
```

## Scripts

| Script | What it does |
|---|---|
| `signal_processor.py` | Reads raw signals from `/inbox/`, calls Claude once per signal (Ralph pattern), writes structured markdown + CLA analysis to `/signals/` |
| `concept_linker.py` | Reads all processed signals from `/signals/`, builds concept co-occurrence graph, writes `graph-data.json` |
| `update_dashboard.py` | Reads processed signals + graph data, writes `dashboard.md` |

## Run locally

```bash
# Set your API key
export ANTHROPIC_API_KEY=sk-...

# Process all unprocessed signals
python pipeline/signal_processor.py

# Process a single signal
python pipeline/signal_processor.py --signal inbox/my-signal.md

# Dry run (no writes)
python pipeline/signal_processor.py --dry-run

# Rebuild graph
python pipeline/concept_linker.py

# Update dashboard
python pipeline/update_dashboard.py
```

## Run via GitHub Actions

Pipeline runs nightly at 02:00 UTC. To trigger manually:
- Go to **Actions** → **A(DAI) Signal Pipeline** → **Run workflow**
- Optionally specify a single signal path or enable dry run

## Required secret

Add `ANTHROPIC_API_KEY` to your repo secrets:
**Settings → Secrets and variables → Actions → New repository secret**

## Signal format

Raw signals in `/inbox/` should be markdown files with optional frontmatter:

```markdown
---
title: Signal title
source_url: https://example.com/article
saved_by: jb
saved_at: 2026-03-09
contribution_method: bookmark
consent: public
---

Signal content here. Can be a pasted article, transcript excerpt,
observation, or any field intelligence worth processing.
```

## Ralph pattern

One Claude API call per signal. Fresh context every time. No chaining.
This keeps outputs independent, provenance clean, and costs predictable.

## Provenance

Every processed signal carries W3C PROV-aligned metadata:
- who contributed it, how, when
- confidence level (high / medium / low / speculative)
- consent status (recorded / anonymous / public)
- license (CC-BY-SA)

Private signals (sensing conversations) are never surfaced via the public query interface.
