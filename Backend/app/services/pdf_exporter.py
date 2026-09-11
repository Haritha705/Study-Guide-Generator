"""PDF export service using ReportLab."""

import io
import logging
from typing import Dict, Any, List

from app.core.exceptions import ExportError

logger = logging.getLogger(__name__)


def generate_pdf(content: Dict[str, Any]) -> bytes:
    """
    Generate a formatted PDF document from a study pack.

    Args:
        content: Dict containing 'notes', 'mcqs', 'glossary', 'short_answers',
                 and 'recommended_study_order'.

    Returns:
        PDF file as bytes.

    Raises:
        ExportError: If PDF generation fails.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.colors import HexColor
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table,
            TableStyle, PageBreak,
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
    except ImportError:
        raise ExportError(
            "ReportLab is not installed. Run: pip install reportlab"
        )

    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
        )

        styles = getSampleStyleSheet()
        elements: List = []

        # Custom styles
        title_style = ParagraphStyle(
            "PackTitle",
            parent=styles["Title"],
            fontSize=22,
            textColor=HexColor("#1a1a2e"),
            spaceAfter=20,
        )
        heading_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=16,
            textColor=HexColor("#16213e"),
            spaceBefore=16,
            spaceAfter=8,
        )
        body_style = styles["BodyText"]
        highlight_style = ParagraphStyle(
            "Highlight",
            parent=body_style,
            backColor=HexColor("#fff3cd"),
            borderPadding=4,
            spaceBefore=4,
            spaceAfter=4,
        )

        # --- Title ---
        title = content.get("title", "StudyPack AI — Study Guide")
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 12))

        # --- Study Order ---
        study_order = content.get("recommended_study_order", [])
        if study_order:
            elements.append(Paragraph("Recommended Study Order", heading_style))
            for i, topic in enumerate(study_order, 1):
                elements.append(Paragraph(f"{i}. {topic}", body_style))
            elements.append(Spacer(1, 12))

        # --- Notes ---
        notes = content.get("notes", [])
        if notes:
            elements.append(Paragraph("Notes", heading_style))
            for note in notes:
                topic = note.get("topic", "Untitled")
                elements.append(Paragraph(f"<b>{topic}</b>", body_style))
                for line in note.get("content", []):
                    elements.append(Paragraph(f"• {line}", body_style))
                for hl in note.get("highlights", []):
                    hl_text = f"[{hl.get('type', '')}] {hl.get('text', '')}"
                    elements.append(Paragraph(hl_text, highlight_style))
                elements.append(Spacer(1, 8))

        # --- Glossary ---
        glossary = content.get("glossary", [])
        if glossary:
            elements.append(PageBreak())
            elements.append(Paragraph("Glossary", heading_style))
            table_data = [["Term", "Definition"]]
            for item in glossary:
                table_data.append([
                    item.get("term", ""),
                    item.get("definition", ""),
                ])
            table = Table(table_data, colWidths=[1.8 * inch, 4.5 * inch])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#16213e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#f8f9fa"), HexColor("#ffffff")]),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 12))

        # --- MCQs ---
        mcqs = content.get("mcqs", [])
        if mcqs:
            elements.append(PageBreak())
            elements.append(Paragraph("Multiple Choice Questions", heading_style))
            for mcq in mcqs:
                q_text = f"Q{mcq.get('id', '?')}. [{mcq.get('difficulty', '')}] {mcq.get('question', '')}"
                elements.append(Paragraph(q_text, body_style))
                for opt in mcq.get("options", []):
                    elements.append(Paragraph(f"    {opt}", body_style))
                ans = mcq.get("answer", "")
                elements.append(Paragraph(f"<b>Answer:</b> {ans}", body_style))
                explanation = mcq.get("explanation", "")
                if explanation:
                    elements.append(Paragraph(f"<i>Explanation: {explanation}</i>", body_style))
                elements.append(Spacer(1, 8))

        # --- Build PDF ---
        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        logger.info(f"PDF generated: {len(pdf_bytes)} bytes")
        return pdf_bytes

    except ExportError:
        raise
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        raise ExportError(f"PDF generation failed: {str(e)}")
