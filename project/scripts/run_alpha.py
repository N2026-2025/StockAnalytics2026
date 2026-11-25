#!/usr/bin/env python
"""CLI para ejecutar el pipeline de Alpha Mining Fase 1.

Uso:
    python scripts/run_alpha.py [--sample-rows N] [--include-sentiment] [--doc-paths PATH ...] [--output-json PATH]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Añadir el directorio del proyecto al path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.alpha.pipeline import run_alpha_pipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="Alpha Mining Pipeline - Fase 1")
    parser.add_argument(
        "--sample-rows",
        type=int,
        default=None,
        help="Número de filas a muestrear (determinista) para pruebas rápidas",
    )
    parser.add_argument(
        "--include-sentiment",
        action="store_true",
        help="Incluir hipótesis con sentimiento macro (requiere --doc-paths)",
    )
    parser.add_argument(
        "--doc-paths",
        nargs="*",
        default=None,
        help="Rutas a documentos de texto para análisis de sentimiento",
    )
    parser.add_argument(
        "--output-json",
        type=str,
        default=None,
        help="Ruta para guardar resultados en JSON",
    )
    parser.add_argument(
        "--dataset-path",
        type=str,
        default=None,
        help="Ruta al dataset .parquet (por defecto usa la configuración ALPHA_DATASET_PATH)",
    )
    parser.add_argument(
        "--optimize",
        action="store_true",
        help="Ejecutar optimización walk-forward (Fase 2) en lugar del pipeline Fase 1",
    )
    args = parser.parse_args()

    if args.optimize:
        return _run_optimization(args)

    print("=== Alpha Mining Pipeline - Fase 1 ===")
    print(f"Sample rows: {args.sample_rows or 'completo'}")
    print(f"Include sentiment: {args.include_sentiment}")
    print(f"Doc paths: {args.doc_paths or 'ninguno'}")
    print()

    try:
        result = run_alpha_pipeline(
            dataset_path=args.dataset_path,
            doc_paths=args.doc_paths,
            include_sentiment=args.include_sentiment,
            sample_rows=args.sample_rows,
        )
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"ERROR inesperado: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

    # Mostrar resumen
    print("=== RESULTADOS ===")
    print(f"Dataset rows: {result.dataset_rows}")
    print(f"Hipótesis totales: {result.n_hypotheses}")
    print(f"Pasaron filtro: {result.n_passed}")
    print(f"Fallaron: {result.n_failed}")
    print(f"Sentimiento macro: {result.macro_sentiment:.4f}")
    print()

    if result.rankings:
        print("--- RANKING (ordenado por Sharpe anualizado) ---")
        for i, r in enumerate(result.rankings, 1):
            status = "PASS" if r["passes_filter"] else "FAIL"
            print(
                f"{i:2d}. {r['hypothesis']:<35s} | "
                f"Sharpe={r['sharpe_annualized']:>7.3f} | "
                f"CAGR={r['cagr']:>7.4f} | "
                f"Trades={r['n_trades']:>4d} | "
                f"PBO={r['pbo']:.3f} | "
                f"DSR={r['deflated_sharpe']:.3f} {status}"
            )

    # Guardar JSON si se pidió
    if args.output_json:
        out_path = Path(args.output_json)
        out_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False))
        print(f"\nResultados guardados en: {out_path}")

    return 0 if result.n_passed > 0 else 2


def _run_optimization(args) -> int:
    """Ejecuta walk-forward optimization (Fase 2)."""
    from app.alpha.optimization import (
        run_walk_forward_optimization,
        WalkForwardResult,
    )

    print("=== Alpha Mining Walk-Forward Optimization - Fase 2 ===")
    print()

    # Cargar dataset muestreado o completo (mismo límite que el Fase 1)
    from app.alpha.pipeline import load_zoomcamp_dataset, align_dataset, _ALPHA_COLUMNS

    df = align_dataset(load_zoomcamp_dataset(path=args.dataset_path, columns=_ALPHA_COLUMNS))
    if args.sample_rows and len(df) > args.sample_rows:
        df = df.sample(n=args.sample_rows, random_state=42).sort_values("Date").reset_index(drop=True)

    from app.alpha.optimization import default_param_grids

    print(f"Dataset: {len(df)} filas | Optimización: {len(default_param_grids())} grillas | Folds: {5}")
    print()

    results: list[WalkForwardResult] = run_walk_forward_optimization(df, n_splits=5)

    if not results:
        print("No se pudieron generar resultados de optimización (dataset demasiado pequeño o sin parámetros válidos).")
        return 1

    # Ordenar por OOS Sharpe (de mejor a peor).
    results.sort(key=lambda r: r.mean_oos_sharpe, reverse=True)

    print("=== RESULTADOS WF-OPT (ordenado por mean OOS Sharpe) ===")
    for r in results:
        print(f"Hipótesis: {r.hypothesis}")
        print(f"  Folds: {len(r.folds)} | OOS Sharpe: {r.mean_oos_sharpe:.3f} | Train Sharpe: {r.mean_train_sharpe:.3f}")
        print(f"  Degradation: {r.degradation:.3f} | Stability: {r.stability:.2f} ({100*r.stability:.0f}% folds con OOS>0)")
        print(f"  Param mode: {r.param_mode}")
        if r.folds:
            for f in r.folds[:3]:  # mostar los primeros 3 folds
                print(f"    Fold {f.fold}: train {f.train_start}->{f.train_end} | OOS {f.oos_sharpe:.3f} trades={f.oos_trades} | params={f.best_params}")
        print()

    # Guardar JSON con los resultados detallados.
    import json
    from pathlib import Path

    out_path = Path(args.output_json) if args.output_json else Path("wf_optimization_results.json")
    out_path.write_text(json.dumps([r.as_dict() for r in results], indent=2, ensure_ascii=False))
    print(f"Resultados detallados guardados en: {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())