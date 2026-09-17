# 📄 Intelligent Document Processing & Advanced RAG Engine

An enterprise-grade Intelligent Document Processing (IDP) and Retrieval-Augmented Generation (RAG) platform built to automate trade finance compliance, document parsing, and business-rule verification. 

Designed specifically for finance workflows (Purchase Orders, Bank Letters of Credit, Goods Receipt Notes, and Shipment Documents), this system reads scanned trade files, extracts critical entities, matches document text against compliance policies using Hybrid Search, and calculates automated Liquidated Damage (LD) penalties.

---

## 🌟 Key Features

* **Automated Document Extraction (OCR + Regex):** Digits scanned PDFs/images using **Pytesseract** and regex-based parsing to extract structured contractual fields (PO numbers, vendors, terms, OBIZ delivery dates).
* **Advanced Hybrid Retrieval (RAG):** Combines **BM25 (Sparse Keyword Search)** and **Dense Vector Embeddings** merged via **Reciprocal Rank Fusion (RRF)** for maximum search recall.
* **Cross-Encoder Reranking:** Re-scores initial document chunks through a Cross-Encoder model to surface exact contextual regulatory clauses before passing context to downstream logic.
* **Automated Business Rule Engine:**
  * **LC Recommendations:** Evaluates payment terms against UCP 600 alignment guidelines.
  * **6-Parameter Discrepancy Checks:** Verifies matching across key fields (Beneficiary, Port, HS Code, Amount, Expiry, Partial Shipments).
  * **Liquidated Damage (LD) Calculation:** Compares actual delivery dates against OBIZ agreed schedules to compute penalty deductibles.
* **Full-Stack Architecture:** RESTful **FastAPI** backend decoupled from an interactive **Streamlit** dashboard.

---

## 🏗️ System Architecture
┌───────────────────────────┐
│ Streamlit Frontend App    │  <-- Drag & Drop File Upload / Parameter Inputs
└─────────────┬─────────────┘
│ HTTP / REST API
▼
┌───────────────────────────┐
│ FastAPI Backend Server    │
├───────────────────────────┤
│ • Pytesseract OCR Layer   │  <-- Converts visual document pixels into text
│ • Regex Entity Parser     │  <-- Extracts PO #, Vendor, Terms, Dates
└─────────────┬─────────────┘
│
▼
┌───────────────────────────┐
│ Advanced RAG Engine       │
├───────────────────────────┤
│ • Sparse BM25 Search      │  <-- Exact keyword/code matching
│ • Dense Embeddings        │  <-- Semantic similarity (Sentence-Transformers)
│ • Reciprocal Rank Fusion │  <-- Merges sparse + dense candidate lists
│ • Cross-Encoder Reranker  │  <-- Re-scores top-k results for precise context
└─────────────┬─────────────┘
│
▼
┌───────────────────────────┐
│ Rule & Penalty Engine     │  <-- Evaluates 6-Parameter LC Checks & OBIZ LD Fines
└───────────────────────────┘


---

## 📁 Repository Structure

```text
Intelligent-Document-Processing-RAG-Engine/
│
├── backend/
│   ├── __init__.py
│   ├── main.py             # FastAPI REST endpoints & application lifecycle
│   ├── rag_engine.py       # Advanced RAG pipeline (BM25 + Dense + Reranker)
│   ├── idp_pipeline.py     # OCR document ingestion & entity extraction
│   └── schemas.py          # Pydantic data validation models
│
├── frontend/
│   └── app.py              # Streamlit interactive dashboard UI
│
├── sample_data/            # Test contractual document text files & scans
├── requirements.txt        # Python package dependencies
└── README.md               # Project documentation
