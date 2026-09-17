# 📄 Intelligent Document Processing & Advanced RAG Engine

An **enterprise-grade Intelligent Document Processing (IDP) and Retrieval-Augmented Generation (RAG) platform** designed to automate **trade finance compliance, document parsing, business-rule verification, and penalty calculation**.

The system processes scanned trade-finance documents such as **Purchase Orders (POs), Letters of Credit (LCs), Goods Receipt Notes (GRNs), and Shipment Documents**. It combines **OCR, regex-based entity extraction, hybrid search, Reciprocal Rank Fusion (RRF), cross-encoder reranking, and deterministic business rules** to automate compliance workflows.

---

## 🚀 Overview

Traditional trade-finance compliance requires employees to manually inspect multiple documents, extract contractual information, compare fields, search regulatory policies, and calculate penalties.

This project automates that workflow through a multi-stage pipeline:

```text
Document Upload
       │
       ▼
┌─────────────────────────┐
│      OCR Processing     │
│      Pytesseract        │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   Entity Extraction     │
│     Regex + Parsing     │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────────────┐
│       Hybrid RAG Retrieval      │
│                                 │
│  BM25 ──────┐                   │
│             ├──► RRF             │
│  Dense ─────┘                   │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────┐
│ Cross-Encoder Reranking │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────────────┐
│      Business Rule Engine       │
│                                 │
│  • LC Compliance Checks         │
│  • Document Discrepancies       │
│  • Liquidated Damages (LD)      │
└────────────┬────────────────────┘
             │
             ▼
       Compliance Results
```

---

# 🌟 Key Features

## 1. 📑 Automated Document Processing

The system accepts scanned PDFs and document images and converts them into structured information.

### OCR Pipeline

**Pytesseract OCR** is used to convert document images into machine-readable text.

The extracted text is then processed using **regex-based parsing** to identify important contractual entities.

### Extracted Information

* Purchase Order (PO) numbers
* Vendor / Beneficiary names
* Contractual terms
* Payment terms
* Shipment dates
* Delivery dates
* Ports
* HS Codes
* Amounts
* LC expiry dates
* Partial shipment conditions
* OBIZ delivery dates

---

# 🔎 2. Advanced Hybrid RAG

The retrieval pipeline combines **sparse keyword search** and **dense semantic search**.

Instead of depending exclusively on vector similarity, the system uses two complementary retrieval strategies.

### Sparse Retrieval — BM25

BM25 is useful when exact terminology matters.

For example:

```text
Query:
"HS Code 8471"

Document:
"Commodity HS Classification: 8471"
```

BM25 can identify this type of exact lexical match effectively.

---

### Dense Retrieval — Embeddings

Dense retrieval converts documents and queries into vector representations using **Sentence Transformers**.

This allows the system to retrieve semantically similar information even when the wording is different.

For example:

```text
Query:
"Goods must be shipped before the specified date."

Document:
"Shipment shall occur no later than the contractual dispatch deadline."
```

Although the wording differs, dense embeddings can identify their semantic similarity.

---

# 🔀 3. Reciprocal Rank Fusion (RRF)

The results from BM25 and dense retrieval are combined using **Reciprocal Rank Fusion (RRF)**.

The general formulation is:

$$
RRF(d) =
\sum_{r \in R}
\frac{1}{k + rank_r(d)}
$$

Where:

* \(d\) = document/chunk
* \(R\) = set of retrieval systems
* \(rank_r(d)\) = rank of document \(d\) from retriever \(r\)
* \(k\) = smoothing constant

### Why RRF?

BM25 is strong at:

* Exact keywords
* Codes
* Numbers
* Regulatory terminology
* Contractual phrases

Dense retrieval is strong at:

* Semantic similarity
* Paraphrased content
* Conceptual relationships
* Natural-language queries

RRF combines the rankings from both approaches to create a stronger candidate set.

---

# 🎯 4. Cross-Encoder Reranking

After hybrid retrieval, the initial candidate documents are passed through a **Cross-Encoder**.

The Cross-Encoder evaluates the query and document together:

