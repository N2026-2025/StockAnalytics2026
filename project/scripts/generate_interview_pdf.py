"""Genera el PDF de preparación para entrevista a partir de interview_prep.md.

Uso:
    python scripts/generate_interview_pdf.py

Fuente:  docs/interview/interview_prep.md
Salida:  docs/interview/RiskAnalytics_InterviewPrep.pdf

Requiere reportlab (ver requirements-pdf.txt). No usa red.
"""

from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_MD = PROJECT_ROOT / "docs" / "interview" / "interview_prep.md"
OUTPUT_PDF = PROJECT_ROOT / "docs" / "interview" / "RiskAnalytics_InterviewPrep.pdf"

DOC_TITLE = "Preparación para Entrevista Técnica"
DOC_SUBTITLE = "Risk Analytics & Multi-Asset Argentina API"

_REPLACEMENTS = {
    "\u2192": "->",
    "\u2190": "<-",
    "\u2194": "<->",
    "\u2265": ">=",
    "\u2264": "<=",
    "\u2260": "!=",
    "\u2248": "~=",
    "\u00d7": "x",
    "\u00f7": "/",
    "\u221a": "sqrt",
    "\u00b2": "^2",
    "\u00b3": "^3",
    "\u00bd": "1/2",
    "\u2013": "-",
    "\u2014": "-",
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
}


def _sanitize(text: str) -> str:
    """Reemplaza caracteres fuera de Latin-1 por equivalentes seguros."""
    for src, dst in _REPLACEMENTS.items():
        text = text.replace(src, dst)
    return text


