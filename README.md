# GeoAI Research Assistant

An LLM-powered research assistant for exploring Earth Observation, Remote Sensing and GeoAI literature using retrieval-based question answering.

The system indexes GeoAI research papers and enables natural-language querying over topics such as Land Use Land Cover (LULC) classification, Vision Transformers and Foundation Models.

---

## Overview

GeoAI Research Assistant helps researchers, students and practitioners quickly explore scientific literature without manually searching through hundreds of papers.

The application retrieves relevant research papers using SQLite Full-Text Search (FTS) and uses a Large Language Model (LLM) to generate grounded answers from the retrieved context.

---

## Features

- Research paper search using SQLite Full-Text Search
- LLM-powered question answering
- Retrieval-based context grounding
- Streamlit web interface
- Topic-based filtering
- Persistent local knowledge base
- Modular retrieval pipeline

---

## Research Topics Covered

- GeoAI
- Earth Observation
- Remote Sensing
- Land Use Land Cover (LULC) Classification
- Vision Transformers
- Foundation Models for Earth Observation
- Change Detection
- Semantic Segmentation
- Deep Learning for Geospatial Analysis

---

## System Architecture

```text
User Question
      │
      ▼
SQLite Full-Text Search
      │
      ▼
Top-K Relevant Papers
      │
      ▼
Context Construction
      │
      ▼
Large Language Model
      │
      ▼
Generated Answer
```

---

## Example Questions

```text
How are Vision Transformers used for remote sensing?

What foundation models exist for Earth Observation?

What are the advantages of Sentinel-2 imagery?

Compare CNNs and Vision Transformers for LULC classification.

How is change detection performed using deep learning?
```

---

## Tech Stack

### AI & LLM

- OpenAI API
- Prompt Engineering

### Retrieval

- SQLite
- SQLite Full-Text Search (FTS)

### Backend

- Python

### Frontend

- Streamlit


---

## Dataset

The knowledge base consists of research papers related to:

- Earth Observation
- GeoAI
- Remote Sensing
- Satellite Image Analysis
- Foundation Models
- Deep Learning Applications

Each paper contains:

- Title
- Abstract
- Authors
- Publication Year
- Topic Category

---

## Future Improvements

- Vector Search
- Hybrid Retrieval (FTS + Semantic Search)
- Paper recommendations
- Research trend analysis
- Multi-document summarization

---

## Skills Demonstrated

This project demonstrates:

- Retrieval-Augmented Generation (RAG) concepts
- Information Retrieval
- LLM Application Development
- Prompt Engineering
- Research Knowledge Base Construction
- Streamlit Deployment
- End-to-End GenAI Workflows

---

## Running Locally

### Clone Repository

```bash
git clone https://github.com/Vaibhav170216/geoai-research-assistant.git
cd geoai-research-assistant
```

### Install Dependencies

```bash
uv sync
```

### Run Application

```bash
streamlit run app.py
```

---

## Motivation

As part of my interest in GeoAI and Earth Observation, I built this project to explore how Large Language Models can be combined with retrieval systems to make scientific literature more accessible and searchable.

---

## Author

**Vaibhav Nagar**