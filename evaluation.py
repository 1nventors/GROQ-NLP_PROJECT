import spacy
import ast
import re
from typing import Dict, Any
import json
from datetime import datetime


class QuestionEvaluator:    
    def __init__(self):
        try:
            self.nlp = spacy.load("pt_core_news_md")
            print("[✓] Modelo spaCy carregado com sucesso")
        except OSError:
            print("[!] Modelo spaCy não encontrado. Execute: python -m spacy download pt_core_news_md")
            self.nlp = None
    
    def evaluate_question(self, original_text: str, generated_text: str) -> Dict[str, Any]:
        results = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "metricas": {}
        }
        
        # 1. semantic analysis with spaCy
        if self.nlp:
            results["metricas"].update(self._semantic_evaluation(original_text, generated_text))
        
        # 2. Latex validation
        results["metricas"].update(self._latex_validation(generated_text))
        
        # 3. Python code validation
        results["metricas"].update(self._python_validation(generated_text))
        
        # 4. Estrutural analysis
        results["metricas"].update(self._estructure_analysis(generated_text))
        
        # 5. General score calculation (1-10)
        results["score_geral"] = self._calculte_score(results["metricas"])
        
        return results
    
    def _semantic_evaluation(self, original: str, generated: str) -> Dict[str, Any]:
        doc1 = self.nlp(original)
        doc2 = self.nlp(generated)
        
        similarity = doc1.similarity(doc2) 
        
        entities_original = set([ent.label_ for ent in doc1.ents])
        entities_generated = set([ent.label_ for ent in doc2.ents])
        
        tokens_original = len([token for token in doc1 if not token.is_stop and not token.is_punct])
        tokens_generated = len([token for token in doc2 if not token.is_stop and not token.is_punct])
        
        return {
            "coerencia_semantica": round(similarity, 4),
            "interpretacao_similaridade": self._similarity_check(similarity),
            "entidades_originais": list(entities_original),
            "entidades_geradas": list(entities_generated),
            "tokens_significativos_original": tokens_original,
            "tokens_significativos_gerado": tokens_generated,
            "razao_tokens": round(tokens_generated / tokens_original if tokens_original > 0 else 0, 2)
        }
    
    def _similarity_check(self, sim: float) -> str:
        if sim > 0.8:
            return "Muito Similar (possível cópia da questão original, por favor verifique a saída)"
        elif sim > 0.6:
            return "Similar (boa variação)"
        elif sim > 0.4:
            return "Moderadamente Similar"
        elif sim > 0.2:
            return "Pouco Similar"
        else:
            return "Muito Diferente"
    
    def _latex_validation(self, text: str) -> Dict[str, Any]:
        latex_patterns = {
            "verbatim_blocks": r"\\begin{verbatim}.*?\\end{verbatim}",
            "enumerate_blocks": r"\\begin{enumerate}.*?\\end{enumerate}",
            "textbf": r"\\textbf{.*?}",
            "texttt": r"\\texttt{.*?}",
            "items": r"\\item"
        }
        
        encontrados = {}
        for name, pattern in latex_patterns.items():
            matches = re.findall(pattern, text, re.DOTALL)
            encontrados[name] = len(matches)
        
        begin_count = len(re.findall(r"\\begin{", text))
        end_count = len(re.findall(r"\\end{", text))
        blocos_balanceados = begin_count == end_count
        total_comandos = sum(encontrados.values())
        latex_ok = blocos_balanceados and (total_comandos > 0)
        
        return {
            "latex_valido": latex_ok,
            "blocos_balanceados": blocos_balanceados,
            "total_comandos_latex": total_comandos
        }
    
    def _python_validation(self, text: str) -> Dict[str, Any]:
        codigos = re.findall(r"\\begin{verbatim}(.*?)\\end{verbatim}", text, re.DOTALL)
        
        resultados = {
            "blocos_codigo_encontrados": len(codigos),
            "codigos_validos": 0,
            "codigos_invalidos": 0,
            "erros_sintaxe": []
        }
        
        for i, codigo in enumerate(codigos):
            codigo_limpo = codigo.strip()
            try:
                ast.parse(codigo_limpo)
                resultados["codigos_validos"] += 1
            except SyntaxError as e:
                resultados["codigos_invalidos"] += 1
                resultados["erros_sintaxe"].append({
                    "bloco": i + 1,
                    "erro": str(e),
                    "linha": e.lineno if hasattr(e, 'lineno') else None
                })
        
        resultados["codigo_python_ok"] = (
            resultados["blocos_codigo_encontrados"] > 0 and
            resultados["codigos_invalidos"] == 0
        )
        
        return resultados
    
    def _estructure_analysis(self, text: str) -> Dict[str, Any]:
        estrutura = {
            "tem_classe": bool(re.search(r"\bclass\s+\w+", text)),
            "tem_metodos": bool(re.search(r"\bdef\s+\w+", text)),
            "tem_atributos": bool(re.search(r"self\.\w+", text)),
            "tem_alternativas": bool(re.search(r"\\item|Alternativas:", text, re.IGNORECASE)),
            "tem_enunciado": len(text) > 100,
            "tamanho_texto": len(text),
            "numero_linhas": len(text.split('\n'))
        }
        
        classes = re.findall(r"\bclass\s+(\w+)", text)
        metodos = re.findall(r"\bdef\s+(\w+)", text)
        
        estrutura["classes_encontradas"] = classes
        estrutura["metodos_encontrados"] = metodos
        estrutura["total_classes"] = len(classes)
        estrutura["total_metodos"] = len(metodos)
        
        return estrutura
    
    # Calculate overall score from 1 to 10
    def _calculte_score(self, metricas: Dict[str, Any]) -> float:
        pontos = 0
        max_pontos = 0
        
        # Semantic coherence (weight 3)
        if "coerencia_semantica" in metricas:
            sim = metricas["coerencia_semantica"]
            # If similarity is very high or very low, penalize
            if 0.4 <= sim <= 0.7:
                pontos += 3
            elif 0.3 <= sim < 0.4 or 0.7 < sim <= 0.8:
                pontos += 2
            else:
                pontos += 1
            max_pontos += 3
        
        # LaTeX (weight 2)
        if metricas.get("latex_valido", False):
            pontos += 2
        max_pontos += 2
        
        # Python code (weight 3)
        if metricas.get("codigo_python_ok", False):
            pontos += 3
        max_pontos += 3
        
        # Estructure (weight 2)
        if metricas.get("tem_classe", False):
            pontos += 0.5
        if metricas.get("tem_metodos", False):
            pontos += 0.5
        if metricas.get("tem_atributos", False):
            pontos += 0.5
        if metricas.get("tem_alternativas", False):
            pontos += 0.5
        max_pontos += 2
        
        score = (pontos / max_pontos) * 10 if max_pontos > 0 else 0
        return round(score, 2)
    
    def generate_report(self, resultados: Dict[str, Any], formato: str = "texto") -> str:
        if formato == "json":
            return json.dumps(resultados, indent=2, ensure_ascii=False)
        
        relatorio = []
        relatorio.append("=" * 80)
        relatorio.append("RELATÓRIO TÉCNICO DE AVALIAÇÃO DE QUESTÃO")
        relatorio.append("=" * 80)
        relatorio.append(f"Timestamp: {resultados['timestamp']}")
        relatorio.append(f"Score Geral: {resultados['score_geral']}/10")
        relatorio.append("")
        
        metricas = resultados["metricas"]
        
        # Semantic Analysis Section
        relatorio.append("─" * 80)
        relatorio.append("1. ANÁLISE SEMÂNTICA")
        relatorio.append("─" * 80)
        if "coerencia_semantica" in metricas:
            relatorio.append(f"  Coerência Semântica: {metricas['coerencia_semantica']}")
            relatorio.append(f"  Interpretação: {metricas['interpretacao_similaridade']}")
            relatorio.append(f"  Tokens Significativos (Original): {metricas['tokens_significativos_original']}")
            relatorio.append(f"  Tokens Significativos (Gerado): {metricas['tokens_significativos_gerado']}")
            relatorio.append(f"  Razão de Tokens: {metricas['razao_tokens']}")
        relatorio.append("")
        
        # LateX Section (Blocos de código removidos)
        relatorio.append("─" * 80)
        relatorio.append("2. VALIDAÇÃO LaTeX")
        relatorio.append("─" * 80)
        relatorio.append(f"  LaTeX Válido: {'✓' if metricas.get('latex_valido') else '✗'}")
        relatorio.append(f"  Blocos Balanceados: {'✓' if metricas.get('blocos_balanceados') else '✗'}")
        relatorio.append(f"  Total de Comandos LaTeX: {metricas.get('total_comandos_latex', 0)}")
        relatorio.append("")
        
        # Python Code Section
        relatorio.append("─" * 80)
        relatorio.append("3. VALIDAÇÃO CÓDIGO PYTHON")
        relatorio.append("─" * 80)
        relatorio.append(f"  Código Python OK: {'✓' if metricas.get('codigo_python_ok') else '✗'}")
        relatorio.append(f"  Blocos de Código: {metricas.get('blocos_codigo_encontrados', 0)}")
        relatorio.append(f"  Válidos: {metricas.get('codigos_validos', 0)}")
        relatorio.append(f"  Inválidos: {metricas.get('codigos_invalidos', 0)}")
        if metricas.get('erros_sintaxe'):
            relatorio.append("  Erros de Sintaxe:")
            for erro in metricas['erros_sintaxe']:
                relatorio.append(f"    • Bloco {erro['bloco']}: {erro['erro']}")
        relatorio.append("")
        
        # Estructural Analysis Section
        relatorio.append("─" * 80)
        relatorio.append("4. ANÁLISE ESTRUTURAL")
        relatorio.append("─" * 80)
        relatorio.append(f"  Tem Classe: {'✓' if metricas.get('tem_classe') else '✗'}")
        relatorio.append(f"  Tem Métodos: {'✓' if metricas.get('tem_metodos') else '✗'}")
        relatorio.append(f"  Tem Atributos: {'✓' if metricas.get('tem_atributos') else '✗'}")
        relatorio.append(f"  Tem Alternativas: {'✓' if metricas.get('tem_alternativas') else '✗'}")
        relatorio.append(f"  Total de Classes: {metricas.get('total_classes', 0)}")
        relatorio.append(f"  Total de Métodos: {metricas.get('total_metodos', 0)}")
        relatorio.append("")
        
        relatorio.append("=" * 80)
        
        return "\n".join(relatorio)


if __name__ == "__main__":
    evaluator = QuestionEvaluator()
    
    original = r"""\textbf{Questão de POO}...\begin{verbatim}class Teste:\end{verbatim}"""
    generated = r"""\textbf{Nova Questão}...\begin{verbatim}class Novo:\end{verbatim}"""
    
    results = evaluator.evaluate_question(original, generated)
    print(evaluator.generate_report(results))