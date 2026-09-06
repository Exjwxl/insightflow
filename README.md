# 📊 InsightFlow — Autonomous AI Data Analyst

> **An autonomous multi-agent data analytics platform powered by LangGraph, DuckDB, Pandas, SQLGlot, FastAPI, and Next.js that converts natural-language business questions into validated SQL queries, deterministic statistical analyses, interactive visualizations, and actionable C-suite reports.**

---

## 🌟 Key Architecture & Highlights

```
                          ┌─────────────────────────────┐
                          │   Next.js 14+ UI Dashboard │
                          │  (Tailwind, shadcn, Plotly) │
                          └──────────────┬──────────────┘
                                         │ REST / SSE Stream
                                         ▼
                          ┌─────────────────────────────┐
                          │    FastAPI Backend Server   │
                          │ (Endpoints, Sessions, Data) │
                          └──────────────┬──────────────┘
                                         │
                                         ▼
    ┌────────────────────────────────────────────────────────────────────────┐
    │                       LangGraph Orchestrator                           │
    │                                                                        │
    │  [1. Profiler / Schema Agent]                                          │
    │              │                                                         │
    │              ▼                                                         │
    │  [2. Planner / Decomposition Agent]                                    │
    │              │                                                         │
    │              ▼                                                         │
    │  [3. SQL Generation Agent] ◄─────────────────┐ (Self-Correction Loop) │
    │              │                               │                         │
    │              ▼                               │                         │
    │  [4. SQLGlot Validator Agent] ──(Invalid)────┘                         │
    │              │ (Valid)                                                 │
    │              ▼                                                         │
    │  [5. DuckDB Execution Engine]                                          │
    │              │                                                         │
    │              ▼                                                         │
    │  [6. Pandas Statistical / Analysis Agent]                              │
    │              │                                                         │
    │              ▼                                                         │
    │      (Need more depth?) ────► [Planner Drill-Down Loop]               │
    │              │                                                         │
    │              ▼                                                         │
    │  [7. Visualization Agent (Plotly)]                                     │
    │              │                                                         │
    │              ▼                                                         │
    │  [8. Findings Validation Agent]                                        │
    │              │                                                         │
    │              ▼                                                         │
    │  [9. Executive Report Agent]                                           │
    └────────────────────────────────────────────────────────────────────────┘
```

### 🎯 The Core Design Principle
* **LLM = Reasoning, Planning, SQL generation, Interpretation & Synthesis**
* **Python / DuckDB / Pandas / SQLGlot = Deterministic execution, Security validation, Exact math & Chart generation**

---

## 🚀 Quickstart Guide

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` to interact with InsightFlow!

---

## 🧪 Testing

Run backend unit tests for SQL validation, AST parsing, and statistical calculations:

```bash
cd backend
python -m pytest tests/
```
