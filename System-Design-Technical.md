# SYSTEM DESIGN & TECHNICAL ARCHITECTURE DOCUMENT
## Software Galaxy - AI Team Platform MVP

**Document Type:** Detailed System Design, UML Diagrams, Microservices Architecture, Technical Specifications  
**Status:** Ready for Development  
**Version:** 1.0  
**Date:** December 2025  
**Prepared by:** Senior System Analyst / Technical Architect  
**Audience:** Engineering Team, Tech Leads, Solution Architects, DevOps Engineers

---

## TABLE OF CONTENTS

1. [System Design Overview](#system-design-overview)
2. [Microservices Decomposition](#microservices-decomposition)
3. [UML Diagrams & Domain Models](#uml-diagrams--domain-models)
4. [API Design Specifications](#api-design-specifications)
5. [Data Flow Diagrams](#data-flow-diagrams)
6. [Component Interaction Patterns](#component-interaction-patterns)
7. [Database Schema Design](#database-schema-design)
8. [Message Queue & Event Architecture](#message-queue--event-architecture)
9. [Integration Patterns](#integration-patterns)
10. [System Constraints & Trade-offs](#system-constraints--trade-offs)
11. [Technical Debt & Mitigation](#technical-debt--mitigation)
12. [Implementation Roadmap](#implementation-roadmap)

---

## SYSTEM DESIGN OVERVIEW

### System Context Diagram (C4 Level 1)

```
┌─────────────────────────────────────────────────────────────────────┐
│                          External Systems                            │
│                                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │  GitHub  │  │   Jira   │  │  Figma   │  │  Docker  │  │ OpenAI ││
│  │  (Code)  │  │ (Tickets)│  │ (Design) │  │ (Infra)  │  │ (LLM)  ││
│  └─────┬────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───┬────┘│
│        │            │             │             │            │      │
└────────┼────────────┼─────────────┼─────────────┼────────────┼──────┘
         │            │             │             │            │
         │  HTTPS/OAuth/API Calls   │             │            │
         │                          │             │            │
┌────────▼──────────────────────────▼─────────────▼────────────▼──────┐
│                    Software Galaxy Platform                          │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Desktop App (Electron)        Web Dashboard (Next.js)       │   │
│  │  ┌────────────────────────┐  ┌──────────────────────────┐   │   │
│  │  │ Agent Control UI       │  │ Sprint Board             │   │   │
│  │  │ MCP Server Hub         │  │ Team Dashboard           │   │   │
│  │  │ Local Agents           │  │ Analytics                │   │   │
│  │  │ SQLite Cache           │  │ Settings                 │   │   │
│  │  └────────────────────────┘  └──────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              ▲                                        │
│                              │                                        │
│  ┌───────────────────────────▼────────────────────────────────────┐  │
│  │              Cloud-Based Control Plane (SaaS)                 │  │
│  │                                                                 │  │
│  │  ┌──────────────────────────────────────────────────────────┐ │  │
│  │  │             Microservices Layer                         │ │  │
│  │  │                                                           │ │  │
│  │  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌──────────┐│ │  │
│  │  │  │  User &   │ │ Project & │ │  Agent    │ │  Tool    ││ │  │
│  │  │  │  Team     │ │ Sprint    │ │ Control   │ │Registry  ││ │  │
│  │  │  └───────────┘ └───────────┘ └───────────┘ └──────────┘│ │  │
│  │  │                                                           │ │  │
│  │  │  ┌───────────────────────────────────────────────────┐  │ │  │
│  │  │  │         Message Queue (Celery + Redis)           │  │ │  │
│  │  │  └───────────────────────────────────────────────────┘  │ │  │
│  │  └──────────────────────────────────────────────────────────┘ │  │
│  │                                                                 │  │
│  │  ┌──────────────────────────────────────────────────────────┐ │  │
│  │  │        Data Layer (PostgreSQL, Redis, S3)              │ │  │
│  │  └──────────────────────────────────────────────────────────┘ │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
         ▲
         │
    ┌────▼────┐
    │  Users  │
    │ (Teams) │
    └─────────┘
```

### System Architecture Layers (C4 Level 2)

```
┌─────────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                              │
│  ┌──────────────────────────────┐  ┌─────────────────────────────┐ │
│  │  Desktop Client (Electron)   │  │  Web Client (Next.js)       │ │
│  │  - UI Components (React)     │  │  - UI Components (React)    │ │
│  │  - State Management (Zustand)│  │  - Server State (TanStack)  │ │
│  │  - Local Storage (SQLite)    │  │  - Browser Cache            │ │
│  │  - System Integration        │  │  - OAuth Flows              │ │
│  └──────────────────────────────┘  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                          ▲
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
   REST/JSON        WebSocket         IPC/REST
        │                 │                 │
┌─────────────────────────────────────────────────────────────────────┐
│                  API GATEWAY & ORCHESTRATION                         │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  FastAPI Server (8-10 workers)                              │   │
│  │  - Request routing & load balancing                         │   │
│  │  - Authentication (OAuth2, JWT)                             │   │
│  │  - Rate limiting & CORS                                     │   │
│  │  - Request/Response validation (Pydantic)                   │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                          ▲
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐
│   User &    │  │  Project &  │  │   Agent     │  │   Tool       │
│   Team      │  │   Sprint    │  │  Control    │  │  Registry    │
│ Management  │  │ Management  │  │ Service     │  │  Service     │
└─────────────┘  └─────────────┘  └─────────────┘  └──────────────┘
┌──────────────────────────────────────────────────────────────────────┐
│                  MICROSERVICES LAYER                                  │
│                                                                        │
│  ┌────────────────┐  ┌──────────────────┐  ┌──────────────────────┐ │
│  │ Business Logic │  │ Agent             │  │ External Integrations│ │
│  │ (CRUD, rules)  │  │ Orchestration     │  │ (MCP Hub, Webhooks) │ │
│  │                │  │ (LangGraph)       │  │                      │ │
│  └────────────────┘  └──────────────────┘  └──────────────────────┘ │
│                                                                        │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  Message Queue Layer (Event-Driven)                             │ │
│  │  - Celery Task Queue                                             │ │
│  │  - Redis Pub/Sub (Real-time updates)                            │ │
│  │  - Event Broadcasting                                            │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
                          ▲
                          │
┌─────────────────────────────────────────────────────────────────────┐
│                   DATA & PERSISTENCE LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ ┌────────────┐│
│  │ PostgreSQL   │  │ Redis        │  │ ChromaDB     │ │ S3 / Cloud ││
│  │ (Primary DB) │  │ (Cache/Queue)│  │ (Vectors)    │ │ Storage    ││
│  └──────────────┘  └──────────────┘  └──────────────┘ └────────────┘│
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ Local Storage (Electron Only)                                │   │
│  │ ┌────────────────┐  ┌──────────────────┐                    │   │
│  │ │ SQLite         │  │ ChromaDB (local) │                    │   │
│  │ │ (Offline Cache)│  │ (Embeddings)     │                    │   │
│  │ └────────────────┘  └──────────────────┘                    │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## MICROSERVICES DECOMPOSITION

### Microservice Inventory

#### 1. User & Team Management Service

**Responsibilities:**
```
- User authentication & authorization
- User profile management
- Team creation & management
- Team member roles & permissions
- Settings & preferences
- API key management
- Session management
```

**Key Entities:**
```
- User (id, email, name, avatar, oauth_provider, settings)
- Team (id, name, owner_id, workspace_slug, settings)
- TeamMember (id, team_id, user_id, role, joined_at)
- UserRole (owner, admin, member, viewer)
- Permission (resource_type, action, role_id)
```

**API Endpoints:**
```
POST   /api/auth/register           - Register new user
POST   /api/auth/login              - OAuth2 callback
POST   /api/auth/refresh            - Refresh JWT token
POST   /api/auth/logout             - Logout (revoke token)
GET    /api/users/{id}              - Get user profile
PUT    /api/users/{id}              - Update user profile
GET    /api/teams                   - List teams for user
POST   /api/teams                   - Create new team
GET    /api/teams/{id}              - Get team details
PUT    /api/teams/{id}              - Update team
POST   /api/teams/{id}/members      - Add team member
DELETE /api/teams/{id}/members/{uid}- Remove team member
PUT    /api/teams/{id}/members/{uid}- Update member role
GET    /api/teams/{id}/permissions  - Get team permissions
```

**Database Tables:**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    avatar_url TEXT,
    oauth_provider VARCHAR(50),
    oauth_id VARCHAR(255),
    password_hash VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE teams (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    owner_id UUID REFERENCES users(id),
    workspace_slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    settings JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE team_members (
    id UUID PRIMARY KEY,
    team_id UUID REFERENCES teams(id),
    user_id UUID REFERENCES users(id),
    role VARCHAR(50) NOT NULL,
    joined_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(team_id, user_id)
);
```

**Async Events Produced:**
```
- user.registered (new user signup)
- user.login (user authenticated)
- team.created (new team)
- team_member.added (user joined team)
- team_member.removed (user left team)
```

---

#### 2. Project & Sprint Management Service

**Responsibilities:**
```
- Project CRUD operations
- Sprint planning & management
- User story backlog management
- Task assignment & tracking
- Burndown chart calculations
- Velocity tracking
- Sprint status transitions
```

**Key Entities:**
```
- Project (id, team_id, name, description, tech_stack, status)
- Sprint (id, project_id, name, start_date, end_date, status, velocity)
- UserStory (id, project_id, sprint_id, title, description, priority, story_points)
- Task (id, user_story_id, title, status, assigned_agent, assigned_user)
- SprintMetrics (id, sprint_id, velocity, completed_points, remaining_points)
```

**API Endpoints:**
```
POST   /api/projects                - Create project
GET    /api/projects                - List projects
GET    /api/projects/{id}           - Get project details
PUT    /api/projects/{id}           - Update project
DELETE /api/projects/{id}           - Delete project
POST   /api/projects/{id}/sprints   - Create sprint
GET    /api/projects/{id}/sprints   - List sprints
GET    /api/sprints/{id}            - Get sprint details
PUT    /api/sprints/{id}            - Update sprint
POST   /api/sprints/{id}/start      - Start sprint
POST   /api/sprints/{id}/complete   - Complete sprint
GET    /api/sprints/{id}/board      - Get sprint board (Kanban)
POST   /api/user-stories            - Create user story
GET    /api/user-stories            - List user stories
PUT    /api/user-stories/{id}       - Update user story
DELETE /api/user-stories/{id}       - Delete user story
POST   /api/tasks                   - Create task
PUT    /api/tasks/{id}              - Update task
POST   /api/tasks/{id}/assign       - Assign task to agent
```

**Database Tables:**
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    team_id UUID REFERENCES teams(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    tech_stack JSONB,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE sprints (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    name VARCHAR(255) NOT NULL,
    start_date DATE,
    end_date DATE,
    status VARCHAR(50),
    velocity INT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_stories (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    sprint_id UUID REFERENCES sprints(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    acceptance_criteria JSONB,
    priority INT,
    story_points INT,
    status VARCHAR(50),
    assigned_to UUID,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    user_story_id UUID REFERENCES user_stories(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    assigned_agent VARCHAR(50),
    assigned_user_id UUID REFERENCES users(id),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Async Events Produced:**
```
- project.created
- sprint.created
- sprint.started
- sprint.completed
- user_story.created
- user_story.assigned
- task.created
- task.status_changed
```

---

#### 3. Agent Control Service

**Responsibilities:**
```
- Agent lifecycle management (start, stop, pause, resume)
- Agent configuration & customization
- Execution status monitoring
- Execution history & logs
- Error handling & retry logic
- Manual override management
- Agent performance metrics
```

**Key Entities:**
```
- Agent (id, team_id, type, model, status, config)
- AgentExecution (id, task_id, agent_type, status, input, output, logs)
- AgentLog (id, execution_id, level, message, timestamp)
- AgentMetric (id, agent_id, metric_type, value, recorded_at)
```

**API Endpoints:**
```
POST   /api/agents/{type}/start     - Start agent
POST   /api/agents/{type}/stop      - Stop agent
GET    /api/agents/{type}/status    - Get agent status
PUT    /api/agents/{type}/config    - Update agent config
GET    /api/agents/{type}/logs      - Get agent logs
POST   /api/executions              - Create execution
GET    /api/executions/{id}         - Get execution details
GET    /api/executions/{id}/logs    - Get execution logs
POST   /api/executions/{id}/override- Override execution
GET    /api/agents/metrics          - Get agent metrics
```

**Agent Types:**
```
1. PM Agent (Product Manager)
   - Generates user stories from requirements
   - Prioritizes backlog
   - Estimates story points

2. Architect Agent
   - Designs system architecture
   - Reviews code for design patterns
   - Suggests optimizations

3. Dev Agent
   - Generates production code
   - Implements features
   - Refactors existing code

4. QA Agent
   - Generates test cases
   - Runs tests
   - Reports bugs

5. DevOps Agent
   - Deploys code
   - Manages infrastructure
   - Monitors deployments
```

**Database Tables:**
```sql
CREATE TABLE agent_executions (
    id UUID PRIMARY KEY,
    task_id UUID REFERENCES tasks(id),
    agent_type VARCHAR(50) NOT NULL,
    agent_model VARCHAR(100),
    status VARCHAR(50),
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    execution_time_ms INT,
    tokens_used INT,
    cost_estimate DECIMAL,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE TABLE agent_logs (
    id UUID PRIMARY KEY,
    execution_id UUID REFERENCES agent_executions(id),
    level VARCHAR(50),
    message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Async Events Produced:**
```
- agent.started
- agent.stopped
- execution.started
- execution.completed
- execution.failed
- execution.overridden
```

---

#### 4. Tool Registry Service

**Responsibilities:**
```
- Integration credential management
- MCP server lifecycle management
- OAuth flow handling
- Tool availability checking
- Tool usage logging & auditing
- Rate limiting per tool
- Credential encryption & decryption
```

**Key Entities:**
```
- Integration (id, team_id, tool_name, account_name, is_connected)
- Credential (id, integration_id, encrypted_token, scopes, expires_at)
- ToolUsage (id, integration_id, user_id/agent_id, action, timestamp)
```

**API Endpoints:**
```
POST   /api/integrations            - Connect new integration
GET    /api/integrations            - List integrations
GET    /api/integrations/{id}       - Get integration details
PUT    /api/integrations/{id}       - Update integration
DELETE /api/integrations/{id}       - Disconnect integration
POST   /api/integrations/{id}/oauth/callback - Handle OAuth
GET    /api/integrations/status     - Check tool availability
GET    /api/integrations/{id}/usage - Get tool usage logs
```

**Supported Tools (MVP):**
```
1. GitHub
   - Credentials: Personal access token or OAuth
   - Scopes: repo, read:user, write:org
   - Actions: clone, branch, push, PR, merge, comment

2. Jira
   - Credentials: API token
   - Scopes: project_admin, user_admin
   - Actions: create issue, update, comment, link, transition

3. Figma
   - Credentials: API token
   - Scopes: files:read, webhooks:write
   - Actions: export, get specs, upload

4. Docker
   - Credentials: Docker Hub token
   - Scopes: repo:read, repo:write
   - Actions: build, push, pull

5. Slack
   - Credentials: Bot token
   - Scopes: chat:write, users:read
   - Actions: send message, create thread, post

6. OpenAPI (Generic)
   - Credentials: API key or OAuth
   - Actions: any REST endpoint (configurable)
```

**Database Tables:**
```sql
CREATE TABLE integrations (
    id UUID PRIMARY KEY,
    team_id UUID REFERENCES teams(id),
    tool_name VARCHAR(100) NOT NULL,
    account_name VARCHAR(255),
    is_connected BOOLEAN DEFAULT false,
    credential_id UUID,
    scopes JSONB,
    last_verified TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tool_usage (
    id UUID PRIMARY KEY,
    integration_id UUID REFERENCES integrations(id),
    actor_type VARCHAR(50),
    actor_id VARCHAR(255),
    action VARCHAR(100),
    request_data JSONB,
    response_data JSONB,
    status_code INT,
    error_message TEXT,
    execution_time_ms INT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Async Events Produced:**
```
- integration.connected
- integration.disconnected
- tool.unavailable
- tool.rate_limited
- credential.expired
```

---

#### 5. Notification & WebSocket Service

**Responsibilities:**
```
- Real-time WebSocket connections
- Event-driven notifications
- Broadcast management
- Message queuing
- Rate limiting per user
- Connection lifecycle management
```

**WebSocket Events:**
```
Client → Server:
- subscribe (channel, topic)
- unsubscribe (channel, topic)
- ping (keep-alive)

Server → Client:
- sprint_board:updated (task status changed)
- agent:status_changed (agent started, stopped)
- notification (user notification)
- error (error message)
```

**Redis Pub/Sub Channels:**
```
sprint:{sprint_id}:updates         - Sprint board updates
agent:{agent_id}:status            - Agent status changes
team:{team_id}:notifications       - Team notifications
user:{user_id}:notifications       - User notifications
```

---

### Microservice Dependencies Map

```
┌────────────────────────────────────────────────────────────┐
│                                                              │
│  User & Team                                                │
│      │                                                       │
│      └──► Project & Sprint ◄─── Agent Control              │
│             │                     │                          │
│             └─────────────────────┴──► Tool Registry        │
│                                        │                     │
│                                        └──► Notification &   │
│                                             WebSocket        │
│                                                               │
└────────────────────────────────────────────────────────────┘

Dependency Rules:
- Tool Registry ← depends on nothing (foundational)
- User & Team ← depends on nothing (foundational)
- Project & Sprint ← depends on User & Team
- Agent Control ← depends on Project & Sprint, Tool Registry
- Notification & WebSocket ← depends on all others
```

---

## UML DIAGRAMS & DOMAIN MODELS

### Class Diagram (User & Team Domain)

```
┌─────────────────────────────┐
│         User                │
├─────────────────────────────┤
│ - id: UUID                  │
│ - email: String             │
│ - name: String              │
│ - avatar_url: String        │
│ - oauth_provider: String    │
│ - created_at: DateTime      │
├─────────────────────────────┤
│ + register()                │
│ + login()                   │
│ + updateProfile()           │
│ + getTeams(): Team[]        │
└──────────────┬──────────────┘
               │
               │ owns (1:N)
               │
┌──────────────▼──────────────┐
│        Team                 │
├─────────────────────────────┤
│ - id: UUID                  │
│ - name: String              │
│ - owner_id: UUID            │
│ - workspace_slug: String    │
│ - settings: JSONB           │
├─────────────────────────────┤
│ + createProject()           │
│ + addMember()               │
│ + getMembers(): User[]      │
│ + removeProject()           │
└──────────────┬──────────────┘
               │
               │ manages (1:N)
               │
┌──────────────▼──────────────┐
│     TeamMember              │
├─────────────────────────────┤
│ - id: UUID                  │
│ - team_id: UUID             │
│ - user_id: UUID             │
│ - role: String              │
├─────────────────────────────┤
│ + hasPermission(perm)       │
│ + updateRole()              │
└─────────────────────────────┘
```

### Class Diagram (Project & Sprint Domain)

```
┌─────────────────────────────┐
│      Project                │
├─────────────────────────────┤
│ - id: UUID                  │
│ - team_id: UUID             │
│ - name: String              │
│ - description: String       │
│ - tech_stack: JSONB         │
│ - status: String            │
├─────────────────────────────┤
│ + createSprint()            │
│ + getSprints(): Sprint[]    │
│ + getBacklog(): Story[]     │
│ + getVelocity(): Int        │
└──────────────┬──────────────┘
               │
               │ contains (1:N)
               │
┌──────────────▼──────────────┐
│       Sprint                │
├─────────────────────────────┤
│ - id: UUID                  │
│ - project_id: UUID          │
│ - name: String              │
│ - start_date: Date          │
│ - end_date: Date            │
│ - status: String            │
│ - velocity: Int             │
├─────────────────────────────┤
│ + addStory()                │
│ + start()                   │
│ + complete()                │
│ + getBurndownData()         │
└──────────────┬──────────────┘
               │
               │ contains (1:N)
               │
┌──────────────▼──────────────────────────┐
│         UserStory                       │
├─────────────────────────────────────────┤
│ - id: UUID                              │
│ - sprint_id: UUID                       │
│ - title: String                         │
│ - description: String                   │
│ - acceptance_criteria: String[]         │
│ - priority: Int (1-10)                  │
│ - story_points: Int                     │
│ - status: String                        │
│ - assigned_to: UUID/AgentType           │
├─────────────────────────────────────────┤
│ + createTasks()                         │
│ + assignToAgent(agent_type)             │
│ + markComplete()                        │
│ + getTasks(): Task[]                    │
└──────────────┬──────────────────────────┘
               │
               │ decomposes to (1:N)
               │
┌──────────────▼──────────────┐
│        Task                 │
├─────────────────────────────┤
│ - id: UUID                  │
│ - story_id: UUID            │
│ - title: String             │
│ - assigned_agent: String    │
│ - assigned_user_id: UUID    │
│ - status: String            │
├─────────────────────────────┤
│ + assignAgent()             │
│ + execute()                 │
│ + override()                │
│ + complete()                │
└──────────────┬──────────────┘
               │
               │ triggers (1:N)
               │
┌──────────────▼──────────────────────────┐
│     AgentExecution                      │
├─────────────────────────────────────────┤
│ - id: UUID                              │
│ - task_id: UUID                         │
│ - agent_type: String                    │
│ - agent_model: String                   │
│ - status: String                        │
│ - input_data: JSONB                     │
│ - output_data: JSONB                    │
│ - execution_time_ms: Int                │
│ - tokens_used: Int                      │
│ - cost_estimate: Decimal                │
├─────────────────────────────────────────┤
│ + start()                               │
│ + complete()                            │
│ + fail()                                │
│ + retry()                               │
│ + getLogs(): AgentLog[]                 │
└─────────────────────────────────────────┘
```

### Class Diagram (Agent Domain)

```
┌──────────────────────────────────┐
│      Agent (Abstract)            │
├──────────────────────────────────┤
│ # id: UUID                       │
│ # team_id: UUID                  │
│ # agent_type: String             │
│ # llm_model: String              │
│ # config: JSONB                  │
│ # status: String                 │
├──────────────────────────────────┤
│ + start()                        │
│ + stop()                         │
│ + execute(context)               │
│ + getMetrics()                   │
│ + configure(config)              │
└──────────────┬───────────────────┘
               │
        ┌──────┴──────┬───────────┬─────────┬─────────┐
        │             │           │         │         │
┌───────▼─┐  ┌───────▼──┐  ┌────▼──┐  ┌──▼────┐  ┌─▼──────┐
│   PM    │  │Architect │  │ Dev   │  │ QA    │  │DevOps  │
│ Agent   │  │ Agent    │  │Agent  │  │Agent  │  │Agent   │
├─────────┤  ├──────────┤  ├───────┤  ├───────┤  ├────────┤
│Generate │  │Design    │  │Write  │  │ Test  │  │Deploy  │
│Stories  │  │System    │  │Code   │  │Code   │  │Infra   │
│Priorit. │  │Review    │  │Refact │  │Debug  │  │Monitor │
└─────────┘  └──────────┘  └───────┘  └───────┘  └────────┘

All inherit from Agent base class
```

### State Diagram (Task Lifecycle)

```
┌─────────────────┐
│   Backlog       │
│  (Unstarted)    │
└────────┬────────┘
         │ (backlog to sprint)
         │
    ┌────▼──────────────┐
    │  To Do             │
    │  (Assigned)        │
    └────┬──────────────┘
         │ (user starts)
         │
    ┌────▼──────────────┐
    │  In Progress       │
    │  (Executing)       │
    └────┬──────────────┘
         │
      ┌──┴──────────────────┐
      │                     │
      ▼ (override)          ▼ (complete)
   ┌────────────┐        ┌────────────────┐
   │ Overridden │        │ In Review      │
   │ (Paused)   │        │ (QA/Review)    │
   └────────────┘        └────┬───────────┘
                              │
                      ┌───────┴──────────┐
                      │                  │
                      ▼ (approved)       ▼ (rejected)
                   ┌──────────┐       ┌─────────────┐
                   │  Done    │       │  Failed     │
                   │(Closed)  │       │ (Retry)     │
                   └──────────┘       └─────────────┘
```

### Sequence Diagram (Agent Execution Flow)

```
User            UI          API          Queue        Agent        MCP Hub
 │              │            │            │            │             │
 │─ Create Task─>│            │            │            │             │
 │              │─ POST /tasks─>          │            │             │
 │              │ <─ Task ID─ │            │            │             │
 │              │            │            │            │             │
 │ Assign to    │            │            │            │             │
 │ Dev Agent    │            │            │            │             │
 │─────────────>│            │            │            │             │
 │              │─ POST /assign─>         │            │             │
 │              │            │            │            │             │
 │              │            │ Create Execution        │             │
 │              │            │─ emit event─────────>│  │             │
 │              │            │            │            │             │
 │              │            │ Queue job  │            │             │
 │              │            │────────────────────────>│             │
 │              │            │            │            │             │
 │              │ WebSocket broadcast (agent started)  │             │
 │              │<───────────────────────────────────│ │             │
 │<─ Status─────│            │            │            │             │
 │              │            │            │Agent running│             │
 │              │            │            │            │─ Get Creds─>│
 │              │            │            │            │<─ Token────│
 │              │            │            │            │             │
 │              │            │            │            │─ Call API──>│
 │              │            │            │            │             │
 │              │            │            │            │<─ Result───│
 │              │            │            │ Complete   │             │
 │              │            │<─ emit event──────────│ │             │
 │              │<─ broadcast─────────────────────────│ │             │
 │<─ Task Done──│            │            │            │             │
 │              │            │            │            │             │
```

### Entity Relationship Diagram (Database)

```
┌─────────────────┐
│     users       │
├─────────────────┤
│ id (PK)         │
│ email           │
│ name            │
│ avatar_url      │
│ created_at      │
└────────┬────────┘
         │
         │ 1:N (owns)
         │
┌────────▼──────────────┐
│     teams             │
├──────────────────────┤
│ id (PK)              │
│ name                 │
│ owner_id (FK:users)  │
│ workspace_slug       │
│ created_at           │
└────────┬─────────────┘
         │
    ┌────┴────────────┐
    │                 │
    │ 1:N             │ 1:N
    │                 │
┌───▼──────────┐   ┌─▼──────────────┐
│team_members  │   │   projects     │
├──────────────┤   ├────────────────┤
│ id (PK)      │   │ id (PK)        │
│ team_id (FK) │   │ team_id (FK)   │
│ user_id (FK) │   │ name           │
│ role         │   │ description    │
└──────────────┘   │ tech_stack     │
                   │ status         │
                   │ created_at     │
                   └────────┬───────┘
                            │
                            │ 1:N
                            │
                   ┌────────▼───────┐
                   │    sprints     │
                   ├────────────────┤
                   │ id (PK)        │
                   │ project_id (FK)│
                   │ name           │
                   │ start_date     │
                   │ end_date       │
                   │ status         │
                   │ velocity       │
                   └────────┬───────┘
                            │
                            │ 1:N
                            │
                   ┌────────▼──────────┐
                   │  user_stories    │
                   ├──────────────────┤
                   │ id (PK)          │
                   │ sprint_id (FK)   │
                   │ title            │
                   │ description      │
                   │ acceptance_crit. │
                   │ priority         │
                   │ story_points     │
                   │ status           │
                   │ assigned_to      │
                   └────────┬─────────┘
                            │
                            │ 1:N
                            │
                   ┌────────▼──────────┐
                   │     tasks        │
                   ├──────────────────┤
                   │ id (PK)          │
                   │ story_id (FK)    │
                   │ title            │
                   │ assigned_agent   │
                   │ assigned_user_id │
                   │ status           │
                   └────────┬─────────┘
                            │
                            │ 1:N
                            │
                   ┌────────▼──────────────┐
                   │agent_executions      │
                   ├──────────────────────┤
                   │ id (PK)              │
                   │ task_id (FK)         │
                   │ agent_type           │
                   │ agent_model          │
                   │ status               │
                   │ input_data           │
                   │ output_data          │
                   │ execution_time_ms    │
                   │ tokens_used          │
                   │ cost_estimate        │
                   └──────────────────────┘
```

---

## API DESIGN SPECIFICATIONS

### RESTful API Design Patterns

#### HTTP Methods & Status Codes

```
Create (POST)
- 201 Created: Resource successfully created
- 400 Bad Request: Invalid input
- 401 Unauthorized: Authentication required
- 403 Forbidden: Permission denied
- 409 Conflict: Resource already exists

Read (GET)
- 200 OK: Resource retrieved
- 304 Not Modified: Cached data valid (ETags)
- 404 Not Found: Resource not found

Update (PUT/PATCH)
- 200 OK: Resource updated
- 204 No Content: Update successful (no response body)
- 400 Bad Request: Invalid input
- 404 Not Found: Resource not found
- 409 Conflict: Concurrent modification

Delete (DELETE)
- 204 No Content: Resource deleted
- 404 Not Found: Resource not found
- 409 Conflict: Resource has dependencies
```

#### Request/Response Format

```json
// Request (Create Project)
POST /api/projects
Content-Type: application/json
Authorization: Bearer {jwt_token}

{
  "name": "E-commerce Platform",
  "description": "Build a scalable e-commerce platform",
  "tech_stack": {
    "language": "Python",
    "framework": "FastAPI",
    "database": "PostgreSQL",
    "frontend": "Next.js"
  }
}

// Response
HTTP/1.1 201 Created
Content-Type: application/json
Location: /api/projects/550e8400-e29b-41d4-a716-446655440000

{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "team_id": "550e8400-e29b-41d4-a716-446655440001",
  "name": "E-commerce Platform",
  "description": "Build a scalable e-commerce platform",
  "tech_stack": {
    "language": "Python",
    "framework": "FastAPI",
    "database": "PostgreSQL",
    "frontend": "Next.js"
  },
  "status": "planning",
  "created_at": "2025-12-05T00:00:00Z",
  "updated_at": "2025-12-05T00:00:00Z"
}

// Error Response
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": "validation_error",
  "message": "Project name is required",
  "details": {
    "name": ["Project name must be at least 3 characters"]
  }
}
```

#### Pagination

```json
// Request with pagination
GET /api/user-stories?page=2&page_size=20&sort=-priority&filter=status:in_progress

// Response
{
  "data": [
    { "id": "...", "title": "..." },
    ...
  ],
  "pagination": {
    "page": 2,
    "page_size": 20,
    "total": 150,
    "total_pages": 8,
    "has_next": true,
    "has_prev": true
  },
  "links": {
    "self": "/api/user-stories?page=2&page_size=20",
    "first": "/api/user-stories?page=1&page_size=20",
    "last": "/api/user-stories?page=8&page_size=20",
    "next": "/api/user-stories?page=3&page_size=20",
    "prev": "/api/user-stories?page=1&page_size=20"
  }
}
```

#### API Versioning

```
Endpoint: /api/v1/projects
Header: Accept: application/vnd.software-galaxy-v1+json
Query: /api/projects?api_version=1

Strategy: URL-based versioning (v1, v2, v3) for stable API
Deprecation: Header X-Deprecation-Warning
Migration Path: Support 2+ API versions simultaneously
```

---

### Core API Endpoints Reference

#### User & Team APIs

```yaml
endpoints:
  # Authentication
  POST /api/auth/register:
    summary: Register new user
    request:
      email: string
      password: string
      name: string
    response: { id, email, name, created_at }

  POST /api/auth/login:
    summary: OAuth2 callback
    request:
      code: string
      state: string
    response: { access_token, refresh_token, expires_in }

  POST /api/auth/refresh:
    summary: Refresh JWT token
    request:
      refresh_token: string
    response: { access_token, expires_in }

  # Teams
  POST /api/teams:
    summary: Create new team
    request:
      name: string
      description?: string
    response: { id, name, owner_id, created_at }

  GET /api/teams:
    summary: List teams for user
    response: [{ id, name, owner_id, member_count }]

  GET /api/teams/{id}:
    summary: Get team details
    response: { id, name, owner_id, settings, created_at }

  POST /api/teams/{id}/members:
    summary: Add team member
    request:
      user_id: string
      role: string (owner|admin|member|viewer)
    response: { id, user_id, team_id, role, added_at }

  DELETE /api/teams/{id}/members/{user_id}:
    summary: Remove team member
    response: { success: boolean }
```

#### Project & Sprint APIs

```yaml
endpoints:
  # Projects
  POST /api/projects:
    summary: Create project
    request:
      team_id: string
      name: string
      tech_stack: object
    response: { id, team_id, name, status, created_at }

  GET /api/projects:
    summary: List projects (paginated)
    query_params:
      page: number
      page_size: number
      sort: string
    response: { data: [...], pagination: {...} }

  GET /api/projects/{id}/board:
    summary: Get sprint board (real-time)
    response:
      columns: [{ name, tasks: [...] }]
      metadata: { sprint_id, sprint_name, velocity }

  # Sprints
  POST /api/projects/{id}/sprints:
    summary: Create sprint
    request:
      name: string
      start_date: date
      end_date: date
    response: { id, project_id, name, status, created_at }

  POST /api/sprints/{id}/start:
    summary: Start sprint
    response: { id, status, started_at }

  POST /api/sprints/{id}/complete:
    summary: Complete sprint
    response: { id, status, velocity, completed_at }

  GET /api/sprints/{id}/burndown:
    summary: Get burndown chart data
    response:
      dates: [date]
      ideal: [points]
      actual: [points]
      completed_points: number
```

#### Agent Execution APIs

```yaml
endpoints:
  # Agent Control
  POST /api/agents/{type}/start:
    summary: Start agent (PM|Dev|QA|DevOps|Architect)
    request:
      config?: object
    response: { agent_type, status, started_at }

  POST /api/agents/{type}/stop:
    summary: Stop agent
    response: { agent_type, status, stopped_at }

  GET /api/agents/{type}/status:
    summary: Get agent status
    response: { agent_type, status, uptime, tasks_completed }

  # Executions
  POST /api/executions:
    summary: Create execution
    request:
      task_id: string
      agent_type: string
    response: { id, task_id, agent_type, status, created_at }

  GET /api/executions/{id}:
    summary: Get execution details
    response:
      id: string
      task_id: string
      agent_type: string
      status: string
      input_data: object
      output_data: object
      execution_time_ms: number
      tokens_used: number
      cost_estimate: number

  GET /api/executions/{id}/logs:
    summary: Get execution logs (streaming)
    response: stream of { timestamp, level, message }

  POST /api/executions/{id}/override:
    summary: Override execution
    request:
      reason: string
      human_input?: object
    response: { id, status: overridden, overridden_at }
```

#### Tool Integration APIs

```yaml
endpoints:
  # Integrations
  POST /api/integrations:
    summary: Connect new integration
    request:
      tool_name: string (github|jira|figma|docker|slack)
      account_name: string
    response: { id, tool_name, oauth_url: string }

  GET /api/integrations:
    summary: List integrations
    response: [{ id, tool_name, account_name, is_connected, last_verified }]

  DELETE /api/integrations/{id}:
    summary: Disconnect integration
    response: { success: boolean }

  POST /api/integrations/{id}/oauth/callback:
    summary: Handle OAuth callback
    query_params:
      code: string
      state: string
    response: { success: boolean, integration_id: string }

  GET /api/integrations/{id}/usage:
    summary: Get tool usage logs
    query_params:
      start_date: date
      end_date: date
    response: [{ timestamp, action, status, execution_time_ms }]
```

---

## DATA FLOW DIAGRAMS

### User Registration Flow

```
User                UI              API           PostgreSQL       Vault
  │                 │               │               │              │
  │─ Click Register─>│               │               │              │
  │                 │ POST /register │               │              │
  │                 ├──────────────>│               │              │
  │                 │               │ Validate input│              │
  │                 │               │               │              │
  │                 │               │ Hash password │              │
  │                 │               ├─────────────>│              │
  │                 │               │ INSERT user  │              │
  │                 │               │<─────────────┤              │
  │                 │               │               │ Emit event  │
  │                 │               ├──────────────────────────>│
  │                 │<──────────────┤ 201 Created   │              │
  │                 │ Success email │               │              │
  │<─ Confirmation──┤               │               │              │
  │                 │               │               │              │
```

### Task Assignment to Agent Flow

```
User                UI              API          Celery        Agent        MCP Hub
  │                 │               │             │             │             │
  │─ Assign to Dev─>│               │             │             │             │
  │                 │ POST /assign  │             │             │             │
  │                 ├────────────>│             │             │             │
  │                 │             │ Validate    │             │             │
  │                 │             │ Queue job   │             │             │
  │                 │             ├──────────>│             │             │
  │                 │             │ 202 Accepted│             │             │
  │                 │<─────────────┤             │             │             │
  │                 │ Task queued  │             │             │             │
  │<─ Notification──┤             │             │             │             │
  │                 │             │    Job ready│             │             │
  │                 │             │             ├──────────>│             │
  │                 │             │             │  Execute  │             │
  │                 │             │             │           │─ Get Creds─>│
  │                 │             │             │           │<─ Token    │
  │                 │             │             │           │             │
  │                 │             │             │           │─ Call API──>│
  │                 │             │             │           │<─ Result    │
  │                 │             │    Complete │           │             │
  │                 │             │<────────────┤           │             │
  │                 │ WebSocket   │             │             │             │
  │                 │ broadcast   │             │             │             │
  │<─ Task Complete─┤             │             │             │             │
```

### Sprint Board Real-Time Update Flow

```
User1              User2           UI2           API         Redis        DB
  │                 │               │             │           │            │
  │ Update Task    │               │             │           │            │
  │ Status        │               │             │           │            │
  │─────────────────────────>UI1─POST /task/status           │            │
  │                 │               │             │           │            │
  │                 │               │             ├──────────>│ PUBLISH   │
  │                 │               │             │ Update    │            │
  │                 │               │             │ DB────────────────────>│
  │                 │               │             │           │ Broadcast  │
  │                 │               │<────────────┤           │            │
  │                 │               │ WebSocket──────────────>│            │
  │                 │               │ Update      │           │            │
  │                 │<──────────────────────────────────────────────────────┤
  │                 │  Real-time    │             │           │            │
  │                 │  Board Update │             │           │            │
```

---

## COMPONENT INTERACTION PATTERNS

### Service-to-Service Communication Pattern

```
Synchronous (REST):
┌─────────────────┐        HTTP         ┌─────────────────┐
│ Service A       │──────────────────>│ Service B       │
│                 │<──────────────────│                 │
│                 │  (Request/Response)│                 │
└─────────────────┘                    └─────────────────┘

Asynchronous (Message Queue):
┌─────────────────┐        Event        ┌─────────────────┐
│ Service A       │───────────────────>│ Message Queue   │
│ (Emits events)  │                    │ (Redis/Celery)  │
└─────────────────┘                    └────────┬────────┘
                                               │
                                               │ Subscribe
                                               │
                                        ┌──────▼─────────┐
                                        │ Service B      │
                                        │ Service C      │
                                        │ Service D      │
                                        └────────────────┘
```

### Circuit Breaker Pattern (Resilience)

```
Closed (Normal)          Open (Failed)         Half-Open (Recovery)
│                        │                     │
├─ Request passes        ├─ Requests rejected  ├─ Single test request
├─ 0-5% error rate       ├─ Fast fail          ├─ If succeeds → Closed
└─ All requests OK       ├─ Timeout: 60s       └─ If fails → Open
                         └─ Fallback response
```

### Retry with Exponential Backoff

```
Attempt 1: Immediate (0ms)
    │ ✓ Success → Return
    │ ✗ Failure → Wait 1s
    │
Attempt 2: 1 second delay
    │ ✓ Success → Return
    │ ✗ Failure → Wait 4s
    │
Attempt 3: 5 second delay
    │ ✓ Success → Return
    │ ✗ Failure → Wait 16s
    │
Attempt 4: 21 second delay
    │ ✓ Success → Return
    │ ✗ Failure → Fail
    │
Max attempts: 4
Total time: ~22 seconds
```

---

## DATABASE SCHEMA DESIGN

### Core Schema (PostgreSQL)

```sql
-- Enums
CREATE TYPE user_role AS ENUM ('owner', 'admin', 'member', 'viewer');
CREATE TYPE team_member_role AS ENUM ('owner', 'admin', 'lead', 'developer', 'viewer');
CREATE TYPE project_status AS ENUM ('planning', 'active', 'paused', 'completed');
CREATE TYPE sprint_status AS ENUM ('planning', 'active', 'completed', 'archived');
CREATE TYPE task_status AS ENUM ('backlog', 'todo', 'in_progress', 'in_review', 'done', 'failed', 'overridden');
CREATE TYPE agent_type AS ENUM ('pm', 'architect', 'dev', 'qa', 'devops');
CREATE TYPE execution_status AS ENUM ('pending', 'running', 'completed', 'failed', 'overridden');

-- Base tables
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    avatar_url TEXT,
    oauth_provider VARCHAR(50),
    oauth_id VARCHAR(255),
    password_hash VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at DESC);

-- Teams
CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    owner_id UUID NOT NULL REFERENCES users(id),
    workspace_slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT valid_slug CHECK (workspace_slug ~ '^[a-z0-9-]+$')
);

CREATE INDEX idx_teams_owner_id ON teams(owner_id);
CREATE INDEX idx_teams_workspace_slug ON teams(workspace_slug);

-- Team members
CREATE TABLE team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role team_member_role NOT NULL DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(team_id, user_id)
);

CREATE INDEX idx_team_members_team_id ON team_members(team_id);
CREATE INDEX idx_team_members_user_id ON team_members(user_id);

-- Projects
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    tech_stack JSONB DEFAULT '{}',
    status project_status DEFAULT 'planning',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_projects_team_id ON projects(team_id);
CREATE INDEX idx_projects_status ON projects(status);

-- Sprints
CREATE TABLE sprints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    start_date DATE,
    end_date DATE,
    status sprint_status DEFAULT 'planning',
    velocity INT DEFAULT 0,
    planned_points INT DEFAULT 0,
    completed_points INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT valid_dates CHECK (start_date IS NULL OR end_date IS NULL OR start_date <= end_date)
);

CREATE INDEX idx_sprints_project_id ON sprints(project_id);
CREATE INDEX idx_sprints_status ON sprints(status);

-- User Stories
CREATE TABLE user_stories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    sprint_id UUID REFERENCES sprints(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    acceptance_criteria JSONB DEFAULT '[]',
    priority INT CHECK (priority BETWEEN 1 AND 10) DEFAULT 5,
    story_points INT DEFAULT 0,
    status task_status DEFAULT 'backlog',
    assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
    assigned_agent agent_type,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_stories_project_id ON user_stories(project_id);
CREATE INDEX idx_user_stories_sprint_id ON user_stories(sprint_id);
CREATE INDEX idx_user_stories_status ON user_stories(status);
CREATE INDEX idx_user_stories_priority ON user_stories(priority DESC);

-- Tasks
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_story_id UUID NOT NULL REFERENCES user_stories(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    assigned_agent agent_type,
    assigned_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    status task_status DEFAULT 'pending',
    estimated_hours INT,
    actual_hours INT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tasks_story_id ON tasks(user_story_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_assigned_agent ON tasks(assigned_agent);

-- Agent Executions
CREATE TABLE agent_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    agent_type agent_type NOT NULL,
    agent_model VARCHAR(100),
    status execution_status DEFAULT 'pending',
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    execution_time_ms INT,
    tokens_used INT DEFAULT 0,
    cost_estimate DECIMAL(10, 6) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    CONSTRAINT valid_time CHECK (completed_at IS NULL OR completed_at >= created_at)
);

CREATE INDEX idx_agent_executions_task_id ON agent_executions(task_id);
CREATE INDEX idx_agent_executions_agent_type ON agent_executions(agent_type);
CREATE INDEX idx_agent_executions_status ON agent_executions(status);
CREATE INDEX idx_agent_executions_created_at ON agent_executions(created_at DESC);

-- Agent Logs
CREATE TABLE agent_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id UUID NOT NULL REFERENCES agent_executions(id) ON DELETE CASCADE,
    level VARCHAR(50),
    message TEXT,
    context JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_agent_logs_execution_id ON agent_logs(execution_id);
CREATE INDEX idx_agent_logs_created_at ON agent_logs(created_at DESC);

-- Integrations
CREATE TABLE integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    tool_name VARCHAR(100) NOT NULL,
    account_name VARCHAR(255),
    is_connected BOOLEAN DEFAULT false,
    credential_id VARCHAR(255),
    scopes JSONB DEFAULT '{}',
    last_verified TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(team_id, tool_name)
);

CREATE INDEX idx_integrations_team_id ON integrations(team_id);
CREATE INDEX idx_integrations_tool_name ON integrations(tool_name);

-- Tool Usage (Audit)
CREATE TABLE tool_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    integration_id UUID NOT NULL REFERENCES integrations(id) ON DELETE CASCADE,
    actor_type VARCHAR(50),
    actor_id VARCHAR(255),
    action VARCHAR(100),
    request_data JSONB,
    response_data JSONB,
    status_code INT,
    error_message TEXT,
    execution_time_ms INT,
    cost_estimate DECIMAL(10, 6) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tool_usage_integration_id ON tool_usage(integration_id);
CREATE INDEX idx_tool_usage_created_at ON tool_usage(created_at DESC);
CREATE INDEX idx_tool_usage_actor ON tool_usage(actor_type, actor_id);

-- Audit Logs (Immutable)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id),
    actor_type VARCHAR(50),
    actor_id VARCHAR(255) NOT NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100),
    entity_id VARCHAR(255),
    changes JSONB,
    ip_address INET,
    user_agent TEXT,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT immutable CHECK (TRUE) -- Triggers to prevent update/delete
);

CREATE INDEX idx_audit_logs_team_id ON audit_logs(team_id);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_actor ON audit_logs(actor_type, actor_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);
```

### View Definitions

```sql
-- Sprint Board View (Kanban)
CREATE VIEW sprint_board AS
SELECT 
    s.id as sprint_id,
    us.id as story_id,
    us.title as story_title,
    us.status,
    us.story_points,
    us.assigned_agent,
    t.id as task_id,
    t.title as task_title,
    t.status as task_status,
    COUNT(*) OVER (PARTITION BY us.id) as task_count
FROM user_stories us
LEFT JOIN tasks t ON t.user_story_id = us.id
RIGHT JOIN sprints s ON s.id = us.sprint_id
WHERE s.status = 'active'
ORDER BY us.priority DESC, us.created_at ASC;

-- Sprint Metrics View
CREATE VIEW sprint_metrics AS
SELECT 
    s.id as sprint_id,
    s.name,
    s.status,
    COUNT(DISTINCT us.id) as total_stories,
    SUM(us.story_points) as total_points,
    COALESCE(SUM(CASE WHEN us.status = 'done' THEN us.story_points ELSE 0 END), 0) as completed_points,
    COALESCE(SUM(CASE WHEN us.status = 'done' THEN us.story_points ELSE 0 END), 0) * 100.0 / 
        NULLIF(SUM(us.story_points), 0) as completion_percentage,
    (s.end_date - s.start_date) as sprint_days,
    (s.end_date::date - CURRENT_DATE) as days_remaining
FROM sprints s
LEFT JOIN user_stories us ON us.sprint_id = s.id
GROUP BY s.id, s.name, s.status, s.start_date, s.end_date;

-- Agent Performance View
CREATE VIEW agent_performance AS
SELECT 
    agent_type,
    COUNT(*) as total_executions,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
    ROUND(100.0 * SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate,
    ROUND(AVG(execution_time_ms), 2) as avg_execution_time_ms,
    SUM(tokens_used) as total_tokens,
    SUM(cost_estimate) as total_cost
FROM agent_executions
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY agent_type;
```

---

## MESSAGE QUEUE & EVENT ARCHITECTURE

### Event-Driven Architecture

```
Domain Events:
├─ User Events
│  ├─ user.registered
│  ├─ user.login
│  ├─ user.updated
│  └─ user.deleted
│
├─ Team Events
│  ├─ team.created
│  ├─ team.member_added
│  ├─ team.member_removed
│  └─ team.updated
│
├─ Project Events
│  ├─ project.created
│  ├─ project.updated
│  └─ project.deleted
│
├─ Sprint Events
│  ├─ sprint.created
│  ├─ sprint.started
│  ├─ sprint.completed
│  └─ sprint.metrics_updated
│
├─ Story Events
│  ├─ story.created
│  ├─ story.assigned
│  ├─ story.status_changed
│  └─ story.completed
│
├─ Task Events
│  ├─ task.created
│  ├─ task.assigned
│  ├─ task.status_changed
│  └─ task.completed
│
├─ Agent Events
│  ├─ agent.started
│  ├─ agent.stopped
│  ├─ execution.started
│  ├─ execution.completed
│  ├─ execution.failed
│  └─ execution.overridden
│
└─ Integration Events
   ├─ integration.connected
   ├─ integration.disconnected
   ├─ integration.rate_limited
   └─ credential.expired
```

### Event Publishing Pattern

```python
# Example: Task assigned to agent
class TaskAssignedEvent:
    event_type = "task.assigned"
    version = 1
    
    def __init__(self, task_id, agent_type, timestamp):
        self.task_id = task_id
        self.agent_type = agent_type
        self.timestamp = timestamp

# Publisher
def assign_task_to_agent(task_id: str, agent_type: str):
    # Update database
    task = Task.query.get(task_id)
    task.assigned_agent = agent_type
    db.session.commit()
    
    # Publish event
    event = TaskAssignedEvent(task_id, agent_type, datetime.now())
    event_bus.publish(
        channel=f"task:{task_id}:assigned",
        message=event.to_json()
    )
    
    # Emit to WebSocket
    websocket_manager.broadcast(
        channel=f"sprint:{task.sprint_id}:updates",
        message={
            "type": "task_assigned",
            "task_id": task_id,
            "agent_type": agent_type
        }
    )

# Subscriber (Agent Control Service)
@event_bus.subscribe("task:*.assigned")
def on_task_assigned(event):
    # Start agent execution
    execution = AgentExecution.create(
        task_id=event.task_id,
        agent_type=event.agent_type
    )
    
    # Queue agent job
    celery.send_task(
        'agents.execute',
        args=[execution.id, event.agent_type]
    )
```

### Celery Task Queue Configuration

```python
# celery_config.py
from celery import Celery
from celery.schedules import crontab

app = Celery('software-galaxy')

# Broker & Backend
app.conf.broker_url = 'redis://localhost:6379/0'
app.conf.result_backend = 'redis://localhost:6379/0'

# Task Configuration
app.conf.task_serializer = 'json'
app.conf.accept_content = ['json']
app.conf.result_serializer = 'json'
app.conf.timezone = 'UTC'
app.conf.enable_utc = True

# Task Routes (Priority queues)
app.conf.task_routes = {
    'agents.execute_deploy': {'queue': 'critical'},
    'agents.execute': {'queue': 'high'},
    'webhooks.handle': {'queue': 'normal'},
    'notifications.send': {'queue': 'low'},
}

# Time Limits
app.conf.task_time_limit = 30 * 60  # 30 minutes
app.conf.task_soft_time_limit = 25 * 60  # 25 minutes (allow cleanup)

# Retry Policy
app.conf.task_acks_late = True
app.conf.task_reject_on_worker_lost = True

# Periodic Tasks
app.conf.beat_schedule = {
    'sync-integrations': {
        'task': 'integrations.sync_all',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'cleanup-old-logs': {
        'task': 'maintenance.cleanup_logs',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
    },
    'calculate-sprint-metrics': {
        'task': 'sprints.calculate_metrics',
        'schedule': crontab(minute='*/10'),  # Every 10 minutes
    },
}

# Worker Configuration
app.conf.worker_prefetch_multiplier = 4
app.conf.worker_max_tasks_per_child = 1000
```

### Example Celery Tasks

```python
# tasks/agents.py
from celery import shared_task, current_task
from agents.pm_agent import PMAgent
from agents.dev_agent import DevAgent

@shared_task(bind=True, max_retries=3)
def execute_agent_task(self, execution_id, agent_type):
    """Execute agent task with retry logic"""
    try:
        execution = AgentExecution.query.get(execution_id)
        task = execution.task.to_dict()
        
        # Update execution status
        execution.status = 'running'
        execution.started_at = datetime.now()
        db.session.commit()
        
        # Emit event
        emit_event('execution.started', {'execution_id': execution_id})
        
        # Select agent
        if agent_type == 'pm':
            agent = PMAgent()
        elif agent_type == 'dev':
            agent = DevAgent()
        
        # Execute
        result = agent.execute(task)
        
        # Save result
        execution.output_data = result
        execution.status = 'completed'
        execution.completed_at = datetime.now()
        db.session.commit()
        
        # Emit event
        emit_event('execution.completed', {'execution_id': execution_id})
        
        return result
        
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)

@shared_task
def handle_webhook(event_type, payload):
    """Process webhook from external tool"""
    try:
        if event_type == 'github.push':
            handle_github_push(payload)
        elif event_type == 'github.pull_request':
            handle_github_pr(payload)
        # ... more webhook handlers
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise

@shared_task
def send_notification(user_id, title, message):
    """Send notification to user"""
    user = User.query.get(user_id)
    
    # Send email
    send_email(user.email, title, message)
    
    # Send WebSocket
    websocket_manager.send(
        user_id=user_id,
        message={'type': 'notification', 'title': title, 'message': message}
    )

# tasks/maintenance.py
@periodic_task.task(run_every=crontab(hour=2, minute=0))
def cleanup_old_logs():
    """Clean up old audit logs (>1 year)"""
    cutoff_date = datetime.now() - timedelta(days=365)
    AuditLog.query.filter(AuditLog.created_at < cutoff_date).delete()
    db.session.commit()

@periodic_task.task(run_every=crontab(minute='*/10'))
def calculate_sprint_metrics():
    """Calculate sprint metrics"""
    for sprint in Sprint.query.filter_by(status='active'):
        metrics = sprint.calculate_metrics()
        db.session.commit()
```

---

## INTEGRATION PATTERNS

### MCP (Model Context Protocol) Integration

```python
# mcp_hub/github_mcp.py
from mcp import Server, Tool, Resource

class GitHubMCP(Server):
    def __init__(self, token: str):
        super().__init__()
        self.token = token
        self.gh = GithubAPI(token)
        
    @Tool(
        name="clone_repo",
        description="Clone a GitHub repository",
        input_schema={
            "type": "object",
            "properties": {
                "repo_url": {"type": "string"},
                "local_path": {"type": "string"}
            },
            "required": ["repo_url", "local_path"]
        }
    )
    async def clone_repo(self, repo_url: str, local_path: str) -> dict:
        """Clone repository"""
        try:
            git.clone(repo_url, local_path)
            return {"status": "success", "path": local_path}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @Tool(name="create_branch", description="Create new branch")
    async def create_branch(self, repo: str, branch: str, from_branch: str = "main") -> dict:
        """Create branch in repository"""
        try:
            self.gh.create_branch(repo, branch, from_branch)
            return {"status": "success", "branch": branch}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @Tool(name="create_pr", description="Create pull request")
    async def create_pr(self, repo: str, title: str, body: str, 
                       head_branch: str, base_branch: str = "main") -> dict:
        """Create PR"""
        try:
            pr = self.gh.create_pr(repo, title, body, head_branch, base_branch)
            return {"status": "success", "pr_number": pr.number, "pr_url": pr.url}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @Resource(
        uri="github://repos/{owner}/{repo}/files",
        description="List repository files"
    )
    async def list_repo_files(self, owner: str, repo: str) -> list:
        """List files in repository"""
        return self.gh.list_files(f"{owner}/{repo}")

# Usage in agent
class DevAgent:
    def __init__(self, mcp_hub):
        self.mcp_hub = mcp_hub
        self.github_mcp = mcp_hub.get_server("github")
    
    async def implement_feature(self, story: dict) -> dict:
        # Get repository files as context
        files = await self.github_mcp.list_repo_files("owner", "repo")
        
        # Generate code using LLM
        code = await self.llm.generate_code(story, files)
        
        # Create branch
        await self.github_mcp.create_branch(
            "owner/repo",
            f"feature/{story['id']}"
        )
        
        # Commit code
        await self.github_mcp.commit_files(
            "owner/repo",
            files=[{"path": "src/feature.py", "content": code}],
            message=f"Implement {story['title']}"
        )
        
        # Create PR
        pr = await self.github_mcp.create_pr(
            "owner/repo",
            title=f"Feature: {story['title']}",
            body=story['description'],
            head_branch=f"feature/{story['id']}"
        )
        
        return {"status": "success", "pr_number": pr['pr_number']}
```

### Webhook Integration Pattern

```python
# integrations/webhooks.py
from fastapi import APIRouter, Request, Depends
from hmac import HMAC, compare_digest

router = APIRouter()

def verify_github_signature(request: Request, signature: str) -> bool:
    """Verify GitHub webhook signature"""
    body = request.body()
    secret = os.getenv("GITHUB_WEBHOOK_SECRET")
    expected = HMAC(
        secret.encode(),
        body,
        'sha256'
    ).hexdigest()
    return compare_digest(f"sha256={expected}", signature)

@router.post("/webhooks/github")
async def handle_github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None)
):
    """Handle GitHub webhook events"""
    if not verify_github_signature(request, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    payload = await request.json()
    event_type = request.headers.get("X-GitHub-Event")
    
    # Queue webhook handler
    celery.send_task(
        'webhooks.handle',
        args=[event_type, payload],
        queue='normal'
    )
    
    return {"status": "queued"}

@router.post("/webhooks/jira")
async def handle_jira_webhook(request: Request):
    """Handle Jira webhook events"""
    payload = await request.json()
    event_type = payload.get("webhookEvent")
    
    celery.send_task(
        'webhooks.handle',
        args=[f"jira.{event_type}", payload],
        queue='normal'
    )
    
    return {"status": "queued"}

# Webhook handlers
@celery.task
def handle_webhook(event_type: str, payload: dict):
    """Main webhook handler"""
    handlers = {
        'push': handle_github_push,
        'pull_request': handle_github_pr,
        'issues': handle_github_issue,
        'issue_comment': handle_github_comment,
    }
    
    if event_type in handlers:
        handlers[event_type](payload)

def handle_github_push(payload: dict):
    """Handle GitHub push event"""
    repo = payload['repository']['full_name']
    branch = payload['ref'].split('/')[-1]
    commits = payload['commits']
    
    # Update project from commit
    for commit in commits:
        message = commit['message']
        
        # Parse story ID from commit message
        # E.g., "Implement feature #123"
        match = re.search(r'#(\d+)', message)
        if match:
            story_id = match.group(1)
            # Update story status based on commit
            update_story_status(story_id, 'in_progress')

def handle_github_pr(payload: dict):
    """Handle GitHub PR event"""
    action = payload['action']
    pr = payload['pull_request']
    
    if action == 'opened':
        # Parse story ID from PR title
        story_id = parse_story_id(pr['title'])
        if story_id:
            # Create task for code review
            create_review_task(story_id, pr['number'])
    
    elif action == 'closed' and pr['merged']:
        # PR merged
        story_id = parse_story_id(pr['title'])
        if story_id:
            update_story_status(story_id, 'in_review')
```

---

## SYSTEM CONSTRAINTS & TRADE-OFFS

### Design Constraints

```
1. Latency Constraints
   - Agent startup: <5 seconds
   - API response: <200ms (p95)
   - Real-time updates: <500ms (p95)
   - Search: <1 second (1M records)

2. Scalability Constraints
   - Concurrent users: 1,000+
   - Concurrent agents: 500+
   - Data volume: 100GB+
   - Transactions/min: 10,000+

3. Data Constraints
   - Session timeout: 24 hours (JWT)
   - Audit log retention: 1 year
   - Cache TTL: 5 minutes (tunable)
   - File upload limit: 100MB per file

4. Security Constraints
   - TLS 1.3 all data in transit
   - AES-256-GCM at rest
   - No credentials in logs
   - API rate limiting: 1000 req/min per user
```

### Trade-offs

```
1. Local Agents vs Cloud Agents
   Trade-off: Lower latency + Cost efficiency vs Operational complexity
   Decision: Local agents (Electron)
   Rationale: Agents need low latency for IDE integration

2. PostgreSQL vs NoSQL
   Trade-off: ACID compliance vs Schema flexibility
   Decision: PostgreSQL + JSON columns
   Rationale: Financial data needs transactions, JSON for flexibility

3. Synchronous vs Asynchronous
   Trade-off: Simplicity vs Resilience
   Decision: Hybrid approach
   - Synchronous: Read operations, real-time queries
   - Asynchronous: Long-running tasks, webhooks
   Rationale: Best of both worlds

4. Microservices vs Monolith
   Trade-off: Scalability vs Operational complexity
   Decision: Microservices (vertically sliced)
   Rationale: Easy to scale independent services, shared database OK for MVP

5. Redis for Queue vs RabbitMQ
   Trade-off: Simpler setup vs Guaranteed delivery
   Decision: Redis
   Rationale: Already using Redis for cache, simpler operations

6. Vector Store Location
   Trade-off: Privacy vs Operational complexity
   Decision: Local (Electron) + Optional cloud sync
   Rationale: User's code stays local, can sync for backup
```

---

## TECHNICAL DEBT & MITIGATION

### Identified Technical Debt

```
1. Monolithic Database (High Priority)
   Issue: All data in single PostgreSQL database
   Impact: Harder to scale, GDPR compliance complex
   Mitigation (Phase 2):
   - Implement database sharding by team_id
   - Separate analytics database
   - Archive old audit logs to data warehouse

2. MCP Server Duplication (Medium)
   Issue: MCP servers duplicated in cloud + Electron
   Impact: Maintenance burden, inconsistent behavior
   Mitigation (Phase 2):
   - Standardize MCP server interface
   - Auto-generate from OpenAPI specs
   - Unified server registry

3. No Rate Limiting on Agent APIs (High)
   Issue: Agents can make unlimited API calls
   Impact: Runaway costs, DoS vulnerability
   Mitigation (Phase 1):
   - Implement per-agent rate limits (Celery)
   - Track token usage per agent
   - Set monthly budgets per project

4. Limited Error Recovery (Medium)
   Issue: Failed agent executions not automatically retried
   Impact: Lost work, poor user experience
   Mitigation (Phase 1):
   - Implement exponential backoff retry
   - Dead letter queue for failed tasks
   - Manual intervention UI

5. No Performance Monitoring (High)
   Issue: No visibility into agent performance
   Impact: Hard to optimize, detect issues
   Mitigation (Phase 1):
   - Add metrics collection (Prometheus)
   - Build dashboards (Grafana)
   - Set up alerting

6. Security: Plain Text in Logs (Critical)
   Issue: Secrets may appear in logs
   Impact: Credential exposure risk
   Mitigation (Phase 1):
   - Implement log redaction
   - Vault integration
   - Regular security audit
```

### Refactoring Roadmap

```
Phase 0 (MVP, Weeks 1-4):
- ✓ Basic system design
- ✓ Microservice structure
- ✓ Database schema

Phase 1 (Polish, Weeks 5-12):
- Add rate limiting
- Implement monitoring
- Security hardening
- Error recovery

Phase 2 (Scale, Month 5-6):
- Database sharding
- MCP standardization
- Multi-region deployment
- Analytics separation

Phase 3 (Optimize, Month 7-12):
- Performance tuning
- Cost optimization
- Compliance certifications
- Enterprise features
```

---

## IMPLEMENTATION ROADMAP

### Phase 0: Foundation (Weeks 1-4)

```
Week 1-2: Core Infrastructure
├─ Database schema
├─ API gateway setup
├─ Auth service
└─ Basic CRUD endpoints

Week 3: Microservices
├─ User & Team service
├─ Project & Sprint service
└─ Tool Registry service

Week 4: Integration
├─ PostgreSQL + Redis connection
├─ Message queue setup
├─ Local MCP hub (Electron)
└─ Deployment to staging

Deliverables:
- ✓ Functional API
- ✓ Database migrations
- ✓ Service-to-service communication
- ✓ Local development setup
```

### Phase 1: Core Features (Weeks 5-12)

```
Week 5-6: Agent Orchestration
├─ LangGraph setup
├─ PM Agent MVP
├─ Dev Agent MVP
└─ Agent execution service

Week 7-8: Real-Time & Integrations
├─ WebSocket implementation
├─ GitHub MCP server
├─ Jira MCP server
└─ Webhook handlers

Week 9-10: Scaling & Resilience
├─ Kubernetes deployment
├─ Circuit breaker pattern
├─ Retry logic
└─ Error handling

Week 11-12: Testing & Hardening
├─ Integration tests (80% coverage)
├─ Load testing
├─ Security audit
└─ Performance optimization

Deliverables:
- ✓ Working agents
- ✓ Real-time sprint board
- ✓ Tool integrations
- ✓ Production-ready infrastructure
```

---

**Document Version:** 1.0  
**Last Updated:** December 2025  
**Next Review:** Phase 0 Completion (Week 4)  
**Owner:** Senior System Analyst / Technical Architect  
**Status:** Ready for Engineering Implementation