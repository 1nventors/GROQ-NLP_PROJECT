import json
import re
import os
import subprocess
import textwrap
from graphviz import Digraph
from datetime import datetime

class QuestionExporter:
    @staticmethod
    def _get_context(generated_output):
        def_block = re.search(r"\[\[\s*def\s*:(.*?)\]\]", generated_output, re.DOTALL | re.IGNORECASE)
        if not def_block:
            print("[!] Bloco [[def:]] não encontrado.")
            return None, None
        
        raw_code = def_block.group(1)
        raw_code = raw_code.strip('\n')
        clean_code = textwrap.dedent(raw_code)
        
        context = {
            "random": __import__("random"),
            "json": __import__("json"),
            "datetime": __import__("datetime"),
            "uuid": __import__("uuid"),
            "nomes_base": ["André", "Beatriz", "Carlos", "Daniela", "Eduardo", "Fernanda"],
            "sobrenomes_base": ["Silva", "Santos", "Oliveira", "Souza", "Costa", "Almeida"]
        }
        
        try:
            exec(clean_code, context)
            return context, clean_code
        except Exception as e:
            try:
                second_attempt_code = "\n".join(clean_code.splitlines()[1:])
                exec(second_attempt_code, context)
                return context, second_attempt_code
            except:
                print(f"\n[✗] Erro persistente no Python gerado pela IA:")
                print(f"    Erro original: {e}")
                print("-" * 40)
                print(clean_code[:500])
                print("-" * 40)
                return None, clean_code

    @staticmethod
    def export_mctest_json(generated_output, model_name, q_type, filename="mctest_import.json"):
        topic = "02-Classes, atributos e métodos"
        short_desc = re.search(r"\\textbf{(.*?)}", generated_output)
        short_desc = short_desc.group(1) if short_desc else "Nova questão de POO"
        clean_text = re.sub(r"\[\[\s*def\s*:.*?\]\]", "", generated_output, flags=re.DOTALL | re.IGNORECASE)

        mctest_data = [{
            "topic_text": topic,
            "type": q_type,
            "difficulty": "3",
            "group": "",
            "short_desc": short_desc,
            "text": clean_text,
            "parametric": "no"
        }]

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(mctest_data, f, indent=2, ensure_ascii=False)
        print(f"[✓] Exportado para MCTest: {filename}")

    @staticmethod
    def export_vpl_cases(generated_output, q_type, filename="questoes.cases"):
        if q_type == "QM":
            if os.path.exists(filename):
                os.remove(filename)
            return None

        if os.path.exists(filename):
            os.remove(filename)

        context, code = QuestionExporter._get_context(generated_output)
        
        if not context:
            print("[!] Aviso: Não foi possível gerar contexto para o arquivo .cases.")
            return None

        inp_list = context.get('inp_list', [])
        out_list = context.get('out_list', [])

        if not inp_list or not out_list:
            print("[!] Erro: O código Python executou mas não gerou 'inp_list' ou 'out_list'.")
            return context

        with open(filename, 'w', encoding='utf-8') as f:
            for i in range(min(len(inp_list), 5)):
                f.write(f"case=case{i+1}\n")
                
                entrada_limpa = str(inp_list[i]).replace('\n', ' ')
                saida_limpa = str(out_list[i]).replace('\n', ' ')
                
                f.write(f"input={entrada_limpa}\n")
                f.write(f"output={saida_limpa}\n\n")

        print(f"[✓] Exportado para VPL: {filename}")
        return context

    @staticmethod
    def export_class_diagram(generated_output, filename="diagrama_classes"):
        print("   -> Gerando Diagrama de Classes UML...")
        class_matches = re.finditer(r"class\s+(\w+)(?:\((\w+)\))?:", generated_output)
        classes_info = {}
        
        for match in class_matches:
            class_name = match.group(1)
            parent_class = match.group(2)
            class_start = match.end()
            next_class = re.search(r"\nclass\s+\w+", generated_output[class_start:])
            class_end = class_start + next_class.start() if next_class else len(generated_output)
            class_body = generated_output[class_start:class_end]
            
            methods = re.findall(r"def\s+(\w+)\(self[^)]*\)", class_body)
            init_match = re.search(r"def\s+__init__.*?(?=\n    def|\nclass|\Z)", class_body, re.DOTALL)
            attributes = []
            if init_match:
                init_body = init_match.group(0)
                attributes = re.findall(r"self\.(_*\w+)\s*=", init_body)
                attributes = list(dict.fromkeys(attributes))
            
            classes_info[class_name] = {'parent': parent_class, 'attributes': attributes, 'methods': methods}
        
        if not classes_info: return
        
        dot = Digraph(comment='UML Class Diagram')
        dot.attr(rankdir='TB', bgcolor='white')
        dot.attr('node', shape='record', fontname='Arial', fontsize='10', style='filled', fillcolor='#e3f2fd')
        dot.attr('edge', arrowhead='empty', color='#1565c0')
        
        for class_name, info in classes_info.items():
            attr_lines = [f"{'-' if a.startswith('_') else '+'} {a}" for a in info['attributes']]
            meth_lines = [f"{'-' if m.startswith('_') else '+'} {m}()" for m in info['methods']]
            
            attrs_str = '\\n'.join(attr_lines)
            meths_str = '\\n'.join(meth_lines)
            
            label = f"{{{class_name}|{attrs_str}|{meths_str}}}"
            dot.node(class_name, label)
            if info['parent']: dot.edge(class_name, info['parent'])
        
        try:
            dot.render(filename, format='png', cleanup=True)
            print(f"[✓] Diagrama UML gerado: {filename}.png")
        except Exception as e: print(f"[✗] Erro no Graphviz: {e}")

    @staticmethod
    def export_pdf_latex(generated_output, filename="questao_oficial", q_type="QT"):
        print("   -> Compilando PDF via LaTeX...")
        
        context, _ = QuestionExporter._get_context(generated_output)
        
        latex_content = re.sub(r"\[\[\s*def\s*:.*?\]\]", "", generated_output, flags=re.DOTALL | re.IGNORECASE)

        patterns_to_remove = [
            r"\\textbf\{Exemplo de Entrada:\}.*?\\end\{verbatim\}",
            r"\\textbf\{Exemplo de Saída:\}.*?\\end\{verbatim\}",
            r"\\textbf\{Solução:\}.*?\\end\{verbatim\}",
            r"\[\[code:caso0_inp\]\]",
            r"\[\[code:caso0_out\]\]"
        ]
        for p in patterns_to_remove:
            latex_content = re.sub(p, "", latex_content, flags=re.DOTALL)

        parts = re.split(r"(\\begin\{verbatim\}.*?\\end\{verbatim\}|\\begin\{lstlisting\}.*?\\end\{lstlisting\})", latex_content, flags=re.DOTALL)
        sanitized_parts = []
        for part in parts:
            if part.startswith(r"\begin{verbatim}") or part.startswith(r"\begin{lstlisting}"):
                sanitized_parts.append(part)
            else:
                clean_text = re.sub(r"```[a-zA-Z]*", "", part).replace("```", "")
                clean_text = clean_text.replace("$", r"\$").replace("%", r"\%").replace("#", r"\#")
                clean_text = re.sub(r"(?<!\\)_", r"\_", clean_text) 
                clean_text = re.sub(r"\\begin\{comment\}.*?\\end\{comment\}", "", clean_text, flags=re.DOTALL)
                sanitized_parts.append(clean_text)
        
        final_body = "".join(sanitized_parts)

        if q_type == "QT" and context:
            inp_list = context.get('inp_list', [])
            out_list = context.get('out_list', [])
            if inp_list and out_list:
                ex_input = str(inp_list[0])
                ex_output = str(out_list[0])
                
                example_latex = f"""
\\vspace{{0.5cm}}
\\noindent\\textbf{{Exemplo de Entrada:}}
\\begin{{verbatim}}
{ex_input}
\\end{{verbatim}}

\\vspace{{0.3cm}}
\\noindent\\textbf{{Exemplo de Saída:}}
\\begin{{verbatim}}
{ex_output}
\\end{{verbatim}}
"""
                final_body += example_latex

        latex_template = r"""\documentclass[a4paper,12pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[brazil]{babel}
\usepackage{geometry}
\usepackage{xcolor}
\usepackage{enumitem}
\usepackage{verbatim}
\usepackage{listings}
\usepackage{fancyhdr}
\usepackage{graphicx}
\geometry{top=2.5cm, bottom=2cm, left=2.5cm, right=2.5cm}
\pagestyle{fancy}
\fancyhf{}
\lhead{Questão Gerada por IA}
\rhead{\today}
\cfoot{\thepage}
\begin{document}
"""
        full_document = latex_template + final_body + r"\end{document}"
        
        with open(f"{filename}.tex", "w", encoding="utf-8") as f: f.write(full_document)
        
        try:
            subprocess.run(["pdflatex", "-interaction=nonstopmode", f"{filename}.tex"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
            if os.path.exists(f"{filename}.pdf"): print(f"[✓] PDF Compilado: {filename}.pdf")
        finally:
            for ext in [".aux", ".log", ".out", ".toc", ".tex"]:
                if os.path.exists(f"{filename}{ext}"): os.remove(f"{filename}{ext}")