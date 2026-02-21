# SheetAgent — Implementation Todo

> **What are we building?**
> An **agentic spreadsheet platform** for college-fest organizers, club leads, and recruitment teams.
> Users manage audition / registration data in a dark-mode, HexaCore-themed spreadsheet.
> **AI agents** watch for row-level status changes and autonomously send WhatsApp messages, emails, create groups, clean data, and provide summaries — all from inside the sheet.

---

## Phase 0 — Project Scaffolding & DevOps Skeleton

- [ ] Initialize monorepo structure (`/client`, `/server`, `/docker`, `/docs`)
- [ ] Scaffold **Next.js 15+ App Router** project inside `/client`
  - [ ] Install TanStack Table v8, TanStack Query, Tailwind CSS, Shadcn/UI, Framer Motion
- [ ] Scaffold **FastAPI** project inside `/server`
  - [ ] Install LangGraph, Celery, Redis driver, SQLAlchemy / asyncpg, Pydantic
- [ ] Create `docker-compose.yml` (PostgreSQL, Redis, FastAPI, Celery worker, Next.js dev)
- [ ] Add base `.env.example` with all required keys (DB, Redis, Twilio, Resend, OpenAI/Anthropic, Clerk)
- [ ] Configure GitHub Actions CI stub (lint + type-check for both ends)

---

## Phase 1 — Database & Core API

### 1A. PostgreSQL Schema

- [ ] `workspaces` table — id, name, owner_id, created_at
- [ ] `sheets` table — id, workspace_id, name, column_schema (JSONB), created_at
- [ ] `rows` table — id, sheet_id, data (JSONB), row_order, created_at, updated_at
- [ ] `agent_rules` table — id, sheet_id, trigger_column, trigger_value, action_type, action_config (JSONB), enabled
- [ ] `agent_logs` table — id, rule_id, row_id, status, message, timestamp
- [ ] Write Alembic migration(s) for all tables

### 1B. FastAPI — Sheet CRUD Routers

- [ ] `POST /workspaces` — Create workspace
- [ ] `GET /workspaces` — List workspaces
- [ ] `POST /workspaces/{id}/sheets` — Create sheet with column schema
- [ ] `GET /sheets/{id}` — Fetch sheet (columns + rows)
- [ ] `PATCH /sheets/{id}/columns` — Add / rename / reorder columns
- [ ] `POST /sheets/{id}/rows` — Create row
- [ ] `PATCH /rows/{id}` — Update cell(s) — **this is the agent trigger point**
- [ ] `DELETE /rows/{id}` — Delete row
- [ ] `POST /sheets/{id}/import-csv` — Bulk import from CSV

### 1C. Real-time Layer

- [ ] Set up WebSocket endpoint (`/ws/sheet/{id}`) for live cell updates
- [ ] Broadcast row changes to all connected clients on PATCH

---

## Phase 2 — Frontend: The Command Center

### 2A. Global Layout & Theme (Design.txt)

- [ ] Configure Tailwind with the HexaCore dark palette
  - Background `#0B0B0B`, Accent `#0905FE`, Neutral `#B0B0B0`, Pending `#4A63C6`, Success `#00FFC2`
- [ ] Add Inter / Montserrat (headers) + monospace (cells) fonts
- [ ] Build **Left Sidebar** — glassmorphism, icon-only, expand-on-hover, Framer Motion transitions
- [ ] Build **Top Header** bar — "Active Agents: N", "System Latency: Xms"
- [ ] Build reusable **Glassmorphic Card** component
- [ ] Build **Toast / System Notification** component (top-right, security-alert style)

### 2B. Spreadsheet UI (TanStack Table)

- [ ] Render dynamic columns from sheet's JSONB schema
- [ ] Support column types: String, Number, Dropdown (enum), Boolean (checkbox)
- [ ] Inline cell editing with auto-save (`PATCH /rows/{id}`)
- [ ] Row selection with blue glow (`#0905FE` 1px border)
- [ ] Row hover highlight (`#1A1A2E`)
- [ ] Column headers with "brushed-metal" texture styling
- [ ] Connect to WebSocket so edits from other users appear live
- [ ] CSV import button → calls backend import endpoint

### 2C. Agent Sidebar (Right Panel)

- [ ] Floating, collapsible right-hand panel (glassmorphic)
- [ ] List existing agent rules per sheet
- [ ] "Add Rule" form — pick trigger column, trigger value, action type, configure action
- [ ] Pulsing blue glow animation on active cell when an agent is processing
- [ ] Collapsible **Process Log / Terminal Output** at bottom — real-time agent log stream

### 2D. Action Bar & Bulk Actions

- [ ] Floating Action Button (FAB) appears when multiple rows are checked
  - [ ] "Send to All Selected", "Create Group from Selected", "Delete Selected"
