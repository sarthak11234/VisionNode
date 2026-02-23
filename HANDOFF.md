# SheetAgent — Complete Project Handoff Document

> **Last Updated**: 2026-02-23
> **Repo**: `https://github.com/sarthak11234/VisionNode`
> **Branch**: `main`

---

## 1. What Is SheetAgent?

An **agentic spreadsheet platform** for college-fest organizers, club leads, and recruitment teams.
Users manage audition/registration data in a dark-mode, HexaCore-themed spreadsheet.
**AI agents** watch for row-level status changes and autonomously send WhatsApp messages, emails, create groups, clean data, and provide summaries — all from inside the sheet.

---

## 2. Monorepo Structure

```
VisionNode/
├── client/                  # Next.js 16 (App Router, Turbopack)
│   ├── src/app/
│   │   ├── components/
│   │   │   ├── ActionBar.tsx      # Floating bulk-action bar (email/whatsapp/delete)
│   │   │   ├── AgentSidebar.tsx   # Right-hand slide-in panel for agent rules
│   │   │   ├── AppShell.tsx       # Main layout wrapper (sidebar + header + content)
│   │   │   ├── DataGrid.tsx       # Spreadsheet UI (TanStack Table, editable cells)
│   │   │   ├── Header.tsx         # Top bar (sheet name, active agents, latency)
│   │   │   └── Sidebar.tsx        # Left nav sidebar (glassmorphism, expand on hover)
│   │   ├── globals.css            # HexaCore dark theme (CSS vars + Tailwind v4)
│   │   ├── layout.tsx             # Root layout (Inter, Montserrat, JetBrains Mono fonts)
│   │   └── page.tsx               # Main page — composes DataGrid + AgentSidebar + ActionBar
│   ├── eslint.config.mjs
│   ├── package.json
│   └── tsconfig.json
│
├── server/                  # FastAPI (Python 3.12)
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py          # Pydantic Settings (DATABASE_URL, REDIS_URL)
│   │   │   ├── database.py        # async SQLAlchemy engine + sessionmaker
│   │   │   └── ws_manager.py      # In-memory WebSocket connection manager (room-based pub/sub)
│   │   ├── models/
│   │   │   ├── base.py            # SQLAlchemy DeclarativeBase
│   │   │   ├── workspace.py       # Workspace model (id, name, owner_id)
│   │   │   ├── sheet.py           # Sheet model (id, workspace_id, column_schema JSONB)
│   │   │   ├── row.py             # Row model (id, sheet_id, data JSONB, row_order)
│   │   │   ├── agent_rule.py      # AgentRule model (trigger_column, trigger_value, action_type)
│   │   │   └── agent_log.py       # AgentLog model (rule_id, row_id, status, message)
│   │   ├── schemas/               # Pydantic request/response schemas (1 file per model)
│   │   ├── services/              # Business logic layer (thin router, fat service pattern)
│   │   │   ├── workspace_service.py
│   │   │   ├── sheet_service.py
│   │   │   ├── row_service.py
│   │   │   └── agent_rule_service.py  # Includes evaluate_rules_for_row() helper
│   │   ├── routers/
│   │   │   ├── workspaces.py      # CRUD /api/v1/workspaces
│   │   │   ├── sheets.py          # CRUD /api/v1/sheets
│   │   │   ├── rows.py            # CRUD /api/v1/rows + POST /sheets/{id}/import-csv
│   │   │   ├── agent_rules.py     # CRUD /api/v1/agent-rules
│   │   │   └── ws.py              # WebSocket /ws/sheet/{sheet_id}
│   │   ├── agents/                # Reserved for LangGraph agent workflow (Phase 3)
│   │   └── main.py                # FastAPI app — registers all routers
│   ├── alembic/
│   │   └── versions/
│   │       └── 0001_initial.py    # Initial migration (all 5 tables)
│   ├── alembic.ini
│   ├── requirements.txt
│   └── ruff.toml
│
├── docker/
│   └── docker-compose.yml         # PostgreSQL + Redis + FastAPI + Next.js dev
├── .github/workflows/ci.yml       # CI: client (eslint + tsc), server (ruff)
├── Design.txt                     # HexaCore-inspired design specification
├── todo.md                        # Full 7-phase implementation roadmap
└── .gitignore
```

