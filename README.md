<p align="center">
  <img src="https://img.shields.io/badge/Status-In%20Development-0905FE?style=for-the-badge" alt="Status" />
  <img src="https://img.shields.io/badge/Frontend-Next.js%2016-000000?style=for-the-badge&logo=next.js" alt="Next.js" />
  <img src="https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Database-PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/AI-LangGraph-FF6F00?style=for-the-badge" alt="LangGraph" />
</p>

# 🤖 SheetAgent

**An agentic spreadsheet platform that automates communication and data management with AI.**

Built for college-fest organizers, club leads, and recruitment teams — manage audition & registration data in a sleek, dark-mode spreadsheet. AI agents watch for status changes and autonomously send WhatsApp messages, emails, create groups, and clean data — all from inside the sheet.

---

## ✨ Features

- 🌑 **HexaCore Dark Theme** — Cyber-industrial aesthetic with glassmorphism, Electric Cobalt accents, and Neon Teal status indicators
- 📊 **Live Spreadsheet** — Powered by TanStack Table with inline editing, row selection, sticky headers, and real-time WebSocket sync
- 🤖 **AI Agent Rules** — Set trigger conditions (e.g., "If Status = Shortlisted → Send Email") and agents execute autonomously
- 💬 **WhatsApp Integration** — Auto-send templated messages and create groups via Twilio / Meta Business API
- 📧 **Email Automation** — Beautiful React Email templates sent through Resend
- ⚡ **Real-time Updates** — WebSocket-powered live cell sync across all connected clients
- 📱 **Bulk Actions** — Select multiple rows → floating action bar for mass email, WhatsApp, or delete
- 📄 **CSV Import** — Upload CSV files to populate sheets instantly

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (Next.js 16)                  │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌───────────┐  │
│  │ DataGrid │  │ Agent    │  │ Action    │  │ AppShell  │  │
│  │ TanStack │  │ Sidebar  │  │ Bar       │  │ Layout    │  │
│  └────┬─────┘  └────┬─────┘  └─────┬─────┘  └───────────┘  │
│       │              │              │                        │
│  ┌────┴──────────────┴──────────────┴────┐                  │
│  │     TanStack Query + WebSocket Hook   │                  │
│  └───────────────────┬───────────────────┘                  │
└──────────────────────┼──────────────────────────────────────┘
                       │ HTTP + WebSocket
┌──────────────────────┼──────────────────────────────────────┐
│                      │    BACKEND (FastAPI)                  │
│  ┌───────────────────┴───────────────────┐                  │
│  │          REST API (/api/v1)           │                  │
│  │  Workspaces · Sheets · Rows · Rules   │                  │
│  └───────────────────┬───────────────────┘                  │
│                      │                                      │
│  ┌──────────┐  ┌─────┴──────┐  ┌───────────────┐           │
│  │ WebSocket│  │  Services  │  │ Agent Engine   │           │
│  │ Manager  │  │  (CRUD)    │  │ (LangGraph)    │           │
│  └──────────┘  └─────┬──────┘  └───────┬───────┘           │
│                      │                 │                    │
│               ┌──────┴──────┐   ┌──────┴──────┐            │
│               │ PostgreSQL  │   │ Celery +    │            │
│               │ (JSONB)     │   │ Redis       │            │
│               └─────────────┘   └─────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 16, React 19, TanStack Table, TanStack Query, Tailwind CSS v4 |
| **Fonts** | Inter (body), Montserrat (headers), JetBrains Mono (data cells) |
| **Backend** | FastAPI, SQLAlchemy (async), Pydantic, Alembic |
| **Real-time** | Native WebSocket (room-based pub/sub) |
| **Agent Engine** | LangGraph + Celery + Redis *(coming soon)* |
| **Database** | PostgreSQL with JSONB for flexible schemas |
| **WhatsApp** | Twilio / Meta Business Cloud API *(coming soon)* |
| **Email** | Resend + React Email *(coming soon)* |
| **Auth** | Clerk *(coming soon)* |
| **CI/CD** | GitHub Actions (eslint + tsc + ruff) |
| **DevOps** | Docker Compose |

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** 20+
- **Python** 3.12+
- **PostgreSQL** 15+ (or use Docker)
- **Redis** (for Celery workers)

### Quick Start

