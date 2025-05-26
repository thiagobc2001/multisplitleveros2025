import pandas as pd
import os

# Caminho para salvar no Desktop
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "condensadoras_multisplit_exemplo.xlsx")

# Dados
evaporadoras = [
    {"TipoEvaporadora": "9.000 BTUs", "BTUs": 9000},
    {"TipoEvaporadora": "12.000 BTUs", "BTUs": 12000},
    {"TipoEvaporadora": "18.000 BTUs", "BTUs": 18000},
    {"TipoEvaporadora": "24.000 BTUs", "BTUs": 24000},
    {"TipoEvaporadora": "30.000 BTUs", "BTUs": 30000},
]

condensadoras = [
    {"ModeloCondensadora": "LG-MULTI48", "CapMin": 18000, "CapMax": 48000, "Marca": "LG", "Código": "LG001"},
    {"ModeloCondensadora": "Samsung-Triple36", "CapMin": 18000, "CapMax": 36000, "Marca": "Samsung", "Código": "SS036"},
    {"ModeloCondensadora": "Fujitsu-Pro54", "CapMin": 27000, "CapMax": 54000, "Marca": "Fujitsu", "Código": "FJ054"},
    {"ModeloCondensadora": "TCL-Smart42", "CapMin": 18000, "CapMax": 42000, "Marca": "TCL", "Código": "TCL42"},
]

# Combina os dados para salvar em uma única planilha
df_evap = pd.DataFrame(evaporadoras)
df_cond = pd.DataFrame(condensadoras)
df_combined = pd.concat([df_evap.iloc[:len(df_cond)].reset_index(drop=True), df_cond], axis=1)

# Salvar no desktop
df_combined.to_excel(desktop_path, index=False)
print(f"✅ Planilha criada com sucesso em: {desktop_path}")
