# 🚀 FAANG 50 LPA Interview Guide: Secure RAG Architecture

To secure a 50 LPA package at Google, Meta, or Microsoft, you are interviewing for a **Senior/Staff AI Architect** role. Interviewers will not just ask *what* you built; they will aggressively ask **WHY** you chose specific algorithms, data structures, and system designs over others.

Use these highly technical, trade-off-focused answers to dominate your interview.

---

## 1. The Algorithm Deep-Dive
**Interviewer:** *"Why did you use Cosine Similarity for the vector search instead of Euclidean Distance or Dot Product?"*

**The 50 LPA Answer:**
> "In RAG systems, the magnitude (length) of the document vector is often irrelevant; we care about the *directional angle* between the user's query and the document, which represents semantic similarity. **Cosine Similarity** mathematically normalizes the vectors, ensuring that a very long document and a short query can still match perfectly if they point in the same semantic direction. 
>
> If I used **Euclidean Distance (L2)**, longer documents would be unfairly penalized. While **Dot Product** is computationally faster, it only works accurately if all vectors are pre-normalized. For a scalable enterprise RAG, Cosine Similarity guarantees the most accurate semantic retrieval regardless of text chunk length."

---

## 2. The Vector Filtering Trade-off (The "Gotcha" Question)
**Interviewer:** *"How exactly did you implement the Role-Based Access Control? Did you filter the vectors before or after the semantic search?"*

**The 50 LPA Answer:**
> "This is the classic **Pre-filtering vs. Post-filtering** trade-off in Vector Databases. 
> 
> If you do **Post-filtering** (finding the top 5 vectors, and *then* checking if the user has access), you risk returning 0 results if all top 5 happen to be restricted documents. It ruins the user experience.
>
> Instead, I implemented **Pre-filtering**. Before the Cosine Similarity calculation even begins, the system pushes down the JWT Role parameter (e.g., `WHERE role = 'HR'`) directly into the database engine. The DB masks out unauthorized vectors in `O(1)` time using a hash index on the metadata, and *then* performs the vector search only on the allowed subset. This guarantees we always return the top authorized documents while completely eliminating data leakage."

---

## 3. The Embedding Model Selection
**Interviewer:** *"Why use a local HuggingFace/SentenceTransformer model instead of OpenAI's `text-embedding-ada-002`?"*

**The 50 LPA Answer:**
> "For a highly secure Enterprise application (like banking or healthcare), sending sensitive internal documents to a third-party API like OpenAI for embedding violates strict compliance laws (GDPR/HIPAA). 
>
> By using a local, open-source model like `all-MiniLM-L6-v2`, we keep the entire embedding pipeline inside our own Virtual Private Cloud (VPC). Furthermore, `MiniLM` produces a 384-dimensional vector, which is 4x smaller than OpenAI's 1536-dimensional vectors. This reduces our Vector Database RAM footprint by 75% and drastically speeds up the `O(N * D)` cosine similarity calculation, without a noticeable drop in retrieval accuracy for standard corporate text."

---

## 4. State & Authentication
**Interviewer:** *"Why did you use JWTs instead of traditional server-side session cookies?"*

**The 50 LPA Answer:**
> "To reach true FAANG scale, the backend must be **Stateless**. If I used server-side sessions, deploying this across 100 AWS Fargate containers would require a sticky-session load balancer or a central Redis cache just to remember who is logged in, which introduces a Single Point of Failure (SPOF) and latency.
>
> **JWT (JSON Web Tokens)** are cryptographically signed using the `HS256` algorithm. The FastAPI backend doesn't need to query a database to know the user's role; it just verifies the cryptographic signature in memory in microseconds. This allows the microservice to scale infinitely horizontally."

---

## 5. System Design & Deployment
**Interviewer:** *"How is this deployed, and how does it scale?"*

**The 50 LPA Answer:**
> "The entire architecture is containerized and deployed using **Terraform** (Infrastructure as Code) to **AWS ECS Fargate**. 
>
> I decoupled the architecture: The React frontend is served via a CDN, while the FastAPI backend sits behind an Application Load Balancer. The Vector Database is mocked locally for development, but in production, Terraform seamlessly swaps it out for a managed distributed vector store like Pinecone. This ensures we can scale from 10 users to 10 million users with zero downtime."

---

## 💡 The "Secret" to Passing at the 50 LPA Level:
When speaking, **always mention the trade-offs.** Senior Engineers don't just say "I did X." They say, *"I could have done Y, but because of memory constraints and security, I chose X."* Use the answers above exactly as written, and you will sound like a tech lead.
