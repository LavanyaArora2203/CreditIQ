# 🤖 AI Loan Advisor System

### 🌐 Live Demo

**Frontend:** https://credit-iq-nine.vercel.app/



---

## Overview

The AI Loan Advisor System is an end-to-end intelligent loan processing platform built using a multi-agent architecture. Instead of relying on a single AI model to handle the complete workflow, the system breaks the loan journey into specialized agents, each responsible for one stage of the decision-making process.

Starting from customer interaction and loan requirement gathering, the platform performs credit analysis, underwriting, document verification, and finally generates a personalized sanction letter. Every agent completes its task before handing control to the next one, creating a transparent and deterministic loan processing pipeline.

The project demonstrates how Agentic AI can be applied to automate traditional banking workflows while maintaining modularity, explainability, and scalability.

---

# Why This Project?

Traditional loan approval systems are often implemented as large monolithic applications where every responsibility is tightly coupled. Such systems become difficult to maintain, extend, and debug.

This project explores an alternative approach by introducing **AI agents** that specialize in individual business functions. Each agent acts independently, performs one responsibility, and passes structured information to the next agent in the workflow.

This makes the system:

* Easier to maintain
* Highly modular
* Scalable
* Explainable
* Suitable for future enterprise integrations

---

# Features

* Multi-Agent Loan Processing
* Secure Customer Authentication (JWT)
* Interactive AI Loan Assistant
* Real-time Application Progress
* Sequential Agent Execution
* Rule-based Loan Eligibility Checks
* Underwriting Analysis
* KYC Verification
* Automated Sanction Letter Generation
* Responsive React Frontend
* FastAPI REST Backend

---

# Tech Stack

## Frontend

* React
* Vite
* TypeScript
* Tailwind CSS
* Axios

## Backend

* FastAPI
* Python
* JWT Authentication
* Server Sent Events (SSE)
* Pydantic

## AI & Orchestration

* CrewAI
* Multi-Agent Workflow
* Sequential Agent Execution

## Storage

* JSON-based data store (for demo purposes)

---

# Agent Architecture

```text
                  Customer
                      │
                      ▼
              Authentication
                      │
                      ▼
              Checker Agent
                      │
                      ▼
               Sales Agent
                      │
                      ▼
           Underwriting Agent
                      │
                      ▼
          Verification Agent
                      │
                      ▼
        Sanction Letter Agent
                      │
                      ▼
          Final Loan Decision
```

Each agent has a single responsibility and communicates using structured outputs. The workflow is intentionally sequential, ensuring that no downstream agent executes unless the previous stage has completed successfully.

---

# Agentic Workflow

## 1. Customer Authentication

The customer signs in using a registered Customer ID and password. JWT authentication is used to secure all subsequent requests.

---

## 2. Checker Agent

The Checker Agent validates the customer's identity and verifies whether the customer exists in the system.

### Responsibilities

* Validate Customer ID
* Load customer profile
* Verify account availability
* Pass customer details to the Sales Agent

---

## 3. Sales Agent

The Sales Agent acts as the conversational assistant. It interacts with the customer to collect loan requirements and understands their borrowing needs.

### Responsibilities

* Understand loan intent
* Collect loan amount
* Collect tenure
* Collect expected interest rate
* Prepare structured application data

---

## 4. Underwriting Agent

The Underwriting Agent performs financial analysis and determines whether the requested loan satisfies predefined eligibility criteria.

### Responsibilities

* Income assessment
* EMI calculation
* Debt analysis
* Credit policy evaluation
* Eligibility decision

---

## 5. Verification Agent

Once underwriting is approved, the Verification Agent performs customer verification.

### Responsibilities

* KYC verification
* Identity validation
* Customer information verification
* Compliance checks

---

## 6. Sanction Letter Agent

If every previous stage succeeds, the Sanction Letter Agent generates the final approval document.

### Responsibilities

* Generate sanction details
* Prepare loan summary
* Generate approval response
* Return final loan decision

---

# Project Workflow

```text
Customer Login
      │
      ▼
Checker Agent
      │
      ▼
Sales Agent
      │
      ▼
Underwriting Agent
      │
      ▼
Verification Agent
      │
      ▼
Sanction Letter Agent
      │
      ▼
Loan Approved / Rejected
```

Each stage must successfully complete before the next one begins. This prevents invalid applications from progressing further into the pipeline.

---

# Project Structure

```text
.
├── frontend/
│   ├── src/
│   ├── components/
│   ├── pages/
│   └── api/
│
├── backend/
│   ├── loan_agents/
│   ├── APIs/
│   ├── services/
│   ├── data/
│   └── utils/
│
└── README.md
```

---

# API Endpoints

| Method | Endpoint       | Description             |
| ------ | -------------- | ----------------------- |
| POST   | `/auth/signup` | Register a customer     |
| POST   | `/auth/login`  | Customer login          |
| GET    | `/me`          | Get customer profile    |
| POST   | `/chat`        | Start loan conversation |
| GET    | `/health`      | Health check            |

---

# Running Locally

## Clone the Repository

```bash
git clone https://github.com/<your-username>/<repository>.git

cd <repository>
```

## Backend

```bash
cd backend

pip install -r requirements.txt

uvicorn APIs.main:app --reload
```

## Frontend

```bash
cd frontend

npm install

npm run dev
```

---

# Future Improvements

* PostgreSQL integration
* Real credit bureau APIs
* Banking API integration
* OCR-based document verification
* AI-powered risk scoring
* Email and SMS notifications
* Loan dashboard for bank employees
* Analytics and monitoring
* Docker & Kubernetes deployment
* CI/CD pipeline

---
