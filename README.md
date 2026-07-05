# Procurement Intel Core

> Local AI-powered backend pipeline for extracting SLA penalty clauses from procurement contracts and calculating financial leakage using deterministic backend services.

---

# Background

One observation repeatedly stood out to me while studying industrial automation and enterprise systems.

Most companies already operate sophisticated ERP platforms capable of processing millions of transactional records with remarkable accuracy. Purchase Orders, invoices, vendor payments, delivery dates, and inventory movements are all stored in structured relational databases.

Ironically, the business rules governing those transactions often remain trapped inside lengthy procurement contracts written as unstructured PDF documents.

A procurement contract may clearly define:

- Service Level Agreements (SLAs)
- Late delivery penalties
- Maximum penalty caps
- Grace periods
- Escalation clauses
- Discount agreements

Yet none of these contractual rules are directly available to the ERP system.

When a vendor delivers products late, procurement officers frequently need to:

1. Locate the original PDF contract.
2. Search dozens or hundreds of pages using **Ctrl + F**.
3. Read dense legal language.
4. Identify the relevant SLA clause.
5. Interpret the legal wording.
6. Calculate the financial penalty manually using a calculator or spreadsheet.

The ERP system knows **what happened**.

The contract knows **what should happen**.

The missing component is the bridge between qualitative legal language and quantitative operational data.

This project was built to create that bridge.

Instead of asking human operators to repeatedly perform document retrieval, legal interpretation, and manual calculations, Procurement Intel Core delegates the extraction process to a fully local Large Language Model operating inside a deterministic backend architecture.

The AI performs the tedious document understanding.

The backend converts legal language into structured relational records.

The analytics engine performs deterministic financial calculations.

Human decision-makers can then focus on evaluating procurement performance, negotiating vendor relationships, and making strategic business decisions rather than spending valuable cognitive effort searching PDFs.

This project reflects the type of engineering problems I enjoy solving—designing robust backend architectures that transform ambiguous real-world information into reliable, machine-readable systems.

---

# System Architecture

```
                Procurement Contract (PDF)
                          │
                          ▼
                 FastAPI Upload Endpoint
                          │
                          ▼
                pdfplumber Text Extraction
                          │
                          ▼
               Sequential Contract Parsing
                          │
                          ▼
        Local Llama 3 8B (Ollama - Offline)
                          │
                          ▼
        Deterministic JSON SLA Extraction
                          │
                          ▼
                  PostgreSQL Persistence
                          │
                          ▼
              SLA Terms Relational Database
                          │
                          ▼
       Pandas Financial Leakage Calculation
                          │
                          ▼
                  REST API JSON Response
```

---

# Technology Stack

| Layer | Technology |
|---------|------------|
| Backend API | FastAPI |
| AI Runtime | Ollama |
| Language Model | Llama 3 8B |
| PDF Parsing | pdfplumber |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Analytics | Pandas |
| Containerization | Docker |
| API Server | Uvicorn |

---

# Architecture & Data Pipeline

## 1. Ingestion Layer

The backend exposes an asynchronous REST API built with FastAPI.

Clients upload procurement contracts together with the associated vendor identifier.

```
POST /api/v1/contracts/upload
```

Responsibilities:

- Accept PDF contracts
- Validate request payload
- Store uploaded document
- Trigger downstream processing pipeline

---

## 2. Parsing Layer

Uploaded contracts are parsed using **pdfplumber**.

The objective is to preserve the sequential flow of legal clauses while extracting raw textual content without introducing structural ambiguity.

Responsibilities:

- Extract text from PDF
- Preserve clause ordering
- Maintain document readability
- Prepare content for language model inference

---

## 3. Cognitive Core

The extracted contract is passed to a locally hosted **Llama 3 8B** model running through **Ollama**.

Rather than generating free-form summaries, the model is instructed to perform deterministic information extraction.

Expected outputs include:

- Penalty rate
- Grace period
- Maximum penalty cap
- SLA duration
- Clause identifier

The model is constrained to emit a strict JSON schema suitable for backend validation.

Example:

```json
{
    "clause_id": "5.2",
    "penalty_rate_per_week": 0.02,
    "max_penalty_cap": 0.10,
    "grace_period_days": 7
}
```

---

## 4. Persistence Layer

Validated extraction results are persisted into PostgreSQL.

Example relational table:

```
sla_terms
```

| Column | Description |
|----------|-------------|
| id | Primary key |
| vendor_id | Vendor identifier |
| contract_id | Source contract |
| clause_id | Legal clause reference |
| penalty_rate_per_week | Weekly penalty percentage |
| max_penalty_cap | Maximum contractual penalty |
| grace_period_days | Grace period before penalty |

The database becomes the single source of truth for contractual SLA parameters.

---

## 5. Analytics Engine

The analytics engine retrieves:

- Contractual SLA rules
- ERP delivery records

Using Pandas, both datasets are cross-referenced to calculate potential financial leakage caused by late deliveries.

Example calculations include:

- Delivery delay
- Applicable penalty rate
- Maximum penalty cap
- Final penalty amount

Unlike the extraction stage, this component is completely deterministic and does not require any AI inference.

---

# Project Structure

```
procurement-intel/
│
├── app/
│   ├── routers/
│   ├── services/
│   ├── repositories/
│   ├── schemas/
│   ├── prompts/
│   └── core/
│
├── migrations/
├── tests/
├── scripts/
├── docker-compose.yml
├── Dockerfile.api
└── README.md
```

---

# REST API

---

## Upload Procurement Contract

### Endpoint

```http
POST /api/v1/contracts/upload
```

### Form Data

| Field | Type |
|---------|------|
| vendor_id | Integer |
| file | PDF |

### Response

```json
{
    "status": "success",
    "message": "Contract uploaded successfully.",
    "vendor_id": 42,
    "processing_status": "queued"
}
```

---

## Financial Leakage Analysis

### Endpoint

```http
GET /api/v1/leakage-analysis
```

### Response

```json
{
    "vendor_id": 42,
    "purchase_order_id": "PO-2025-00412",
    "days_of_delay": 16,
    "contract_penalty_rate_per_week": 0.02,
    "contract_max_penalty_cap": 0.10,
    "calculated_leakage_amount": 18450000
}
```

---

## Health Check

### Endpoint

```http
GET /health
```

### Response

```json
{
    "status": "healthy",
    "database": "connected",
    "ollama": "online",
    "api": "running"
}
```

---

# Deployment

## 1. Start PostgreSQL

```bash
docker-compose up -d postgres
```

---

## 2. Pull Llama 3 via Ollama

```bash
ollama pull llama3:8b
```

---

## 3. Start FastAPI

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```
http://localhost:8000
```

Interactive API documentation:

```
http://localhost:8000/docs
```

---

# Design Principles

- Deterministic backend architecture
- Local AI inference (no external API dependency)
- Clear separation of concerns
- Strict schema validation
- Structured relational persistence
- Reproducible financial calculations
- Maintainable service-oriented codebase

---

# Future Improvements

- Vector search using pgvector
- Retrieval-Augmented Generation (RAG) for contract querying
- Multi-contract comparison
- Vendor performance dashboards
- Background processing workers
- OCR support for scanned contracts
- Role-based access control (RBAC)
- Audit logging for AI extraction results

---

# License

This project is intended for educational, portfolio, and research purposes.