```text
Query + Document
       │
       ▼
 Cross-Encoder
       │
       ▼
Relevance Score
```

This allows the system to perform more precise contextual relevance scoring.

### Retrieval vs Reranking

```text
User Query
    │
    ▼
BM25 + Dense Retrieval
    │
    ▼
Top-K Candidates
    │
    ▼
Cross-Encoder
    │
    ▼
Final Ranked Results
```

The purpose of the reranking stage is to improve the relevance of the context that is passed to the downstream compliance logic.

---

# ⚙️ 5. Automated Business Rule Engine

The system uses deterministic business rules to evaluate trade-finance documents.

The rule engine performs:

* Letter of Credit compliance checks
* Multi-document discrepancy detection
* Contractual date validation
* Delivery-delay calculation
* Liquidated Damage calculation

---

# 💳 6. Letter of Credit Recommendations

The system evaluates payment and LC-related terms against relevant **UCP 600 alignment guidelines**.

It can identify potential inconsistencies between contractual requirements and the information present in the LC/document set.

> **Note:** The system is intended as an automated decision-support tool and does not replace professional legal, banking, or compliance review.

---

# 🔍 7. Six-Parameter Discrepancy Checks

The platform verifies consistency across six important Letter of Credit parameters.

| Parameter             | Validation                                                |
| --------------------- | --------------------------------------------------------- |
| **Beneficiary**       | Checks beneficiary consistency across documents           |
| **Port**              | Compares relevant shipment/loading/discharge ports        |
| **HS Code**           | Verifies product classification consistency               |
| **Amount**            | Compares financial amounts                                |
| **Expiry**            | Validates LC expiry information                           |
| **Partial Shipments** | Checks whether partial shipment conditions are consistent |

The output can be used to highlight potential document discrepancies before manual review.

---

# 💰 8. Liquidated Damage (LD) Calculation

The system automatically evaluates delivery delays using the agreed **OBIZ delivery schedule**.

The basic calculation is:

$$
Delay =
Actual\ Delivery\ Date -
Agreed\ OBIZ\ Date
$$

If:

$$
Actual\ Delivery\ Date > OBIZ\ Date
$$

the system identifies a delivery delay and applies the applicable contractual LD calculation.

### Example

```text
Agreed OBIZ Date : 10-Jan-2026
Actual Delivery  : 15-Jan-2026

Delay = 5 Days
```

The applicable contractual penalty rule can then be used to calculate the liquidated damages.

---

# 🏗️ System Architecture

```text
                    ┌───────────────────────────┐
                    │    Streamlit Frontend     │
                    │                           │
                    │ • File Upload             │
                    │ • Parameter Inputs        │
                    │ • Compliance Results      │
                    └─────────────┬─────────────┘
                                  │
                              HTTP/REST
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │     FastAPI Backend       │
                    │                           │
                    │ • API Endpoints           │
                    │ • Request Validation      │
                    │ • Application Lifecycle   │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │    IDP Processing Layer   │
                    │                           │
                    │ • Pytesseract OCR         │
                    │ • Text Extraction         │
                    │ • Regex Entity Parsing    │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
              ┌─────────────────────────────────────┐
              │          Advanced RAG Engine         │
              │                                     │
              │  ┌─────────────┐  ┌─────────────┐  │
              │  │    BM25     │  │   Dense     │  │
              │  │   Search    │  │ Embeddings  │  │
              │  └──────┬──────┘  └──────┬──────┘  │
              │         │                │          │
              │         └───────┬────────┘          │
              │                 ▼                   │
              │        Reciprocal Rank              │
              │           Fusion (RRF)              │
              │                 │                   │
              │                 ▼                   │
              │        Cross-Encoder               │
              │           Reranking                │
              └─────────────────┬───────────────────┘
                                │
                                ▼
                    ┌───────────────────────────┐
                    │   Business Rule Engine   │
                    │                           │
                    │ • LC Checks               │
                    │ • Discrepancy Detection   │
                    │ • LD Calculation           │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │     Compliance Output     │
                    └───────────────────────────┘
```

---

