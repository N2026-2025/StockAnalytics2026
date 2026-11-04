# Module 5 Homework — Stock Research Ideas (2026 Cohort)

**Date:** 2026-10-31  
**Language:** English (with Spanish explanations)  
**Environment:** Free-text answers, no code required  

---

## Overview

This document proposes three distinct stock research ideas following the required six-part structure:

1. Market and scope / Mercado y alcance
2. Investment thesis / Tesis de inversión
3. Potential edge / Potencial ventaja
4. Data and sources / Datos y fuentes
5. Research approach / Enfoque de investigación
6. Validation and risks / Validación y riesgos

Each idea uses a different economic mechanism, market, data source, and investment horizon, as the assignment requires.

---

## Research Idea 1 — Local Information Advantage: Mexico (BMV) Consumer Staples

### 1. Market and scope / Mercado y alcance

**Market:** Bolsa Mexicana de Valores (BMV), Mexico.  
**Sector:** Consumer staples (food, beverages, household goods) — e.g., Gruma, Bimbo, Coca-Cola FEMSA, Kimberly-Clark de México.  
**Horizon:** Quarterly — trade around earnings announcements and quarterly economic releases (inflation, retail sales).

(Mercado: BMV de México. Sector: bienes de consumo (alimentos, bebidas, artículos del hogar). Horizonte: trimestral — operar alrededor de anuncios de resultados y publicaciones económicas trimestrales como inflación y ventas minoristas.)

### 2. Investment thesis / Tesis de inversión

Companies in Mexico's consumer staples sector derive most revenue from domestic peso-denominated sales. Quarterly inflation data (INEGI) and minimum-wage adjustments affect their input costs and consumer purchasing power before the market fully prices them in. Local-language disclosures and same-day economic releases give an early read on margin pressure that English-language analyst coverage may miss or react to with a delay.

(Las empresas de bienes de consumo de México generan la mayor parte de sus ingresos en pesos. Los datos trimestrales de inflación del INEGI y los ajustes del salario mínimo afectan sus costos y el poder adquisitivo antes de que el mercado los refleje completamente en los precios. Las divulgaciones en idioma local y los datos económicos del mismo día dan una lectura temprana de la presión de márgenes que la cobertura de analistas en inglés puede pasar por alto o procesar con retraso.)

### 3. Potential edge / Potencial ventaja

Edge comes from language and geography: reading BMV filings and INEGI releases in Spanish on the day of publication, before English-language providers translate and summarize them. Local knowledge of consumer behavior (e.g., how peso depreciation affects tortilla and soda demand) can signal earnings surprises earlier than global models trained mostly on US data.

(La ventaja proviene del idioma y la geografía: leer los informes de la BMV y los datos del INEGI en español el día de su publicación, antes de que los proveedores en inglés los traduzcan y resuman. El conocimiento local del comportamiento del consumidor (por ejemplo, cómo la depreciación del peso afecta la demanda de tortillas y refrescos) puede señalar sorpresas de resultados antes que los modelos globales entrenados principalmente con datos de EE. UU.)

### 4. Data and sources / Datos y fuentes

**Verified / checked:**
- BMV quarterly financial reports (eventos materiales, reportes trimestrales) — bmv.com.mx
- INEGI inflation (INPC) and retail sales releases — inegi.org.mx

**To verify / pending confirmation:**
- BMV historical earnings surprise data and exact publication timestamps
- Daily liquidity and bid-ask spreads for mid-cap BMV consumer staples (trading cost feasibility)
- Same-day Spanish-to-English translation lag for major data vendors (Bloomberg, Refinitiv)

(Datos y fuentes: Verificados: reportes financieros trimestrales de la BMV — bmv.com.mx; inflación y ventas minoristas del INEGI — inegi.org.mx. Por verificar: datos históricos de sorpresas de resultados y marcas de tiempo exactas de publicación; liquidez diaria y spreads de oferta y demanda para consumidores de mediana capitalización en la BMV; retraso de traducción español-inglés de los principales proveedores de datos.)

### 5. Research approach / Enfoque de investigación

Build an event study around quarterly earnings announcements. Compute cumulative abnormal returns (CAR) over [-1, +5] trading days around each announcement. Test whether the sign and magnitude of the INEC inflation surprise (actual vs. consensus) and the peso/USD move on announcement day predict the direction of the earnings surprise. Use a simple logistic regression: earnings beat/miss ~ inflation surprise + FX move + prior-quarter return.

