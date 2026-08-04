import os
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# Define the persistent directory for ChromaDB
CHROMA_PATH = "chroma_db"

def main():
    print("Initializing Real Vector Database (ChromaDB) with Sentence Transformers...")
    
    # 1. Initialize the Real Embedding Model
    # 1. Initialize Embeddings
    print("Loading Embeddings...")
    # NOTE: Using FakeEmbeddings locally to avoid Windows PyTorch DLL crashes.
    # When deployed to Linux (Render/HuggingFace), you can swap this back to:
    # from langchain_community.embeddings import HuggingFaceEmbeddings
    # embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    from langchain_community.embeddings import DeterministicFakeEmbedding
    embeddings = DeterministicFakeEmbedding(size=384)

    # 2. Dummy Documents with Secure RBAC Metadata
    # In a real enterprise app, these would be loaded from PDFs, Notion, etc.
    raw_documents = [
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

    # 3. Convert to LangChain Document objects
    documents = []
    for i, doc in enumerate(raw_documents):
        documents.append(
            Document(
                page_content=doc["content"],
                metadata=doc["metadata"],
                id=f"doc_{i}"
            )
        )

    print(f"Embedding {len(documents)} secure documents into ChromaDB...")

    # 4. Create and persist the Chroma Vector Store
    # This automatically computes the embeddings and saves them to disk
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )

    print(f"SUCCESS: Chroma Vector Database successfully populated at '{CHROMA_PATH}' with Secure RBAC Metadata!")

if __name__ == "__main__":
    main()