# 🔄 End-to-End Workflow

```text
1. Upload Documents
        ↓
2. OCR Processing
        ↓
3. Text Extraction
        ↓
4. Entity Extraction
        ↓
5. Document Chunking
        ↓
6. BM25 Retrieval
        +
   Dense Vector Retrieval
        ↓
7. Reciprocal Rank Fusion
        ↓
8. Cross-Encoder Reranking
        ↓
9. Relevant Context Selection
        ↓
10. Business Rule Evaluation
        ↓
11. LC Discrepancy Checks
        ↓
12. Delivery / LD Calculation
        ↓
13. Compliance Results
```

---

# 📁 Repository Structure

```text
Intelligent-Document-Processing-RAG-Engine/
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   │   └── FastAPI REST endpoints
│   │
│   ├── rag_engine.py
│   │   └── BM25 + Dense Retrieval + RRF + Reranking
│   │
│   ├── idp_pipeline.py
│   │   └── OCR + Entity Extraction
│   │
│   └── schemas.py
│       └── Pydantic validation models
│
├── frontend/
│   └── app.py
│       └── Streamlit Dashboard
│
├── sample_data/
│   └── Test contractual documents and scans
│
├── requirements.txt
│
└── README.md
```

---

# 🧩 Technology Stack

| Component           | Technology                 |
| ------------------- | -------------------------- |
| Frontend            | Streamlit                  |
| Backend             | FastAPI                    |
| API Validation      | Pydantic                   |
| OCR                 | Pytesseract                |
| Text Processing     | Python / Regex             |
| Sparse Retrieval    | BM25                       |
| Dense Retrieval     | Sentence Transformers      |
| Retrieval Fusion    | Reciprocal Rank Fusion     |
| Reranking           | Cross-Encoder              |
| Document Processing | Python                     |
| Architecture        | REST API                   |
| Domain              | Trade Finance / Compliance |

---

# 📌 Why Hybrid Search?

A trade-finance document contains many fields where **exact matching is extremely important**.

For example:

```text
PO Number: PO-2026-00451
HS Code: 847130
Amount: USD 125,000
```

A purely semantic retrieval system may not always prioritize these exact identifiers.

BM25 handles exact lexical matches, while dense retrieval handles semantic similarity.

Therefore:

```text
BM25
  +
Dense Retrieval
  ↓
RRF
  ↓
Better Candidate Retrieval
```

This is particularly useful for documents containing:

* PO numbers
* LC numbers
* HS codes
* Contract clauses
* Dates
* Financial values
* Regulatory terminology

---

# 🧠 Why RAG Instead of Only an LLM?

An LLM by itself may not have access to the organization's latest contractual policies or documents.

RAG provides external context at inference time.

```text
User Query
    ↓
Retriever
    ↓
Relevant Documents
    ↓
Context
    ↓
LLM / Compliance Logic
    ↓
Response
```

This helps the system ground its decisions in the available document corpus.

---

# 🛡️ RAG + Deterministic Rules

A key architectural principle of this project is separating **information retrieval** from **business-rule evaluation**.

### RAG is responsible for:

* Finding relevant clauses
* Retrieving contextual information
* Handling semantic search
* Finding supporting document evidence

### Business rules are responsible for:

* Field comparisons
* Date calculations
* Threshold checks
* LC discrepancy validation
* LD calculations

```text
                 ┌───────────────┐
                 │     RAG       │
                 │               │
                 │ Retrieve      │
                 │ Context       │
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │ Business Rule │
                 │    Engine     │
                 │               │
                 │ Validate      │
                 │ Calculate     │
                 └───────┬───────┘
                         │
                         ▼
                   Final Result
```

This separation helps reduce reliance on generative models for calculations and deterministic compliance checks.

---

# 📊 Example Input

A document set might contain:

```text
Purchase Order
        +
Letter of Credit
        +
Goods Receipt Note
        +
Shipment Document
```

The system extracts information such as:

