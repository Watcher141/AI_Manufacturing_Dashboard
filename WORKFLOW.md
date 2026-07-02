# AI Manufacturing Dashboard — System Architecture & Workflow Guide

Welcome to the **Sentry Fab AI Manufacturing Dashboard** workflow documentation. This guide details the end-to-end operational workflows, data pipelines, machine learning integration, and Role-Based Access Control (RBAC) architecture that power the platform.

---

## 1. High-Level Architecture Overview

The system operates on a modern, decoupled cloud infrastructure designed for low latency, real-time analytics, and high reliability:

```mermaid
graph TD
    subgraph Frontend [Frontend Layer - Vercel]
        UI[React + Vite SPA]
        State[Zustand State Stores]
        AuthClient[Axios Auth Interceptor]
    end

    subgraph Backend [AI API Layer - Hugging Face Spaces]
        API[FastAPI Asynchronous Server]
        AuthGuard[RBAC Security Middleware]
        ML[ML & Analytics Engine]
        LLM[Groq Llama-3 AI Assistant]
    end

    subgraph Database [Persistence Layer - Neon Serverless PostgreSQL]
        NeonDB[(PostgreSQL Database)]
    end

    UI -->|REST API Requests + Bearer Token| API
    API <-->|Asyncpg / SQLAlchemy Async| NeonDB
    API <-->|Context-Aware Prompts| LLM
```

| Layer | Technologies | Role & Purpose |
| :--- | :--- | :--- |
| **Frontend** | React, Vite, Vanilla CSS, Zustand, Lucide Icons | Premium glassmorphism UI, real-time dashboard telemetry monitoring, interactive charting, and role-sensitive action rendering. |
| **Backend** | Python 3.11, FastAPI, Pydantic, SQLAlchemy Async | Handles REST API endpoints, input validation, ML model inference, background tasks, and authentication guards. |
| **Database** | Neon Serverless PostgreSQL (`asyncpg`) | Persistent relational storage for equipment metadata, sensor logs, defect registries, inventory tracking, and system alerts. |
| **AI / ML Engine** | Scikit-Learn, NumPy, Groq Llama-3 API | Powers predictive degradation forecasting, vision/sensor defect classification, and natural language query resolution. |

---

## 2. Role-Based Access Control (RBAC) Workflow

To maintain production integrity while ensuring data visibility across the enterprise, the application divides capabilities into **Read-Only Operational Access** and **Admin Management Access**.

```mermaid
sequenceDiagram
    autonumber
    actor User as Regular Operator
    actor Admin as Plant Supervisor (Admin)
    participant UI as Dashboard Frontend
    participant Auth as Auth Store / Interceptor
    participant API as FastAPI Backend

    Note over User,API: 1. Read-Only Operational Flow
    User->>UI: Access Dashboard / Telemetry
    UI->>API: GET /api/overview, /api/equipment
    API-->>UI: 200 OK (Data returned)
    UI-->>User: Render live telemetry (Action buttons hidden)

    Note over Admin,API: 2. Admin Authentication Flow
    Admin->>UI: Click "Admin Login" & Enter Password
    UI->>API: POST /api/auth/login { password: ADMIN_SECRET }
    API-->>UI: 200 OK { token: session_token }
    UI->>Auth: Save token in localStorage & update store
    UI-->>Admin: Show ADMIN Shield Badge & unlock mutations

    Note over Admin,API: 3. Admin Mutation Execution
    Admin->>UI: Click "Restock Inventory" / "Resolve Defect"
    UI->>API: PATCH /api/defects/102/resolve (Authorization: Bearer token)
    API->>API: Verify session in active stores
    API-->>UI: 200 OK (Defect marked resolved)
```

### Access Permission Matrix

| Feature / Page | Regular Operator (Unauthenticated) | Admin Supervisor (`ADMIN_SECRET`) |
| :--- | :---: | :---: |
| **View Telemetry & KPIs** | ✅ Full Visibility | ✅ Full Visibility |
| **Predictive Maintenance Charts** | ✅ Read-Only | ✅ Read-Only |
| **Ask AI Assistant Questions** | ✅ Unlimited Queries | ✅ Unlimited Queries |
| **Run Quality Scan Audits** | ❌ Hidden / Forbidden | ✅ Trigger Scan Audits |
| **Resolve Defect Records** | ❌ Hidden / Forbidden | ✅ Mark Defects Resolved |
| **Dismiss / Mark Alerts Read**| ❌ Hidden / Forbidden | ✅ Manage Alert Center |
| **Restock Inventory Orders** | ❌ Hidden / Forbidden | ✅ Execute Restocks |
| **System Settings & Data Seeding** | ❌ Locked / Redirected | ✅ Full Configuration Access |

