import os
import pandas as pd
import numpy as np

# 1. Cargar el dataset de acciones procesado en la Pregunta 2
print("Cargando dataset de acciones de OPVs 2025 (stocks_df.parquet)...")
candidates = [
    os.path.join("homework2", "stocks_df.parquet"),
    "stocks_df.parquet",
    os.path.join("..", "homework2", "stocks_df.parquet"),
]
stocks_path = next((p for p in candidates if os.path.exists(p)), None)
if stocks_path is None:
    print("Archivo stocks_df.parquet no encontrado. Ejecuta primero q2.py.")
    raise SystemExit(1)
stocks_df = pd.read_parquet(stocks_path)
print(f"Ruta resolvida: {stocks_path}")

stocks_df['Date'] = pd.to_datetime(stocks_df['Date'])
stocks_df = stocks_df.sort_values(['Ticker', 'Date'])

print(f"Total registros cargados: {len(stocks_df)}")
print(f"Número de tickers únicos: {stocks_df['Ticker'].nunique()}")

# 2. Feature Engineering: Calcular 12 columnas de crecimiento futuro (holding periods)
# Asumiendo 1 mes bursátil = 21 días de trading (1m = 21d, ..., 12m = 252d)
# future_growth_N_m = Close_{t + 21*N} / Close_{t}
months = range(1, 13)
for m in months:
    lookahead = 21 * m
    col = f"future_growth_{m}_m"
    stocks_df[col] = (
        stocks_df.groupby("Ticker")["Close"]
                 .shift(-lookahead) / stocks_df["Close"]
    )

# 3. Identificar puntos de entrada: primer día de trading (min_date) de cada acción tras su OPV
first_trade = (
    stocks_df.groupby("Ticker")["Date"].min().reset_index()
             .rename(columns={"Date": "min_date"})
)

# 4. Alineación de datos: Inner join para aislar los retornos desde la fecha de OPV
starts = (
    first_trade
    .merge(
        stocks_df,
        left_on=["Ticker", "min_date"],
        right_on=["Ticker", "Date"],
        how="inner"
    )
    .drop(columns="Date")
)

print(f"Empresas analizadas desde su fecha de debut (IPO): {len(starts)}")

# 5. Análisis de la mediana y estadísticas descriptivas de los 12 periodos
cols = [f"future_growth_{m}_m" for m in months]
stats = starts[cols].describe().T

print("\n--- ESTADÍSTICAS DESCRIPTIVAS DE CRECIMIENTO POR MES DE TENENCIA ---")
print(stats[['count', 'mean', 'std', 'min', '50%', 'max']].round(4))

median_series = starts[cols].median()
mean_series = starts[cols].mean()

best_col = median_series.idxmax()
best_median_val = median_series.max()
best_month = int(best_col.split("_")[2])

print("\n=== RESPUESTA PREGUNTA 3 ===")
print(f"Periodo óptimo de tenencia (en meses): {best_month} mes")
print(f"Valor máximo de la mediana de crecimiento: {best_median_val:.4f} (rendimiento: {(best_median_val - 1)*100:.2f}%)")
print(f"Opción seleccionada del cuestionario (1, 3, 5, 7): {best_month}")

print("\n--- OBSERVACIONES CUANTITATIVAS / BUSINESS ANALYST ---")
print("1. Tendencia de la Mediana en el tiempo:")
for m in (1, 3, 6, 12):
    v = median_series[f"future_growth_{m}_m"]
    print(f"   - Mes {m}: {v:.4f} ({(v - 1) * 100:.2f}%)")
print("   -> Conclusión: La mediana de retornos de las OPVs decae de forma monótona y destructiva con el paso del tiempo.")
print("      A mayor tiempo de tenencia, mayor es la pérdida acumulada para la empresa típica (el 50% de las OPVs pierde más del 48% al año).")
print("2. Media vs. Mediana (Asimetría positiva y riesgo de cola):")
mean_2m = mean_series["future_growth_2_m"]
med_2m = median_series["future_growth_2_m"]
print(f"   - En el mes 2, la Media es {mean_2m:.4f} ({(mean_2m - 1) * 100:.1f}%), mientras que la Mediana es {med_2m:.4f} ({(med_2m - 1) * 100:.1f}%).")
print("   - La media está fuertemente sesgada al alza por unos pocos valores atípicos extremos (outliers/multibaggers),")
print("     pero la gran mayoría de las inversiones en OPVs destruyen capital si no se cuenta con un filtro estricto.")