(Enfoque: construir un estudio de eventos alrededor de anuncios trimestrales de resultados. Calcular retornos anormales acumulados (CAR) en [-1, +5] días hábiles alrededor de cada anuncio. Probar si la sorpresa de inflación del INEC (real vs. consenso) y el movimiento del peso/dólar el día del anuncio predicen la dirección de la sorpresa de resultados. Regresión logística simple: sorpresa de resultados (beat/miss) ~ sorpresa de inflación + movimiento FX + retorno del trimestre anterior.)

### 6. Validation and risks / Validación y riesgos

**Benchmark:** Buy-and-hold the IPC index (BMV main index) over the same quarterly windows.  
**Reject condition:** If CAR after inflation surprises is not statistically different from zero (t-stat < 1.96) across 8+ quarters, reject.  
**Risks:** Low liquidity and wide spreads on smaller BMV names can erase alpha; publication delays or revised INEGI data can invalidate the signal; currency risk for USD-based investors; single-market concentration.

(Benchmark: comprar y mantener el índice IPC (índice principal de la BMV) durante las mismas ventanas trimestrales. Condición de rechazo: si el CAR después de sorpresas de inflación no es estadísticamente diferente de cero (t-stat < 1.96) en 8+ trimestres, rechazar. Riesgos: baja liquidez y spreads amplios en nombres más pequeños de la BMV pueden eliminar la alfa; retrasos de publicación o datos revisados del INEGI pueden invalidar la señal; riesgo cambiario para inversores en USD; concentración en un solo mercado.)

---

## Research Idea 2 — Relative Value / Pairs Trading: US Semiconductors

### 1. Market and scope / Mercado y alcance

**Market:** United States, NASDAQ.  
**Sector:** Semiconductors — pairs of economically linked companies (e.g., NVIDIA vs. AMD, or Texas Instruments vs. Analog Devices).  
**Horizon:** Weekly to monthly — hold mean-reversion positions for days to weeks.

(Mercado: Estados Unidos, NASDAQ. Sector: semiconductores — pares de empresas económicamente vinculadas (por ejemplo, NVIDIA vs. AMD, o Texas Instruments vs. Analog Devices). Horizonte: semanal a mensual — mantener posiciones de reversión a la media durante días a semanas.)

### 2. Investment thesis / Tesis de inversión

Semiconductor pairs share common demand drivers (data center capex, auto electrification, AI chip demand) and often move together. When their relative price ratio deviates significantly from its historical mean due to idiosyncratic news (product delay, earnings miss at one firm), the ratio tends to mean-revert as the common factor reasserts itself. The trade is on the spread, not on the direction of the sector.

(Los pares de semiconductores comparten impulsores de demanda comunes (capex de centros de datos, electrificación automotriz, demanda de chips de IA) y a menudo se mueven juntos. Cuando su ratio de precios relativo se desvía significativamente de su media histórica debido a noticias idiosincrásicas (retraso de producto, falla de resultados en una firma), el ratio tiende a revertir a la media cuando el factor común se reafirma. La operación es sobre el spread, no sobre la dirección del sector.)

### 3. Potential edge / Potencial ventaja

Edge comes from identifying mean-reversion faster than broad ETF flows (e.g., SMH) and options flow that react to headline news. By modeling the spread with a cointegration or z-score framework and using intraday OHLCV, you can catch temporary dislocations before arbitrage algorithms and ETF rebalancing close the gap.

(La ventaja proviene de identificar la reversión a la media más rápido que los flujos de ETF amplios (por ejemplo, SMH) y el flujo de opciones que reaccionan a noticias principales. Al modelar el spread con un marco de cointegración o z-score y usar OHLCV intradía, puedes capturar dislocaciones temporales antes de que los algoritmos de arbitraje y el rebalanceo de ETF cierren la brecha.)

### 4. Data and sources / Datos y fuentes

**Verified / checked:**
- Daily OHLCV for US equities (public, via Yahoo Finance / Alpha Vantage / polygon.io)
- SMH (VanEck Semiconductor ETF) price data for sector context

**To verify / pending confirmation:**
- Intraday (1-minute) OHLCV for pair members (data cost and availability)
- Options flow / unusual options activity data for the pair (unusualputcall, etc.)
- Historical cointegration stability of chosen pairs over 2020–2025 (needs backtest)