- [ ] High-gloss rounded action buttons with blue glow drop-shadow

### 2E. Mobile Quick-View

- [ ] Responsive condensed sheet — shows only Score + Status columns
- [ ] One-tap grouping from mobile FAB

---

## Phase 3 — Agent Orchestration (LangGraph + Celery)

### 3A. Rule Engine

- [ ] CRUD API for agent rules (`/sheets/{id}/rules`)
- [ ] On `PATCH /rows/{id}`, evaluate all rules for that sheet
- [ ] If a rule matches, enqueue a Celery task with the rule + row context

### 3B. LangGraph Agent Workflow

- [ ] Define state-machine graph: **Check → Trigger → Confirm → Log**
- [ ] "Check" node — validate the row data matches the rule condition
- [ ] "Trigger" node — call the appropriate communication tool
- [ ] "Confirm" node — verify delivery (read receipts / API success)
- [ ] "Log" node — write result to `agent_logs` table
- [ ] Implement retry-on-failure loop (max 3 retries with exponential backoff)

### 3C. LLM-Powered Tools

- [ ] "Clean Sheet" command — LLM reads sheet context, suggests/applies cleaning
  - [ ] De-duplicate by Roll No / Email
  - [ ] Format normalization (phone numbers → E.164)
- [ ] "Summarize Sheet" — LLM generates a natural-language summary of the data
- [ ] "Draft Message" — LLM drafts a WhatsApp / Email message from a template + row data

---

## Phase 4 — Communication Integrations

### 4A. WhatsApp (Twilio / Meta Business API)

- [ ] Configure Twilio WhatsApp sandbox or Meta Cloud API credentials
- [ ] Agent tool: Send 1-to-1 templated WhatsApp message
- [ ] Agent tool: Create WhatsApp group + generate & distribute invite link
- [ ] Log delivery status to `agent_logs`

### 4B. Email (Resend + React Email)

- [ ] Configure Resend API key + verified sender domain
- [ ] Build React Email templates (selection notification, invite, PDF attachment)
- [ ] Agent tool: Send email with template + row data
- [ ] Log delivery status to `agent_logs`

---

## Phase 5 — Authentication & Multi-User

- [ ] Integrate **Clerk** for auth (sign-up, sign-in, org management)
- [ ] Protect all API routes with Clerk JWT verification middleware
- [ ] Associate workspaces/sheets with Clerk user IDs
- [ ] Role-based access: Owner vs. Editor vs. Viewer per workspace

---

## Phase 6 — Data Cleaning Tools

- [ ] One-click "De-duplicate" button (by Roll No or Email column)
- [ ] Phone number format normalisation (prepend country code if missing)
- [ ] Backend endpoints: `POST /sheets/{id}/deduplicate`, `POST /sheets/{id}/normalize-phones`
- [ ] Surface results in UI with undo capability

---

## Phase 7 — Polish, Testing & Deployment

### 7A. Testing

- [ ] Backend: pytest unit tests for sheet CRUD, rule evaluation, agent tools
- [ ] Backend: integration test for full rule → agent → communication flow (mocked APIs)
- [ ] Frontend: Vitest / React Testing Library for critical components (Table, Sidebar)
- [ ] E2E: Playwright test — create sheet → add rule → change status → verify log entry

### 7B. Performance & UX Polish

- [ ] Virtualize table rows for large datasets (TanStack Virtual)
- [ ] Debounce cell edits (300ms) before API call
- [ ] Skeleton loaders for sheet loading state
- [ ] Micro-animations: row insert, status badge change, agent pulse

### 7C. Deployment

- [ ] Dockerize frontend + backend + workers
- [ ] Deploy frontend to **Vercel**
- [ ] Deploy backend + Celery workers to **Railway / AWS EC2**
- [ ] Provision managed PostgreSQL + Redis
- [ ] Configure environment variables in production
- [ ] Set up GitHub Actions CI/CD pipeline (build → test → deploy)

---

## Summary of Stack

| Layer            | Technology                               |
|------------------|------------------------------------------|
| Frontend         | Next.js 15, TanStack Table, Tailwind CSS, Shadcn/UI, Framer Motion |
| State Sync       | TanStack Query + WebSockets              |
| Backend API      | FastAPI (Python)                         |
| Agent Engine     | LangGraph + LLM (GPT-4o-mini / Claude)  |
| Task Queue       | Celery + Redis                           |
| Database         | PostgreSQL (JSONB)                       |
| Real-time        | WebSockets (or Supabase Realtime)        |
| WhatsApp         | Twilio / Meta Business Cloud API         |
| Email            | Resend + React Email                     |
| Auth             | Clerk                                    |
| Deployment       | Docker, Vercel, Railway/AWS, GitHub Actions |