---

## 3. What Has Been Completed

### ✅ Phase 0 — Project Scaffolding
- Monorepo with `/client` + `/server` + `/docker`
- Next.js 16 scaffolded with App Router + Turbopack
- FastAPI scaffolded with async SQLAlchemy + Pydantic Settings
- Docker Compose for local dev (PostgreSQL, Redis, FastAPI, Next.js)
- GitHub Actions CI (client: eslint + tsc, server: ruff check + format)

### ✅ Phase 1A — Database Models
All 5 SQLAlchemy models with async support:
- `Workspace` → `Sheet` → `Row` (parent-child hierarchy)
- `AgentRule` (trigger_column, trigger_value, action_type, action_config JSONB)
- `AgentLog` (rule_id, row_id, status, message, timestamp)
- Uses **JSONB** for flexible column schemas and row data
- Uses **fractional indexing** for row ordering
- Uses **UUIDs** as primary keys

### ✅ Phase 1B — Backend API
All routers registered in `main.py` under `/api/v1`:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/workspaces` | POST, GET | Create / list workspaces |
| `/api/v1/workspaces/{id}/sheets` | POST | Create sheet with column schema |
| `/api/v1/sheets/{id}` | GET, PATCH | Fetch / update sheet |
| `/api/v1/sheets/{id}/rows` | POST | Create row |
| `/api/v1/sheets/{id}/import-csv` | POST | Bulk import rows from CSV file |
| `/api/v1/rows/{id}` | PATCH, DELETE | Update / delete row |
| `/api/v1/agent-rules` | Full CRUD | Rules for agent automation |

**Architecture pattern**: Thin routers → fat services. Each router calls a service layer that handles all business logic and DB operations.

### ✅ Phase 1C — WebSocket Real-time Layer
- **Endpoint**: `/ws/sheet/{sheet_id}` — clients connect to receive live row updates
- **`ws_manager.py`**: In-memory `ConnectionManager` using room-based pub/sub (keyed by `sheet_id`)
- **Integration**: `rows.py` broadcasts `row_created`, `row_updated`, `row_deleted` events after each mutation
- **Scaling path**: Currently in-memory (single-server). Clear upgrade path to Redis Pub/Sub for multi-server

### ✅ Phase 2 — Frontend: The Command Center

**Theme** (`globals.css`):
- HexaCore dark palette via CSS custom properties
- Registered as Tailwind v4 theme tokens via `@theme inline`
- Colors: `#0B0B0B` bg, `#0905FE` accent, `#B0B0B0` neutral, `#00FFC2` success
- Custom scrollbar styles matching the dark theme

**Fonts** (`layout.tsx`):
- **Inter** — body text (variable: `--font-inter`)
- **Montserrat** — headers (variable: `--font-heading`)
- **JetBrains Mono** — spreadsheet cells (variable: `--font-mono`)
- All loaded via `next/font/google` for zero layout shift

**Components**:

| Component | File | What it does |
|-----------|------|-------------|
| Sidebar | `Sidebar.tsx` | Left nav, glassmorphism, icon-only at 64px, expands to 200px on hover. Inline SVGs (no icon library). CSS-only animation. |
| Header | `Header.tsx` | Top bar: sheet name + "Active Agents: N" + "Latency: Xms". Command-center aesthetic. |
| AppShell | `AppShell.tsx` | Layout wrapper: fixed sidebar + margin-left offset content + header. |
| DataGrid | `DataGrid.tsx` | Spreadsheet UI using **@tanstack/react-table** (headless, ~14KB). Click-to-edit cells, row checkboxes, sticky headers, hover highlights. Uses `useMemo` + `CellContext` type. |
| AgentSidebar | `AgentSidebar.tsx` | Floating right panel (320px). Slide-in toggle. Glassmorphic rule cards showing `If {col} = "{val}" → {action}`. Toggle switches. Process log preview. |
| ActionBar | `ActionBar.tsx` | Floating bottom pill. Appears when rows are selected. Bulk Email / WhatsApp / Delete buttons. GPU-accelerated `translateY` animation. |

**Current state**: All components render with **demo data** (5 audition entries, 3 agent rules). Not yet connected to the backend API.

