# Project status and engineering notes

This document records the boundary between what this repository is intended to demonstrate, what has been verified in the repository, and what still needs evidence. It is deliberately more specific than a feature list.

## Current stage

**Personal technical notebook**

## Why this exists

I built this site to keep project notes, engineering decisions, and learning reflections in a format that is easier to revisit than scattered repository notes.

## Scope and known limitations

The blog is a static personal publication, not a continuously updated knowledge base. Articles can become stale, project descriptions are curated summaries, and external links or screenshots may change over time.

## Verified evidence (2026.10.16)

- **Open source contributions**: 7 merged upstream PRs across `n8n-io/n8n`, `Draculabo/AntigravityManager`, `HKUDS/DeepTutor`, and `StarTrail-org/PixelRAG`, with linkable CI logs and test coverage.
- **CountyResearchAI**: Upgraded to Plan-and-Execute multi-agent architecture with dynamic question trees, Critic loop, and 299 pytest tests passing locally and in CI.
- **Lingshan AI Guide**: Spatiotemporal tourism agent with dual-engine separation (LLM + deterministic route planner), formal route validation, and reproducible RAG ablation report.
- **Engineering logs**: Documented real-world debugging workflows on Fastify 413 route scoping, SRS state idempotency, and multimodal visual RAG preprocessing.

## Maintenance rule

Future changes should describe one concrete behavior, include the smallest relevant verification step, and update this document whenever the project boundary changes.
