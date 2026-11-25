# Guía de Preparación para Entrevista Técnica
## Risk Analytics & Multi-Asset Argentina API

---

## 1. Resumen del proyecto (elevator pitch)

**Risk Analytics & Multi-Asset Argentina API** es una API REST construida con FastAPI que expone un motor cuantitativo de riesgo de mercado para una canasta de activos vinculados a la Argentina y una canasta de criptoactivos.

- **Activos vinculados a Argentina:** soja en Chicago (`ZS=F`), petróleo Brent (`BZ=F`) e YPF S.A. (`YPF`).
- **Criptoactivos:** Bitcoin (`BTC-USD`), Ethereum (`ETH-USD`), Solana (`SOL-USD`), XRP (`XRP-USD`) y BNB (`BNB-USD`).
- **Capacidades analíticas:** VaR histórico y paramétrico, Expected Shortfall (CVaR), Maximum Drawdown, pruebas de estrés con escenarios macro argentinos, simulación de Monte Carlo (GBM y bootstrap, hasta 100.000 escenarios) y métricas de cartera (Sharpe, Sortino, Calmar, MDD).
- **Propuesta de valor:** un único punto de acceso (API documentada con OpenAPI/Swagger) que estandariza la medición de riesgo para activos que normalmente se analizan en silos: commodities agrícolas, energía argentina y cripto.

**Pitch de 30 segundos:** "Construí una API de analítica de riesgo en FastAPI que, a partir de precios históricos descargados con yfinance, calcula VaR, Expected Shortfall, drawdown y métricas de cartera, y corre pruebas de estrés y Monte Carlo con escenarios pensados para el contexto macro argentino. La API es reproducible (semilla fija), tolerante a fallos (caché local con fallback determinista) y está documentada con OpenAPI y una suite de tests con pytest."

---

## 2. Arquitectura y flujo de datos

La aplicación sigue una separación en capas: los routers solo manejan HTTP, la lógica cuantitativa vive en la capa de servicios y la configuración y el logging están aislados en `core`.

```
Cliente (curl / navegador / Swagger)
        |
        v
+-------------------+
| FastAPI (app)     |  app/main.py, uvicorn
+-------------------+
        |
        v
+-------------------+
| Routers API v1    |  health, assets, risk, stress, monte-carlo, portfolio
+-------------------+
        |
        v
+-------------------+
| Capa de servicios |  data_engine, risk_engine, stress_testing, monte_carlo, portfolio
+-------------------+
        |
        v
+-------------------+
| Core              |  config.py (pydantic-settings), logging.py
+-------------------+
```

**Flujo de datos, ejemplo VaR:**

1. El cliente llama `GET /api/v1/risk/var?confianza=0.95`.
2. `app/api/v1/risk.py` obtiene el `DataEngine` mediante la dependencia `get_data_engine()`.
3. `data_engine.descargar_datos_multiasset()` devuelve los precios (desde caché CSV o descargando con yfinance).
4. `RiskEngine.retornos_diarios()` calcula los retornos porcentuales diarios.
5. `RiskEngine.var_historico()` y `var_parametrico()` calculan el VaR.
6. Se serializa la respuesta con el schema Pydantic `VaRResponse`.

**Patrones de diseño aplicados:**

- **Separación de capas:** routers (HTTP) / servicios (dominio cuantitativo) / core (config y logging).
- **Inyección de dependencias:** `Depends` de FastAPI para acceso a datos y validación de tickers.
- **Singleton con caché:** `get_data_engine()` con `@lru_cache` y persistencia en CSV bajo `data/cache/`.
- **Fallback determinista:** si yfinance falla (por ejemplo, sin red), `data_engine` genera precios sintéticos con semilla fija (42) para no bloquear la API.

---

## 3. Componentes técnicos con detalle de código

### 3.1 Motor de riesgo (`app/services/risk_engine.py`)

