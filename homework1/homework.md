## Tareas del Módulo 1 ya Resueltas y Validadas (Resultados 2026)

- **Q1 (S&P 500 Additions):** Año con más adiciones desde 2020 fue **2025** (18 adiciones). Acciones con >20 años en el índice = **218**.
- **Q2 (World Indices YTD):** Solo **2** índices mundiales (Japón e Canada) superaron el YTD del S&P 500 en el tramo ene-ago 2026.
- **Q3 (Corrections):** Mediana del drawdown histórico de correcciones (>=5%) es **8.71%**, con una duración media de caída de **85 días**.
- **Q4 (Earnings Surprise - AMZN):** Mediana de retorno de 2 días pos-sorpresa positiva = **+2.45%** (Correlación moderada de ~0.38).
- **Q****5. [Exploratory, optiona****l]** Brainstorm potential idea for your capstone project
- **Q6.**

**My capstone project will develop a quantitative risk and asset allocation engine for an Argentine multi-asset portfolio (`YPF`, `ZS=F`, `BZ=F`) integrated with crypto-native risk factors (`BTC-USD`, `USDT-ARS`).**

The core objective is to model how high-frequency crypto indicators, such as the 24/7 stablecoin devaluation premium and options-implied volatility indexes (Deribit DVOL), can act as early warning signals for traditional asset shocks.

Proposed Strategy & Framework

* **Target Assets:** Argentine equities (`YPF`), agricultural futures (`ZS=F`), energy commodities (`BZ=F`), and crypto liquid assets (`BTC-USD`).
* **Investment Horizon:** A **30-day tactical reallocation window** based on daily and intraday stress signals.
* **Methodology & ML Focus:****I will feed traditional technical indicators (RSI, MACD) combined with custom features like the ****Cripto-Peso Spread** into a **Machine Learning regime-switching model** (such as a Hidden Markov Model or XGBoost classifier).

  **The model's predictions will dynamically shift portfolio weights between aggressive crypto hedges and defensive commodity futures before major domestic currency jumps occur.**

  **Rigorous ****Value at Risk (VaR)** boundaries and **10,000-scenario Monte Carlo simulations** will calibrate the risk parameters under non-normal distribution (fat-tail) environments.
