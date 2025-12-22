from groq import Groq
from sentence_transformers import SentenceTransformer, util
from dotenv import load_dotenv
import os
import re
import time
import json
from datetime import datetime
from evaluation import QuestionEvaluator
from exporter import QuestionExporter 

# initialize clients
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
model_embed = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
evaluator = QuestionEvaluator()

PICK_MODE = "most_similar"  # most_simillar or most_different

# question prompt
original_question = r"""
\textbf{EP2\_3} \textbf{Classe Aluno} — Encapsulamento com Getters e Setters

Um dos pilares da Programação Orientada a Objetos (POO) é o \textbf{encapsulamento}, que protege os dados internos de um objeto e controla seu acesso por meio de métodos públicos.

Sua tarefa é:

\begin{itemize}[itemsep=2pt, parsep=0pt]
  \item Criar a classe \textbf{Aluno} com \textbf{atributos privados}: nome e matrícula.
  \item Utilizar um \textbf{construtor} para inicializar os atributos.
  \item Criar métodos públicos:
    \begin{itemize}[itemsep=1pt, parsep=0pt]
      \item \texttt{getNome()} e \texttt{setNome()} para acessar e modificar o nome.
      \item \texttt{getMatricula()} apenas para leitura da matrícula.
      \item \texttt{apresentar\_aluno()} para apresentar os atributos formatados da classe.
    \end{itemize}
  \item Apresentar a saída formatada para cada método escolhido na entrada de dados, conforme exemplo a seguir.
\end{itemize}


\vspace{2mm}\noindent\textbf{Exemplo de Entrada:}\vspace{-2mm}
\begin{verbatim}
[[code:caso0_inp]]
\end{verbatim}

\vspace{-2mm}\noindent\textbf{Exemplo de Saída:}\vspace{-2mm}
\begin{verbatim}
[[code:caso0_out]]
\end{verbatim}

\medskip

\begin{comment}
[[code:moodle_cases]]
\end{comment}

[[def:
import json
import random

class Aluno:
    def __init__(self, nome, matricula):
        self.__nome = nome
        self.__matricula = matricula

    def getNome(self):
        return self.__nome

    def setNome(self, novo_nome):
        self.__nome = novo_nome

    def getMatricula(self):
        return self.__matricula

    def apresentar_aluno(self):
        return f"Aluno: {self.__nome}, Matrícula: {self.__matricula}"

inp_list, out_list = [], []
num_test_cases = 10

for i in range(num_test_cases):
    nome_inicial = f"{random.choice(nomes_base)} {random.choice(sobrenomes_base)}"
    matricula_inicial = f"{random.randint(2023, 2025)}{random.randint(100, 999):03d}"

    aluno_teste = Aluno(nome_inicial, matricula_inicial)

    operacao = random.choice(["apresentar", "alterar_nome", "get_matricula"])

    if operacao == "apresentar":
        entrada = f"{nome_inicial}, {matricula_inicial}; apresentar_aluno()"
        saida = aluno_teste.apresentar_aluno()
    elif operacao == "alterar_nome":
        novo_nome = f"{random.choice(nomes_base)} {random.choice(sobrenomes_base)}"
        aluno_teste.setNome(novo_nome)
        entrada = f"{nome_inicial}, {matricula_inicial}; setNome('{novo_nome}'); apresentar_aluno()"
        saida = aluno_teste.apresentar_aluno()
    else:
        entrada = f"{nome_inicial}, {matricula_inicial}; getMatricula()"
        saida = aluno_teste.getMatricula()

    inp_list.append(entrada)
    out_list.append(saida)

cases = {
    "input": inp_list,
    "output": out_list
}

moodle_cases = json.dumps(cases)

caso0_inp = inp_list[0]
caso0_out = out_list[0]
]]


"""


def detect_question_type(text):
    if r"\begin{enumerate}" in text:
        return "QM"
    return "QT"


def generate_prompt(question_text, question_type):
    if question_type == "QT":
        prompt = f"Reescreva do zero uma questão de POO, mantendo o formato LaTeX, mas usando novos nomes de classe, atributos, métodos, adicionando novos desafios e alterando o tema ficticio da questão. Não gere uma questão parametrizada, gere uma questão nova. Mantenha os exemplos de entrada/saída e o bloco [[def:...]].:\n\n{question_text}"
    if question_type == "QM":
        prompt = f"Gere uma nova questão de múltipla escolha no mesmo formato que a seguinte, no formato LaTeX com \\begin{{verbatim}} para código e \\begin{{enumerate}} para alternativas:\n\nQuestão:\n{question_text}"
    return prompt


