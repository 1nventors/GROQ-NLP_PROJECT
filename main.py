from groq import Groq
from sentence_transformers import SentenceTransformer, util
import os, re

# inicializa clientes
client = Groq(api_key="GROQ_API_KEY")
model_embed = SentenceTransformer("all-MiniLM-L6-v2")  # fast model

# prompt base
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

# Listas de nomes e sobrenomes para gerar nomes de alunos
nomes_base = ["Ana", "Bruno", "Carla", "Daniel", "Eduarda", "Felipe", "Gabriela", "Hugo", "Isabela", "João"]
sobrenomes_base = ["Silva", "Santos", "Oliveira", "Souza", "Lima", "Pereira", "Costa", "Rodrigues", "Almeida", "Nunes"]

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

# Geração dos casos de teste
inp_list, out_list = [], []
num_test_cases = 10

for i in range(num_test_cases):
    nome_inicial = f"{random.choice(nomes_base)} {random.choice(sobrenomes_base)}"
    # Gera uma matrícula aleatória com 7 dígitos (ex: 2023001)
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
    else: # get_matricula
        entrada = f"{nome_inicial}, {matricula_inicial}; getMatricula()"
        saida = aluno_teste.getMatricula()

    inp_list.append(entrada)
    out_list.append(saida)

cases = {
    "input": inp_list,
    "output": out_list
}

moodle_cases = json.dumps(cases)

# Define o exemplo para a descrição da questão
caso0_inp = inp_list[0]
caso0_out = out_list[0]
]]
"""

prompt = f"Reescreva a seguinte questão de POO, mantendo o formato LaTeX, mas usando novos nomes de classe, atributos e métodos. Mantenha os exemplos de entrada/saída e o bloco [[def:...]].:\n\n{original_question}"

# call groq API
def generate_with_model(model_name, prompt):
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
        temperature=0.9,
    )
    return response.choices[0].message.content

# validates the output
def validate_output(original, generated):
    # 1. sematic similarity
    emb1 = model_embed.encode(original, convert_to_tensor=True)
    emb2 = model_embed.encode(generated, convert_to_tensor=True)
    similarity = util.cos_sim(emb1, emb2).item()

    # 2. structure check
    structure = bool(re.search(r"Classe|class", generated, re.IGNORECASE)) and bool(re.search(r"atribut", generated, re.IGNORECASE))

    return similarity, structure

# generates with both models
out_llama = generate_with_model("llama-3.1-8b-instant", prompt)
out_gpt = generate_with_model("openai/gpt-oss-20b", prompt)

# validates
sim_llama, ok_llama = validate_output(original_question, out_llama)
sim_gpt, ok_gpt = validate_output(original_question, out_gpt)

# chooses the best valid output
chosen = None
if ok_llama and (sim_llama >= sim_gpt):
    chosen = out_llama
elif ok_gpt:
    chosen = out_gpt
else:
    chosen = "⚠ Nenhuma saída válida, tente gerar novamente."

print("\nSaída escolhida:\n", chosen)
