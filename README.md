# prototype-knowledge

Private, AI-first cross-repository knowledge registry and context compiler for the `ulfbou` prototype repository family.

## Purpose

This repository stores machine-readable cross-repository knowledge about development status, decisions, lessons, contracts, invariants, procedures, commands, DevOps, response considerations, repository relationships, and verification. Repository-local source, tests, issues, and implementation documentation remain authoritative in their owning repositories.

## Architecture

- `registry/`: surgically maintained vocabularies and current identities.
- `events/`: immutable accepted events. Existing event files may not be edited or deleted.
- `knowledge/`: versioned durable knowledge. Semantic changes create a new version and supersede the old one.
- `sources/`: pointers to canonical external repositories and documents.
- `queries/`: reusable context-selection requests.
- `schemas/`: JSON Schema contracts.
- `src/prototype_knowledge/`: dependency-free validator, query engine, context compiler, and exporters.
- `.dx/`: ignored generated indexes, context bundles, and delivery artifacts.

All `.yaml` files use the JSON-compatible subset of YAML 1.2. This permits conventional YAML tooling while keeping runtime validation dependency-free.

## Mutation policy

1. Events are append-only.
2. Accepted knowledge versions are immutable; changes create a successor version.
3. Registries, schemas, queries, source pointers, and this README receive only minimal reviewed edits.
4. Generated projections are replaceable and remain under `.dx/` by default.
5. Security, privacy, legal, or corruption remediation may require history rewriting and credential rotation.

## Quick start

```bash
python3 -m prototype_knowledge validate
python3 -m prototype_knowledge query --file queries/lead-planning.yaml --format json
python3 -m prototype_knowledge compile --file queries/dx-recovery.yaml --format dx --out .dx/dx-recovery.dx.txt
python3 -m unittest discover -s tests -v
```

When running from a source checkout without installation:

```bash
PYTHONPATH=src python3 -m prototype_knowledge validate
```

## Retrieval model

Queries select active, current knowledge by repository, topic, role, lifecycle phase, kind, and minimum authority. Results retain source references and relationship links. The compiler emits JSON, YAML-compatible JSON, Markdown, or readonly DX v1.3.1.

## Authority precedence

Current explicit instructions, accepted repository contracts, and current source plus executable tests outrank cross-repository coordination knowledge. Generated summaries never outrank their sources.
