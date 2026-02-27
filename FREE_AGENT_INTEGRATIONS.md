# 100% Free Integration Methods for WhatsApp & Email Agents

This guide documents the architecture, tools, and algorithms required to build WhatsApp and Email AI agents with a strictly $0 budget.

---

## 🟢 1. The 100% Free WhatsApp Method: Unofficial Web Wrappers

Instead of using the expensive official Meta Cloud API, you use libraries that reverse-engineer the WhatsApp Web protocol. You link your agent to a WhatsApp account by scanning a QR code, exactly as you would when logging into WhatsApp Web on a browser.

### The Best Tools
*   **WAHA (WhatsApp HTTP API)** or **Evolution API**: Open-source servers that run locally. They spin up a headless browser, provide a QR code to scan from your phone, and instantly expose a free local REST API (e.g., `POST http://localhost:3000/sendText`) that you can call from your Python/FastAPI backend.
*   **whatsapp-web.js / Baileys**: If you are writing Node.js microservices instead of Python.

### Pros
*   **Absolutely Free:** $0 cost forever. No per-message conversation fees to Meta or Twilio.
*   **No Approvals:** You don't need a registered business, and you don't need Meta to approve message templates. The agent can send unrestricted free-form text.
*   **Access to Groups:** Unofficial wrappers can easily read and reply to WhatsApp Group messages.

### Cons & Risks (Important!)
*   **Massive Ban Risk:** Meta actively hunts for automated bots on personal accounts. If your bot sends 500 messages a minute, the phone number *will* get permanently banned. **Always use a secondary/burner phone number for development, never your personal number.**
*   **Local Hosting Resources:** Requires keeping a headless browser running in the background (Puppeteer), which consumes RAM locally or on your VPS.

---

## ✉️ 2. The 100% Free Email Method: Standard SMTP (Gmail)

Instead of using modern transactional email services like Resend or Sendgrid (which require owning a domain and a credit card), you use a standard Gmail account to send and receive emails.

### The Best Tool
*   **Python `smtplib` + `imaplib`**: Built right into the standard Python library.
*   **Gmail App Password**: Go to Google Account -> Security -> 2-Step Verification -> App Passwords. Generate a 16-character password. Your FastAPI server can now authenticate and send emails acting as that standard Gmail account.

### Pros
*   **Zero Setup Time:** No DNS configuration, DKIM, or domain purchasing necessary.
*   **100% Free:** No credit card required.

### Cons & Risks
*   **Strict Rate Limits:** Gmail limits you to sending approximately 500 emails per rolling 24-hour period. If your agent goes viral, it will hit a hard wall.
*   **Deliverability Issues:** If you send too many automated-looking emails, Google's spam filters might temporarily lock the sending account.

---

## 🧠 System Architecture & Algorithms for a $0 Setup

When using free, unofficial tools, your underlying architecture needs to be significantly smarter to protect your accounts from being banned or rate-limited.

### 1. Aggressive Humanizing (Jitter-Delay Algorithm)
Because Meta bans unofficial bots that reply instantly, you *cannot* reply to a WhatsApp message in 0.1 seconds.
*   **Implementation:** When the LLM generates a text response, calculate a deliberate delay: `delay = (word_count / 4) + random_jitter(2, 5)`. Sleep for that many seconds before sending the message so it looks like a human typing. 
*   *Bonus:* Trigger a "typing..." presence event if the wrapper API supports it during the delay.

### 2. Hard Rate-Limiting (Token Buckets)
Since free tools have hard daily limits (like Gmail's 500/day limit), you MUST implement a Token Bucket algorithm in your backend.
*   **Implementation:** Set a strict limit of 10 messages per user per day. Deduct a token on every received message. If tokens hit 0, silently drop the message or queue it for the next day. This prevents one user from exhausting your free tier.

### 3. Local Webhook Queues (Debouncing)
Scanning a WhatsApp Web QR code implies a persistent websocket connection. As messages stream in, you cannot process them synchronously on the main thread.
*   **Implementation:** Push incoming messages immediately into a local queue (like Redis or Python's `asyncio.Queue`). 
*   **Debouncing:** Group rapid sequential messages from the same user within a 5-second window into a single payload before sending it to the LLM agent.

### 4. Idempotency Keys
*   **Implementation:** Cache the `message_id` of every incoming message. If the web wrapper reconnects or double-fires an event, check the cache first to ensure the agent doesn't reply to the exact same message twice.
