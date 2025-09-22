# NLP & Groq Project 🤖📝 (WORKING ON)

This project focuses on **Natural Language Processing (NLP)** and the **Groq API** to automate the **generation and validation of programming questions** in LaTeX format.  
It explores Python development, prompt engineering, and semantic validation with guidance from Dr. Francisco Zampirolli (UFABC).

---

## 📌 Project Overview

The project takes a LaTeX-based **Object-Oriented Programming (OOP)** question and automatically:

- Generates variations with **new class names, attributes, and methods**.  
- Maintains the **original LaTeX formatting**, including input/output examples and test case blocks.  
- Validates the generated questions for **semantic similarity** and **structural correctness**.

The workflow combines:

- **Groq API** for advanced text generation.  
- **Sentence Transformers (`all-MiniLM-L6-v2`)** for semantic similarity checks.  
- Python scripting for processing, randomization, and automated test case generation.  

---

## 🛠️ Features & Skills Developed

- **Prompt Engineering**: Crafting effective prompts to generate LaTeX-formatted programming questions.  
- **Automated Test Case Generation**: Producing randomized, realistic test inputs and outputs.  
- **Semantic Similarity Validation**: Ensuring new questions preserve the meaning of the original.  
- **Structural Validation**: Checking that outputs respect expected OOP structures (classes, attributes, methods).  
- **Python Scripting & Automation**: Integrating multiple libraries into a single content generation pipeline.  
- **Version Control Best Practices**: Handling sensitive API keys safely and keeping a clean repo history.  

---

## ⚡ Challenges Solved

- Maintaining **LaTeX formatting** while generating multiple variations.  
- Guaranteeing **semantic integrity**: new questions differ in names but are equivalent in meaning.  
- Preventing **secret leakage** (API keys) in Git history.  
- Integrating multiple models for **high-quality content validation**.  

---

## 📝 How It Works

1. Define a base OOP question in LaTeX format.  
2. Generate new question variations via **Groq API**.  
3. Validate outputs using **semantic similarity** and **structural checks**.  
4. Select the best valid output for final use.  
5. Generate test cases for automated evaluation.  

---

## 🖥️ Requirements

- **Python 3.10+**  
- `groq` Python SDK  
- `sentence-transformers`

---

## 🚀 Next Steps

- Expand support for **other OOP concepts** (inheritance, polymorphism, etc.).  
- Add more advanced **semantic validation checks**.  
- Build a **web or GUI interface** for interactive question generation.  
