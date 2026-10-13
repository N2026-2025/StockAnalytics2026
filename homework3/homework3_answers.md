# Homework 3 — Respuestas (Module 3, cohorte 2026)

Pipeline reproducible: `data.parquet` (33 tickers US/EU/India) filtrado a `Date >= 2000-01-01`
(`191,465` filas), target `is_positive_growth_30d_future`, split temporal 70/15/15 por fecha:
train hasta `2017-10-15` (`129,481`), validation hasta `2021-08-07` (`30,625`), test `31,359`.
Limpieza como en el notebook: `±inf -> NaN`, `NaN -> 0`, sin recorte de outliers para el árbol.
Árboles con `random_state=42`.

## Q1 — Dummy `month_wom` más correlacionada
- Construcción: `week_of_month=(Date.day-1)//7+1`; `month_wom=Month_w{week}`.
- Categóricas: `Month, Weekday, Ticker, ticker_type, month_wom`.
- `pd.get_dummies(...)`: **115 dummies**, **60** de `month_wom` (12×hasta 5 semanas).
- Correlación Pearson contra `is_positive_growth_30d_future`; ranking por `abs_corr`.
- Mejor dummy: `month_wom_September_w3`, `corr=-0.030270`.

**Respuesta Q1: `0.030`**

Top-5 `month_wom` por `|corr|`: `September_w3 0.030270`, `February_w3 0.026895`,
`October_w5 0.023846`, `March_w4 0.020862`, `June_w3 0.017640`.
Lectura quant: el efecto calendario existe pero es débil (`|r|≈0.03`); sirve como regularizador
estacional, no como señal principal.

## Q2 — Nuevas reglas manuales macro
- `pred3_manual_dgs10_5 = (DGS10 <= 4.5) & (DGS5 <= 4)`
- `pred4_manual_dgs10_fedfunds = (DGS10 > 4) & (FEDFUNDS <= 4.795)`
- Precisión en TEST (`TP/(TP+FP)` con `sklearn.metrics.precision_score`):
  `pred3`: `17,836` positivos, precisión `0.537340`;
  `pred4`: `5,330` positivos, precisión `0.524765`.
- Baselines previas en TEST: `pred0 0.540984`, `pred1 0.537147`, `pred2 0.539255`.

**Respuesta Q2: `0.537` (mejor nueva: `pred3_manual_dgs10_5`)**

## Q3 — `pred5_clf_10` únicamente correcto
- `DecisionTreeClassifier(max_depth=10, random_state=42)` entrenado en TRAIN+VALIDATION
  (`160,106` filas, 299 features numéricas+dummies limpias).
- Predicción sobre todo el dataset en orden original (`X_all`, 191,465 filas) en
  `pred5_clf_10`; precisión TEST `0.544886` (`25,910` positivos en test).
- `only_pred5_is_correct = (pred5==y) & ~(pred0..pred4==y)` como entero; conteo en TEST.

**Respuesta Q3: `2366`**

## Q4 — Tuning `max_depth` 1–12
Precisión TEST por profundidad (`random_state=42`, train TRAIN+VALIDATION):

| depth | precision | accuracy | n_pos_test |
|---:|---:|---:|---:|
| 1 | 0.537294 | 0.537294 | 31359 |
| 2 | 0.537382 | 0.537453 | 31352 |
| 3 | 0.542865 | 0.542460 | 29173 |
| 4 | 0.540232 | 0.532702 | 27279 |
| 5 | 0.537192 | 0.529258 | 28057 |
| 6 | 0.536859 | 0.529386 | 28365 |
| 7 | 0.536538 | 0.528046 | 28039 |
| 8 | 0.545668 | 0.527313 | 22182 |
| 9 | 0.535448 | 0.526643 | 28281 |
| 10 | 0.544886 | 0.536879 | 25910 |
| 11 | 0.545897 | 0.537326 | 25492 |
| 12 | 0.543927 | 0.528716 | 23562 |

Reentrenado con la mejor profundidad y predicción full-sample en `pred6_clf_best`.
Comparación TEST: `pred5_clf_10 0.544886` vs `pred6_clf_best(depth=11) 0.545897`;
hand rules `pred0..pred4`: `0.541/0.537/0.539/0.537/0.525`.
No se alcanza `0.58` en este corte 30d: la señal a 30 días es más ruidosa y el árbol
profundo gana cobertura positiva pero con más falsos positivos.

**Respuesta Q4: `11` (precisión TEST `0.546`)**

## Q5 — Qué datos faltan (exploratorio)
1. Régimen de riesgo: VIX/realized-vol, spreads de crédito (HY OAS), pendiente 2s10s y
   sorpresas macro; el árbol ya usa `DGS/FEDFUNDS`, pero sin proxy de aversión al riesgo.
2. Divergencia regional: para India/EU/US incluir política RBI/ECB/Fed, FX
   USD/EUR/INR, prima ADR/GDR y pertenencia a índices; `ticker_type` es demasiado grueso.
3. Microestructura: turnover sobre free-float, rango intradía/ATR normalizado, corporate
   actions y borrow-cost/short-interest si hay licencia.
4. Fundamental forward-looking: earnings yield vs `DGS10`, revisiones de ventas/BPA y
   calendario de resultados; evitar leakage con point-in-time.
5. Alternativos: sentimiento de noticias/llamadas (GDELT/RavenPack) y breadth sectorial.
Fuentes: FRED, ECB Data Portal, RBI DBIE, OHLCV existente, TA-Lib; Worldscope/Compustat
o proveedor bursátil para fundamentales point-in-time.

*Nota de reproducibilidad: ver `Homework03_HW03_Solution.ipynb`; usa `data.parquet` local.
Si se corre contra el parquet de Drive del Colab, los valores pueden variar porque el
universo/fechas no son idénticos.*