def generate_with_model(model_name, prompt):
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000,
        temperature=0.9,
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
    print(f"\n[✓] Resultados salvos em: {filename}")


def main():
    print("=" * 80)
    print("SISTEMA DE GERAÇÃO E AVALIAÇÃO DE QUESTÕES POO")
    print("=" * 80)
    
    question_type = detect_question_type(original_question)
    print(f"\n[DEBUG] Tipo de questão detectado: {question_type}")
    prompt = generate_prompt(original_question, question_type)

    MODELS = {
        "llama": "llama-3.1-8b-instant",
        "gpt": "openai/gpt-oss-20b",
        "kimi": "moonshotai/kimi-k2-instruct-0905",
    }

    chosen = None
    all_evaluations = []

    for attempt in range(3):
        try:
            results = []

            print(f"\n{'─' * 80}")
            print(f"TENTATIVA {attempt + 1}")
            print(f"{'─' * 80}")

            for model_name_key, model_id in MODELS.items():
                print(f"\nGerando com {model_name_key}...")
                
                output = generate_with_model(model_id, prompt)
                
                sim, is_structure_ok = validate_output(original_question, output)
                
                # spaCy Evaluation
                print(f"Avaliando com spaCy...")
                evaluation = evaluator.evaluate_question(original_question, output)
                
                results.append({
                    "name": model_name_key,
                    "output": output,
                    "similarity": sim,
                    "valid": is_structure_ok,
                    "evaluation": evaluation
                })

            print(f"\n{'=' * 80}")
            print("RELATÓRIO DE VALIDAÇÃO RÁPIDA")
            print(f"{'=' * 80}")
            for res in results:
                status = "OK" if res["valid"] else "Estrutura Inválida"
                score = res["evaluation"]["score_geral"]
                print(f"{res['name'].capitalize():<10} → Sim: {res['similarity']:.4f} | Score: {score}/10 | {status}")

            # Filter the valid results
            valid_results = [r for r in results if r["valid"]]

            if not valid_results:
                print("\n⚠ Nenhuma saída válida nesta tentativa. Tentando novamente...")
                chosen = None
            else:
                valid_results.sort(key=lambda x: x["similarity"], 
                                 reverse=(PICK_MODE == "most_similar"))
                
                best_result = valid_results[0]
                chosen = best_result["output"]
                # Quick report of the winner
                print(f"\n{'=' * 80}")
                print(f"VENCEDOR: {best_result['name'].upper()}")
                print(f"{'=' * 80}")
                print(f"Similaridade: {best_result['similarity']:.4f}")
                print(f"Score Geral: {best_result['evaluation']['score_geral']}/10")
                
                # Full complete report
                print(f"\n{evaluator.generate_report(best_result['evaluation'])}")
                
                # Shows the chosen question
                print(f"\n{'=' * 80}")
                print("QUESTÃO GERADA (VENCEDORA)")
                print(f"{'=' * 80}")
                print(chosen)
                print(f"{'=' * 80}")

                exporter = QuestionExporter()
                exporter.export_mctest_json(chosen, best_result["name"], question_type)
                exporter.export_vpl_cases(chosen)
                
                # Save all evaluations
                all_evaluations = results
                break

        except Exception as e:
            print(f"\n Erro na API do Groq(tentativa {attempt + 1}): {e}")
            if "rate_limit" in str(e).lower():
                print(" Aguardando 45 segundos...")
                time.sleep(45)

    # Save final results in JSON
    if all_evaluations:
        final_results = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "original_question": original_question,
            "models_evaluated": len(all_evaluations),
            "results": [
                {
                    "model": r["name"],
                    "similarity": r["similarity"],
                    "valid": r["valid"],
                    "score_geral": r["evaluation"]["score_geral"],
                    "metricas": r["evaluation"]["metricas"],
                    "output": r["output"]
                }
                for r in all_evaluations
            ]
        }
        save_results(final_results)
        
        # Save the detailed report in a text file
        with open("relatorio_detalhado.txt", 'w', encoding='utf-8') as f:
            for r in all_evaluations:
                f.write(f"\n{'=' * 80}\n")
                f.write(f"MODELO: {r['name'].upper()}\n")
                f.write(f"{'=' * 80}\n")
                f.write(evaluator.generate_report(r['evaluation']))
                f.write(f"\n\nQUESTÃO GERADA:\n{'-' * 80}\n")
                f.write(r['output'])
                f.write(f"\n\n")
        print(f"Relatório detalhado salvo em: relatorio_detalhado.txt")


if __name__ == "__main__":
    main()