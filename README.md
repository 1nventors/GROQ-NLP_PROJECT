# NLP & Groq Question Generation System 🤖📝

This project develops a robust pipeline for the **automated generation and structured evaluation of programming questions** (specifically focusing on Object-Oriented Programming - OOP), using advanced Large Language Models (LLMs) via the **Groq API** and Natural Language Processing (NLP) techniques.

It serves as the core system for research guided by Dr. Francisco Zampirolli (UFABC) on automated content generation for educational platforms like MCTest and TestCodeAI.

---

## 📌 Project Overview

The system takes a base OOP question in LaTeX format and executes a complete cycle of multi-model generation, comprehensive validation, and intelligent selection.

### Key Advancements:

- **Multi-Model Generation Benchmark:** The system tests question generation across various high-speed LLMs to compare output quality.
- **Weighted Quality Score (1-10):** Implementation of a custom evaluation module (`QuestionEvaluator`) that assigns a final quality score based on a weighted combination of structural, semantic, and syntactic correctness.
- **Active Code Validation:** Uses Python's Abstract Syntax Tree (`ast` module) to ensure the syntactic validity of generated code blocks within the LaTeX output.
- **Detailed Reporting:** Automated generation of JSON and TXT reports with all metrics for in-depth analysis and academic reference.

---

## 🛠️ Features & Technologies

| Category | Features | Core Technologies |
| :--- | :--- | :--- |
| **Generation** | Resilient Multi-Model Generation Pipeline | **Groq API**, **llama-3.1-8b-instant**, **gpt-oss-20b**, **kimi-k2-instruct-0905** |
| **Semantic Validation** | Coherence checks between original and generated questions | `Sentence-Transformers` (`paraphrase-multilingual-MiniLM-L12-v2`), `spaCy` (`pt_core_news_md`) |
| **Structural Validation**| LaTeX command balance checks, Python code syntax parsing, OOP structure analysis (classes, methods, attributes). | `ast`, Regular Expressions (`re`) |
| **Automation** | Automated *Test Case* generation based on base question's `[[def:...]]` block. | Python Scripting, `json`, `datetime` |

---

## 📈 Quality Metrics & Scoring

The **QuestionEvaluator** module generates a **General Score (1-10)** by assigning weights to key validation areas:

| Metric | Tool Used | Weight | Goal |
| :--- | :--- | :--- | :--- |
| **Semantic Coherence** | spaCy / Sentence-Transformers | 3 | Ensure the new question maintains the core meaning of the original. |
| **Python Code Validity** | `ast` module | 3 | Ensure all generated code blocks are syntactically sound. |
| **LaTeX Integrity** | RegEx | 2 | Verify command balancing (`\begin`, `\end`) and command usage. |
| **Structural Integrity** | RegEx | 2 | Confirm the presence of key OOP elements (class, def, self). |

---

## 📝 How It Works

1.  **Input:** A base OOP question in LaTeX format is defined in `main.py`.
2.  **Generation Loop:** The system iterates through the list of LLMs, generating a variation from each.
3.  **Evaluation:** Each generated output is passed to the `QuestionEvaluator` for scoring.
4.  **Selection:** The best valid output is selected based on a pre-defined criterion (`PICK_MODE`: `most_similar` or `most_different`).
5.  **Reporting:** Detailed metrics and the generated question are saved in structured `.json` and `.txt` files.

---

## 🚀 Next Steps & Future Work

The immediate goal is to finalize the data persistence layer:

- **Data Persistence (Database):** Implement a database connection (e.g., using **SQLite or PostgreSQL**) to save all high-scoring, validated questions for permanent storage and deployment onto the target educational platform.
- **Using the Database, maybe will have a ML training using fine tuning:** At the start I didn't have plans to do a fine tuning in a LLM to made my own model for exam question generation, but I'm evaluating if it's possible to make one... 
---

## 🖥️ Requirements

- **Python 3.10+**
- `groq` Python SDK
- `sentence-transformers`
- `spacy`
- **spaCy Model:** `pt_core_news_md` (Install via `python -m spacy download pt_core_news_md`)
