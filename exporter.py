import json
import re
import os

class QuestionExporter:
    @staticmethod
    def export_mctest_json(generated_output, model_name, q_type, filename="mctest_import.json"):
        # Extract some metadata
        topic = "02-Classes, Atributos e Métodos"
        short_desc = re.search(r"\\textbf{(.*?)}", generated_output)
        short_desc = short_desc.group(1) if short_desc else "Nova Questão POO"
        
        # MCTest JSON structure
        mctest_data = [{
            "topic_text": topic,
            "type": q_type,
            "difficulty": "3",
            "group": "",
            "short_desc": short_desc,
            "text": generated_output,
            "parametric": "no"
        }]

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(mctest_data, f, indent=2, ensure_ascii=False)
        print(f"[✓] Exportado para MCTest: {filename}")

    @staticmethod
    def export_vpl_cases(generated_output, filename="questoes.cases"):
        
        # Localize the [[def:]] block
        def_block = re.search(r"\[\[def:(.*?)\]\]", generated_output, re.DOTALL)
        if not def_block:
            print("[!] Aviso: Bloco [[def:]] não encontrado para gerar .cases")
            return

        code = def_block.group(1)
        
        context = {
            "random": __import__("random"),
            "json": __import__("json"),
            "nomes_base": ["André", "Beatriz", "Carlos", "Daniela"],
            "sobrenomes_base": ["Silva", "Santos", "Oliveira", "Souza"]
        }

        try:
            # Execute the code to find inp_list and out_list
            exec(code, context)
            
            inp_list = context.get('inp_list', [])
            out_list = context.get('out_list', [])

            if not inp_list:
                print("[!] Aviso: inp_list está vazia no código da questão.")
                return

            # Write to .cases file
            with open(filename, 'w', encoding='utf-8') as f:
                for i in range(len(inp_list)):
                    f.write(f"case=caso{i+1}\n")
                    entrada = str(inp_list[i]).replace('\n', ' ')
                    saida = str(out_list[i]).replace('\n', ' ')
                    f.write(f"input={entrada}\n")
                    f.write(f"output={saida}\n")
            
            print(f"[✓] Exportado para VPL: {filename}")
            
        except Exception as e:
            print(f"[✗] Erro ao executar o código da questão para gerar .cases: {e}")