```json
{
    "po_number": "PO-2026-00451",
    "beneficiary": "ABC International Ltd.",
    "hs_code": "847130",
    "amount": "125000 USD",
    "port": "Nhava Sheva",
    "expiry_date": "2026-04-30",
    "partial_shipments": "Not Allowed",
    "obiz_date": "2026-03-15"
}
```

The extracted entities can then be compared across documents and evaluated against the applicable business rules.

---

# 📤 Example Output

```text
========================================
        COMPLIANCE ANALYSIS
========================================

PO Number       : PO-2026-00451
Beneficiary     : ✓ Match
HS Code         : ✓ Match
Amount          : ✓ Match
Port            : ✓ Match
Expiry          : ✓ Valid
Partial Shipment: ✓ Consistent

----------------------------------------

OBIZ Date       : 15-Mar-2026
Actual Delivery : 20-Mar-2026
Delay           : 5 Days

LD Status       : Applicable
----------------------------------------

Overall Status  : REVIEW REQUIRED
========================================
```

---

# 🔌 API Architecture

The backend is implemented using **FastAPI** and exposes REST endpoints for communication with the Streamlit frontend.

```text
Streamlit
    │
    │ HTTP Request
    ▼
FastAPI
    │
    ├── Document Processing
    │
    ├── OCR
    │
    ├── Entity Extraction
    │
    ├── RAG Retrieval
    │
    └── Rule Engine
    │
    ▼
JSON Response
    │
    ▼
Streamlit Dashboard
```

This decoupled architecture allows the frontend and backend to be developed, tested, and deployed independently.

---

# 🖥️ Frontend

The Streamlit dashboard provides an interactive interface for:

* Uploading documents
* Entering required parameters
* Triggering document processing
* Viewing extracted entities
* Reviewing compliance checks
* Viewing retrieved context
* Reviewing discrepancies
* Viewing LD calculations

---

# 📦 Installation

## 1. Clone the Repository

```bash
git clone https://github.com/Ashis153/Intelligent-Document-Processing-RAG-Engine.git
```

```bash
cd Intelligent-Document-Processing-RAG-Engine
```

---

## 2. Create a Virtual Environment

Using Python:

```bash
python -m venv venv
```

Activate the environment.

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Running the Application

## Start the FastAPI Backend

From the project root:

```bash
uvicorn backend.main:app --reload
```

The API will be available locally through the configured FastAPI server.

---

## Start the Streamlit Frontend

In another terminal:

```bash
streamlit run frontend/app.py
```

The Streamlit dashboard will then open in your browser.

---

# 🧪 Sample Data

The `sample_data/` directory contains test documents used to demonstrate the pipeline.

Typical document categories include:

```text
sample_data/
│
├── purchase_orders/
├── letters_of_credit/
├── goods_receipts/
└── shipment_documents/
```

These documents can be processed through the IDP and RAG pipeline for testing.

---

# 🔬 Technical Highlights

### Intelligent Document Processing

```text
Scanned Document
       ↓
      OCR
       ↓
Raw Text
       ↓
Regex / Entity Extraction
       ↓
Structured Data
```

### Hybrid Retrieval

```text
             Query
               │
       ┌───────┴───────┐
       ▼               ▼
     BM25          Embeddings
       │               │
       └───────┬───────┘
               ▼
              RRF
               │
               ▼
       Candidate Documents
               │
               ▼
       Cross-Encoder
               │
               ▼
        Ranked Context
```

---

# 📈 Advantages

The architecture provides several advantages over a simple keyword-search or vector-only solution:

* **Better retrieval recall** through hybrid search
* **Better contextual precision** through cross-encoder reranking
* **Structured information extraction** from scanned documents
* **Automated compliance validation**
* **Deterministic calculations for contractual penalties**
* **Modular FastAPI backend**
* **Interactive Streamlit frontend**
* **Separation between retrieval and business logic**
* **Reduced dependence on manual document inspection**

---

# ⚠️ Limitations

The system may encounter challenges with:

* Poor-quality scanned documents
* Handwritten content
* Complex tables
* Unusual document layouts
* OCR recognition errors
* Ambiguous contractual language
* Conflicting information across documents

