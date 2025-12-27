# NLP & Groq Question Generation System 🤖📝

This project is a high-performance pipeline for the **automated generation, evaluation, and exporting of programming questions** (specifically Object-Oriented Programming - OOP). It leverages multiple Large Language Models (LLMs) via the **Groq API** and NLP techniques to ensure educational quality and technical accuracy.

Developed for research guided by **Dr. Francisco Zampirolli (UFABC)** to support educational platforms like **MCTest** and **VPL**.

---

## 📌 Project Overview

The system takes an original OOP question (Open-Ended or Multiple Choice) in LaTeX, generates new versions using different LLMs, evaluates them using `spaCy` and semantic similarity, and selects the best candidate based on a weighted scoring system.

### 🚀 Key Features
* **Multi-Model Tournament:** Compares outputs from Llama 3.1, GPT-OSS, and Kimi in real-time.
* **Automatic Asset Generation:**
    * **PDF:** Compiled via `pdflatex` (automatically hiding validation blocks).
    * **UML:** Class diagrams generated via **Graphviz**.
    * **HTML Report:** Visual dashboard for analyzing the generation quality.
* **Active Code Validation:** Executes generated Python code in a sandbox to ensure `inp_list` and `out_list` are correctly defined.
* **Moodle-Ready:** Exports `.json` for MCTest and `.cases` for VPL.

---

## 🛠️ System Architecture

| Module | Responsibility |
| :--- | :--- |
| `main.py` | Orchestrates generation attempts, model comparison, and selection logic. |
| `exporter.py` | Handles Python context extraction, UML rendering, and PDF compilation. |
| `evaluation.py` | Assigns a 1-10 quality score based on NLP and structural metrics. |
| `html_view.py` | Generates a final web-based report for user visualization. |

---

## 📈 Quality Metrics & Scoring

The **QuestionEvaluator** assigns a **General Score (1-10)** by analyzing:

| Metric | Weight | Goal |
| :--- | :--- | :--- |
| **Semantic Coherence** | 30% | Meaning consistency using `Sentence-Transformers`. |
| **Python Code Validity** | 30% | Executional integrity of the `[[def:...]]` validation script. |
| **LaTeX Integrity** | 20% | Correct tag balancing and syntax for math/code blocks. |
| **OOP Structure** | 20% | Presence and correctness of classes, attributes, and methods. |

---

## 🐳 Running with Docker

Running via Docker is highly recommended to avoid local dependency issues with LaTeX and Graphviz.

### 1. Execute the Generation
Run the container and provide your **Groq API Key**. Replace `my_test_session` with any name you prefer:
```bash
docker run --name my_test_session -it -e GROQ_API_KEY="YOUR_KEY_HERE" gerador-ia-ufabc
```
### 2. Copy the Results
After the script finishes, copy all generated files (PDF, JSON, PNG, HTML) to your current local directory:
```bash
docker cp my_test_session:/app/. .
```
### 3. Cleanup
Remove the container to free up resources and prepare for the next run:
```bash
docker rm my_test_session
```

---

## ⚙️ Configuration (models&question_config.yaml)
### You can customize the generation behavior:
* **attempts:** Number of retries (default: 3) if models fail code validation.
* **pick_mode:** Use most_similar to stay close to the original or least_similar for more creative variations.
* **original_question:** Paste your base LaTeX question here to start a new generation.

---

## 🖥️ Local Requirements (Non-Docker)
### If running natively, ensure you have:
* **Python 3.10+**
* **TexLive / pdflatex installed and in your PATH.**
* **Graphviz installed.**
* **spaCy Model: python -m spacy download pt_core_news_md**

### You can download all necessary packages directly by the requirements.txt