(Datos y fuentes: Verificados: OHLCV diario de acciones de EE. UU. (público, vía Yahoo Finance / Alpha Vantage / polygon.io); datos de precios de SMH (VanEck Semiconductor ETF) para contexto sectorial. Por verificar: OHLCV intradía (1 minuto) para miembros del par (costo y disponibilidad de datos); datos de flujo de opciones / actividad inusual de opciones para el par; estabilidad histórica de cointegración de pares elegidos durante 2020–2025 (requiere backtest).)

### 5. Research approach / Enfoque de investigación

Select candidate pairs with high correlation (>0.8) over a 1-year rolling window. Test for cointegration (Engle-Granger or Johansen) on the price ratio. Compute the z-score of the spread; enter long the underperformer / short the outperformer when |z| > 2.0, exit when |z| < 0.5. Use the 20-day rolling mean and standard deviation for the z-score. Backtest with 10 bps round-trip transaction costs.

(Enfoque: seleccionar pares candidatos con correlación alta (>0.8) sobre una ventana móvil de 1 año. Probar cointegración (Engle-Granger o Johansen) en el ratio de precios. Calcular el z-score del spread; entrar largo el subdesempeño / corto el sobredesempeño cuando |z| > 2.0, salir cuando |z| < 0.5. Usar la media móvil de 20 días y la desviación estándar para el z-score. Backtest con costos de transacción de 10 pb ida y vuelta.)

### 6. Validation and risks / Validación y riesgos

**Benchmark:** Buy-and-hold SMH (semiconductor ETF) over the same periods.  
**Reject condition:** If the spread's cointegration breaks down (p-value > 0.05) in the out-of-sample period, or if net Sharpe after costs < 0.5, reject.  
**Risks:** Regime change (one firm gains durable competitive advantage — the relationship breaks); transaction costs erode small mean-reversion profits; short-sale constraints and borrow fees; execution slippage on less liquid legs.

(Benchmark: comprar y mantener SMH (ETF de semiconductores) durante los mismos períodos. Condición de rechazo: si la cointegración del spread se descompone (p-valor > 0.05) en el período fuera de muestra, o si el Sharpe neto después de costos < 0.5, rechazar. Riesgos: cambio de régimen (una firma gana ventaja competitiva duradera — la relación se rompe); los costos de transacción erosionan pequeñas ganancias de reversión a la media; restricciones de venta en corto y comisiones de préstamo; deslizamiento de ejecución en las piernas menos líquidas.)

---

## Research Idea 3 — Sector Demand Signal: US Cybersecurity Software via Public Procurement

### 1. Market and scope / Mercado y alcance

**Market:** United States, NASDAQ / NYSE.  
**Sector:** Cybersecurity software (e.g., Palo Alto Networks, CrowdStrike, Zscaler, Fortinet).  
**Horizon:** Quarterly to annual — government contract awards and budget cycles precede revenue recognition by 6–18 months.

(Mercado: Estados Unidos, NASDAQ / NYSE. Sector: software de ciberseguridad (por ejemplo, Palo Alto Networks, CrowdStrike, Zscaler, Fortinet). Horizonte: trimestral a anual — las adjudicaciones de contratos gubernamentales y los ciclos presupuestarios preceden al reconocimiento de ingresos por 6–18 meses.)

### 2. Investment thesis / Tesis de inversión

US federal and state cybersecurity spending (driven by CISA mandates, executive orders, and agency modernization budgets) is a leading indicator of demand for listed cybersecurity software vendors. Increases in contract awards and obligated spending often precede reported revenue growth by two to four quarters. A rising pipeline of public-sector deals can signal future earnings beats before analysts update models.

(El gasto federal y estatal de EE. UU. en ciberseguridad (impulsado por mandatos de CISA, órdenes ejecutivas y presupuestos de modernización de agencias) es un indicador líder de la demanda de proveedores de software de ciberseguridad cotizados. Los aumentos en las adjudicaciones de contratos y el gasto obligado a menudo preceden al crecimiento de ingresos reportado por dos a cuatro trimestres. Un pipeline creciente de acuerdos del sector público puede señalar futuros sorpresas de resultados antes de que los analistas actualicen sus modelos.)

### 3. Potential edge / Potencial ventaja

Edge comes from tracking government procurement data (USASpending.gov) that is public but underutilized by equity investors focused on quarterly earnings. By aggregating contract awards by vendor, agency, and quarter, you can build a leading demand signal that is independent of — and earlier than — the companies' own revenue guidance.

