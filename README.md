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
    User(["User / Employee"]) -->|"Query + JWT Token"| API("FastAPI Security Gateway")
    
    subgraph "Secure RAG Architecture"
        API -->|"1. Validate JWT Role"| Auth{"RBAC Engine"}
        Auth -->|"Invalid"| 401["401 Unauthorized"]
        Auth -->|"Valid Role (e.g. HR)"| Embedder["Embedding Model"]
        
        Embedder -->|"Vector"| VDB[("Vector Database")]
        
        VDB -->|"2. Hard Filter applied:"| Filter["WHERE role = 'HR'"]
        Filter --> Context["Retrieve Allowed Context"]
    end
    
    Context -->|"3. Safe Context"| LLM(("LLM Generation"))
    LLM --> Answer["Secure Answer Generated"]
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

### 1. Run the Full Stack with Docker (Recommended)
You can launch the FastAPI Backend and the React Frontend simultaneously using Docker Compose.
```bash
# Clone the repository
git clone https://github.com/Vamshi868876/Secure-Enterprise-RAG.git
cd Secure-Enterprise-RAG

# Launch the entire architecture
docker-compose up --build
```
* The API will run on `http://localhost:8000`
* The React Chat UI will run on `http://localhost:5173`

### 2. Local Python & Node.js Setup
If you prefer running without Docker:
```bash
# Terminal 1: Run the Backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python populate_db.py
uvicorn main:app --reload

# Terminal 2: Run the React Frontend
cd frontend
npm install
npm run dev
```

## ☁️ AWS Cloud Deployment (Terraform)
This repository includes production-ready **Infrastructure-as-Code** to deploy the architecture to AWS ECS (Elastic Container Service) on Fargate.

```bash
cd terraform
terraform init
terraform plan
terraform apply
```
This automatically provisions the VPC, Subnets, Security Groups, Application Load Balancer, and the ECS Fargate Cluster.

## 🧪 Security Simulation (Hacker Test)

To prove the security works, open the React UI (`http://localhost:5173`) and test the two different JWT roles.

1. ❌ **Login as Software Engineer:** Attempt to ask "What is the CEO's salary?". The system mathematically blocks access to the HR documents at the Vector level. The AI is completely unaware of the salary.
2. ✅ **Login as HR Manager:** Ask the exact same question. The system verifies the role, unlocks access to the HR documents, and securely outputs the correct $850,000 salary.

---
*Built as a demonstration of Secure Enterprise AI Architecture.*