---

## 4. What Needs To Be Done Next

### Phase 3 — Frontend ↔ Backend Wiring (PRIORITY)
Connect the demo-data frontend to the real API:

1. **Install TanStack Query** (`@tanstack/react-query`) for data fetching + caching
2. **Create API client** (`src/lib/api.ts`) — wrapper around `fetch` with base URL config
3. **Create custom hooks**:
   - `useWorkspaces()` → `GET /workspaces`
   - `useSheet(id)` → `GET /sheets/{id}` (columns + rows)
   - `useMutateRow()` → `PATCH /rows/{id}` (cell edit)
   - `useCreateRow()` → `POST /sheets/{id}/rows`
   - `useDeleteRows()` → `DELETE /rows/{id}` (bulk)
   - `useImportCSV()` → `POST /sheets/{id}/import-csv`
   - `useAgentRules(sheetId)` → `GET /agent-rules?sheet_id=...`
4. **Wire DataGrid**: Replace `demoRows`/`demoColumns` with `useSheet()` data
5. **Wire cell edits**: `onCellEdit` → `useMutateRow()` with optimistic updates
6. **Wire AgentSidebar**: Replace `demoRules` with `useAgentRules()` data
7. **Wire ActionBar**: Bulk delete/email/whatsapp → call corresponding endpoints
8. **WebSocket integration**: Connect to `/ws/sheet/{id}`, update TanStack Query cache on incoming events

### Phase 4 — Agent Orchestration (LangGraph + Celery)
The core AI feature:

1. **Install**: LangGraph, Celery, Redis driver
2. **Rule Engine**: On `PATCH /rows/{id}`, evaluate all rules → enqueue Celery task if match
3. **LangGraph state machine**: Check → Trigger → Confirm → Log (with retry loop)
4. **LLM Tools**: Clean Sheet, Summarize Sheet, Draft Message
5. **Connect Process Log**: Stream agent execution to frontend via WebSocket

### Phase 5 — Communication Integrations
1. **WhatsApp** via Twilio / Meta Business API (send messages, create groups)
2. **Email** via Resend + React Email templates

### Phase 6 — Authentication (Clerk)
- Protect API routes with JWT middleware
- Associate workspaces with user IDs
- Role-based access (Owner/Editor/Viewer)

### Phase 7 — Data Cleaning Tools
- De-duplicate by Roll No / Email
- Phone number normalization (E.164)
- Undo capability

### Phase 8 — Polish, Testing & Deployment
- pytest for backend, Vitest for frontend, Playwright for E2E
- Table virtualization (TanStack Virtual) for large datasets
- Debounced cell edits (300ms)
- Docker deployment, Vercel (frontend), Railway/AWS (backend)

---

## 5. Design Specification Reference

The full design spec is in `Design.txt` at the repo root. Key points:

- **Core Aesthetic**: Dark Mode, Cyber-Industrial, High-Contrast (HexaCore inspired)
- **Colors**: Background `#0B0B0B`, Accent `#0905FE`, Neutral `#B0B0B0`, Pending `#4A63C6`, Success `#00FFC2`
- **Typography**: Bold sans-serif headers (Montserrat), Monospace cells (JetBrains Mono)
- **Layout**: Left sidebar (glassmorphism, icon-only), minimalist header, dark spreadsheet
- **Agent UX**: Floating right panel, pulsing blue glow on active cells, terminal-style process log
- **Interactions**: Glassmorphic cards for rules, high-gloss action buttons with blue glow, system notification toasts

---

## 6. Key Architecture Decisions

