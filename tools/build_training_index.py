"""Build the editable training-index Word document from its Markdown source.

Install requirements-docs.txt; run from any directory:
    python tools/build_training_index.py --output docs/LangGraph_Training_Index.docx
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
NAVY = "17324D"
TEAL = "087F8C"
GRAY = "536477"


def hyperlink(paragraph, url: str) -> None:
    relation = paragraph.part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
    link = OxmlElement("w:hyperlink")
    link.set(qn("r:id"), relation)
    run = OxmlElement("w:r")
    props = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), TEAL)
    props.append(color)
    run.append(props)
    text = OxmlElement("w:t")
    text.text = url
    run.append(text)
    link.append(run)
    paragraph._p.append(link)


def rich_text(paragraph, text: str) -> None:
    for part in re.split(r"(\*\*.*?\*\*|\*[^*\n]+\*|`[^`]+`|https?://[^\s]+)", text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            paragraph.add_run(part[2:-2]).bold = True
        elif part.startswith("*") and part.endswith("*"):
            paragraph.add_run(part[1:-1]).italic = True
        elif part.startswith("`") and part.endswith("`"):
            run = paragraph.add_run(part[1:-1])
            run.font.name = "Consolas"
            run.font.size = Pt(9)
        elif part.startswith(("https://", "http://")):
            hyperlink(paragraph, part)
        else:
            paragraph.add_run(part)


def field(paragraph, name: str) -> None:
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar"); begin.set(qn("w:fldCharType"), "begin")
    instruction = OxmlElement("w:instrText"); instruction.text = name
    separate = OxmlElement("w:fldChar"); separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t"); text.text = "1"
    end = OxmlElement("w:fldChar"); end.set(qn("w:fldCharType"), "end")
    for element in (begin, instruction, separate, text, end):
        run._r.append(element)


def build(output: Path) -> None:
    document = Document()
    section = document.sections[0]
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    section.top_margin, section.bottom_margin = Cm(1.7), Cm(1.7)
    section.left_margin, section.right_margin = Cm(1.8), Cm(1.8)
    section.header_distance, section.footer_distance = Cm(0.75), Cm(0.8)
    normal = document.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(10)
    normal.font.color.rgb = RGBColor.from_string(NAVY)
    normal.paragraph_format.line_spacing = 1.06
    normal.paragraph_format.space_after = Pt(5)
    normal.paragraph_format.widow_control = True
    for name, size, color in (("Title", 34, NAVY), ("Subtitle", 20, TEAL),
                               ("Heading 1", 18, TEAL), ("Heading 2", 12, NAVY)):
        style = document.styles[name]
        style.font.name = "Calibri"
        style.font.size = Pt(size)
        style.font.color.rgb = RGBColor.from_string(color)
        style.paragraph_format.space_before = Pt(8 if name == "Heading 2" else 0)
        style.paragraph_format.space_after = Pt(6)
        style.paragraph_format.keep_with_next = True
    header = section.header.paragraphs[0]
    r = header.add_run("LANGGRAPH  /  PYTHON TRAINING")
    r.font.size = Pt(8)
    r.font.color.rgb = RGBColor.from_string(GRAY)
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = footer.add_run("DRAFT v0.1  |  3 November 2026  |  ")
    r.font.size = Pt(8)
    field(footer, "PAGE")
    document.core_properties.title = "LangGraph Python Training — Complete Training Index"
    document.core_properties.subject = "Timestamped course index for scope approval"
    document.core_properties.author = "Manus AI"
    document.core_properties.keywords = "LangGraph, Python, Anthropic, LangSmith, LangWatch, training index"

    markdown = (ROOT / "course/training_index.md").read_text(encoding="utf-8")
    blocks = re.split(r"\n\s*\n", markdown.strip())
    next_page = False
    first_heading = True
    cover = True
    for block in blocks:
        if block.strip() == "<!-- pagebreak -->":
            next_page = True
            cover = False
            continue
        if block.startswith("# "):
            paragraph = document.add_paragraph(style="Title" if first_heading else "Heading 1")
            paragraph.paragraph_format.page_break_before = next_page
            next_page = False
            paragraph.add_run(block[2:].strip())
            if first_heading:
                paragraph.paragraph_format.space_before = Pt(42)
                paragraph.paragraph_format.space_after = Pt(14)
            first_heading = False
        elif block.startswith("## "):
            paragraph = document.add_paragraph(style="Subtitle" if cover else "Heading 2")
            paragraph.add_run(block[3:].strip())
        else:
            paragraph = document.add_paragraph()
            if next_page:
                paragraph.paragraph_format.page_break_before = True
                next_page = False
            for index, line in enumerate(block.splitlines()):
                if index:
                    paragraph.add_run().add_break()
                rich_text(paragraph, line.strip())
            if block.startswith("**Video ") or block.startswith("**Added "):
                paragraph.paragraph_format.space_after = Pt(4)
                for run in paragraph.runs:
                    run.font.size = Pt(9)
                    run.font.color.rgb = RGBColor.from_string(GRAY)
            if block.startswith(("**Review basis.", "**Current stage.")):
                paragraph.paragraph_format.space_before = Pt(8)
                props = paragraph._p.get_or_add_pPr()
                shade = OxmlElement("w:shd"); shade.set(qn("w:fill"), "EDF4F7"); props.append(shade)
                paragraph.paragraph_format.left_indent = Cm(0.2)
                paragraph.paragraph_format.right_indent = Cm(0.2)
    output.parent.mkdir(parents=True, exist_ok=True)
    document.save(output)
    print(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/LangGraph_Training_Index.docx")
    arguments = parser.parse_args()
    destination = arguments.output
    if not destination.is_absolute():
        destination = ROOT / destination
    build(destination)
