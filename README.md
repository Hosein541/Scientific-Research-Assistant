# Scientific Research Assistant

An AI-powered research assistant for analyzing scientific papers using Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), and semantic knowledge graphs.

The system automatically extracts the content of scientific papers, generates hierarchical summaries, builds a searchable vector database, enables question answering over uploaded papers, and discovers semantic relationships between papers by constructing a knowledge graph from LLM-generated metadata and embedding similarities.

---

## Features

* 📄 Automatic PDF scientific paper extraction
* 📝 Hierarchical section-level and paper-level summarization
* 💬 RAG-based Question Answering
* 📊 Figure and table caption extraction
* 🧠 LLM-generated document profiling
* 🔗 Semantic Knowledge Graph construction
* 📚 Multi-paper library management
* 🌐 Interactive Streamlit interface

---

## How It Works

```text
Scientific Papers (PDF)
            │
            ▼
Content Extraction
(Text, Figures, Tables)
            │
            ▼
Section Detection
            │
            ▼
Hierarchical Summarization
            │
            ├──────────────► Vector Database (ChromaDB)
            │                       │
            │                       ▼
            │                RAG Question Answering
            │
            └──────────────► Document Profiling (LLM)
                                    │
                                    ▼
                         Semantic Similarity Analysis
                                    │
                                    ▼
                         Knowledge Graph Construction
```

---

## Knowledge Graph

Instead of relying on citation networks, the project constructs a semantic knowledge graph.

For each paper, the LLM generates a structured document profile containing information such as:

* Research field
* Research topics
* Keywords
* Methods
* Applications
* Main contributions

Semantic embeddings are generated from these profile components. Pairwise similarity between papers is then computed, and edges are created only when the similarity exceeds predefined thresholds. Different semantic categories contribute independently to the final edge weight, allowing the graph to reveal meaningful relationships between research papers.

---

## Technologies

* Python
* Streamlit
* LangChain
* Google Gemini
* Ollama
* ChromaDB
* Hugging Face
* NetworkX
* Matplotlib
* Poetry

---

## Installation

### Clone the repository

```bash
git clone https://github.com/<YOUR_USERNAME>/scientific-research-assistant.git
cd scientific-research-assistant
```

### Install dependencies

```bash
pip install poetry
poetry install
```

### Install the embedding model

Make sure Ollama is installed and running.

```bash
ollama pull embeddinggemma
```

Start the Ollama server:

```bash
ollama serve
```

### Launch the application

```bash
poetry run streamlit run app.py
```

---

## Requirements

Before starting a session, provide:

* Google Gemini API Key
* Hugging Face Access Token

These credentials are entered through the application interface and are used only during the current session.

---

## Project Structure

```text
extractor/        # PDF extraction pipeline
summarize/        # Hierarchical summarization
qa_chain/         # RAG question answering
graph/            # Semantic graph construction
vector_db/        # Chroma vector database
pages/            # Streamlit pages
inputs/           # Uploaded papers
outputs/          # Generated artifacts
core/             # Session manager
session/          # Settings
pipeline.py       # Main processing pipeline
app.py            # Streamlit application
```

---

## Application Workflow

1. Upload one or more scientific papers.
2. Configure the required API keys.
3. Start a processing session.
4. The system automatically:

   * extracts paper contents,
   * detects document sections,
   * generates hierarchical summaries,
   * creates structured document profiles,
   * builds the vector database,
   * constructs the semantic knowledge graph.
5. Explore the processed papers through:

   * Library
   * Question Answering
   * Knowledge Graph

---

## License

This project is intended for educational and research purposes.
