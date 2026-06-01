from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import jwt
from datetime import datetime, timedelta

app = FastAPI(
    title="Secure Enterprise RAG API",
    description="FAANG-Level Role-Based Access Control RAG System",
    version="1.0.0"
)

# --- CONFIG ---
SECRET_KEY = "faang_super_secret_key_change_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- MODELS ---
class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class QueryRequest(BaseModel):
    question: str

# --- MOCK DATABASE ---
# In a real system, this comes from a Postgres database
USERS = {
    "alice_hr": {"password": "password123", "role": "HR_Manager"},
    "bob_eng": {"password": "password123", "role": "Software_Engineer"}
}

# --- AUTHENTICATION ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/token", response_model=Token)
async def login(req: LoginRequest):
    user = USERS.get(req.username)
    if not user or user["password"] != req.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": req.username, "role": user["role"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "role": user["role"]}

import json
import hashlib
import math
import os

class MockEmbeddings:
    def embed_documents(self, texts):
        return [self.embed_query(text) for text in texts]
        
    def embed_query(self, text):
        h = hashlib.sha256(text.encode()).digest()
        return [(b / 128.0) - 1.0 for b in h[:64]]

def cosine_similarity(v1, v2):
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0 or norm2 == 0: return 0
    return dot / (norm1 * norm2)

class SimpleSecureVectorDB:
    def __init__(self, db_path):
        self.db_path = db_path
        self.data = []
            
    def load(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r') as f:
                self.data = json.load(f)
                
    def query(self, query_embeddings, n_results=3, where=None):
        query_vec = query_embeddings[0]
        results = []
        for item in self.data:
            # APPLY SECURE RBAC FILTERING
            if where:
                conditions = where.get("$or", [])
                allowed = False
                for cond in conditions:
                    for k, v in cond.items():
                        if item["metadata"].get(k) == v:
                            allowed = True
                if not allowed:
                    continue # SECURITY BLOCK
                    
            sim = cosine_similarity(query_vec, item["embedding"])
            results.append((sim, item))
            
        results.sort(key=lambda x: x[0], reverse=True)
        top_results = results[:n_results]
        
        if not top_results:
            return {"documents": [[]], "metadatas": [[]]}
            
        return {
            "documents": [[r[1]["document"] for r in top_results]],
            "metadatas": [[r[1]["metadata"] for r in top_results]]
        }

print("Loading custom secure vector database...")
embeddings = MockEmbeddings()
db = SimpleSecureVectorDB("secure_vector_store.json")
db.load()

def get_current_user_role(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("role")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/query")
async def secure_query(req: QueryRequest, token: str):
    # 1. Authenticate & Get Role
    user_role = get_current_user_role(token)
    if not user_role:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    print(f"User authenticated with role: {user_role}")

    # 2. Embed the question
    question_vector = embeddings.embed_query(req.question)

    # 3. SECURE RETRIEVAL: Hard-filter the vector search by the user's role!
    results = db.query(
        query_embeddings=[question_vector],
        n_results=3,
        where={"$or": [{"role": user_role}, {"role": "Public"}]}
    )
    
    if not results['documents'][0]:
        return {"answer": "I do not have access to any documents to answer this question."}
        
    context = "\n".join(results['documents'][0])
    sources = results['metadatas'][0]
    
    # 4. Generate Answer (Mocking LLM generation for now to avoid needing OpenAI keys)
    llm_mock_answer = f"Based on the secure documents I found:\n\n{context}"
    
    return {
        "role_authorized": user_role,
        "answer": llm_mock_answer,
        "sources_accessed": sources
    }