---

## 3. Core Operational Pipelines

### A. Predictive Maintenance & Telemetry Pipeline
When equipment operates on the factory floor, telemetry readings flow through continuous monitoring loops:

```mermaid
flowchart LR
    A[IoT Sensor Simulation / Data Ingestion] --> B[API: POST /api/equipment/readings]
    B --> C[Store SensorReading in Database]
    C --> D[ML Degradation Model Analysis]
    D --> E{Remaining Useful Life RUL < Threshold?}
    E -->|Yes: Risk Detected| F[Generate Critical Maintenance Alert]
    E -->|No: Optimal| G[Update Machine Status: Operational]
```

1. **Ingestion**: Sensor metrics (temperature, vibration, acoustic pressure, RPM) are ingested via protected endpoints.
2. **Analysis**: The analytical engine calculates the **Health Score** and estimates the **Remaining Useful Life (RUL)** in hours based on stress tolerances.
3. **Automated Alerting**: If vibration or temperature exceeds designated thresholds, an anomaly alert is dispatched immediately to the **Alert Center**.

---

### B. Defect Detection Quality Audit Workflow
Automated anomaly classification scans product batches to identify manufacturing defects before shipments leave the facility:

```mermaid
flowchart TD
    Scan[Quality Audit Triggered] --> Query[Fetch Latest Line Sensor & Image Metrics]
    Query --> Classifier[Defect Detection Classifier Pipeline]
    Classifier --> Type[Classify Fault Type: Surface Scratch, Cracking, Void, etc.]
    Type --> Score[Calculate Confidence Score %]
    Score --> Register[Insert DefectRecord into Database]
    Register --> AdminAction[Admin Review & Physical Verification]
    AdminAction --> Resolve[Admin Clicks 'Resolve' -> Update Register]
```

---

### C. Inventory Demand Forecasting & Auto-Reorder Flow
To prevent assembly line shutdowns caused by stockouts, the inventory engine projects component depletion rates:

```mermaid
flowchart LR
    Hist[Historical Consumption Data] --> Forecaster[Time-Series Demand Forecaster]
    Forecaster --> Project[Project 7, 14, 30, or 90 Day Depletion]
    Project --> Safety{Projected Stock <= Reorder Point?}
    Safety -->|Yes: Stockout Warning| Rec[Calculate Recommended Reorder Qty]
    Rec --> Alert[Create Inventory Alert]
    Alert --> Restock[Admin Restocks Item -> Inventory Replenished]
```

---

### D. Conversational AI Assistant Workflow
The integrated **Groq Llama-3** LLM acts as an expert manufacturing engineer, synthesizing live database context into actionable advice:

```mermaid
sequenceDiagram
    actor User as Operator / Admin
    participant UI as AI Assistant UI
    participant API as Backend AI Router
    participant DB as Neon PostgreSQL
    participant Groq as Groq Llama-3 API

    User->>UI: Ask: "Which machine needs maintenance first?"
    UI->>API: POST /api/assistant/chat { message }
    API->>DB: Query Critical Alerts & Lowest RUL Equipment
    DB-->>API: Return Equipment Health Metrics
    API->>API: Build System Prompt with Live Telemetry Context
    API->>Groq: Stream Inference Request
    Groq-->>API: Natural Language Diagnostic Summary
    API-->>UI: Return Formatted Engineering Advice
    UI-->>User: Display Insights & Preventive Action Steps
```

---

## 4. Summary of Key Files & Modules

| Component Area | Key Files | Description |
| :--- | :--- | :--- |
| **Security & Auth** | `backend/app/auth_deps.py`<br>`backend/app/routers/auth.py`<br>`frontend/src/store/useAuthStore.js` | Token generation, Bearer validation middleware, and frontend session persistence. |
| **Database & Config** | `backend/app/config.py`<br>`backend/app/database.py` | Connection URL sanitization (removing driver-incompatible query flags for `asyncpg`) and async session lifecycle. |
| **ML & Analytics** | `backend/app/ml/predictive_maintenance.py`<br>`backend/app/ml/defect_detection.py`<br>`backend/app/ml/inventory_forecast.py` | Mathematical heuristics and predictive classification algorithms. |
| **User Interface** | `frontend/src/components/layout/Sidebar.jsx`<br>`frontend/src/pages/AdminLogin.jsx` | Dynamic navigation menus, glowing RBAC badges, and interactive modals. |
