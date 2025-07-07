import webbrowser
import os

# Caminho absoluto ou relativo do seu arquivo HTML
caminho_html = os.path.abspath("login.html")

# Abre o arquivo no navegador padrão
webbrowser.open(f"file://{caminho_html}")
