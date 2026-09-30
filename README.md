# 🚀 OmniOnboard AI - Agentic Client Onboarding Workflow

An intelligent, AI-powered automated workflow that reduces client onboarding time from 3 days to under 2 minutes.

## 💼 Business Impact
- ⏱️ **Time Saved:** Reduced manual data entry and processing time by 95%.
- 🎯 **Error Reduction:** Eliminated human data-entry errors using Pydantic-validated structured AI outputs.
- 🔒 **Reliability:** Built with Human-in-the-Loop (HITL) approval and comprehensive audit logging.

## 🛠️ Tech Stack
- **Orchestration:** LangGraph (Python)
- **AI/LLM:** OpenAI GPT-4o / Anthropic Claude (with Structured Output)
- **Data Validation:** Pydantic
- **Integrations:** HubSpot API (CRM), Slack API (Approvals), SQLite (Audit/Storage)

## 🏗️ Architecture
```mermaid
graph TD
    A[📧 Incoming Email] --> B(🤖 Extractor Agent)
    B --> C{🔍 Validator Agent}
    C -->|Failed| D[❌ End: Log Error]
    C -->|Passed| E(⏸️ Approver Agent)
    E -->|Rejected| D
    E -->|Approved| F(⚡ Executor Agent)
    F --> G[💾 Save to SQLite]
    F --> H[🏢 Sync to HubSpot CRM]
    F --> I[💬 Slack Success Notification]