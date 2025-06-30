# 📄 PDF Chatbot RAG

An AI-powered chatbot designed to answer queries from complex PDF documents using a full RAG-based pipeline.

---

## 🔧 Technologies Used

- **FastAPI** – REST API backend  
- **OpenAI** – Language models for embeddings and response generation  
- **LangChain & LangGraph** – RAG orchestration & knowledge graph capabilities  
- **Redis** – Task queue for handling PDF processing  
- **PDF‑to‑Image** – Layout parsing support  
- **QdrantDB** – Vector store for semantic search  
- **Neo4j** – Knowledge graph for structured context  
- **MongoDB** – Metadata & chat history storage (for long‑term context)  
- **Docker & DevContainers** – Containerized and reproducible environment  

---

## 🚀 Features

1. **Concurrent PDF Processing**  
   - Uploaded PDFs are queued via Redis and processed asynchronously.
   - Generates embeddings, images, semantic vectors, and knowledge graph entries.

2. **Semantic QA**  
   - Queries are answered using semantic search with embeddings in Qdrant.
   - Responses are enriched using context from Neo4j graph.

3. **Contextual Memory**  
   - MongoDB stores prior chats for long-term session context.

4. **Real-world PDF Handling**  
   - Layout-based parsing using PDF-to-image conversion.
   - OCR-ready for structured documents.

5. **Scalable, Deployable**  
   - Dockerized services (API, Redis, Qdrant, Neo4j, MongoDB).
   - Run in dev or production configurations via DevContainer.

---

## 🗂️ Repository Structure


---

## 🛠️ Setup & Run

### Prerequisites

- Docker & Docker Compose
- OpenAI API key (set in `.env`)
- Cohere API Key (set in `.env`)
- MongoURL (set in `.env`)
- GPU server (optional for image processing and embeddings)

### Quick Start (Docker)

```bash
git clone https://github.com/kratinsoni/Pdf-Chatbot-Rag.git
cd Pdf-Chatbot-Rag
cp .env.example .env             # Fill in `OPENAI_API_KEY`
docker compose up --build -d    # Launch all services

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m app.main.py
rq worker --with-scheduler --url redis://valkey:6379         # Start PDF ingestion manually
