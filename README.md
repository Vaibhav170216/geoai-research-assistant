# 🌍 GeoAI Research Assistant

<p align="center">
  <img src="images/app.png" alt="GeoAI Research Assistant" width="1000"/>
</p>

<p align="center">
An end-to-end <b>Retrieval-Augmented Generation (RAG)</b> system for exploring <b>GeoAI</b>, <b>Earth Observation</b> and <b>Remote Sensing</b> research papers using hybrid retrieval and Large Language Models.
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![RAG](https://img.shields.io/badge/RAG-Hybrid-green)
![SQLite](https://img.shields.io/badge/SQLite-FTS-blue)
![SentenceTransformers](https://img.shields.io/badge/SentenceTransformers-Embeddings-orange)
![Evaluation](https://img.shields.io/badge/RAGAS-Evaluated-success)

</p>

---

# 📖 Overview

GeoAI Research Assistant helps researchers, students and practitioners efficiently explore scientific literature without manually searching through hundreds of papers.

The system combines traditional information retrieval with semantic search and Large Language Models to generate grounded, context-aware answers from GeoAI research papers.

---

# ✨ Features

-  Hybrid Retrieval (SQLite FTS + Semantic Search)
-  Context Grounded Responses
-  Reciprocal Rank Fusion (RRF)
-  Topic-based Filtering
-  Interactive Streamlit Interface
-  Automated RAG Evaluation using RAGAS

---

# 📚 Research Topics

- GeoAI
- Earth Observation
- Remote Sensing
- Foundation Models
- Vision Transformers
- Self-Supervised Learning
- Sentinel-2
- Satellite Imagery
- Land Use Land Cover (LULC) Classification
- Change Detection

---

# 🏗️ System Architecture

```text
User Query
     │
     ▼
SQLite Full-Text Search
     │
     ▼
Semantic Vector Search
     │
     ▼
Reciprocal Rank Fusion
     │
     ▼
Top-k Research Papers
     │
     ▼
Prompt Construction
     │
     ▼
Llama 3.3 70B (Groq)
     │
     ▼
Grounded Answer
```

---

# 💻 Application

Example Questions

```text
How are Vision Transformers used in Remote Sensing?

Compare CNNs and Vision Transformers for LULC classification.

What are Foundation Models for Earth Observation?

Explain Self-Supervised Learning in GeoAI.

What are recent trends in Change Detection?
```

---

# ⚙️ Tech Stack

## LLM

- Groq API
- Llama-3.3-70B-versatile for the final grounded answers
- all-MiniLM-L6-v2 for vector search embeddings

## Retrieval

- SQLite FTS5 (Full Text Search)
- Sentence Transformers
- Hybrid Search
- Reciprocal Rank Fusion (RRF)

## Frameworks

- Streamlit
- Python

## Evaluation

- Ragas
- Llama-3.1-8B-instant (LLM Judge)

---

# 📂 Dataset

The knowledge base was built by querying the [arXiv API](https://arxiv.org/help/api) across 13 topic-specific searches spanning GeoAI, Earth Observation, Remote Sensing, Vision Transformers and Foundation Models, sorted by most recent submission date. After collection, this indexes around **1,000 research papers**.

### Indexing Pipeline

The `build_index.py` script orchestrates the full ingestion-to-index flow:

1. **Ingesting** - `ingest.py` queries the arXiv API across the 13 topic searches and returns paper metadata (title, abstract, authors, year, topic, URL).
2. **Keyword index** - papers are added to a `TextSearchIndex` (SQLite FTS5), searchable on `title`, `authors` and `abstract`, with `topic` as a filterable keyword field. Saved to `geoai.db`.
3. **Vector index** - `build_embeddings.py` encodes the same documents into sentence-transformer embeddings for semantic search. Saved to `geoai_embeddings.pkl`.


Each document contains:

- Title
- Abstract
- Authors
- Publication Year
- Topic
- Source URL

---

# 📊 Evaluation Pipeline

```text
Research Papers
       │
       ▼
Automatic Question Generation
       │
       ▼
questions.json
       │
       ▼
Run RAG Pipeline
       │
       ▼
rag_outputs.json
       │
       ▼
Ragas Evaluation
       │
       ▼
Evaluation Metrics
```

The evaluation pipeline automatically:

- Generates evaluation questions from the indexed papers.
- Runs the complete RAG pipeline.
- Evaluates generated answers using Ragas.
- Produces quantitative evaluation reports.

---

# 📈 Evaluation Results

| Metric | Score |
|---------|------:|
| Faithfulness | **0.7386** |
| Answer Relevancy | **0.8267** |
| Context Precision | **0.8600** |

### Interpretation

- ✅ Responses remain well grounded in retrieved literature.
- ✅ High answer relevancy indicates the assistant answers user questions effectively.
- ✅ Hybrid retrieval consistently retrieves relevant scientific papers.

---

# 🚀 Running Locally

Clone the repository

```bash
git clone https://github.com/Vaibhav170216/geoai-research-assistant.git

cd geoai-research-assistant
```

Install dependencies

```bash
uv sync
```

Create a `.env`

```text
GROQ_API_KEY=your_groq_api_key
```

Build the index

```bash
python build_index.py
```

Run the application

```bash
streamlit run app.py
```

---

# 🔮 Future Improvements

- PDF Parsing Pipeline
- Agentic Literature Review

---

# 👨‍💻 Author

**Vaibhav Nagar**