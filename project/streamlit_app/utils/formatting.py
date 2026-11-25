"""Utilidades de formateo y visualizacion para los componentes de Streamlit."""

from __future__ import annotations

import pandas as pd
import altair as alt


def fmt_percent(val: float) -> str:
    """Formatea un decimal como porcentaje con 2 decimales."""
    return f"{val * 100:.2f}%"


def fmt_float(val: float, dec: int = 4) -> str:
    """Formatea un float a string con n decimales."""
    return f"{val:.{dec}f}"


def series_to_df(vals: dict[str, float], col_name: str = "valor") -> pd.DataFrame:
    """Convierte un dict {activo: valor} a DataFrame largo (activo, valor)."""
    if not vals:
        return pd.DataFrame(columns=["activo", col_name])
    return pd.Series(vals, name=col_name).reset_index().rename(columns={"index": "activo"})


def bar_chart(df: pd.DataFrame, y_col: str, title: str, height: int = 300) -> alt.Chart:
    """Barras horizontales ordenadas de mayor a menor."""
    if df.empty:
        return alt.Chart(df).mark_bar().encode(x=y_col)
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(f"{y_col}:Q"),
            y=alt.Y("activo:N", sort="-x"),
            tooltip=["activo", y_col],
        )
        .properties(title=title, height=height)
    )
    return chart


def heatmap_style(df: pd.DataFrame) -> pd.DataFrame:
    """Devuelve un DataFrame listo para st.dataframe (mantener simple; Styler opcional)."""
    return df


def style_correlation(df: pd.DataFrame):
    """Devuelve un Styler para matriz de correlacion con gradiente de color."""
    return df.style.background_gradient(cmap="Blues", vmin=-1, vmax=1).format("{:.2f}")


def style_metrics(df: pd.DataFrame):
    """Styler para tabla de metricas de cartera (formato numérico)."""
    return df.style.format("{:.4f}").set_properties(**{"text-align": "right"})