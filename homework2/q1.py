import io
import requests
import pandas as pd
import numpy as np

# 1. Carga de datos con User-Agent y StringIO para compatibilidad Windows/pandas
url = "https://iposcoop.com/ipos-recently-filed/"
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/119.0.0.0 Safari/537.36"
    )
}

print("Descargando tabla de OPVs recientemente presentadas (iposcoop.com)...")
resp = requests.get(url, headers=headers, timeout=30)
resp.raise_for_status()

# Envolver en io.StringIO para evitar advertencias y errores OSError en Windows
df_raw = pd.read_html(io.StringIO(resp.text))[0]

# Filtrar empresas retiradas ('Withdrawn')
df_withdrawn = df_raw[df_raw['Expected To Trade'] == 'Withdrawn'].copy()
print(f"Total registros retirados identificados: {len(df_withdrawn)}")

# 2. Clasificación de tipo de empresa por reglas de precedencia estricta
def classify_company_type(name: str) -> str:
    name = str(name)
    # 1. "Technologies" -> Technologies (coincidencia exacta del patrón)
    if "Technologies" in name:
        return "Technologies"
    # 2. "Acquisition Corp", "Acquisition Corporation" o "Corp" -> Acquisition Corp
    if any(p in name for p in ["Acquisition Corp", "Acquisition Corporation", "Corp"]):
        return "Acquisition Corp"
    # 3. "Inc" o "Incorporated" -> Inc.
    if any(p in name for p in ["Inc", "Incorporated"]):
        return "Inc."
    # 4. "Group" -> Group
    if "Group" in name:
        return "Group"
    # 5. "Ltd" o "Limited" -> Limited
    if any(p in name for p in ["Ltd", "Limited"]):
        return "Limited"
    # 6. "Holdings" o "Holding" -> Holdings
    if any(p in name for p in ["Holdings", "Holding"]):
        return "Holdings"
    # 7. Otros -> Other
    return "Other"

df_withdrawn['Company Type'] = df_withdrawn['Company'].apply(classify_company_type)

# 3. Parseo de precios y cálculo de Avg_price
def parse_price(val) -> float:
    if pd.isna(val):
        return np.nan
    s = str(val).replace('$', '').replace(',', '').strip()
    if s in ['', '-', 'nan', 'none']:
        return np.nan
    try:
        return float(s)
    except ValueError:
        return np.nan

df_withdrawn['Price_Low_num'] = df_withdrawn['Price Low'].apply(parse_price)
df_withdrawn['Price_High_num'] = df_withdrawn['Price High'].apply(parse_price)
df_withdrawn['Avg_price'] = df_withdrawn[['Price_Low_num', 'Price_High_num']].mean(axis=1)

# 4. Conversión numérica de acciones y volumen estimado
def parse_millions(val) -> float:
    if pd.isna(val):
        return np.nan
    s = str(val).replace('$', '').replace(',', '').strip()
    if s in ['', '-', 'nan', 'none']:
        return np.nan
    try:
        return float(s)
    except ValueError:
        return np.nan

df_withdrawn['Shares_clean'] = df_withdrawn['Shares (millions)'].apply(parse_millions)
df_withdrawn['Est_Vol_clean'] = df_withdrawn['Est $ Vol (millions)'].apply(parse_millions)

# 5. Cálculo del valor de las acciones ofrecidas (Shares_offered_value)
shares_calc = df_withdrawn['Shares_clean'] * df_withdrawn['Avg_price']
df_withdrawn['Shares_offered_value'] = np.where(
    shares_calc.notna(),
    shares_calc,
    df_withdrawn['Est_Vol_clean']
)

# 6. Agregación y reporte financiero por clase de empresa
summary = df_withdrawn.groupby('Company Type')['Shares_offered_value'].agg(['sum', 'count'])
summary = summary.sort_values(by='sum', ascending=False)

print("\n--- RESUMEN DE RETIRADAS POR TIPO DE EMPRESA ---")
print(summary)

top_class = summary['sum'].idxmax()
top_value = summary['sum'].max()

print("\n=== RESPUESTA PREGUNTA 1 ===")
print(f"Tipo de empresa con mayor valor retirado: {top_class}")
print(f"Valor total retirado: ${top_value:.3f} millones (Aproximado a opciones del formulario: ~500)")