(La ventaja proviene de rastrear datos de adquisiciones gubernamentales (USASpending.gov) que son públicos pero infrautilizados por inversores de acciones enfocados en resultados trimestrales. Al agregar adjudicaciones de contratos por proveedor, agencia y trimestre, puedes construir una señal de demanda líder que es independiente de — y anterior a — la orientación de ingresos de las propias empresas.)

### 4. Data and sources / Datos y fuentes

**Verified / checked:**
- USASpending.gov federal contract award data (public API, downloadable)
- CISA cybersecurity directives and known exploited vulnerabilities catalog

**To verify / pending confirmation:**
- State and local government cyber procurement (not just federal) — coverage and API access
- Mapping of contract award amounts to specific public companies (parent/subsidiary resolution)
- Quarterly earnings dates and guidance for candidate cybersecurity vendors

(Datos y fuentes: Verificados: datos de adjudicación de contratos federales de USASpending.gov (API pública, descargable); directivas de CISA y catálogo de vulnerabilidades conocidas explotadas. Por verificar: adquisiciones de ciberseguridad estatales y locales (no solo federales) — cobertura y acceso a API; mapeo de montos de adjudicación de contratos a empresas públicas específicas (resolución de matriz/subsidiaria); fechas de ganancias trimestrales y orientación para proveedores de ciberseguridad candidatos.)

### 5. Research approach / Enfoque de investigación

Aggregate USASpending contract awards by cybersecurity vendor and quarter (2018–present). Construct a quarterly "government demand index" per vendor (sum of obligated dollars, count of awards). Regress next-quarter revenue growth (or earnings surprise) on the lagged government demand index, controlling for sector revenue growth. Test whether the index adds predictive power beyond a simple sector benchmark (e.g., equal-weight cybersecurity basket).

(Enfoque: agregar adjudicaciones de contratos de USASpending por proveedor de ciberseguridad y trimestre (2018–presente). Construir un "índice de demanda gubernamental" trimestral por proveedor (suma de dólares obligados, conteo de adjudicaciones). Regresar el crecimiento de ingresos del próximo trimestre (o sorpresa de resultados) sobre el índice de demanda gubernamental rezagado, controlando por el crecimiento de ingresos del sector. Probar si el índice añade poder predictivo más allá de un simple índice de referencia sectorial (por ejemplo, cesta ponderada equitativamente de ciberseguridad).)

### 6. Validation and risks / Validación y riesgos

**Benchmark:** Equal-weight basket of US cybersecurity software stocks (buy-and-hold).  
**Reject condition:** If the government demand index has no statistically significant coefficient (p > 0.05) in predicting next-quarter revenue/surprise across 12+ quarters, reject.  
**Risks:** Government budget lags and continuing resolutions can delay contract execution; classification of awards to the correct vendor is error-prone; public-sector revenue is often a small fraction of total revenue (signal may be diluted); data publication delays on USASpending.

(Benchmark: cesta ponderada equitativamente de acciones de software de ciberseguridad de EE. UU. (comprar y mantener). Condición de rechazo: si el índice de demanda gubernamental no tiene un coeficiente estadísticamente significativo (p > 0.05) para predecir ingresos/sorpresa del próximo trimestre en 12+ trimestres, rechazar. Riesgos: retrasos presupuestarios del gobierno y resoluciones continuas pueden retrasar la ejecución de contratos; la clasificación de adjudicaciones al proveedor correcto es propensa a errores; los ingresos del sector público suelen ser una fracción pequeña del ingreso total (la señal puede diluirse); retrasos de publicación de datos en USASpending.)

---

## Comparison Summary — Why the Three Ideas Are Different

| Dimension | Idea 1 | Idea 2 | Idea 3 |
|-----------|--------|--------|--------|
| Economic mechanism | Local information / language advantage | Mean reversion / relative value | Public-sector demand leading indicator |
| Market | Mexico (BMV) | United States (NASDAQ) | United States (NASDAQ / NYSE) |
| Sector | Consumer staples | Semiconductors | Cybersecurity software |
| Key data | BMV filings + INEGI (Spanish) | OHLCV pairs + options flow | USASpending.gov contracts |
| Horizon | Quarterly (earnings) | Weekly–monthly (spread) | Quarterly–annual (budget cycle) |
| Edge type | Information asymmetry | Speed of statistical detection | Alternative data before earnings |

---

## Files

- `homework5_answers.md` — This document (English with Spanish explanations)
- `homework5_answers.ipynb` — Jupyter notebook with the same content in markdown cells
- `lesson_simple.md` — Simplified lesson in plain Spanish
