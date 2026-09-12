# Parte 2: El Tablero de Volatilidad (Risk Analytics Engine)
# Una vez que los datos están guardados en tu computadora, la Parte 2 se apaga de internet y procesa las matemáticas en tu casa (Riesgo legal = cero) [💡].
# ¿Qué hace el código? Calcula los retornos diarios (cuánto sube o baja porcentualmente el precio cada día) y mide la volatilidad (qué tan fuerte salta el precio de cada juguete). 
# Las materias primas y los activos argentinos suelen tener saltos muy bruscos en comparación con mercados estables.

print("\n--- PARTE 2: Analizando movimientos y volatilidad ---")

# Calcular las variaciones de porcentaje diarias de los precios
retornos = data.pct_change().dropna()

# Calcular la desviación estándar (volatilidad diaria) de cada activo
volatilidad = retornos.std()

print("Volatilidad diaria promedio de cada activo (mientras más alto, más salta):")
print(volatilidad * 100)  # Convertido a porcentaje para leerlo fácil