- **VaR histórico:** percentil empírico de la cola inferior de los retornos: `retornos.quantile(1 - confianza)`. No asume distribución.
- **VaR paramétrico:** asume normalidad, `VaR = mu + sigma * z_alpha`, donde `z_alpha = norm.ppf(1 - confianza)`.
- **Expected Shortfall (CVaR):** media de los retornos que caen por debajo del VaR histórico. Responde a "¿cuánto pierdo en promedio cuando supero el VaR?".
- **Maximum Drawdown:** sobre la serie de precios, `drawdown = (precio - max_acumulado) / max_acumulado`; el MDD es el mínimo de esa serie.
- **Volatilidad anualizada:** `std(retornos) * sqrt(252)`.

### 3.2 Pruebas de estrés (`app/services/stress_testing.py`)

Cuatro escenarios deterministas que aplican shocks porcentuales sobre los últimos precios conocidos:

- **Devaluación FX del 25%:** `YPF -25%`, transmisión parcial a soja `-10%` y a Brent `-5%`.
- **Shock de soja (-15%):** impacto directo en `ZS=F`, con transmisión a YPF y Brent.
- **Shock de petróleo (-20%):** impacto directo en `BZ=F`, con transmisión a YPF y soja.
- **Crisis conjunta histórica:** se toma el peor día observado de retornos desde 2020 y se reaplica sobre los precios actuales.

El P&L de una cartera igual ponderada se calcula como el promedio simple del P&L por activo.

### 3.3 Monte Carlo (`app/services/monte_carlo.py`)

- **GBM (Movimiento Browniano Geométrico):** `drift = (mu - 0.5*sigma^2)*dt`, `diffusion = sigma*sqrt(dt)`, con `dt = 1/252`. Simula trayectorias log-normales de precios.
- **Bootstrap:** remuestreo con reemplazo de filas completas de retornos históricos. Conserva colas gruesas y la dependencia empírica entre activos (no asume normalidad).
- **Resumen de P&L:** percentiles 1%, 5%, 50%, 95%, 99%, probabilidad de pérdida (`prob_perdida`) y P&L esperado.
- **Reproducibilidad:** `np.random.default_rng(seed)` con semilla configurable (por defecto 42).

### 3.4 Métricas de cartera (`app/services/portfolio.py`)

- **Pesos:** por defecto igual ponderada (1/n) o personalizados; se normalizan para que sumen 1.
- **Sharpe:** `(media_exceso / std) * sqrt(252)`.
- **Sortino:** igual que Sharpe pero usando la desviación de los retornos negativos (downside deviation).
- **Maximum Drawdown de la cartera:** sobre la curva de capital acumulada `(1 + r).cumprod()`.
- **Calmar:** retorno anualizado (CAGR) dividido por el valor absoluto del MDD.
- **VaR/ES de cartera al 95%:** percentil 5% y media de la cola.

### 3.5 Motor de datos (`app/services/data_engine.py`)

- Descarga precios de cierre ajustados (`Adj Close`) con yfinance.
- **Caché en CSV:** clave determinista construida con tickers, fecha inicio y fin; evita descargas repetidas.
- **Fallback determinista:** random walk con deriva pequeña y volatilidad por tipo de activo, semilla 42, cuando falla la descarga.

---

## 4. Preguntas técnicas de entrevista con respuestas modelo

### 4.1 Diseño de API y FastAPI

**P: ¿Por qué elegiste FastAPI en lugar de Flask o Django?**

R: FastAPI ofrece validación automática con Pydantic, documentación OpenAPI/Swagger generada automáticamente (`/docs` y `/redoc`), soporte nativo de async y un sistema de dependencias (`Depends`) muy limpio para inyectar el motor de datos y validar parámetros. Para una API analítica con muchos parámetros tipados (confianza, fechas, tickers, número de escenarios), esto reduce código repetitivo y errores.

**P: ¿Cómo organizaste los routers y por qué?**

R: Un router agregado (`api/v1/router.py`) incluye sub-routers por dominio: `health`, `assets`, `risk`, `stress`, `monte-carlo` y `portfolio`, cada uno con su prefijo y tag. Esto da una API navegable por dominio en Swagger y permite versionar (`/api/v1`).