```bash
# Clone the repo
git clone https://github.com/sarthak11234/VisionNode.git
cd VisionNode

# ── Frontend ──────────────────────────
cd client
npm install
npm run dev                    # → http://localhost:3000

# ── Backend ───────────────────────────
cd ../server
pip install -r requirements.txt
cp .env.example .env           # Configure DATABASE_URL, etc.
alembic upgrade head           # Run migrations
uvicorn app.main:app --reload  # → http://localhost:8000

# ── Docker (full stack) ───────────────
docker compose -f docker/docker-compose.yml up
```

### Environment Variables

```env
# Backend (server/.env)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/sheetagent
REDIS_URL=redis://localhost:6379

# Frontend (client/.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

---

## 📂 Project Structure

```
VisionNode/
├── client/                          # Next.js 16 Frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/          # UI components
│   │   │   │   ├── DataGrid.tsx     #   Spreadsheet (TanStack Table)
│   │   │   │   ├── AgentSidebar.tsx #   Agent rules panel
│   │   │   │   ├── ActionBar.tsx    #   Bulk actions bar
│   │   │   │   ├── AppShell.tsx     #   Layout wrapper
│   │   │   │   ├── Header.tsx       #   Top status bar
│   │   │   │   └── Sidebar.tsx      #   Left navigation
│   │   │   ├── providers/           # React context providers
│   │   │   ├── globals.css          # HexaCore dark theme
│   │   │   ├── layout.tsx           # Root layout + fonts
│   │   │   └── page.tsx             # Main page
│   │   ├── hooks/                   # Data hooks (TanStack Query)
│   │   └── lib/                     # API client
│   └── package.json
│
├── server/                          # FastAPI Backend
│   ├── app/
│   │   ├── models/                  # SQLAlchemy models (5 tables)
│   │   ├── schemas/                 # Pydantic request/response
│   │   ├── services/                # Business logic layer
│   │   ├── routers/                 # API endpoints + WebSocket
│   │   ├── core/                    # Config, DB, WebSocket manager
│   │   ├── agents/                  # LangGraph workflows (Phase 4)
│   │   └── main.py                  # App entry point
│   ├── alembic/                     # Database migrations
│   └── requirements.txt
│
├── docker/                          # Docker Compose configs
├── .github/workflows/ci.yml        # CI pipeline
├── Design.txt                       # UI design specification
├── todo.md                          # Full implementation roadmap
└── HANDOFF.md                       # Detailed developer handoff doc
```

---

## 🎨 Design Philosophy

Inspired by **HexaCore's cyber-industrial aesthetic**:

- **Dark Mode First** — Deep charcoal backgrounds (`#0B0B0B`) with high-contrast accents
- **Electric Cobalt** (`#0905FE`) — Primary action color with glow effects
- **Glassmorphism** — Frosted-glass panels with `backdrop-filter: blur(16px)`
- **Monospace Data** — JetBrains Mono for spreadsheet cells (engineering feel)
- **Command Center UX** — Active agent count, system latency, process logs

---

## 📋 Development Roadmap

- [x] **Phase 0** — Project scaffolding, Docker, CI
- [x] **Phase 1** — Database models, REST API, WebSocket layer
- [x] **Phase 2** — Frontend UI (theme, layout, spreadsheet, agent sidebar, action bar)
- [x] **Phase 3** — Frontend ↔ Backend wiring (TanStack Query, WebSocket hooks)
- [ ] **Phase 4** — Agent orchestration (LangGraph + Celery)
- [ ] **Phase 5** — WhatsApp & Email integrations
- [ ] **Phase 6** — Authentication (Clerk)
- [ ] **Phase 7** — Data cleaning tools
- [ ] **Phase 8** — Testing, polish & deployment

> See [`todo.md`](todo.md) for the full granular roadmap.

---

## 🧪 CI / Linting

Every push to `main` triggers:

```bash
# Frontend
npx eslint src/       # ESLint
npx tsc --noEmit      # TypeScript type check

# Backend
ruff check app/       # Python lint
ruff format --check   # Python format check
```

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Commit atomically with conventional commits (`feat:`, `fix:`, `docs:`)
4. Push and open a PR

---

## 📄 License

This project is part of a college initiative. License TBD.

---

<p align="center">
  Built with ☕ and 🤖 by <a href="https://github.com/sarthak11234">Sarthak</a>
</p>
