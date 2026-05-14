# Agentic Marketing Platform

**Full-funnel, multi-channel marketing pipeline powered by LLM agents.**

```ascii
Research → Copy → Creative → Repurpose → Publish → Analytics
   ↓         ↓        ↓          ↓          ↓          ↓
Audience  3 var   FLUX img   10+ pieces  Multi-platform   ROI
insights  /plat  (Modal)    from 1       scheduling       tracking
```

## Features

- **10-stage pipeline** — Research → Strategy → Brief → Copy → Creative → Repurpose → Ad → Email → Publish → Analytics
- **CHAI quality gates** — 5-dimension review (Complete, Helpful, Accurate, Insightful, Actionable) with 2-round retry
- **Multi-platform publishing** — Twitter/X, LinkedIn, Facebook, Instagram, Buffer
- **FLUX image generation** — via Modal serverless GPU
- **LangGraph orchestration** — stateful, resumable pipeline with EP (Executive Producer) pattern
- **Multi-tenant** — User → Workspace → Campaign hierarchy
- **Analytics dashboard** — cross-platform metrics, campaign performance, ROI tracking

## Quick Start

```bash
# 1. Clone
git clone https://github.com/n00n0i/agentic-marketing.git
cd agentic-marketing

# 2. Python environment
python -m venv .venv && source .venv/bin/activate
pip install -e ".[server]"

# 3. Environment variables
cp .env.example .env
# Edit .env and add your API keys

# 4. Frontend
cd frontend && npm install && npm run dev
# → http://localhost:3000

# 5. Run a demo pipeline
python -m src.agentic_marketing.api "AI Automation for SaaS Teams" twitter
```

## Architecture

```
agentic-marketing/
├── src/agentic_marketing/
│   ├── agents/          # LangGraph agent nodes
│   │   ├── marketing_agent.py   # Main orchestrator (EP pattern)
│   │   ├── copy_agent.py       # Copy generation
│   │   ├── creative_agent.py   # FLUX image gen
│   │   └── repurposing_agent.py
│   ├── chains/          # LangChain chains
│   │   ├── copy_chain.py       # LLM copy generation
│   │   ├── research_chain.py   # Market research
│   │   ├── publish_chain.py   # Publishing workflow
│   │   └── review_chain.py     # CHAI review
│   ├── social/          # Platform clients
│   │   ├── twitter_client.py    # Twitter API v2
│   │   ├── linkedin_client.py   # LinkedIn API v2
│   │   ├── facebook_client.py  # Meta Graph API
│   │   ├── buffer_client.py     # Buffer API v1
│   │   ├── publish_manager.py  # Unified publish interface
│   │   └── analytics.py        # Cross-platform analytics
│   ├── review/          # CHAI quality gates
│   │   ├── chai_reviewer.py    # 5-dimension scorer
│   │   ├── quality_gates.py    # Gate definitions
│   │   └── moderation.py      # Content moderation
│   ├── workflows/       # LangGraph workflow nodes
│   │   ├── marketing_agent.py  # Main graph
│   │   ├── publish_workflow.py
│   │   └── review_workflow.py
│   ├── state.py         # EP_STATE management
│   ├── budget.py        # Cost estimation
│   ├── pipeline_loader.py
│   ├── vectorstore.py   # Qdrant integration
│   └── api/             # FastAPI routes
│       └── analytics_api.py
├── frontend/
│   └── app/
│       ├── page.tsx           # Main dashboard
│       └── analytics/page.tsx # Analytics dashboard
├── skills/              # Director skills
│   └── pipelines/marketing/  # 12 stage director skills
└── pipeline_defs/       # YAML pipeline manifests
```

## Pipeline Stages

| # | Stage | Description |
|---|-------|-------------|
| 1 | Research | Market research, audience analysis, competitor tracking |
| 2 | Strategy | Strategic angles, positioning, competitive differentiation |
| 3 | Brief | Content brief with goals, audience, key messages |
| 4 | Copy | 3-5 copy variants per platform (problem/stat/outcome-led) |
| 5 | Creative | FLUX image generation via Modal (or placeholder) |
| 6 | Repurpose | Transform 1 piece → 10+ pieces across platforms |
| 7 | Ad Creative | Ad variations for paid campaigns |
| 8 | Email | Email sequence generation |
| 9 | Publish | Multi-platform scheduling and posting |
| 10 | Analytics | Cross-platform metrics and ROI tracking |

## Environment Variables

See [`.env.example`](.env.example) for all configuration options.

Key variables:
- `OPENAI_API_KEY` — for copy generation and CHAI review
- `TWITTER_*` — Twitter API credentials
- `LINKEDIN_ACCESS_TOKEN` — LinkedIn API
- `MODAL_TOKEN_ID` / `MODAL_TOKEN_SECRET` — for FLUX image generation
- `DATABASE_URL` — PostgreSQL connection string

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check src/

# Type check
mypy src/
```

## License

MIT