**P: ¿Cómo manejás errores en la API?**

R: Cada endpoint envuelve la lógica en `try/except` y traduce fallos a `HTTPException`, típicamente `503` cuando la fuente de datos no responde y no hay caché, y `404` cuando un ticker solicitado no está disponible. También hay endpoints con `raise HTTPException` re-lanzada para no enmascarar errores HTTP intencionales.

### 4.2 Finanzas cuantitativas

**P: ¿Cuál es la diferencia entre VaR histórico y VaR paramétrico?**

R: El VaR histórico es no paramétrico: toma el percentil empírico de la distribución de retornos observados, por lo que captura colas gruesas y asimetrías. El VaR paramétrico asume una distribución normal y usa `mu + sigma*z`. El paramétrico es más estable y rápido, pero subestima el riesgo cuando hay colas gruesas o crisis; el histórico depende de la ventana de datos y puede no reflejar eventos no vistos.

**P: ¿Por qué calcular Expected Shortfall además del VaR?**

R: El VaR indica un umbral de pérdida pero no dice cuánto se pierde más allá de ese umbral. El Expected Shortfall (CVaR) es la pérdida esperada condicionada a superar el VaR, es coherente como medida de riesgo (subaditivo) y por eso es preferido en marcos regulatorios como Basilea.

**P: ¿Qué supuestos tiene tu GBM y cuándo no sirve?**

R: El GBM asume retornos log-normales, volatilidad y deriva constantes y ausencia de saltos. No captura colas gruesas, clustering de volatilidad ni saltos de régimen. Por eso ofrezco también bootstrap, que remuestrea retornos históricos reales y conserva la dependencia empírica entre activos.

**P: ¿Por qué el bootstrap preserva mejor la estructura de dependencia?**

R: Porque remuestrea **filas completas** de retornos (todos los activos del mismo día juntos), manteniendo la correlación contemporánea observada. El GBM, en cambio, simula cada activo con shocks independientes salvo que se modele explícitamente una matriz de covarianza.

**P: ¿Cómo interpretarías un MDD y un Calmar negativos?**

R: El MDD siempre es negativo o cero (es una caída desde un máximo). El Calmar es retorno anualizado sobre el valor absoluto del MDD; si es negativo, la cartera tuvo retorno anualizado negativo en el período, es decir, no compensó el riesgo de drawdown.

### 4.3 Ingeniería de software y datos

**P: ¿Cómo garantizás reproducibilidad en las simulaciones?**

R: Uso `np.random.default_rng(seed)` con `RANDOM_SEED = 42` configurable. Tanto el fallback de datos como el Monte Carlo son deterministas, así que dos ejecuciones con el mismo input producen los mismos resultados, lo que permite tests estables.

**P: ¿Qué pasa si yfinance no responde?**

R: El `DataEngine` captura la excepción, registra el error con logging estructurado y genera datos sintéticos deterministas (random walk con semilla 42). Así la API sigue respondiendo y los tests pueden correr sin red. Si la descarga falla y no hay caché, el endpoint responde `503` con el detalle.

**P: ¿Cómo testeás una API que depende de datos externos?**

R: Con fixtures sintéticas deterministas en `tests/conftest.py` que generan precios de prueba, y con `TestClient` de FastAPI para los endpoints. Al separar la lógica cuantitativa en servicios puros, puedo testear el motor de riesgo, el stress testing, el Monte Carlo y la cartera sin tocar la red.

**P: ¿Qué es el look-ahead bias y cómo lo evitás?**

R: Es usar información futura al construir señales o métricas. Aquí las métricas se calculan solo con retornos pasados hasta la fecha `end`; el estrés reaplica shocks sobre precios actuales sin mirar el futuro, y el bootstrap solo muestrea días históricos previos. Igual, al ser una API de análisis y no de trading, el riesgo de look-ahead es menor, pero se mantiene la disciplina temporal.

**P: ¿Adj Close vs Close en yfinance?**

