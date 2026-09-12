import pandas as pd
import yfinance as yf


def descargar_metricas_exploratorias():
    """
    Descarga métricas cripto-macro avanzadas para el proyecto 2026.
    """
    tickers = {
        "Dólar Cripto": "USDT-ARS",
        "Bitcoin Liquidez": "BTC-USD",
        "Estabilidad Tether": "USDT-USD",
    }

    print("🔍 Recuperando series temporales exploratorias...")
    df_metrics = yf.download(list(tickers.values()), period="6mo")["Close"]

    # Renombrar columnas para claridad metodológica
    df_metrics.rename(
        columns={v: k for k, v in tickers.items()}, inplace=True
    )

    # Calcular indicador proxy: Volatilidad Móvil del Dólar Cripto (Ventana de 14 días)
    df_metrics["Volatilidad_USDT_ARS"] = (
        df_metrics["Dólar Cripto"].pct_change().rolling(14).std()
    )

    return df_metrics.dropna()


if __name__ == "__main__":
    datos_nuevos = descargar_metricas_exploratorias()
    print("\n📈 Últimos registros de las nuevas métricas:")
    print(datos_nuevos.tail(3))
