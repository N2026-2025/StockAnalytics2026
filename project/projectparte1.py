# Risk analytics and financial risk modelling (🔴 Marcado en Rojo - Baja Cobertura): 
# Porque estás programando el "Simulador de Terremotos" (Stress Testing) y calculando el VaR (Value at Risk) [💡]. 
# Estás midiendo matemáticamente cuánto daño puede aguantar tu billetera si el mercado se desploma.
# 
# Multi-asset and alternative-market applications (🟢 Marcado en Verde - Buena Cobertura): 
# Porque en lugar de analizar acciones comunes de EE. UU. (como Apple o Google que hacen todos), estás analizando activos alternativos clave para la economía argentina como la Soja (granos/commodities), el Petróleo (energía) y la volatilidad del riesgo local a través de YPF [📈, 📊].

# Parte 1: Multi-Asset Data Engine (Recolección de "Juguetes Raros" )
# Esta parte se encarga exclusivamente de conectarse a internet de forma legal para traer los precios históricos de los activos financieros alternativos relacionados con Argentina [💡].¿Qué hace el código? Descarga los precios de cierre diarios de tres mercados clave para nuestro país: la Soja (grano clave de exportación), el Petróleo (materia prima que afecta los costos locales) y las acciones de YPF (reflejo de la renta variable argentina) [📈, 📊].
#
#
import io
import numpy as np
import pandas as pd
import yfinance as yf  # Para descargar precios mundiales con riesgo cero

# 1. Definir los activos (Soja, Petróleo Brent, YPF)
tickers = ['ZS=F', 'BZ=F', 'YPF']

print("--- PARTE 1: Descargando precios históricos ---")
# Descargamos datos objetivos desde 2020 hasta el presente año 2026
data = yf.download(tickers, start='2020-01-01', end='2026-08-01')['Adj Close']
print("¡Datos descargados con éxito!")
print(data.tail())  # Muestra los últimos registros en la pantalla
