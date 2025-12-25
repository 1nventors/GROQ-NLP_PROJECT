# NLP & Groq Question Generation System 🤖📝 (IN PROGRESS)

This project develops a robust pipeline for the **automated generation and structured evaluation of programming questions** (specifically focusing on Object-Oriented Programming - OOP), using advanced Large Language Models (LLMs) via the **Groq API** and Natural Language Processing (NLP) techniques.

It serves as the core system for research guided by **Dr. Francisco Zampirolli (UFABC)** on automated content generation for educational platforms like MCTest(UFABC).

---

## 📌 Project Overview

The system takes a base OOP question in LaTeX format and executes a complete cycle of multi-model generation, comprehensive validation, and intelligent selection. 



### Key Advancements:

* **Multi-Model Generation Benchmark:** The system tests question generation across various high-speed LLMs to compare output quality.
* **Weighted Quality Score (1-10):** Implementation of a custom evaluation module (`QuestionEvaluator`) that assigns a final quality score based on a weighted combination of structural, semantic, and syntactic correctness.
* **Active Code Validation:** Uses Python's Abstract Syntax Tree (`ast` module) to ensure the syntactic validity of generated code blocks within the LaTeX output.
* **Automated Exporting:** Generates structured `.json` for MCTest and `.cases` for VPL (Virtual Programming Lab) automatically.

---

## 🛠️ Features & Technologies

| Category | Features | Core Technologies |
| :--- | :--- | :--- |
| **Generation** | Resilient Multi-Model Generation Pipeline | **Groq API**, Llama 3.1, GPT-OSS, Kimi |
| **Semantic Validation** | Coherence checks between original and generated questions | `Sentence-Transformers`, `spaCy` (`pt_core_news_md`) |
| **Structural Validation**| LaTeX command balance checks and OOP structure analysis. | `ast` module, Regular Expressions (`re`) |
| **Automation** | Automated *Test Case* generation based on `[[def:...]]` blocks. | Python Scripting, `json`, `datetime` |

---

## 📈 Quality Metrics & Scoring

The **QuestionEvaluator** module generates a **General Score (1-10)** by assigning weights to key validation areas:

| Metric | Weight | Goal |
| :--- | :--- | :--- |
| **Semantic Coherence** | 3 | Ensure the new question maintains the core educational meaning. |
| **Python Code Validity** | 3 | Ensure all generated code blocks are syntactically sound. |
| **LaTeX Integrity** | 2 | Verify command balancing (`\begin`, `\end`) and command usage. |
| **Structural Integrity** | 2 | Confirm the presence of key OOP elements (class, def, self). |

---

## 🐳 Running with Docker (Recommended/IN PROGRESS)

To ensure all dependencies (NLP models, libraries, and LaTeX environments) work regardless of the host OS, it is highly recommended to run the project via Docker.

### 1. Pull the Image from Docker Hub
You don't need the source code to run the generator. Simply pull the latest image:
```bash
docker pull 1nventors/gerador-ia-ufabc
```

### 2. Run the Container
You can pass your Groq API Key directly as an environment variable. This avoids the need for a local .env file and allows different users to use their own keys:
```bash
docker run -it --rm -e GROQ_API_KEY="your_api_key_here" -v "$(pwd):/app" gerador-ia-ufabc
```

Note: The -v "$(pwd):/app" flag (Volume) is essential. It synchronizes the container's output with your local folder, allowing the generated .json, .cases, and reports to appear on your machine instantly.

### 🚀 Next Steps & Future Work

The project is currently evolving to include automated asset production and data persistence:

* **Automatic Asset Generation:** Implementation of automated generation of UML Class Diagrams (PNG) using Graphviz and Compiled Question Papers (PDF) using internal LaTeX compilers (pdflatex).
* **Visual Reporting:** Development of a dynamic HTML Dashboard to visualize evaluation metrics and generated content in a browser-friendly format.
* **Data Persistence (Database):** Implement a database connection (e.g., SQLite or PostgreSQL) to save all high-scoring, validated questions for permanent storage.


🖥️ Local Requirements (Non-Docker)

If running without Docker, ensure the following are installed:

* **Python 3.10+**
* **Groq**
* **Sentence-Transformers**
* **spaCy model:**
```bash
python -m spacy download pt_core_news_md
```
