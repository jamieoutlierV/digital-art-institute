# Provenance Standards

Every signal processed by A(DAI) carries W3C PROV-aligned metadata that records its full lineage.

## Required fields

| Field | Values | Notes |
|---|---|---|
| `contributor` | name or handle | Who submitted the signal |
| `contribution_date` | ISO 8601 date | When it was submitted |
| `contribution_method` | `practitioner_interview` · `web_scan` · `team_observation` · `submitted_link` · `bookmark` · `transcript` | How it entered the system |
| `confidence` | `high` · `medium` · `low` · `speculative` | Verifiability of the source |
| `lived_experience` | `true` · `false` | Did the contributor directly experience this? |
| `consent` | `recorded` · `anonymous` · `public` | For practitioner contributions: was consent given to attribute? |
| `license` | `CC-BY-SA` | Default for all signals |

## Confidence guidance

- **high** — Named practitioner, direct interview, verified primary source
- **medium** — Credible secondary source, indirect observation, team member reporting
- **low** — Unverified, algorithmically sourced, single data point
- **speculative** — Explicitly marked inference or projection — not observation

## Consent guidance

- **recorded** — Practitioner said yes to being named; interview recorded
- **anonymous** — Contribution is real but contributor not named publicly
- **public** — Publicly available source; no personal consent needed

## Processing metadata (added automatically)

The signal processor adds:
- `processed_at` — UTC timestamp of Claude API call
- `processor_version` — script version
- `model` — Claude model used

## Principle

Provenance is infrastructure, not bureaucracy. Every edge in the graph carries a confidence score derived from provenance. Practitioner-contributed signals with high confidence create stronger graph connections than algorithmically sourced signals with low confidence.
