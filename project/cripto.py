import yfinance as yf

# Lista de criptomonedas que queremos consultar
tickers_crypto = ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "BNB-USD"]

# Descargar datos históricos (precio de cierre) de los últimos 3 meses
datos = yf.download(tickers_crypto, period="3mo")["Close"]

# Mostrar los datos en pantalla
print(datos.tail())
