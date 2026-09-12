#Parte 3: El Simulador de Crisis (Stress Testing & VaR)
# Esta es la parte más avanzada, innovadora y la que está menos explotada por los estudiantes de tu cohorte.
# ¿Qué hace el código? Ejecuta dos pruebas de estrés sobre tu cartera:Value at Risk (VaR Histórico): 
# Calcula matemáticamente cuál es la pérdida máxima esperable en un día normal con un 95% de confianza.
# Prueba de Estrés (Stress Test): Busca de manera automática cuál fue el peor día de crisis conjunta desde el 2020 en adelante y simula qué le pasaría a tu dinero si esa misma crisis exacta se repitiera hoy.

print("\n--- PARTE 3: Ejecutando el Simulador de Terremotos (Crisis) ---")

# 1. Calcular el VaR histórico al 95% de confianza para cada activo

# Nos dice qué es lo peor que pasa el 5% de las veces
var_95 = retornos.quantile(0.05)

# 2. Stress Test: Buscar el peor día de caída de la historia de nuestro registro
peor_escenario = retornos.min()

print("Pérdida máxima esperada en un día normal (VaR 95%):")
print(var_95 * 100)

print("\nRESULTADO STRESS TEST:")
print("Si se repitiera la peor crisis registrada desde 2020, tus activos caerían:")
print(peor_escenario * 100)
