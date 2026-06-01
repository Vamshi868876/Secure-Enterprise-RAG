import json
import hashlib
import math
import os

class MockEmbeddings:
    def embed_documents(self, texts):
        return [self.embed_query(text) for text in texts]
        
    def embed_query(self, text):
        h = hashlib.sha256(text.encode()).digest()
        # Create a simple 64-dimensional vector
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
        
    def add(self, embeddings, documents, metadatas, ids):
        for emb, doc, meta, _id in zip(embeddings, documents, metadatas, ids):
            self.data.append({
                "id": _id,
                "embedding": emb,
                "document": doc,
                "metadata": meta
            })
        with open(self.db_path, 'w') as f:
            json.dump(self.data, f)
            
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
                    continue # SECURITY BLOCK: User not allowed to see this document
                    
            sim = cosine_similarity(query_vec, item["embedding"])
            results.append((sim, item))
            
        results.sort(key=lambda x: x[0], reverse=True)
        top_results = results[:n_results]
        
        return {
            "documents": [[r[1]["document"] for r in top_results]],
            "metadatas": [[r[1]["metadata"] for r in top_results]]
        }

if __name__ == "__main__":
    print("Initializing Custom Secure Vector Database...")
    embeddings = MockEmbeddings()
    db = SimpleSecureVectorDB("secure_vector_store.json")

    # Dummy Documents
    documents = [
        {
            "content": "The CEO's base salary for 2026 is $850,000 with a potential performance bonus of $2,000,000. Access restricted to HR.",
            "metadata": {"role": "HR_Manager", "source": "ceo_compensation.pdf"}
        },
        {
            "content": "All software engineers will receive a 15% bonus this year if the product launches on time.",
            "metadata": {"role": "HR_Manager", "source": "engineering_bonuses.pdf"}
        },
        {
            "content": "The production database password is 'SuperSecretDBPass2026!'. Ensure this is never committed to GitHub.",
            "metadata": {"role": "Software_Engineer", "source": "infrastructure_secrets.md"}
        },
        {
            "content": "Our AWS architecture uses 5 EKS clusters in us-east-1 and a multi-region RDS setup.",
            "metadata": {"role": "Software_Engineer", "source": "aws_architecture.md"}
        },
        {
            "content": "The company was founded in 2010. We have 500 employees worldwide.",
            "metadata": {"role": "Public", "source": "company_handbook.pdf"}
        }
    ]

    print(f"Embedding {len(documents)} secure documents into the Vector Database...")

    docs = [doc["content"] for doc in documents]
    metadatas = [doc["metadata"] for doc in documents]
    ids = [f"doc_{i}" for i in range(len(documents))]

    vectors = embeddings.embed_documents(docs)

    db.add(
        embeddings=vectors,
        documents=docs,
        metadatas=metadatas,
        ids=ids
    )

    print("SUCCESS: Custom Vector Database populated with Secure RBAC Metadata!")
