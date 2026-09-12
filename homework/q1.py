import io
import pandas as pd
import requests

# 1. Configurar URL y headers del navegador solicitados
url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

# Realizar la petición HTTP
response = requests.get(url, headers=headers)

# CORRECCIÓN: Envolver response.text en io.StringIO() para evitar el FutureWarning
html_data = io.StringIO(response.text)
tables = pd.read_html(html_data)
df = tables[0] # Seleccionamos la primera tabla (componentes del S&P 500)

# 2. Limpieza de datos y extracción de fechas
df['Date_clean'] = pd.to_datetime(df['Date added'].str.slice(0, 10), errors='coerce')
df['Year'] = df['Date_clean'].dt.year

# --- Pregunta 1: Año con mayor número de adiciones desde 2020 ---
df_since_2020 = df[df['Year'] >= 2020]
additions_by_year = df_since_2020['Year'].value_counts().sort_index()

max_year = additions_by_year.idxmax()
max_additions = additions_by_year.max()

# --- Pregunta Adicional: Acciones con más de 20 años en el índice ---
cutoff_year = 2026 - 20
stocks_older_than_20_years = df[df['Year'] < cutoff_year]
total_older_stocks = len(stocks_older_than_20_years)

# Mostrar resultados limpios
print("Adiciones al S&P 500 por año:")
print(additions_by_year)
print(f"\nEl año completo con mayor número de adiciones es: {max_year} ({max_additions} adiciones)")
print(f"Número de acciones actuales en el índice por más de 20 años: {total_older_stocks}")