For production deployment, additional validation, human review, audit logging, access control, and domain-specific testing would be required.

---

# 🔮 Future Improvements

Potential improvements include:

### 1. Advanced Document Understanding

Integrate document-understanding models capable of handling:

* Tables
* Layouts
* Signatures
* Stamps
* Multi-column documents

### 2. Better Entity Extraction

Replace or complement regex with:

* Named Entity Recognition
* Layout-aware transformers
* LLM-based structured extraction

### 3. Vector Database

Introduce a production vector database such as:

```text
FAISS
Qdrant
Milvus
Pinecone
Weaviate
```

depending on deployment requirements.

### 4. Production Monitoring

Add:

* Retrieval metrics
* RAG evaluation
* Latency monitoring
* Error tracking
* Audit logs
* Document-processing statistics

### 5. Human-in-the-Loop Review

Introduce a workflow where high-risk or ambiguous cases are automatically sent to compliance professionals for verification.

---

# 📊 Evaluation Metrics

The retrieval component can be evaluated using metrics such as:

### Precision@K

$$
Precision@K =
\frac{\text{Relevant documents in top K}}
{K}
$$

### Recall@K

$$
Recall@K =
\frac{\text{Relevant documents retrieved}}
{\text{Total relevant documents}}
$$

### Mean Reciprocal Rank

$$
MRR =
\frac{1}{N}
\sum_{i=1}^{N}
\frac{1}{rank_i}
$$

These metrics can be used to compare:

```text
BM25
   vs
Dense Retrieval
   vs
Hybrid Retrieval
   vs
Hybrid + Reranking
```

---

# 🔐 Security Considerations

Trade-finance documents may contain confidential business information.

A production implementation should therefore consider:

* Authentication
* Authorization
* Role-based access control
* Encryption in transit
* Encryption at rest
* Secure document storage
* Access logging
* Data retention policies
* PII/confidential-data handling
* Audit trails

---

# 🧱 Design Principles

The project follows several important engineering principles:

### Modular Architecture

Each major responsibility is separated:

```text
Frontend
   ↓
API
   ↓
IDP
   ↓
RAG
   ↓
Business Rules
```

### Separation of Concerns

OCR, retrieval, reranking, and business-rule calculations are independent components.

### Deterministic Business Logic

Calculations and contractual comparisons should be handled by explicit rules rather than relying solely on generative model outputs.

### Retrieval Grounding

Compliance-related contextual information should be supported by retrieved document evidence.

---

# 🎯 Project Objectives

The primary objectives of this project are:

1. Automate extraction of information from trade-finance documents.
2. Reduce manual document verification.
3. Improve retrieval of relevant compliance clauses.
4. Detect discrepancies across multiple documents.
5. Automate contractual delivery-delay calculations.
6. Provide a modular API-driven architecture.
7. Create an extensible foundation for enterprise compliance automation.

---

# 🏆 Key Takeaway

This project combines:

```text
OCR
 +
NLP
 +
Information Retrieval
 +
Dense Embeddings
 +
Hybrid Search
 +
RRF
 +
Cross-Encoder Reranking
 +
Business Rules
 +
FastAPI
 +
Streamlit
```

to build an end-to-end **Intelligent Document Processing and RAG platform for trade-finance compliance automation**.

---

# 👨‍💻 Author

**Ashish Kumar**

Final-Year Student
**BIT Mesra**

Interested in:

* Data Science
* Business Intelligence
* Machine Learning
* Generative AI
* Intelligent Automation

---

# ⭐ Project Highlights

```text
📄 Intelligent Document Processing
🔎 Hybrid RAG Retrieval
🔀 BM25 + Dense Search
🎯 Reciprocal Rank Fusion
🧠 Cross-Encoder Reranking
💳 Letter of Credit Compliance
🔍 Multi-Parameter Discrepancy Detection
💰 Liquidated Damage Calculation
⚡ FastAPI Backend
🖥️ Streamlit Dashboard
```

---

## 📜 License

This project is intended for educational, research, and demonstration purposes. Add an appropriate open-source license here if the repository is intended for public distribution.

