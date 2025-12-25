import os

class QuestionReporter:
    @staticmethod
    def generate_html(generated_output, score, model_name, filename="relatorio_final.html"):
        print("   -> Gerando relatório com HTML ...")
        score_color = "#4caf50" if score >= 8 else "#ff9800" if score >= 6 else "#f44336"
        
        display_output = generated_output.replace('<', '&lt;').replace('>', '&gt;')
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>AI Gen Report</title>
            <style>
                body {{ font-family: sans-serif; background: #f4f4f9; padding: 20px; }}
                .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); max-width: 800px; margin: auto; }}
                .badge {{ background: #007bff; color: white; padding: 4px 8px; border-radius: 4px; }}
                .score {{ float: right; background: {score_color}; color: white; padding: 10px; border-radius: 50%; width: 40px; height: 40px; text-align: center; line-height: 40px; font-weight: bold; }}
                pre {{ background: #222; color: #fff; padding: 10px; overflow: auto; border-radius: 5px; white-space: pre-wrap; }}
                .btn {{ display: inline-block; padding: 10px 15px; margin: 5px; text-decoration: none; color: white; border-radius: 5px; }}
                .pdf {{ background: #dc3545; }} .json {{ background: #ffc107; color: #000; }} .vpl {{ background: #17a2b8; }}
                .diagram {{ text-align: center; margin-top: 20px; }}
                .diagram img {{ max-width: 100%; border: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="card">
                <div class="score">{score}</div>
                <h2>Generation Report</h2>
                <p>Model: <span class="badge">{model_name}</span></p>
                <div>
                    <a href="questao_oficial.pdf" class="btn pdf">Official PDF</a>
                    <a href="mctest_import.json" class="btn json">Moodle JSON</a>
                    <a href="questoes.cases" class="btn vpl">VPL Cases</a>
                </div>

                <div class="diagram">
                    <h3>UML Class Diagram</h3>
                    <img src="diagrama_classes.png" alt="Diagram not generated">
                </div>

                <h3>Original LaTeX Content</h3>
                <pre>{display_output}</pre>
            </div>
        </body>
        </html>
        """
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[✓] HTML Gerado : {filename}")