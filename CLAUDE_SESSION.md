# A(DAI) — Claude Code Session Start Document
**Drop this file at the start of every Claude Code session.**

---

## What you are building

**A(DAI) — A Digital Arts Institute** is a commons-first field intelligence system for the digital arts. It is not a product company. It operates as a knowledge commons and semantic graph, with two modes:

- **Mode 1 — Commons Intelligence**: open, provenance-tracked, field-wide knowledge
- **Mode 2 — Advisory Intelligence**: applied intelligence for partners and institutions

---

## Architecture: Git-first

Everything lives in the `jbADAI/digital-arts-institute` GitHub repository. This is both the website repo and the intelligence layer. Notion is for **operations only** — not queried directly, not a source of truth.

### Repository
- **GitHub org**: `jbADAI/digital-arts-institute`
- **Hosted on**: Vercel
- **Status**: Active — 12 commits, substantially built. Not currently cloned locally.

### Confirmed repo structure (as of 2026-03-09)

```
.github/workflows/  ← pipeline.yml (implemented, not a stub)
concepts/
config/
inbox/              ← all signals land here first
outputs/
pipeline/           ← Python pipeline scripts (NOT scripts/)
  signal_processor.py
  concept_linker.py
  update_dashboard.py
  README.md
practitioners/
scenes/
signals/
skills/             ← all 5 skill files present (see below)
threads/
transcriber/        ← transcriber app lives in-repo
graph-data.json     ← auto-generated, exists at root
graph.html          ← graph visualisation page
field-intelligence.html  ← likely the /query interface
contribute.html     ← contribution UI
drop-link.html      ← link submission UI
index.html
ADAI_CONTEXT.md     ← system context doc
SCHEMA.md           ← schema spec (v0.2, 2026-03-05)
requirements.txt
vercel.json
```

### Skills files (all present in `skills/`)
- `tendency-vocabulary.md`
- `cla-extraction.md`
- `scout-editorial.md`
- `provenance-standards.md`
- `practitioner-profiling.md`

---

## Pipeline scripts

Located at `pipeline/` (not `scripts/` — the CLAUDE.md spec uses `scripts/` as target names but the actual folder is `pipeline/`).

| Script | Purpose |
|---|---|
| `pipeline/signal_processor.py` | Reads `/inbox/`, extracts structured intelligence via Claude, writes to `/signals/` |
| `pipeline/concept_linker.py` | Builds concept co-occurrence graph → `graph-data.json` (equivalent to `export_graph.py` in spec) |
| `pipeline/update_dashboard.py` | Generates human-readable dashboard from signals + graph data |

**Note**: No `scout.py` visible in the pipeline folder yet.

GitHub Actions workflow (`pipeline.yml`) is implemented with actual job steps — runs processor → linker → dashboard in sequence, with dry-run support and conditional single/batch processing.

---

## Build phase status (updated from repo scan)

| Phase | What | Status |
|---|---|---|
| 0 | Notion bootstrap (signal capture, prototype pipeline) | ✅ Complete |
| 1 | Signal processor (`pipeline/signal_processor.py`) | ✅ Exists — verify if functional end-to-end |
| 2 | Graph export (`pipeline/concept_linker.py` → `graph-data.json`) | ✅ Exists — `graph-data.json` present at root |
| 3 | Transcriber rewired → repo `/inbox/` | ⚠️ `transcriber/` folder in repo — wiring status unconfirmed |
| 4 | `graph.html` wired to live `graph-data.json` | ⚠️ Both exist — wiring status unconfirmed |
| 5 | `/contribute` page at digitalartsinstitute.io | ⚠️ `contribute.html` exists — live routing unconfirmed |
| 6 | `/query` page | ⚠️ `field-intelligence.html` likely this — confirm |
| 7 | Scout agent (`scripts/scout.py`) | ❌ Not visible in pipeline folder |
| 8 | GitHub Actions nightly pipeline | ✅ `pipeline.yml` implemented |

---

## Analytical framework

- **CLA** (Causal Layered Analysis) — four depth registers: Litany (surface facts), Social (structural patterns), Discourse (conceptual vocabularies), Myth (lived meaning). Most systems only reach L1–L2; A(DAI) targets all four.
- **Tendency vocabulary** — machine-readable ontology (in `skills/tendency-vocabulary.md`)
- **Six-stage open protocol**: SENSE → QUERY → SPECULATE → REACT → COLLABORATE → EXPERIMENT
- **Current field stage**: SENSE — all signals in initial capture phase

Schema: v0.2 (2026-03-05). Review schema after every 20 processed signals.

---

## Starting questions for this session

Before building, verify:
- Is `pipeline/signal_processor.py` functional? Can it process a test signal from `/inbox/` end-to-end?
- Is the transcriber (`transcriber/` folder) wired to push to `/inbox/` on the main repo?
- Is `graph.html` actually reading from `graph-data.json` or is it using static/mock data?
- Is `field-intelligence.html` the `/query` interface, and is it wired to anything?
- What is in `config/`? (likely `scout-queries.yaml` and `example.env`)
- Does `scout.py` need to be written, or is it in progress somewhere?

---

## Key principle
> The commons does not get sold.

Mode 1 (the knowledge commons) and Mode 2 (advisory services) are architecturally and ethically separate. Nothing built in these sessions should compromise that separation.

---

*Last updated: 2026-03-09 | Repo: github.com/jbADAI/digital-arts-institute | Scanned live*
