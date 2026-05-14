# Agentic Marketing Pipeline

Full-funnel content generation, publishing & analytics powered by LLM-driven multi-agent orchestration.

## Overview

The Agentic Marketing Pipeline is a YAML-driven, LangChain/LangGraph-based system that automates the complete marketing content lifecycle — from strategic research through content creation, repurposing, and performance analytics.

No hardcoded pipeline logic. Each stage is defined in YAML and rendered by an LLM reading Markdown skill definitions.

## Architecture

```
agentic-marketing/
├── pipeline_defs/          # YAML pipeline manifests (the "source of truth")
├── skills/                 # Markdown skill definitions per stage
│   ├── pipelines/marketing/  # Per-director skill files
│   └── meta/                # Cross-cutting meta skills (reviewer, etc.)
├── schemas/                # JSON Schema for all artifacts
│   ├── pipelines/            # Pipeline manifest schemas
│   └── artifacts/            # Artifact schemas
└── src/                   # Python source (langchain/langgraph implementations)
```

### Core Principles

1. **YAML-first**: Pipeline definitions in `pipeline_defs/` control stage sequencing, checkpoints, and approval gates
2. **LLM-driven**: Each director (Research, Copy, Creative, etc.) is a LangChain agent that reads its Markdown skill file at runtime
3. **Schema-validated**: All artifacts are JSON-schema validated at each stage boundary
4. **CHAI Review**: Every artifact passes through a Consistent, Helpful, Accurate, Insightful (CHAI) review loop
5. **Decision-logged**: All significant choices are recorded with alternatives considered, scores, and reasoning

## Phases

| Phase | Description |
|-------|-------------|
| **Phase 1** | Core Content Loop — research → brief → copy → creative → repurpose → publish |
| **Phase 2** | Paid Ads Integration — audience targeting, ad creative, budget optimization |
| **Phase 3** | Analytics & Optimization — performance tracking, A/B testing, ROI analysis |
| **Phase 4** | Multi-tenant & White-label — SaaS-ready, per-client isolation |
| **Phase 5** | Autonomous AI Agents — self-improving agents with memory and learned patterns |

## Stages (Phase 1)

| # | Director | Artifact | Description |
|---|----------|----------|-------------|
| 1 | Marketing Director | `market_brief` | Top-level orchestrator, gates all downstream work |
| 2 | Research Director | `market_brief` (enriched) | Audience, competitor, strategic angle analysis |
| 3 | Strategy Director | `channel_strategy` | Channel selection, budget allocation, sequencing |
| 4 | Brief Director | `content_brief` | Per-channel content specifications |
| 5 | Copy Director | `copy_variants` | 3–5 variants per platform, A/B scored |
| 6 | Creative Director | `creative_assets` | Visual assets, format adaptation, brand compliance |
| 7 | Repurpose Director | `repurpose_plan` | 1 → 10+ pieces from a single asset |
| 8 | Publish Director | `publish_log` | Scheduling, publishing, cross-channel coordination |

## Setup

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .

# Verify installation
python -c "from agentic_marketing import __version__; print(__version__)"
```

## Usage

```python
from agentic_marketing import AgenticMarketingPipeline

pipeline = AgenticMarketingPipeline.from_manifest("pipeline_defs/agentic-marketing.yaml")
result = pipeline.run(topic="Launching our new B2B SaaS analytics product")
```

## Development

```bash
# Run tests
pytest

# Validate all schemas
python -m jsonschema --dry-run schemas/**/*.json

# Lint
ruff check src/
```

## Tech Stack

- **Orchestration**: LangChain / LangGraph
- **Structured Output**: Pydantic v2
- **Schema Validation**: jsonschema
- **Primary DB**: PostgreSQL (relational artifacts, decision logs)
- **Document Store**: MongoDB (content variants, creative assets)
- **Vector Search**: Qdrant (semantic lookup, RAG)
- **Frontend**: Next.js (dashboard, pipeline monitoring)

## License

MIT