# System Architecture: VisionNode (Local Audition Agent)

This document outlines the architecture for **VisionNode**, a Local-First Agentic System designed to automate audition registration using Computer Vision and WhatsApp automation, entirely on-device.

## High-Level Data Flow

The system operates in a linear flow: **See -> Think -> Verify -> Act**.

```mermaid
graph TD
    User((User))
    
    subgraph "Frontend Layer (React + Tailwind)"
        UI[Web Interface]
        Upload[Dropzone / Camera]
        Review[Interactive Data Table]
    end
    
    subgraph "Backend Layer (FastAPI)"
        API[API Gateway]
        Orchestrator[Agent Orchestrator]
        DB[(SQLite History)]
        Whatsapp[Automation Service]
    end
    
    subgraph "Intelligence Layer (Ollama)"
        Llama[Llama 3.2 Vision]
    end
    
    subgraph "Action Layer"
        WA[WhatsApp Desktop / Web]
    end

    %% Flow
    User -->|1. Uploads Sheet Image| Upload
    Upload -->|2. POST Image| API
    API --> Orchestrator
    
    Orchestrator -->|3. Send Image + System Prompt| Llama
    Llama -->|4. Return JSON (Name, Phone, Act)| Orchestrator
    
    Orchestrator -->|5. Store Rough Draft| DB
    Orchestrator -->|6. Return Extracted Data| Review
    
    User -->|7. Edits & Approves| Review
    Review -->|8. POST /invite| API
    
    API --> Whatsapp
    Whatsapp -->|9. Automate Keystrokes| WA
    WA -->|10. Message Sent| User
```

## Core Components

### 1. The "Eyes": Intelligence Layer (Ollama)
*   **Role**: Extracts structured data from unstructured images.
*   **Tech**: **Ollama** running `llama3.2-vision`.
*   **Operation**: It receives an image and a strict system prompt ("You are a registrar... output JSON..."). It performs OCR and semantic understanding to output `Name`, `Phone`, and `Performance Type`.

### 2. The "Brain": Backend Layer (FastAPI)
*   **Role**: Orchestrates the workflow and manages state.
*   **Tech**: **FastAPI** (Python).
*   **Key Responsibilities**:
    *   **Orchestration**: Sends images to Ollama and parses the response.
    *   **Memory**: Uses **SQLite** to verify if a phone number has already been invited (Deduplication).
    *   **Validation**: Cleaning phone numbers (removing spaces, adding +91).

### 3. The "Face": Frontend Layer (React)
*   **Role**: Provides the "Human-in-the-Loop" interface.
*   **Tech**: **React**, **Tailwind CSS**, **Zustand**.
*   **Key Features**:
    *   **Confidence UI**: Highlights "uncertain" numbers (e.g., if the model flagged a digit) for manual review.
    *   **Live Editing**: Allows the user to fix typos before messages are sent.

### 4. The "Hands": Action Layer (PyWhatKit)
*   **Role**: Executes the physical action of sending messages.
*   **Tech**: `pywhatkit` (Python library).
*   **Operation**: It acts as a "Headless User", controlling the browser/desktop to send messages via WhatsApp Web/Desktop. It includes **throttling** (random delays) to simulate human behavior and avoid spam detection.
