# LUNA: Chief Executive Multi-Agent System

> **LUNA** is an autonomous executive AI agent operating as your personal CEO to supervise dynamic, domain-specific sub-agents across **Home Automation**, **Project & Engineering Management**, and **Social Media Marketing**.

Based on the [Building AI Agents Architecture](Building%20AI%20Agents%20Architecture.pdf) specification.

---

## 🏛️ System Architecture

```text
               +------------------------+
               |     You (Founder)      |
               +-----------+------------+
                           |
        [WebSocket / Web Dashboard / Terminal CLI]
                           |
               +-----------v------------+
               |    LUNA (CEO Agent)    |
               | - Intent Decomposition |
               | - Task Delegation      |
               | - Safety Guardrails    |
               | - Executive Debriefing |
               +-----------+------------+
                           |
         +-----------------+-----------------+
         |                 |                 |
+--------v-------+ +-------v-------+ +-------v--------+
|   Smart Home   | |   Projects    | |   Marketing    |
|   Specialist   | |   & Tech      | |    & Growth    |
+--------+-------+ +-------+-------+ +-------+--------+
         |                 |                 |
  [Home Assistant]  [GitHub/Linear]    [Social APIs]
  [IoT Webhooks]    [Local Git & CI]   [Content Copy]
                           |
               +-----------v------------+
               |  Unified Persistence   |
               |  - SQLite Memory DB    |
               |  - Audit Log & History |
               +------------------------+
```

---

## 🚀 Quickstart

### 1. Requirements & Setup
- Python 3.11+ (Python 3.13 configured in `.venv/`)
- Install / update dependencies:
  ```powershell
  .\.venv\Scripts\python.exe -m pip install -r requirements.txt
  ```

### 2. Configure Environment (`.env`)
Copy `.env.example` to `.env` to configure your API credentials:
```ini
OPENAI_API_KEY=your_openai_api_key_here
LUNA_CEO_MODEL=gpt-4o
LUNA_WORKER_MODEL=gpt-4o-mini

# Service Integrations (Optional)
HOME_ASSISTANT_URL=http://homeassistant.local:8123
HOME_ASSISTANT_TOKEN=
GITHUB_ACCESS_TOKEN=
LINEAR_API_KEY=
TWITTER_BEARER_TOKEN=
```
> **Note:** LUNA has an intelligent fallback engine. Even without external API keys, all delegation workflows, local Git inspection, IoT simulation, and executive debriefs operate out-of-the-box!

---

## 🖥️ Running LUNA

### Option A: Modern Executive Web Dashboard (Recommended)
Launch the FastAPI backend and real-time streaming web dashboard:
```powershell
.\.venv\Scripts\python.exe main.py --web
```
Open **[http://127.0.0.1:8888](http://127.0.0.1:8888)** in your browser.

**Web Dashboard Features:**
- **Founder Command Center**: Issue complex natural language mandates with one-click quick action pills.
- **WebSocket Streaming**: Watch LUNA plan, decompose tasks, and stream agent executions in real-time.
- **Interactive Safety Modal**: Visually approve or abort high-risk operations (e.g., prod deployments, unlocking doors).
- **Executive CEO Debrief Card**: Highlights, operational summaries, and proactive strategic recommendations.
- **Persistent Operational Memory**: SQLite history drawer of past sessions, clickable for instant review.

---

### Option B: Interactive Terminal CLI
Prefer working strictly in your command line? Launch the terminal interface:
```powershell
.\.venv\Scripts\python.exe main.py
```

---

## 💡 Example Mandates to Try

1. **Multi-Domain Coordination**:
   > *"Dim office lights to 30%, inspect latest build status, and prep a tweet announcing our beta."*
2. **Safety Sign-Off Test (Human-in-the-Loop)**:
   > *"Deploy current main branch to production and unlock the front door."*  
   *(LUNA intercepts the dangerous keywords and demands Founder confirmation).*
3. **Engineering Telemetry**:
   > *"Check our local git branch, recent commits, and open pull requests."*
4. **Growth & Analytics**:
   > *"Give me an update on our marketing metrics and draft a post for X."*
5. **Dynamic Web Research**:
   > *"Research the top 2026 AI agent architecture trends."*

---

## 📁 Project Structure

```
LUNA/
├── .env.example                   # Environment configuration template
├── requirements.txt               # Dependencies
├── main.py                        # Entry point (CLI & Web Dashboard)
├── luna_memory.db                 # SQLite persistent memory database
├── README.md                      # System documentation
└── luna/
    ├── config.py                  # Settings & environment variables
    ├── models/
    │   └── schemas.py             # Pydantic schemas (CEODecision, SubTask, CEOFinalReport)
    ├── core/
    │   ├── engine.py              # LunaCEOEngine (Planner, Dispatcher, Synthesizer)
    │   └── state.py               # Session state & audit logs
    ├── agents/
    │   ├── base.py                # Base specialist agent
    │   ├── smart_home.py          # Smart Home Specialist (IoT / Home Assistant)
    │   ├── projects.py            # Project & Tech Lead (Local Git & GitHub CI/CD)
    │   ├── marketing.py           # Marketing & Growth Lead (Social Copy & Metrics)
    │   └── adhoc.py               # Dynamic On-Demand Specialist (Web Research)
    ├── integrations/
    │   ├── home_assistant.py      # Home Assistant REST client & device controls
    │   ├── github_client.py       # Git & GitHub REST integration
    │   ├── social_client.py       # Social media formatter & staging queue
    │   └── web_research.py        # DuckDuckGo live search & web scraper
    ├── safety/
    │   └── guardrails.py          # Founder sign-off gate for high-risk actions
    ├── memory/
    │   └── database.py            # Async SQLite memory storage
    ├── api/
    │   ├── server.py              # FastAPI server & WebSocket streaming
    │   └── static/
    │       └── index.html         # Executive Founder Web Dashboard
    └── cli/
        └── console.py             # Interactive Rich terminal UI
```

---

## 🏁 Completed Phases

- [x] **Phase 1: Core Foundation & CEO Supervisor Engine**
- [x] **Phase 2: Real Service Tool Connectors & Integrations**
- [x] **Phase 3: Executive Web Dashboard, WebSocket Streaming & Persistent Memory**
