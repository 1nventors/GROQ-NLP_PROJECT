# NLP and Groq Project

This project demonstrates my work with **Natural Language Processing (NLP)** and **Groq API** to automate the generation and validation of programming questions in LaTeX format. The repository focuses on **Python development**, **prompt engineering**, and **semantic validation**.

## Overview

The project takes a LaTeX-based question about **Object-Oriented Programming (OOP)** and automatically:

1. Generates variations of the question with new class names, attributes, and methods.
2. Maintains the original format of the question, including input/output examples and test case blocks.
3. Validates the generated content for **semantic similarity** and **structural correctness**.

The process integrates:

- **Groq API** for advanced text generation.
- **Sentence Transformers (`all-MiniLM-L6-v2`)** to calculate semantic similarity.
- Python for processing, randomization, and test case generation.

## Features & Skills Developed

- **Prompt Engineering**: Designing effective prompts to produce LaTeX-formatted programming questions.
- **Automated Test Case Generation**: Creating random, realistic test inputs and outputs for OOP exercises.
- **Semantic Similarity Validation**: Ensuring that generated questions preserve meaning using embedding models.
- **Structural Validation**: Checking that generated text adheres to expected OOP structures (classes, attributes, methods).
- **Python Scripting & Automation**: Combining multiple libraries to build a reliable pipeline for content generation.
- **Version Control Practices**: Managing sensitive API keys and maintaining a clean repository history.

## Challenges Solved

- Maintaining **LaTeX formatting** while generating multiple question variations.
- Ensuring **semantic integrity**: new questions are different in names but equivalent in meaning.
- Preventing sensitive information leakage (e.g., API keys) in version control.
- Integrating multiple models (Groq, Sentence Transformers) for **high-quality content validation**.

## How It Works

1. Define the base OOP question in LaTeX format.
2. Generate new variations using the **Groq API**.
3. Validate the output using semantic similarity and structural checks.
4. Select the best valid output for final use.
5. Generate test cases for automated evaluation.

## Requirements

- Python 3.10+
- `groq` Python SDK
- `sentence-transformers`
- JSON and standard Python libraries

## Usage

```bash
pip install -r requirements.txt
python main.py