R: Uso `Adj Close` (cierre ajustado por dividendos y splits) para series de precios multi-asset, porque refleja el retorno total y evita saltos artificiales por eventos corporativos. Para cripto uso `Close`, ya que no hay splits ni dividendos.

---

## 5. Preguntas de System Design con respuesta

**P: ¿Cómo escalarías esta API a producción multi-tenant?**

R: Separaría tres planos: (1) **cómputo** sin estado en contenedores detrás de un balanceador, escalando horizontalmente; (2) **datos** con una caché compartida (Redis) en lugar de CSV local, con TTL y claves por ticker/rango; (3) **trabajos pesados** (Monte Carlo de 100k escenarios) movidos a una cola (Celery/RQ) con workers, devolviendo un job id y resultados por polling o webhook. Añadiría rate limiting por tenant, autenticación con API keys/OAuth y cuotas.

**P: ¿Cómo versionarías la API sin romper clientes?**

R: Mantengo el prefijo `/api/v1` y, ante cambios incompatibles, publico `/api/v2` en paralelo, deprecando v1 con aviso y ventana de migración. El contrato `openapi.yaml` se versiona junto con el código.

**P: ¿Qué observabilidad agregarías?**

R: Logging estructurado ya existe en stdout; sumaría métricas (latencia por endpoint, tasa de error, hits/miss de caché) con Prometheus y trazas distribuidas (OpenTelemetry) para seguir una request a través de routers y servicios. También alertas sobre errores 503 y latencia p95.

**P: ¿Cómo cachearías de forma correcta?**

R: Clave determinista por `tickers + start + end` (ya implementada en CSV). En producción usaría Redis con TTL alineado a la frecuencia de datos (por ejemplo, refresco diario tras el cierre), invalidación explícita y cache stampede protection (lock por clave).

---

## 6. Preguntas de comportamiento (formato STAR)

Usá estas historias adaptándolas al proyecto. Estructura **STAR**: Situación, Tarea, Acción, Resultado.

**Historia 1 — Tolerancia a fallos sin red.**

- **Situación:** la API dependía de yfinance para descargar precios; en un entorno sin red o con el proveedor caído, los endpoints fallaban.
- **Tarea:** garantizar que la API siguiera siendo demostrable y testeable sin conexión.
- **Acción:** implementé caché en CSV y un fallback determinista que genera precios sintéticos con semilla 42, además de logging estructurado del error.
- **Resultado:** la API responde de forma consistente en demos y los tests corren sin red.

**Historia 2 — Reproducibilidad de resultados.**

- **Situación:** las simulaciones de Monte Carlo variaban entre ejecuciones, dificultando validar resultados y escribir tests.
- **Tarea:** hacer los resultados deterministas para un mismo input.
- **Acción:** centralicé `RANDOM_SEED` en `config.py` y usé `np.random.default_rng(seed)` en el simulador.
- **Resultado:** resultados idénticos entre corridas y tests estables.

**Historia 3 — Separación de responsabilidades.**

- **Situación:** al principio la lógica de cálculo y el HTTP estaban mezclados, lo que dificultaba testear y extender.
- **Tarea:** refactorizar a capas claras.
- **Acción:** moví la lógica cuantitativa a `services/` (motores puros) y dejé los routers solo para HTTP, con inyección de dependencias para el acceso a datos.
- **Resultado:** tests unitarios por servicio, endpoints finos y código más mantenible.

**Historia 4 — Trade-off de alcance.**

- **Situación:** el proyecto tenía muchas features posibles (Docker, CI/CD, despliegue cloud) y tiempo acotado.
- **Tarea:** priorizar lo que demostrara valor técnico real.
- **Acción:** prioricé el motor cuantitativo, la reproducibilidad, los tests y la documentación OpenAPI, dejando Docker/CI/CD documentados como roadmap.
- **Resultado:** entregable completo y verificable, con limitaciones explícitas en el README.

---

## 7. Ejemplos por empresa y rol

