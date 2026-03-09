# Practitioner Profiling

How A(DAI) builds and maintains practitioner records.

## When to create a practitioner record

A practitioner record is created when a person, organisation, collective, or institution appears in two or more processed signals. Single mentions are tracked as inline references only.

## Required fields

| Field | Notes |
|---|---|
| `id` | `practitioner-kebab-name` |
| `label` | Display name |
| `type` | `person` · `organisation` · `collective` · `institution` |
| `signal_count` | Number of signals mentioning this practitioner |
| `first_seen` | Date of earliest signal |

## Provenance

Practitioner records inherit confidence from their source signals. A practitioner mentioned in a high-confidence practitioner interview carries more weight than one found via web scan.

## Principle

Practitioners are nodes, not profiles. The graph tracks what they do and who they connect to — not biographical data. The commons records contributions to the field, not personal information.
