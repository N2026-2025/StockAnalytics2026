"""CLI de ingesta: descarga universo de activos y guarda Parquet + catálogo SQLite."""

import sys
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import yfinance as yf

from app.quant.data.ingestion import download_and_cache, ParquetStorage, SQLiteCatalog
from app.quant.data.universe import ASSETS, BENCHMARK


def main():
    tickers = ASSETS
    start = "2020-01-01"
    end = "2026-08-01"  # fecha actual aproximada

    print(f"Ingestando datos para {len(tickers)} tickers desde {start} hasta {end}...")
    results = download_and_cache(tickers=tickers, start=start, end=end)

    # Resumen
    for ticker, df in results.items():
        rows = len(df)
        last_date = df.index[-1].strftime("%Y-%m-%d") if not df.empty else "N/A"
        print(f"  {ticker}: {rows} filas, última fecha={last_date}")

    # Guardar metadatos del dataset en JSON para referencia rápida
    dataset_info = {
        "generated_at": datetime.now().isoformat(),
        "tickers": tickers,
        "start": start,
        "end": end,
        "rows_per_ticker": {t: len(df) for t, df in results.items()},
    }
    info_path = Path("data") / "ingest_info.json"
    info_path.parent.mkdir(parents=True, exist_ok=True)
    with open(info_path, "w", encoding="utf-8") as f:
        json.dump(dataset_info, f, indent=2, default=str)

    print(f"\nIngesta completada. Metadatos guardados en {info_path}")


if __name__ == "__main__":
    main()