Adaptá el énfasis del pitch según el entrevistador. La misma base técnica se cuenta distinto según el contexto.

### 7.1 Argentina — energía y commodities

- **YPF / empresas de energía:** destacá el modelado de riesgo de precio de Brent y la transmisión a YPF, el escenario de devaluación FX del 25% y la sensibilidad de la cartera a shocks de petróleo. Enfatizá el entendimiento del contexto macro argentino.
- **Agro / exportadoras (soja):** destacá el shock de soja, la correlación entre soja, energía y YPF, y cómo el VaR/ES ayuda a dimensionar coberturas.

### 7.2 Argentina — fintech y banca

- **MercadoLibre / Mercado Pago, Ualá, neobanks:** destacá la API REST, validación con Pydantic, manejo de errores, caché y escalabilidad. Enfatizá la parte de ingeniería de software más que la cuantitativa pura.
- **Bancos (Galicia, BBVA, Santander):** destacá VaR/ES, stress testing y la conexión con marcos regulatorios (Basilea, pruebas de estrés). Mencioná la importancia de la auditabilidad y reproducibilidad.

### 7.3 Global — banca de inversión y riesgo cuantitativo

- **J.P. Morgan, Goldman Sachs, Morgan Stanley (roles de Market Risk / Quant):** destacá la coherencia del Expected Shortfall frente al VaR, los supuestos del GBM vs bootstrap, el model risk y la validación de modelos. Hablá de Basilea y de por qué ES es preferido regulatoramente.
- **Asset managers / hedge funds:** destacá métricas de performance (Sharpe, Sortino, Calmar), construcción de cartera y análisis de drawdown.

### 7.4 Global — cripto y exchanges

- **Exchanges y fintechs cripto:** destacá el módulo de precios cripto, la volatilidad y las colas gruesas (por qué bootstrap supera a GBM en cripto), y la latencia/caché para datos de mercado.

### 7.5 Cómo adaptar el pitch en 20 segundos

- **Rol backend/plataforma:** "API FastAPI por capas, con inyección de dependencias, caché, manejo de errores y tests; el dominio es analítica de riesgo."
- **Rol quant/riesgo:** "Motor de VaR histórico y paramétrico, ES, stress testing con escenarios macro argentinos y Monte Carlo GBM/bootstrap reproducible."
- **Rol data/ML:** "Pipeline de datos financieros con fallback determinista, simulaciones a gran escala y métricas de performance."

---

## 8. Preguntas que deberías hacer vos al entrevistador

**Generales:**

- ¿Cómo miden y monitorean el riesgo de mercado hoy y qué herramientas usan?
- ¿Qué parte del stack es Python y qué parte es otro lenguaje/servicio?
- ¿Cómo es el ciclo de vida de un modelo: desarrollo, validación y monitoreo?

**Para roles backend/plataforma:**

- ¿Cómo manejan caché y consistencia de datos de mercado en producción?
- ¿Qué estrategia de versionado y deprecación de APIs usan?
- ¿Qué observabilidad (métricas, trazas, alertas) tienen hoy?

**Para roles quant/riesgo:**

- ¿Usan VaR paramétrico, histórico o simulación, y con qué horizonte y nivel de confianza?
- ¿Cómo incorporan pruebas de estrés regulatorias y qué escenarios son obligatorios?
- ¿Cómo validan y documentan los modelos (model risk management)?

**Para roles fintech/crypto:**

- ¿Cómo manejan la latencia y la calidad de datos de mercado?
- ¿Qué regulación aplica a los activos con los que trabajan?

---

## 9. Limitaciones actuales y roadmap (para "¿qué mejorarías?")

Sé honesto y específico. Estas limitaciones están documentadas en el README y son una oportunidad para mostrar criterio.

