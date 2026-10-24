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
            [Terminal CLI / WebSocket / REST]
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
  [IoT Webhooks]    [CI/CD & VPS]      [Content Copy]
```

---

## 🚀 Quickstart

### 1. Requirements & Setup
- Python 3.11+ (Python 3.13 supported)
- Virtual environment is already configured in `.venv/`

To install or update dependencies:
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. Configure Environment (`.env`)
Copy `.env.example` to `.env` and set your API keys:
```ini
OPENAI_API_KEY=your_openai_api_key_here
LUNA_CEO_MODEL=gpt-4o
LUNA_WORKER_MODEL=gpt-4o-mini

# Optional Integrations
HOME_ASSISTANT_URL=http://homeassistant.local:8123
HOME_ASSISTANT_TOKEN=
GITHUB_ACCESS_TOKEN=
LINEAR_API_KEY=
```
> **Note:** If `OPENAI_API_KEY` is not provided or is invalid, LUNA automatically operates in **Intelligent Simulation Mode**, allowing you to test full delegation, safety guardrails, and debriefing without breaking.

### 3. Launch LUNA
Run the interactive Founder CLI:
```powershell
.\.venv\Scripts\python.exe main.py
```

---

## 💡 Example Directives to Try in CLI

1. **Multi-Domain Coordination**:
   ```text
   Founder > Dim the office lights to 40%, check the latest GitHub build status, and draft a tweet announcing our launch.
   ```
2. **Safety Sign-Off Test (Human-in-the-Loop)**:
   ```text
   Founder > Deploy main branch to production and unlock the front door for the guest.
   ```
   *LUNA detects high-risk operations and prompts for Founder sign-off before executing.*
3. **Engineering Status**:
   ```text
   Founder > Inspect open issues and check if CI/CD pipelines are passing.
   ```
4. **Growth & Social**:
   ```text
   Founder > Summarize our weekly marketing reach and prepare 3 post ideas for X.
   ```

---

## 📁 Directory Structure

```
LUNA/
├── .env.example              # Environment variables template
├── requirements.txt          # Dependencies
├── main.py                   # System entry point
├── README.md                 # Documentation
└── luna/
    ├── config.py             # Settings & environment variables
    ├── models/
    │   └── schemas.py        # Pydantic schemas (CEODecision, SubTask, CEOFinalReport)
    ├── core/
    │   ├── engine.py         # LunaCEOEngine (Planner, Dispatcher, Synthesizer)
    │   └── state.py          # State tracking & audit logs
    ├── agents/
    │   ├── base.py           # Base specialist agent
    │   ├── smart_home.py     # Smart Home specialist
    │   ├── projects.py       # Projects & Dev specialist
    │   ├── marketing.py      # Marketing & Growth specialist
    │   └── adhoc.py          # Dynamic on-demand specialist
    ├── safety/
    │   └── guardrails.py     # Founder confirmation & RBAC security gate
    └── cli/
        └── console.py        # Interactive rich terminal UI
```

---

## 🛣️ Roadmap

- [x] **Phase 1: Core Engine & Sub-Agent Coordinator (Completed)**
  - Hierarchical CEO-worker architecture
  - Structured output schemas with Pydantic
  - Safety guardrails for high-risk operations
  - Interactive terminal CLI
- [ ] **Phase 2: Live Service Connectors**
  - Home Assistant REST / WebSocket client
  - PyGithub & Linear GraphQL client
  - Social media APIs (X / Meta / YouTube)
- [ ] **Phase 3: Web Dashboard & Semantic Memory**
  - Next.js founder dashboard with real-time streaming updates
  - Vector DB (ChromaDB / Qdrant) for long-term memory
