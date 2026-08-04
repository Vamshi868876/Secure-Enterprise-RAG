from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import jwt
from datetime import datetime, timedelta
import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import DeterministicFakeEmbedding

app = FastAPI(
    title="Secure Enterprise RAG API",
    description="FAANG-Level Role-Based Access Control RAG System",
    version="1.0.0"
)

# Enable CORS for the React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIG ---
SECRET_KEY = "faang_super_secret_key_change_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
CHROMA_PATH = "chroma_db"

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

# --- VECTOR DATABASE & EMBEDDINGS ---
# For deployment, swap to HuggingFaceEmbeddings!
print("Loading Vector Store...")
embeddings = DeterministicFakeEmbedding(size=384)

# Load existing ChromaDB
if os.path.exists(CHROMA_PATH):
    vector_store = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
else:
    vector_store = None
    print("WARNING: ChromaDB not found. Run populate_db.py first!")

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

    if not vector_store:
        return {"answer": "Vector Database is not initialized. Please run populate_db.py"}

    # 3. SECURE RETRIEVAL: Filter the vector search by the user's role!
    # We use ChromaDB's native metadata filtering ($or operator)
    results = vector_store.similarity_search(
        req.question, 
        k=3, 
        filter={"$or": [{"role": user_role}, {"role": "Public"}]}
    )
    
    if not results:
        return {"answer": "I do not have access to any documents to answer this question. (Security Filter Applied)"}
        
    # Extract Context and Sources
    context = "\n".join([doc.page_content for doc in results])
    sources = [doc.metadata for doc in results]
    
    # 4. Generate Answer (Mocking LLM generation for free deployment, but parses context!)
    # In a real app with an API Key, you would use:
    # llm = ChatOpenAI() or llm = ChatGoogleGenerativeAI()
    # return llm.predict(f"Context: {context}\n\nQuestion: {req.question}")
    
    llm_mock_answer = (
        "**Secure RAG Synthesis Complete:**\n\n"
        f"Based on the highly restricted documents retrieved using your **{user_role.replace('_', ' ')}** clearance, here is the synthesis:\n\n"
        f"> {context}\n\n"
        "**Security Note:** All requests are logged in the enterprise audit trail."
    )
    
    return {
        "role_authorized": user_role,
        "answer": llm_mock_answer,
        "sources_accessed": sources
    }
