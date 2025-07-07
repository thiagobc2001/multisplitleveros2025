import pandas as pd
import json
import re
import numpy as np

# Caminhos locais (ajuste se necessário)
caminho_excel = r'C:\Users\thiago.camargo\Downloads\LG_Catalogo_Completo_Com_Qtd (1).xlsx'
caminho_html = r'C:\Users\thiago.camargo\Python\teste\simulador.html'

# Lê a planilha
df = pd.read_excel(caminho_excel)

# Condensadoras fixas
condensadoras_nominais = {
    "18 (133%)": 18000,
    "21 (143%)": 21000,
    "24 (150%)": 24000,
    "30 (170%)": 30000,
    "36 (150%)": 36000,
    "48 (150%)": 48000
}

# Evaporadoras únicas (extraídas do catálogo)
evap_btus = df["Comb. Evap KBTU/h"].str.extractall(r'(\d+)')[0].astype(int).unique()
evaporadoras = [{"tipo": f"{b}.000 BTUs", "btus": int(b * 1000)} for b in sorted(evap_btus)]

# Condensadoras formatadas (sem campo 'codigo')
condensadoras = []
for nome, nominal in condensadoras_nominais.items():
    max_btu = df[df[nome] != "X"]["Soma Cap. Evap. KBTU/h"].max()
    condensadoras.append({
        "modelo": f"LG-{nome.replace(' ', '').replace('(', '').replace(')', '')}",
        "min": int(nominal),
        "max": int(max_btu),
        "marca": "LG"
    })

# Garante tipos serializáveis
dados_json = {
    "evaporadoras": evaporadoras,
    "condensadoras": condensadoras
}

def converter(obj):
    if isinstance(obj, (np.int64, np.integer)):
        return int(obj)
    if isinstance(obj, (np.float64, np.floating)):
        return float(obj)
    return obj

json_str = json.dumps(dados_json, indent=2, ensure_ascii=False, default=converter)

# Lê o HTML original
with open(caminho_html, 'r', encoding='utf-8') as f:
    html = f.read()

# Substitui o bloco do JSON
html = re.sub(r'const dadosJSON = \{.*?\};', f'const dadosJSON = {json_str};', html, flags=re.DOTALL)

# Substitui função JS renderizarCondensadoras com cálculo e visual dinâmico
bloco_render = """
<script>
function renderizarCondensadoras() {
  const cont = document.getElementById('condensadoras');
  cont.innerHTML = '';

  dadosJSON.condensadoras
    .filter(c => c.marca === marcaSelecionada)
    .forEach(cond => {
      const usoPercentual = totalBTUs > 0 ? Math.round((totalBTUs / cond.max) * 100) : 0;
      const compat = totalBTUs >= cond.min && totalBTUs <= cond.max;

      let status = "Incompatível";
      let bgColor = "bg-red-50 border-red-400";
      let textColor = "text-red-700";
      let onclick = "";

      if (compat && usoPercentual > 130) {
        status = "Compatível com Alerta";
        bgColor = "bg-yellow-50 border-yellow-400";
        textColor = "text-yellow-700";
        onclick = `onclick="alert('Atenção: Uso acima de 130% da capacidade máxima desta condensadora.')"`
      } else if (compat) {
        status = "Compatível";
        bgColor = "bg-green-50 border-green-500";
        textColor = "text-green-700";
      }

      const usoTexto = totalBTUs > 0
        ? `<p class="text-sm"><strong>Capacidade Utilizada:</strong> ${usoPercentual}%</p>`
        : "";

      cont.innerHTML += `
        <div class="p-5 border rounded-lg shadow-sm card-hover ${bgColor}" ${onclick}>
          <h3 class="text-lg font-semibold text-gray-800 mb-1">${cond.modelo}</h3>
          <p class="text-sm"><strong>Capacidade:</strong> ${cond.min} - ${cond.max} BTUs</p>
          <p class="text-sm"><strong>Marca:</strong> ${cond.marca}</p>
          <p class="text-sm"><strong>Uso Atual:</strong> ${usoPercentual}%</p>
          ${usoTexto}
          <p class="mt-2 text-sm font-semibold ${textColor}">${status}</p>
        </div>`;
    });
}
</script>
"""

# Substitui função JS
html = re.sub(r"<script>\s*function renderizarCondensadoras\(\)[\s\S]+?</script>", bloco_render.strip(), html, flags=re.MULTILINE)

# Salva o HTML atualizado
with open(caminho_html, 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ HTML atualizado com dados dinâmicos e cálculo de uso percentual incluído!")