| Decision | Choice | Rationale | Alternative |
|----------|--------|-----------|-------------|
| Table library | TanStack Table (headless) | Full rendering control, ~14KB, MIT license | AG Grid (250KB, hard to restyle), Handsontable (400KB, AGPL) |
| CSS approach | Tailwind v4 + CSS custom properties | Design tokens as CSS vars, registered in `@theme inline` | CSS-in-JS (runtime overhead), CSS Modules (no design tokens) |
| Font loading | `next/font/google` | Self-hosted, zero layout shift, auto subsetting | CDN `<link>` (FOIT flash), manual `@font-face` (no optimizations) |
| Sidebar animation | CSS transitions (width) | Zero JS re-renders, GPU-accelerated | Framer Motion (30KB extra for a simple width transition) |
| Agent sidebar | Floating overlay panel | Preserves max horizontal space for spreadsheet | Fixed sidebar (permanently eats 320px) |
| Action bar | Floating bottom pill | Contextual — only shows when relevant | Header toolbar (always visible, clutters UI) |
| Backend pattern | Thin routers, fat services | Testable business logic, clean separation | Controller-only (hard to test) |
| Row data | JSONB | Flexible schema per sheet, no migrations on column changes | Separate columns table + EAV (complex joins) |
| Row ordering | Fractional indexing | O(1) reorder without renumbering all rows | Integer positions (requires cascade update) |
| WebSocket | In-memory pub/sub | Simple, fast for single server | Redis Pub/Sub (needed only for multi-server) |
| Cell editing | Click-to-edit pattern | Best performance, one `<input>` at a time | Always-editable (1000+ inputs = terrible perf) |

---

## 7. Development Commands

### Frontend (client/)
```bash
cd client
npm install              # install dependencies
npm run dev              # start dev server (http://localhost:3000)
npx tsc --noEmit         # type check
npx eslint src/          # lint
```

### Backend (server/)
```bash
cd server
pip install -r requirements.txt   # install dependencies
uvicorn app.main:app --reload     # start dev server (http://localhost:8000)
python -m ruff check app/         # lint
python -m ruff format --check app/ # format check
alembic upgrade head              # run migrations (needs PostgreSQL running)
```

### Docker (full stack)
```bash
docker compose -f docker/docker-compose.yml up
```

### CI (runs automatically on push to main)
- **Client**: `npx eslint src/` + `npx tsc --noEmit`
- **Server**: `ruff check app/` + `ruff format --check app/`

---

## 8. Dependencies

### Frontend (`client/package.json`)
- `next` 16.x — React framework
- `react` 19.x — UI library
- `@tanstack/react-table` — headless table library
- `tailwindcss` 4.x — utility CSS
- `eslint-config-next` — linting

### Backend (`server/requirements.txt`)
- `fastapi` + `uvicorn` — ASGI web framework
- `sqlalchemy[asyncio]` + `asyncpg` — async ORM + PostgreSQL driver
- `alembic` — database migrations
- `pydantic` + `pydantic-settings` — data validation + config
- `python-multipart` — file upload support (CSV import)
- `ruff` — linting + formatting

### Not Yet Installed (needed for upcoming phases)
- `@tanstack/react-query` — data fetching (Phase 3)
- `langgraph` + `celery` + `redis` — agent orchestration (Phase 4)
- `twilio` — WhatsApp integration (Phase 5)
- `resend` — email sending (Phase 5)
- `@clerk/nextjs` — authentication (Phase 6)

---

## 9. Commit Conventions

- **Minimum 200 atomic commits** throughout the project lifecycle
- Format: `type(scope): description`
- Types: `feat`, `fix`, `refactor`, `deps`, `docs`, `test`, `ci`, `chore`
- Scopes: `ui`, `grid`, `page`, `api`, `ws`, `db`, `client`, `server`
- Examples:
  - `feat(grid): add editable DataGrid with TanStack Table`
  - `fix(grid): resolve eslint errors — use CellContext type and useMemo`
  - `deps(client): add @tanstack/react-table for spreadsheet UI`

---

## 10. Known Issues / Notes

1. **ESLint warning**: `react-hooks/exhaustive-deps` fires on `useReactTable()` call in `DataGrid.tsx` — this is a false positive from a library call. Non-fatal, CI passes.
2. **Tailwind `@theme` lint**: CSS linter may flag `@theme inline` as unknown — this is valid Tailwind v4 syntax. Safe to ignore.
3. **No database yet**: Backend is fully coded but hasn't been run against a real PostgreSQL instance. Running `alembic upgrade head` + `uvicorn` requires a PostgreSQL connection (`DATABASE_URL` in `.env`).
4. **Demo data**: Frontend currently uses hardcoded demo data in `page.tsx`. Phase 3 replaces this with API calls.
5. **WebSocket manager**: In-memory only (single server). For multi-server deployment, upgrade to Redis Pub/Sub in `ws_manager.py`.
