from groq import Groq
from sentence_transformers import SentenceTransformer, util
from dotenv import load_dotenv
import os, re
import time

# initialize clients
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
model_embed = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")  # NLP model for semantic similarity

PICK_MODE = "most_similar"  # or "most_different"

# question prompt, in that case is a multiple choice question
original_question = r"""
\textbf{Questão de POO — Acesso a atributos privados}

Considere a seguinte classe em Python:

\begin{verbatim}
class Pessoa:
    def __init__(self, nome, idade):
        self.__nome = nome
        self.__idade = idade

    def get_nome(self):
        return self.__nome

    def set_nome(self, novo_nome):
        self.__nome = novo_nome
\end{verbatim}

Qual das alternativas abaixo descreve corretamente o que acontece ao tentar acessar \texttt{pessoa.__nome} diretamente?

\begin{enumerate}
    \item Acesso direto a \texttt{\_\_nome} não é permitido, pois o atributo é privado. % correta
    \item O Python permite o acesso e retorna o valor do atributo normalmente.
    \item O Python lança um erro de sintaxe.
    \item O Python converte automaticamente \texttt{\_\_nome} em público.
\end{enumerate}

"""


def detect_question_type(text):
    # Se o texto tiver \begin{enumerate} ou \item, consideramos múltipla escolha
    if r"\begin{enumerate}" in text:
        return "QM"
    return "QT"


def generate_prompt(question_text, question_type):
    if question_type == "QT":
        prompt = f"Reescreva do zero a seguinte questão de POO, mantendo o formato LaTeX, mas usando novos nomes de classe, atributos, métodos, adicionando novos desafios e alterando o tema ficticio da questão. Mantenha os exemplos de entrada/saída e o bloco [[def:...]].:\n\n{original_question}"
    if question_type == "QM":
        prompt = f"Gere uma nova questão de múltipla escolha similar à seguinte, no formato:\nEnunciado...\nAlternativas:\nA: (correta)\nB: (errada)\nC: (errada)\nD: (errada)\n\nQuestão:\n{question_text}"
    return prompt

# call groq API
def generate_with_model(model_name, prompt):
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000,
        temperature=0.9,
    )
    return response.choices[0].message.content

# validates the output
def validate_output(original, generated):
    # 1. sematic similarity
    emb1 = model_embed.encode(original, convert_to_tensor=True)
    emb2 = model_embed.encode(generated, convert_to_tensor=True)
    similarity = util.cos_sim(emb1, emb2).item()
    print(f"Similaridade semântica, quanto mais próximo de 1, maior similiridade: {similarity:.4f}")

    # 2. structure check
    structure = bool(re.search(r"Classe|class", generated, re.IGNORECASE)) and bool(re.search(r"atribut", generated, re.IGNORECASE))

    #3. another checks
    is_qm = bool(re.search(r"A:\s|Alternativas:", generated))
    is_qt = bool(re.search(r"Classe|atribut", generated, re.IGNORECASE))


    return similarity, structure

# Detect question type and generate prompt
question_type = detect_question_type(original_question)
print(f"[DEBUG] Tipo de questão detectado: {question_type}")
prompt = generate_prompt(original_question, question_type)


for attempt in range(3):  # tries up to 3 times
    try: 
        # generates with both models
        out_llama = generate_with_model("llama-3.1-8b-instant", prompt)
        out_gpt = generate_with_model("openai/gpt-oss-20b", prompt)

        # validates
        sim_llama, ok_llama = validate_output(original_question, out_llama)
        sim_gpt, ok_gpt = validate_output(original_question, out_gpt)

         # prints validation details
        print("\n=== Validação semântica ===")
        print(f"LLaMA → Similaridade: {sim_llama:.4f}, Estrutura OK: {ok_llama}")
        print(f"GPT   → Similaridade: {sim_gpt:.4f}, Estrutura OK: {ok_gpt}")

        # chooses the best valid output
        chosen = None
        if ok_llama and ok_gpt:
            if PICK_MODE == "most_similar":
                chosen = out_llama if sim_llama >= sim_gpt else out_gpt
            else:
                chosen = out_llama if sim_llama < sim_gpt else out_gpt
        elif ok_llama:
            chosen = out_llama
        elif ok_gpt:
            chosen = out_gpt
        else:
            chosen = "⚠ Nenhuma saída válida, tente gerar novamente."

        print(f"\n[Modo: {PICK_MODE}]")
        print("\nSaída escolhida:\n", chosen)

    except Exception as e:
        print(f"Erro na API (tentativa {attempt + 1}): {e}")
        if "rate_limit" in str(e).lower():
            print("Aguardando 45 segundos")
            time.sleep(45)