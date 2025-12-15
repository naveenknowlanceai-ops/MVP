PM AGENT ARCHITECTURE
graph TD
    User[Human Director] --> UI[Web Interface (HTML/CSS/JS)]

    subgraph "Frontend Layer (Control Plane)"
        UI --> Editor[Collaborative Editor]
        UI --> Chat[Strategy Chat]
        UI --> Controls[Override/Approve Buttons]
    end

    UI -- WebSocket/JSON --> API[Backend API (FastAPI)]

    subgraph "Orchestration Layer (The Brain)"
        API --> Manager[Manager Agent (Supervisor)]
        Manager --> State[Shared State (SQLite/Redis)]

    Manager -- Delegates to --> Researcher[Researcher Agent]
        Manager -- Delegates to --> Writer[Spec Writer Agent]
        Manager -- Delegates to --> Scrum[Scrum Master Agent]
    end

    subgraph "Tool Layer (MCP Servers)"
        Researcher --> WebSearch[Google Search API]
        Writer --> Docs[Notion/Confluence API]
        Scrum --> Tickets[Jira/Linear API]
    end

    subgraph "Compute Infrastructure (Google Cloud)"
        Manager -- Reasoning --> VertexAI[Gemini 1.5 Pro]
        Researcher -- Embeddings --> VertexEmbed[Gecko/Text-Embedding-004]
    end
