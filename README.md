# SheetAgent

> An agentic spreadsheet platform for college-fest organizers, club leads, and recruitment teams.

Manage audition & registration data in a dark-mode spreadsheet UI. AI agents watch for status changes and autonomously handle WhatsApp messages, emails, group creation, and data cleaning.

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | Next.js 15, TanStack Table, Tailwind CSS, Shadcn/UI, Framer Motion |
| Backend | FastAPI, LangGraph, Celery + Redis |
| Database | PostgreSQL (JSONB) |
| Comms | Twilio WhatsApp, Resend Email |
| Auth | Clerk |

## Project Structure

```
client/   → Next.js frontend
server/   → FastAPI backend + agent engine
docker/   → Docker & Compose configs
docs/     → Documentation & specs
```

## Getting Started

> Coming soon — see `todo.md` for the roadmap.