def _escape_xml(text: str) -> str:
    """Escapa caracteres especiales de XML usados por reportlab Paragraph."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _inline(text: str) -> str:
    """Convierte marcado inline de Markdown a tags de reportlab."""
    text = _sanitize(text)
    text = _escape_xml(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    return text


def _build_styles() -> dict[str, ParagraphStyle]:
    """Construye los estilos de párrafo del documento."""
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=26,
            leading=32,
            alignment=TA_CENTER,
            spaceAfter=6,
            textColor=colors.HexColor("#0b3d5c"),
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=15,
            leading=20,
            alignment=TA_CENTER,
            spaceAfter=18,
            textColor=colors.HexColor("#2a6f97"),
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            spaceBefore=6,
            spaceAfter=10,
            textColor=colors.HexColor("#0b3d5c"),
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            spaceBefore=12,
            spaceAfter=6,
            textColor=colors.HexColor("#1d5c7a"),
        ),
        "h3": ParagraphStyle(
            "H3",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            spaceBefore=8,
            spaceAfter=4,
            textColor=colors.HexColor("#2a6f97"),
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            spaceAfter=3,
        ),
        "quote": ParagraphStyle(
            "Quote",
            parent=base["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=10,
            leading=14,
            leftIndent=12,
            textColor=colors.HexColor("#444444"),
            spaceAfter=6,
        ),
        "code": ParagraphStyle(
            "Code",
            parent=base["Code"],
            fontName="Courier",
            fontSize=8,
            leading=10,
            leftIndent=6,
            textColor=colors.HexColor("#222222"),
        ),
        "table": ParagraphStyle(
            "Table",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
        ),
        "table_head": ParagraphStyle(
            "TableHead",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            textColor=colors.white,
        ),
    }


def _make_table(rows: list[list[str]], styles: dict[str, ParagraphStyle]) -> Table:
    """Construye una tabla con encabezado a partir de filas de Markdown."""
    header, body = rows[0], rows[1:]
    data = [[Paragraph(_inline(cell), styles["table_head"]) for cell in header]]
    for row in body:
        data.append([Paragraph(_inline(cell), styles["table"]) for cell in row])

    n_cols = len(header)
    table = Table(data, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d5c7a")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#96a5b0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef3f7")]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def _parse_table_row(line: str) -> list[str]:
    """Divide una fila de tabla Markdown en celdas."""
    stripped = line.strip().strip("|")
    return [cell.strip() for cell in stripped.split("|")]


def _is_separator_row(line: str) -> bool:
    """Detecta la fila separadora |---|---| de las tablas Markdown."""
    return bool(re.fullmatch(r"\|?[\s:|-]+\|?", line.strip())) and "-" in line


def _markdown_to_flowables(text: str, styles: dict[str, ParagraphStyle]) -> list:
    """Convierte el texto Markdown en una lista de flowables de reportlab."""
    flowables: list = []
    lines = text.splitlines()
    i = 0
    first_heading = True
    used_title = False

    para_buffer: list[str] = []
    list_buffer: list[str] = []
    table_buffer: list[list[str]] = []
    code_buffer: list[str] = []
    in_code = False

    def flush_paragraph() -> None:
        nonlocal para_buffer
        if para_buffer:
            flowables.append(Paragraph(_inline(" ".join(para_buffer)), styles["body"]))
            para_buffer = []

    def flush_list() -> None:
        nonlocal list_buffer
        if list_buffer:
            items = [ListItem(Paragraph(_inline(t), styles["bullet"]), leftIndent=12) for t in list_buffer]
            flowables.append(
                ListFlowable(items, bulletType="bullet", start="circle", leftIndent=14, bulletFontSize=6)
            )
            list_buffer = []

    def flush_table() -> None:
        nonlocal table_buffer
        if table_buffer:
            if len(table_buffer) >= 2:
                flowables.append(_make_table(table_buffer, styles))
                flowables.append(Spacer(1, 6))
            table_buffer = []

    def flush_code() -> None:
        nonlocal code_buffer
        if code_buffer:
            flowables.append(Preformatted("\n".join(code_buffer), styles["code"]))
            flowables.append(Spacer(1, 6))
            code_buffer = []

    def flush_all() -> None:
        flush_paragraph()
        flush_list()
        flush_table()
        flush_code()

    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()

        if line.strip().startswith("```"):
            if in_code:
                in_code = False
                flush_code()
            else:
                flush_all()
                in_code = True
            i += 1
            continue

        if in_code:
            code_buffer.append(raw)
            i += 1
            continue

        if not line.strip():
            flush_paragraph()
            flush_list()
            flush_table()
            i += 1
            continue

        if line.strip() == "---":
            flush_all()
            flowables.append(PageBreak())
            i += 1
            continue

        if line.startswith("# "):
            flush_all()
            title = line[2:].strip()
            if not used_title:
                flowables.append(Paragraph(_inline(title), styles["title"]))
                flowables.append(HRFlowable(width="60%", color=colors.HexColor("#2a6f97"), spaceBefore=4))
                flowables.append(Spacer(1, 6))
                used_title = True
            else:
                flowables.append(Paragraph(_inline(title), styles["h1"]))
            first_heading = False
            i += 1
            continue

        if line.startswith("## "):
            flush_all()
            heading = line[3:].strip()
            if used_title and first_heading:
                flowables.append(Paragraph(_inline(heading), styles["subtitle"]))
                first_heading = False
            else:
                flowables.append(Paragraph(_inline(heading), styles["h1"]))
            i += 1
            continue

        if line.startswith("### "):
            flush_paragraph()
            flush_list()
            flush_table()
            flowables.append(Paragraph(_inline(line[4:].strip()), styles["h2"]))
            i += 1
            continue

        if line.startswith("#### "):
            flush_paragraph()
            flush_list()
            flush_table()
            flowables.append(Paragraph(_inline(line[5:].strip()), styles["h3"]))
            i += 1
            continue

        if line.lstrip().startswith(">"):
            flush_paragraph()
            flush_list()
            flush_table()
            flowables.append(Paragraph(_inline(line.lstrip()[1:].strip()), styles["quote"]))
            i += 1
            continue

        if line.startswith("|"):
            flush_paragraph()
            flush_list()
            if _is_separator_row(line):
                i += 1
                continue
            table_buffer.append(_parse_table_row(line))
            i += 1
            continue
        if table_buffer:
            flush_table()

        stripped = line.strip()
        if stripped.startswith("- "):
            flush_paragraph()
            flowables_code_pending = False
            list_buffer.append(stripped[2:].strip())
            i += 1
            continue
        if re.match(r"^\d+\.\s+", stripped):
            flush_paragraph()
            list_buffer.append(re.sub(r"^\d+\.\s+", "", stripped))
            i += 1
            continue
        if list_buffer:
            flush_list()

        para_buffer.append(stripped)
        i += 1

    flush_all()
    return flowables


def _on_page(canvas, doc) -> None:
    """Dibuja encabezado y pie de página con numeración."""
    canvas.saveState()
    width, height = A4
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(2 * cm, height - 1.3 * cm, DOC_TITLE)
    canvas.drawRightString(width - 2 * cm, height - 1.3 * cm, DOC_SUBTITLE)
    canvas.setStrokeColor(colors.HexColor("#c7d3dc"))
    canvas.setLineWidth(0.5)
    canvas.line(2 * cm, height - 1.45 * cm, width - 2 * cm, height - 1.45 * cm)
    canvas.drawCentredString(width / 2, 1.1 * cm, f"Página {doc.page}")
    canvas.restoreState()


def main() -> None:
    """Genera el PDF a partir del Markdown fuente."""
    if not SOURCE_MD.exists():
        raise FileNotFoundError(f"No se encontró el Markdown fuente: {SOURCE_MD}")

    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    text = SOURCE_MD.read_text(encoding="utf-8")
    styles = _build_styles()
    flowables = _markdown_to_flowables(text, styles)

    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=1.8 * cm,
        title=f"{DOC_TITLE} - {DOC_SUBTITLE}",
        author="Risk Analytics Project",
    )
    doc.build(flowables, onFirstPage=_on_page, onLaterPages=_on_page)
    print(f"PDF generado: {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
