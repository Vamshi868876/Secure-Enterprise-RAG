# Secure Enterprise RAG Architecture 🛡️

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Security](https://img.shields.io/badge/security-RBAC%20Enabled-blue)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-teal)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

A production-grade **Retrieval-Augmented Generation (RAG)** API designed with **Zero-Trust Security** and **Role-Based Access Control (RBAC)**. This architecture prevents Large Language Models (LLMs) from leaking sensitive enterprise data (e.g., HR salaries, Engineering passwords) to unauthorized users by enforcing cryptographic hard-filters at the Vector Database level.

## 🌟 The Problem it Solves
Standard RAG systems connect an LLM to a unified Vector Database, meaning any user can query any document. If an intern asks a standard RAG system for the CEO's salary, the AI will confidently expose it. 

This project solves this by wrapping the Vector Database in a secure JWT-authenticated API that intercepts the query and injects cryptographic role-metadata filtering.

## 🏗️ Architecture Diagram

```mermaid
graph TD
    User([User / Employee]) -->|Query + JWT Token| API(FastAPI Security Gateway)
    
    subgraph "Secure RAG Architecture"
        API -->|1. Validate JWT Role| Auth{RBAC Engine}
        Auth -->|Invalid| 401[401 Unauthorized]
        Auth -->|Valid Role (e.g. HR)| Embedder[Embedding Model]
        
        Embedder -->|Vector| VDB[(Vector Database)]
        
        VDB -->|2. Hard Filter applied:| Filter["WHERE role = 'HR'"]
        Filter --> Context[Retrieve Allowed Context]
    end
    
    Context -->|3. Safe Context| LLM((LLM Generation))
    LLM --> Answer[Secure Answer Generated]
    Answer --> User
```

## 🚀 Features
* **Zero-Trust Vector Retrieval:** Documents are tagged with security metadata upon ingestion. The API physically blocks unauthorized retrieval.
* **JWT Authentication:** Cryptographically signed tokens prove the user's role (`HR_Manager`, `Software_Engineer`, etc.).
* **Dockerized:** Fully containerized microservice ready for AWS ECS, Google Cloud Run, or Kubernetes.
* **FastAPI Backend:** High performance asynchronous Python API.

## 🛠️ Tech Stack
* **Framework:** FastAPI, Uvicorn
* **Security:** PyJWT, hashlib
* **AI/ML:** LangChain, HuggingFace SentenceTransformers
* **Vector DB:** ChromaDB (Mocked for cross-platform compatibility)
* **DevSecOps:** Docker

## 🚀 Quick Start

### 1. Local Python Setup
```bash
# Clone the repository
git clone https://github.com/Vamshi868876/Secure-Enterprise-RAG.git
cd Secure-Enterprise-RAG

# Create virtual environment & install
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Populate the Secure Vector Database
python populate_db.py

# Run the API server
uvicorn main:app --reload
```

### 2. Docker Deployment
```bash
docker build -t secure-rag-api .
docker run -p 8000:8000 secure-rag-api
```

## 🧪 Security Simulation (Hacker Test)

To prove the security works, run the included `test_rag.py` simulation. 
It attempts to steal the CEO's salary using two different JWT tokens.

```bash
python test_rag.py
```

**Results:**
1. ❌ **As Software Engineer:** The system blocks access to the HR documents. The AI is completely unaware of the salary.
2. ✅ **As HR Manager:** The system verifies the role, allows access to the HR documents, and outputs the correct $850,000 salary.

---
*Built as a demonstration of Secure Enterprise AI Architecture.*
