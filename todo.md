# Vision Node (Local Audition Agent) Implementation Checklist

## 1. Project Initialization & Infrastructure
- [x] **Repository Setup**
    - [x] Initialize Git repository
    - [x] Create directory structure: `/backend`, `/frontend`, `/docker`
    - [x] Create `docker-compose.yaml` for FastAPI + Ollama orchestration
- [x] **Backend Environment**
    - [x] Initialize Python environment (Poetry or venv)
    - [x] Install dependencies: `fastapi`, `uvicorn`, `httpx`, `pydantic`, `sqlalchemy` (or `tortoise-orm`), `pywhatkit`, `python-multipart`
- [x] **Frontend Environment**
    - [x] Initialize React App (Vite + TypeScript)
    - [x] Install dependencies: `tailwindcss` (v4.0), `zustand`, `lucide-react`, `framer-motion` (for animations), `axios`/`tanstack-query`
    - [x] Install UI Library: `shadcn/ui` or `heroui`

## 2. Backend Implementation (FastAPI + Ollama)
- [ ] **Database & Models**
    - [ ] Design SQLite Schema: `Participant` (id, name, phone, act, status, created_at, sheet_id)
    - [ ] Setup ORM (SQLAlchemy/Tortoise) and migration scripts
    - [ ] Implement Deduplication Logic (Check if phone number already exists/invited)
- [x] **Ollama Integration (Inference Layer)**
    - [x] Create `OllamaClient` service to interface with local API
    - [x] specific Vision Prompt Engineering ("Professional registrar" persona, JSON output enforcement)
    - [ ] Implement "Chain of Thought" validation logic (Phone digit verification)
- [x] **Core API Endpoints**
    - [x] `POST /upload`: Handle image upload and trigger Vision processing
    - [ ] `GET /participants`: Retrieve list of extracted participants (with status)
    - [ ] `PATCH /participants/{id}`: Update participant details (Manual correction)
    - [ ] `POST /invite`: Trigger WhatsApp invitation flow for selected participants
- [ ] **WhatsApp Automation Service (Action Layer)**
    - [ ] Implement `pywhatkit` wrapper
    - [ ] Create "Messaging Loop" with throttling (15-30s random delay)
    - [ ] Implement Template Engine for dynamic messages ("Hey {name}, loved the {performance}...")
    - [ ] Add safety checks (skip invalid numbers marked with "??")

## 3. Frontend Implementation (React + Tailwind)
- [x] **Visual Identity & Theming**
    - [x] Configure Tailwind theme:
      - [x] Background: `#0F0F12`
      - [x] Surfaces: `#1A1A1E`
      - [x] Accent: `#00D1FF` (Cyan)
      - [x] Success: `#00FF94`, Warning: `#FFB800`
    - [x] Setup Fonts: *Geist Sans* (Headings) and *JetBrains Mono* (Data)
- [x] **Layout & Components**
    - [x] **Header**: Status indicator for "Ollama Connected"
    - [x] **Hero/Dropzone**:
      - [x] Drag-and-drop file input
      - [x] "Scanning Beam" animation (CSS/Framer Motion)
    - [x] **Agentic Data Table**:
      - [x] Display Name, Phone, Act, Status
      - [x] Inline editing capabilities
      - [x] Skeleton loaders for "Scanning" state
      - [x] Confidence Warning (Amber underline for unsure digits)
    - [x] **Action Panel**:
      - [x] "Fire Invites" button with Progress Ring animation
- [x] **State Management (Zustand)**
    - [x] Create store for `participants`, `uploadStatus`, `agentStatus`
    - [x] Implement optimistic updates for inline editing

## 4. Integration & Logic
- [x] **End-to-End Wiring**
    - [x] Connect Generic Upload component to Backend `/upload`
    - [x] Render API results in Data Table
    - [x] Wire up "Send Invites" button to triggering the backend automation loop
- [ ] **Real-time Updates (Optional but recommended)**
    - [ ] Poll status or use WebSockets for progress updates during messaging loop ("Sent 1/15...", "Waiting...")

## 5. Testing & Verification
- [ ] **OCR Accuracy Test**: Run against sample handwritten and printed sheets
- [ ] **Automation Safety**: Verify `pywhatkit` opens WhatsApp Web and handles delays correctly
- [ ] **Data Persistence**: Ensure reloading the app doesn't lose the parsed list (SQLite verification)

## 6. Documentation & Packaging
- [ ] Write `README.md` with:
    - [ ] Prerequisites (Ollama, Chrome, WhatsApp Login)
    - [ ] Setup instructions
- [ ] Finalize Docker setup for easy deployment
