"""Rebuild only the original synthetic L11 teaching PDF; no network required."""
from pathlib import Path
import json
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak


def main() -> None:
    directory = Path(__file__).resolve().parent
    source = json.loads((directory / "rag_teaching_handbook.json").read_text())
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        "Replacement", fontName="Helvetica-Bold", fontSize=9,
        leading=13, textColor=colors.HexColor("#8a321c"), spaceAfter=18,
    ))
    styles["BodyText"].fontSize = 12
    styles["BodyText"].leading = 18
    styles["BodyText"].spaceAfter = 16
    story = []
    for number, page in enumerate(source["pages"], start=1):
        if number > 1:
            story.append(PageBreak())
        story.append(Paragraph(escape(source["label"]), styles["Replacement"]))
        story.append(Paragraph(escape(source["title"]), styles["Title"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph(escape(page["heading"]), styles["Heading1"]))
        for text in page["paragraphs"]:
            story.append(Paragraph(escape(text), styles["BodyText"]))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 9)
        canvas.drawString(48, 32, "L11 / C01 synthetic practice source")
        canvas.drawRightString(A4[0] - 48, 32, f"Page {doc.page}")
        canvas.restoreState()

    output = directory / "rag_teaching_handbook.pdf"
    SimpleDocTemplate(
        str(output), pagesize=A4, rightMargin=48, leftMargin=48,
        topMargin=46, bottomMargin=54, title=source["title"],
        author="LangGraph course — original synthetic teaching asset",
    ).build(story, onFirstPage=footer, onLaterPages=footer)
    print(output)


if __name__ == "__main__":
    main()