- **CI/CD:** no hay pipeline configurado aún; el siguiente paso es GitHub Actions con `pytest --cov` y linting.
- **Contenedores:** no hay Dockerfile obligatorio; la API corre nativa en el host. Se puede containerizar con la imagen oficial de Python.
- **Despliegue:** documentado en local; falta despliegue cloud con health checks y autoescalado.
- **Observabilidad:** hay logging estructurado, pero faltan métricas y tracing (Prometheus/OpenTelemetry).
- **Caché:** CSV local; en producción conviene Redis con TTL e invalidación.
- **Cómputo pesado:** Monte Carlo corre en el request; conviene moverlo a colas con workers para no bloquear.
- **Datos:** yfinance es una fuente no oficial; para producción conviene un proveedor con SLA y datos point-in-time.

**Respuesta modelo:** "El proyecto prioriza el motor cuantitativo, la reproducibilidad y la documentación. Para llevarlo a producción agregaría CI/CD con GitHub Actions, containerización, caché distribuida, colas para el Monte Carlo pesado y observabilidad con métricas y tracing. También migraría de yfinance a un proveedor de datos con SLA."

---

## 10. Anexo: endpoints y glosario

### 10.1 Endpoints principales

| Método | Ruta | Descripción |
|---|---|---|
| GET | /api/v1/health | Estado de la API |
| GET | /api/v1/assets/prices | Precios históricos multi-asset (ZS=F, BZ=F, YPF) |
| GET | /api/v1/assets/prices/all | Precios de todos los activos multi-asset |
| GET | /api/v1/assets/prices/crypto | Precios cripto (BTC, ETH, SOL, XRP, BNB) |
| GET | /api/v1/assets/correlation | Matriz de correlación de retornos |
| GET | /api/v1/risk/var | VaR histórico y paramétrico |
| GET | /api/v1/risk/expected-shortfall | Expected Shortfall / CVaR |
| GET | /api/v1/risk/drawdown | Maximum Drawdown por activo |
| GET | /api/v1/stress | Pruebas de estrés (4 escenarios) |
| GET | /api/v1/monte-carlo | Simulación Monte Carlo (gbm o bootstrap) |
| GET | /api/v1/portfolio/summary | Métricas de cartera igual ponderada |
| GET | /api/v1/portfolio/metrics | Métricas con pesos personalizados |

### 10.2 Ejemplos de request

```
GET /api/v1/risk/var?confianza=0.95&start=2020-01-01
GET /api/v1/stress?start=2020-01-01
GET /api/v1/monte-carlo?n_scenarios=10000&metodo=bootstrap&start=2020-01-01
GET /api/v1/portfolio/metrics?pesos={"ZS=F":0.4,"BZ=F":0.3,"YPF":0.3}
```

### 10.3 Glosario

- **VaR (Value at Risk):** pérdida máxima esperada en un horizonte y nivel de confianza dados.
- **Expected Shortfall (CVaR / ES):** pérdida promedio en la cola que supera el VaR.
- **MDD (Maximum Drawdown):** mayor caída porcentual desde un máximo histórico.
- **GBM (Movimiento Browniano Geométrico):** modelo de precios con retornos log-normales.
- **Bootstrap:** remuestreo con reemplazo de datos históricos para simular escenarios.
- **Sharpe:** retorno excedente por unidad de volatilidad total.
- **Sortino:** retorno excedente por unidad de volatilidad negativa (downside).
- **Calmar:** retorno anualizado dividido por el MDD absoluto.

### 10.4 Stack técnico

- Python 3.10+, FastAPI, uvicorn, Pydantic v2, pydantic-settings.
- pandas, numpy, scipy, yfinance.
- pytest y pytest-cov para testing.
- Documentación: OpenAPI (`openapi.yaml`), Swagger UI (`/docs`), ReDoc (`/redoc`).

---

## Cierre

Este proyecto demuestra competencias en tres dimensiones que suelen evaluarse por separado: **ingeniería de software** (API por capas, validación, errores, caché, tests), **finanzas cuantitativas** (VaR, ES, stress testing, Monte Carlo, métricas de cartera) y **criterio de producto** (reproducibilidad, documentación, roadmap honesto). La clave en la entrevista es conectar cada decisión técnica con un problema real de negocio y demostrar que entendés los supuestos y límites de cada modelo.
