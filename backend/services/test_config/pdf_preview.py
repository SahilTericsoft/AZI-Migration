"""Report-layout preview → PDF (test-config).

Python re-implementation of the legacy preview that GkReactPdfService rendered
with React-PDF. It turns a report-layout definition (the FE report designer's
`blocks`, plus disclaimer/foot-note) into a sample laboratory-report PDF so the
admin can see how the configured layout will look. Result/reference columns are
intentionally blank — this is a layout preview, not a real patient result.

Rendering uses ReportLab (pure Python, no system libraries) so it works in the
slim Docker image without extra build deps.
"""

from __future__ import annotations

from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# A "section" is one titled block with an ordered list of biomarker ids.
Section = tuple[str, list[int]]


def _sections_from_payload(payload: dict[str, Any]) -> list[Section]:
    """Normalise the several possible layout shapes into flat titled sections.

    Accepts, in priority order:
      * FE designer:   blocks = [{title, biomarkerIds}]
      * legacy simple: tableTitle = [{title, biomarkerIds}]
      * legacy nested: blocks = [{groups: [{tableTitle: [{title, biomarkerIds}]}]}]
    """
    sections: list[Section] = []

    def _add(entry: dict[str, Any]) -> None:
        title = entry.get("title") or ""
        ids = entry.get("biomarkerIds") or []
        sections.append((title, [int(i) for i in ids if i is not None]))

    blocks = payload.get("blocks")
    table_title = payload.get("tableTitle")

    if isinstance(blocks, list) and blocks and isinstance(blocks[0], dict) and "groups" in blocks[0]:
        # legacy nested (layout6)
        for block in blocks:
            for group in block.get("groups") or []:
                for table in group.get("tableTitle") or []:
                    _add(table)
    elif isinstance(blocks, list) and blocks:
        for block in blocks:
            _add(block)
    elif isinstance(table_title, list):
        for table in table_title:
            _add(table)

    return sections


def render_layout_pdf(
    payload: dict[str, Any],
    biomarker_names: dict[int, str],
) -> bytes:
    """Render the layout preview to PDF bytes.

    `biomarker_names` maps biomarker id → display name (resolved by the caller).
    """
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        title="Report Preview",
    )

    styles = getSampleStyleSheet()
    h_title = ParagraphStyle(
        "ReportTitle", parent=styles["Title"], fontSize=16, spaceAfter=2
    )
    h_sub = ParagraphStyle(
        "ReportSub", parent=styles["Normal"], fontSize=9,
        textColor=colors.grey, alignment=1, spaceAfter=10,
    )
    section_title = ParagraphStyle(
        "SectionTitle", parent=styles["Heading4"], fontSize=11,
        backColor=colors.HexColor("#f1f5f9"), leftIndent=4, spaceBefore=8, spaceAfter=4,
    )
    small = ParagraphStyle("Small", parent=styles["Normal"], fontSize=8, textColor=colors.grey)
    disc = ParagraphStyle("Disclaimer", parent=styles["Normal"], fontSize=8, spaceBefore=10)

    layout = payload.get("layout") or "layout1"
    test_name = payload.get("testName") or "Sample Report"

    story: list[Any] = []
    story.append(Paragraph("Laboratory Report", h_title))
    story.append(Paragraph(f"{test_name} &middot; Preview &middot; {layout}", h_sub))

    sections = _sections_from_payload(payload)
    if not sections:
        story.append(
            Paragraph("Add a block with a title and test(s) to preview the report.", small)
        )
    else:
        for idx, (title, ids) in enumerate(sections, start=1):
            story.append(Paragraph(title or f"Section {idx}", section_title))
            rows: list[list[str]] = [["Test", "Result", "Reference Range", "Unit"]]
            if not ids:
                rows.append(["No tests selected", "", "", ""])
            else:
                for bid in ids:
                    rows.append([biomarker_names.get(bid, f"#{bid}"), "—", "—", "—"])
            table = Table(rows, colWidths=[2.6 * inch, 1.3 * inch, 1.9 * inch, 0.9 * inch])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#334155")),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                        ("TOPPADDING", (0, 0), (-1, -1), 5),
                        ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#e5e7eb")),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ]
                )
            )
            story.append(table)

    disclaimer = payload.get("disclaimer")
    foot_note = payload.get("footNote")
    if disclaimer:
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"<b>Disclaimer:</b> {disclaimer}", disc))
    if foot_note:
        story.append(Paragraph(foot_note, small))

    doc.build(story)
    return buf.getvalue()
