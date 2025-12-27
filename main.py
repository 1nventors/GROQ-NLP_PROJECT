from groq import Groq
from sentence_transformers import SentenceTransformer, util
from dotenv import load_dotenv
import os
import re
import time
import json
import yaml
from datetime import datetime
from evaluation import QuestionEvaluator
from exporter import QuestionExporter 
from html_view import QuestionReporter

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
model_embed = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
evaluator = QuestionEvaluator()

def load_config(path="models&question_config.yaml"):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def detect_question_type(text):
    if r"\begin{enumerate}" in text:
        return "QM"
    return "QT"

def generate_prompt(question_text, question_type):
    common_instruction = (
        "É OBRIGATÓRIO incluir ao final da resposta o bloco [[def:...]] contendo o código Python, porém este bloco não deve sair no PDF final."
        "que gera as listas inp_list e out_list para validação no VPL. Não esqueça dos colchetes duplos."
        "gere cerca de 5 casos de teste variados."
        "Use identação estrita de 4 espaços (NUNCA use tabs). "
        "Certifique-se que o código Python dentro de [[def:]] esteja alinhado à esquerda (sem indentação inicial relativa ao bloco)."
    )
    if question_type == "QT":
        prompt = f"Reescreva do zero uma questão de POO, mantendo o formato LaTeX, mas usando novos nomes de classe, atributos, métodos, adicionando novos desafios e alterando o tema ficticio da questão. Não gere uma questão parametrizada, gere uma questão nova. Mantenha os exemplos de entrada/saída e o bloco [[def:...]].:\n\n{question_text} {common_instruction}"
    if question_type == "QM":
        prompt = f"Gere uma nova questão de múltipla escolha no mesmo formato que a seguinte, inclua 5 alternativas usando \\begin{{enumerate}}, mas NÃO inclua o gabarito no texto. NÃO gere exemplos de entrada e saída no texto. Use o formato LaTeX com \\begin{{verbatim}} para o código da questão e \\begin{{enumerate}} para alternativas:\n\nQuestão:\n{question_text}{common_instruction}"
    return prompt

def generate_with_model(model_name, prompt, temperature, max_tokens):
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content

def validate_output(original, generated):
    emb1 = model_embed.encode(original, convert_to_tensor=True)
    emb2 = model_embed.encode(generated, convert_to_tensor=True)
    similarity = util.cos_sim(emb1, emb2).item()
    structure = bool(re.search(r"Classe|class", generated, re.IGNORECASE)) and \
                bool(re.search(r"atribut", generated, re.IGNORECASE))

    return similarity, structure

def save_results(results, filename="resultados_geracao.json"):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n[✓] Results saved to: {filename}")

def main():
    config = load_config()
    
    original_question = config['original_question']
    models_dict = config['llm_params']['models']
    temp = config['llm_params']['temperature']
    max_t = config['llm_params']['max_tokens']
    pick_mode = config['experiment']['pick_mode']
    attempts_max = config['experiment']['attempts']

    print("=" * 80)
    print("SISTEMA DE GERAÇÃO E AVALIAÇÃO DE QUESTÕES DE POO")
    print("=" * 80)
    
    question_type = detect_question_type(original_question)
    print(f"\n[DEBUG] Tipo de questão detectado: {question_type}")
    prompt = generate_prompt(original_question, question_type)

    all_evaluations = []

    for attempt in range(attempts_max):
        try:
            results = []
            print(f"\n{'─' * 80}")
            print(f"TENTATIVA {attempt + 1}")
            print(f"{'─' * 80}")

            for model_name_key, model_id in models_dict.items():
                print(f"\nGerando com {model_name_key}...")
                output = generate_with_model(model_id, prompt, temp, max_t)
                sim, is_structure_ok = validate_output(original_question, output)
                
                print(f"Avaliando com spaCy...")
                evaluation = evaluator.evaluate_question(original_question, output)
                
                results.append({
                    "name": model_name_key,
                    "output": output,
                    "similarity": sim,
                    "valid": is_structure_ok,
                    "evaluation": evaluation
                })

            valid_results = [r for r in results if r["valid"]]

            if not valid_results:
                print("\n⚠ Nenhum resultado válido nesta tentativa. Tentando novamente...")
            else:
                valid_results.sort(key=lambda x: x["similarity"], reverse=(pick_mode == "most_similar"))
                best_result = valid_results[0]
                chosen = best_result["output"]
                
                print(f"\n{'=' * 80}")
                print(f"VENCEDOR: {best_result['name'].upper()}")
                print(f"{'=' * 80}")

                exporter = QuestionExporter()
                reporter = QuestionReporter()
                
                exporter.export_mctest_json(chosen, best_result["name"], question_type)
                exporter.export_vpl_cases(chosen, question_type)
                exporter.export_class_diagram(chosen)
                exporter.export_pdf_latex(chosen, "questao_oficial", q_type=question_type)
                
                score_final = best_result["evaluation"]["score_geral"]
                reporter.generate_html(chosen, score_final, best_result["name"])
                all_evaluations = results
                break

        except Exception as e:
            print(f"\n Erro na API do Groq (Tentativa {attempt + 1}): {e}")
            time.sleep(5)

    if all_evaluations:
        final_results = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "original_question": original_question,
            "models_evaluated": len(all_evaluations),
            "results": [
                {"model": r["name"], "similarity": r["similarity"], "valid": r["valid"], "output": r["output"]}
                for r in all_evaluations
            ]
        }
        save_results(final_results)

if __name__ == "__main__":
    main()