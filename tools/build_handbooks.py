"""Assemble the Student Handbook, Teacher Handbook, and Exercise Workbook.

Requires all lesson chapters, tested code, rendered diagrams and execution evidence.
Run from any directory: python tools/build_handbooks.py --output-dir docs
HTML files embed illustrations and are self-contained. Markdown uses relative assets.
"""
from __future__ import annotations

import argparse
import base64
from collections import Counter
from datetime import datetime, timezone
import hashlib
import html
import json
import mimetypes
import os
from pathlib import Path
import re

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor
from markdown_it import MarkdownIt
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
NAVY, TEAL, GRAY = "17324D", "087F8C", "536477"
BOOKS = {
    "student": ("LangGraph_Student_Handbook", "Student Handbook"),
    "teacher": ("LangGraph_Teacher_Handbook", "Teacher Handbook"),
    "workbook": ("LangGraph_Exercise_Workbook", "Exercise Workbook"),
}
MD = MarkdownIt("commonmark", {"html": True}).enable("table")


def relative(asset: str | Path, output: Path) -> str:
    path = Path(asset)
    if not path.is_absolute():
        path = ROOT / path
    if not path.is_file():
        raise FileNotFoundError(f"Missing deliverable dependency: {path}")
    return Path(os.path.relpath(path, output)).as_posix()


def illustration(asset: str, caption: str, output: Path) -> str:
    return f"![{caption}]({relative(asset, output)})\n\n*{caption}*\n"


def code_block(path: Path) -> str:
    code = path.read_text(encoding="utf-8").rstrip()
    return f"```python\n{code}\n```\n"


def execution_block(ident: str, evidence: dict, output: Path) -> str:
    blocks = []
    for role in ("demonstration", "exercise-solution"):
        record = evidence[(ident, role)]
        if record["status"] != "passed" or not record.get("screenshot"):
            raise ValueError(f"No genuine successful execution screenshot: {ident} {role}")
        caption = (f"{ident} {role}: actual captured execution on macOS, "
                   f"{record['completed_at_utc'][:19]} UTC; exit {record['exit_code']}. "
                   f"{'Real Anthropic calls enabled' if record['live'] else 'Deterministic Python execution'}. "
                   "Browser screenshot of the captured output; the complete log is linked below.")
        blocks.append(illustration(record["screenshot"], caption, output))
        log = relative(record["log"], output)
        blocks.append(f"[Complete {ident} {role} execution log]({log}). "
                      f"Source SHA-256: `{record['source_sha256'][:20]}…`.\n")
    return "\n".join(blocks)


def frontmatter(kind: str, title: str, modules: list) -> str:
    purpose = {
        "student": "Read the explanations, run the complete baseline examples, then attempt the separate starter tasks before consulting instructor solutions. Basic Python is assumed; LangGraph, messages, tools, persistence, and retrieval are introduced step by step.",
        "teacher": "Use the same module IDs and sequence as the Student Handbook. Each chapter supplies demonstration guidance, complete exercise solutions, assessment answers with reasoning, misconceptions, and recovery steps. Distribute the student materials separately from the instructor solution directory when appropriate.",
        "workbook": "Work in exercises/starters, record observations, and use the progressive hints before opening exercises/solutions. Acceptance criteria describe behavior rather than a single wording from a language model. This workbook accompanies the Student Handbook; it is not a substitute for the explanations or complete examples.",
    }[kind]
    contents = "\n".join(f"- [{m['id']} — {m['title']}](#{m['id'].lower()})" for m in modules)
    return f'''# LangGraph Python Training

## {title}

**Version 1.1 · 3 November 2026 · Author: Manus AI**

A self-contained, step-by-step Python course for learners who know basic Python and are new to LangGraph. Course repository: https://github.com/nuvear/01_LangGraph.

{purpose}

The course progresses through eleven core lessons, preparation P00, durable memory U1, safe approval/state U2, LangSmith S1, LangWatch S2, and capstone C01. The estimated full teaching track is 29 hours 55 minutes excluding breaks, combining explanation, demonstration, guided practice, independent work, and assessment.

**Validation and platforms.** Delivered demonstrations and independent reference solutions are executed and recorded in the validation appendix. Model-based checks use the real configured Anthropic API; offline tests use explicitly identified test doubles. macOS/Python 3.12 is the actual execution platform. Windows commands are supplied but Windows execution is untested. Dashboard visual inspection is not implied by API ingestion checks.

**Credentials and data.** Keep `ANTHROPIC_API_KEY` in the local ignored `.env` and select the model with `ANTHROPIC_MODEL`. Do not put keys in state, prompts, source files, screenshots, traces, or submissions. Tracing sends synthetic lesson data to the selected service. A local embedding model requires a first download but no additional paid embedding API key. Examples are teaching applications, not production-security certifications.

**How to run the code.** Commands assume the repository root and an activated Python 3.12 virtual environment. Start with P00. Without activation, substitute `.venv/bin/python` on macOS or `.\\.venv\\Scripts\\python.exe` in PowerShell for `python`. `--live` is an explicit opt-in to paid model calls; it is never a fake-response switch. Use a new `--output-dir` when repeating a save exercise because file writes do not silently overwrite existing work.

<!-- PAGEBREAK -->

# Contents

Use these links in HTML/Markdown and Word’s linked contents or Navigation Pane. Module IDs remain the same in all three manuals.

{contents}
- [Appendices: commands, versions, validation, and sources](#appendices)

'''


def appendices(kind: str, modules: list, report: dict, output: Path) -> str:
    records = report["records"]
    passed = sum(r["status"] == "passed" for r in records)
    env_path = ROOT / "course/validation/environment.json"
    env = json.loads(env_path.read_text()) if env_path.exists() else {}
    tests_path = ROOT / "course/validation/test_summary.json"
    tests = json.loads(tests_path.read_text()) if tests_path.exists() else {}
    versions = "\n".join(f"- `{name}=={number}`" for name, number in env.get("versions", {}).items())
    commands = []
    for m in modules:
        ident = m["id"].lower()
        flag = " --live" if m["live"] else ""
        tracing = {"S1": " --backend langsmith", "S2": " --backend langwatch", "C01": " --backend both"}.get(m["id"], "")
        commands.append(f"python -m course_lessons.{ident}{flag}{tracing}")
        if kind == "teacher":
            commands.append(f"python -m exercises.solutions.{ident}{flag}{tracing}")
        if kind == "workbook":
            commands.append(f"python -m exercises.starters.{ident}")
    return f'''

<!-- PAGEBREAK -->
<a id="appendices"></a>
# Appendices

## A. Execution command reference

Run commands from the repository root, not from inside a lesson folder. Starters intentionally report `STARTER_NOT_COMPLETED` until edited; that is not a successful completed exercise. The matching instructor solution is the executable acceptance reference.

```bash
{chr(10).join(commands)}
python -m pytest -q
```

## B. Reproducible setup and versions

For a fresh checkout, first install Git and Python 3.12, then obtain the course branch. Skip cloning when you already have this repository open:

```bash
git clone --branch course/anthropic-observability-2026-11-03 https://github.com/nuvear/01_LangGraph.git
cd 01_LangGraph
```

macOS:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.lock.txt
test -f .env || cp .env.example .env
chmod 600 .env
```

Windows PowerShell, without activation or execution-policy changes:

```powershell
py -3.12 -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install -r requirements.lock.txt
if (-not (Test-Path .env)) {{ Copy-Item .env.example .env }}
.\\.venv\\Scripts\\python.exe -m examples.observability_demo --backend none
```

Privately edit `.env` in a local text editor: set `ANTHROPIC_API_KEY` to your own Anthropic Console key and keep or replace the configurable `ANTHROPIC_MODEL`. The supplied example uses `claude-opus-5-5`, which passed this project's real connection check; your account must have access to the selected model. LangSmith and LangWatch fields are needed only for the corresponding tracing modules or a command selecting both. Choose the LangSmith endpoint for your actual account region. Close the file before screen sharing and never paste its contents into a terminal command. These guarded copy commands preserve an existing `.env`; do not replace them with an unconditional overwrite.

Install the locked runtime before trying the per-lesson commands. Authoring/rendering tools are separated in `requirements-docs.txt`; students do not need Mermaid, LibreOffice, Playwright, or Word-building tools to run ordinary lessons.

Actual validation interpreter: `{report.get('python','3.12')}`. Runtime package versions:

{versions}

The complete transitive pins are in `requirements.lock.txt`. Platform-specific wheels and native libraries can differ; a successful macOS install is not a Windows test. The first local-embedding run downloads model weights; offline tests do not stand in for that real download/indexing check.

## C. Actual execution and test results

The validation harness recorded **{passed}/{len(records)} successful demonstration/reference-solution executions**. It records command, UTC time, duration, exit code, backend, code hash, log hash, and screenshot path in `course/validation/execution_manifest.json`.

Offline test result: **{tests.get('passed','see test report')} passed**, **{tests.get('failed',0)} failed**, **{tests.get('skipped',0)} skipped**. Offline model doubles validate orchestration deterministically; the separate `--live` runs validate actual provider behavior. Each screenshot in the two handbooks is captured from a browser displaying the actual stdout/stderr produced by the indicated process. It is explicitly labeled rather than made to resemble a native Terminal application. A viewport can show only part of a long log; complete text logs are supplied alongside images.

[Full validation report]({relative('course/validation_report.md', output)}). [Machine-readable execution manifest]({relative('course/validation/execution_manifest.json', output)}).

The local supplied Anthropic model is configurable; exact model wording and latency are not guaranteed. Independent exercises have executable reference solutions. Optional design extensions are not additional validated software deliverables unless their solution is explicitly implemented and tested.

## D. Troubleshooting map

A missing module normally means the environment or working directory is wrong: verify the selected interpreter, install the lock, and run a module command from the repository root. A graph-build error should be diagnosed before adding an LLM. A recursion-limit failure means the loop did not terminate as intended; inspect state, routing labels, and tool results instead of increasing the limit blindly.

HTTP 401 indicates a credential/authentication problem, not proof of an unavailable graph. Model access, usage limits, network errors, and regional tracing endpoints are separate checks. Never paste a key into an exception report. A missing trace can result from a wrong backend, key scope, endpoint, or unflushed exporter; verify ingestion independently from callback completion. No-tracing mode should remain available for privacy and debugging.

For file-save errors, check the explicitly selected output directory and filename. A rejected traversal, symlink, or overwrite is an intended safety check. For SQLite persistence, keep the same database and thread ID when testing recovery, and use different IDs when testing isolation. For RAG, inspect pages, chunks, collection path, embedding identity, and retrieved evidence before judging the generated answer.

## E. Original illustrations and technical references

The concept illustrations and flowcharts are original diagrams created for this course. Editable Mermaid sources are supplied under `assets/diagrams`. Concept diagrams explain data flow and mental models; complete implementation flowcharts include more detailed guards and error paths.

Execution screenshots are separate evidence of actual runs, not conceptual mockups. Chapter-specific official technical documentation is retained beside the material it supports. Source/page citations in retrieval exercises refer to the supplied synthetic teaching dataset and must remain inspectable.

## F. Delivery and classroom use

The Student Handbook, Teacher Handbook, and Exercise Workbook share the same identifiers and sequence. Runnable baselines live in `course_lessons`, unfinished tasks in `exercises/starters`, instructor answers in `exercises/solutions`, and regression tests in `tests/lessons`. Directory separation is not an access-control boundary: instructors should omit solutions when distributing a learner-only package.

Word contains embedded images. HTML embeds its images for standalone reading. Markdown keeps relative links and should be distributed with the supplied asset folders or complete course archive.

## G. Working glossary

**State** is the graph's structured working data. A **partial update** contains only the state fields a node changes. A **TypedDict** describes expected dictionary keys for type checking; it does not automatically validate arbitrary input at runtime.

A **node** is a named processing step. An **edge** schedules a next step. A **conditional edge** chooses a destination from state. **START** and **END** are graph boundaries, not work-performing business functions. A **compiled graph** is the executable produced by the builder; compilation does not prove its answers are correct.

A **reducer** defines how an update combines with an existing state field. Without an accumulating reducer, a later update commonly replaces an earlier value. **MessagesState** supplies a message channel with **add_messages**, which handles message identity as well as appending new turns.

A **tool schema** describes an available function. A **tool call** is the model's request to use it, not the function's execution. The application executes the tool and returns a **tool result** linked to that call. A **ReAct-style loop** alternates model and tool steps until an exit condition is reached.

A **thread ID** selects a unit of conversation/checkpoint history; it is not an operating-system thread. A **checkpoint** records graph execution state. **Durable persistence** survives the process only when the chosen storage backend actually retains the data. An **interrupt** pauses execution at an explicit point, and a resume command supplies the human decision to the persisted workflow.

**Retrieval** selects passages relevant to a query. An **embedding** maps text to a numeric vector; the index and query must use compatible embeddings. A **vector store** such as Chroma stores and searches vectors with their document metadata. **RAG**, retrieval-augmented generation, supplies retrieved evidence to a model; it does not guarantee that every generated claim is correct. A **citation** should lead to inspectable source/page evidence.

A **trace** records an execution; a **span** records an operation within it. Traces can expose inputs and outputs, so they require deliberate data selection. **Latency** is elapsed time, and **token usage** measures provider-accounted input/output units. Neither tracing nor a token count reveals private model chain-of-thought.
'''


def assemble(kind: str, output: Path) -> str:
    modules = json.loads((ROOT / "course/lesson_manifest.json").read_text())
    report = json.loads((ROOT / "course/validation/execution_manifest.json").read_text())
    evidence = {(r["id"], r["role"]): r for r in report["records"]}
    text = frontmatter(kind, BOOKS[kind][1], modules)
    for module in modules:
        ident, low = module["id"], module["id"].lower()
        chapter = (ROOT / "course/chapters" / low / f"{kind}.md").read_text()
        if not chapter.startswith("# "):
            raise ValueError(f"Chapter must begin with a heading: {ident}/{kind}")
        chapter = re.sub(r"^#\s+[^\n]+", f"# {ident} — {module['title']}", chapter, count=1)
        overview = ROOT / "assets/diagrams/overviews" / f"{low}.png"
        diagram_path = f"assets/diagrams/overviews/{low}.png" if overview.is_file() else f"assets/diagrams/{low}.png"
        diagram_caption = f"{ident}: original {'overview' if overview.is_file() else 'teaching'} diagram for this implementation. Detailed guards and error paths are explained in the text and complete flowchart."
        diagram = illustration(diagram_path, diagram_caption, output)
        diagram += f"\n[Editable complete {ident} flowchart]({relative(f'assets/diagrams/{low}.mmd', output)}).\n"
        replacements = {
            "<!-- EXAMPLE_CODE -->": code_block(ROOT / "course_lessons" / f"{low}.py"),
            "<!-- SOLUTION_CODE -->": code_block(ROOT / "exercises/solutions" / f"{low}.py"),
            "<!-- ORIGINAL_DIAGRAM -->": diagram,
            "<!-- EXECUTION_FIGURES -->": execution_block(ident, evidence, output) if kind != "workbook" else "",
        }
        concept = ROOT / "assets/diagrams" / f"{low}-concept.png"
        concept_caption = f"{ident}: original concept diagram — {module['title']}."
        if ident == "L05":
            concept_caption += " Operand pairs remain independent; the calculation steps run sequentially."
        replacements["<!-- CONCEPT_FIGURE -->"] = illustration(concept, concept_caption, output) if concept.is_file() else ""
        for marker, replacement in replacements.items():
            chapter = chapter.replace(marker, replacement)
        # Explicitly distinguish optional design prompts from executed core work.
        chapter = re.sub(r"(?im)^(#{2,3})\s+(?:Optional )?[Ss]tretch(?: task| exercise| challenge)?", r"\1 Optional design extension — not part of the validated execution set", chapter)
        if re.search(r"<!-- (?:EXAMPLE|SOLUTION|ORIGINAL|CONCEPT|VIDEO|EXECUTION)_", chapter):
            raise ValueError(f"Unresolved injection marker in {ident}/{kind}")
        # Link-reference definitions alone are invisible in rendered Markdown.
        # Keep them for citations, and show their titles/URLs in the source list.
        definitions = re.findall(r'^\[(\d+)\]:\s+(\S+)\s+"([^"]+)"\s*$', chapter, re.M)
        inline_references = "<!-- REFERENCES_INLINE -->" in chapter
        chapter = chapter.replace("<!-- REFERENCES_INLINE -->", "")
        if definitions and not inline_references:
            visible = "\n".join(f"- [{number}: {name}]({url})" for number, url, name in definitions)
            heading = re.search(r"(?im)^#{2,3}\s+(?:References?|Sources|Official sources|Current official sources)\s*$", chapter)
            if heading:
                chapter = chapter[:heading.end()] + "\n\n" + visible + "\n" + chapter[heading.end():]
            else:
                chapter += "\n\n## Current official sources\n\n" + visible + "\n"
        text += f'\n\n<!-- PAGEBREAK -->\n<a id="{low}"></a>\n' + chapter.rstrip() + "\n"
    text += appendices(kind, modules, report, output)
    return text


def add_field(paragraph, instruction: str) -> None:
    run = paragraph.add_run()
    for tag, value in (("w:fldChar", "begin"), ("w:instrText", instruction), ("w:fldChar", "end")):
        node = OxmlElement(tag)
        if tag == "w:fldChar":
            node.set(qn("w:fldCharType"), value)
        else:
            node.text = value
        run._r.append(node)


def link(paragraph, text: str, href: str, bold=False, italic=False) -> None:
    node = OxmlElement("w:hyperlink")
    if href.startswith("#"):
        node.set(qn("w:anchor"), href[1:])
    else:
        rid = paragraph.part.relate_to(href, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
        node.set(qn("r:id"), rid)
    run = OxmlElement("w:r"); props = OxmlElement("w:rPr")
    color = OxmlElement("w:color"); color.set(qn("w:val"), TEAL); props.append(color)
    if bold: props.append(OxmlElement("w:b"))
    if italic: props.append(OxmlElement("w:i"))
    run.append(props)
    content = OxmlElement("w:t"); content.text = text; run.append(content)
    node.append(run); paragraph._p.append(node)


def inline(document, paragraph, children: list, base: Path) -> None:
    bold = italic = False
    href = None
    for token in children or []:
        kind = token.type
        if kind == "strong_open": bold = True
        elif kind == "strong_close": bold = False
        elif kind == "em_open": italic = True
        elif kind == "em_close": italic = False
        elif kind == "link_open": href = token.attrGet("href")
        elif kind == "link_close": href = None
        elif kind == "image":
            path = (base / token.attrGet("src")).resolve()
            if not path.is_file(): raise FileNotFoundError(path)
            image = Image.open(path)
            width, height = image.size
            maximum_width, maximum_height = 6.7, 6.0
            display_width = min(maximum_width, maximum_height * width / height)
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph.paragraph_format.keep_with_next = True
            paragraph.add_run().add_picture(str(path), width=Inches(display_width))
        elif kind in ("text", "code_inline"):
            if href:
                link(paragraph, token.content, href, bold, italic)
            else:
                run = paragraph.add_run(token.content); run.bold = bold; run.italic = italic
                if kind == "code_inline":
                    run.font.name = "Consolas"; run.font.size = Pt(9)
        elif kind == "hardbreak": paragraph.add_run().add_break()
        elif kind == "softbreak": paragraph.add_run(" ")
        elif kind == "html_inline":
            if token.content in ("<br>", "<br/>", "<br />"): paragraph.add_run().add_break()


def configure_document(title: str):
    doc = Document(); section = doc.sections[0]
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    section.top_margin = section.bottom_margin = Cm(1.8)
    section.left_margin = section.right_margin = Cm(1.8)
    section.header_distance, section.footer_distance = Cm(.75), Cm(.85)
    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"; normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor.from_string(NAVY)
    normal.paragraph_format.line_spacing = 1.12
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.widow_control = True
    for name, size, color in (("Title",32,NAVY),("Subtitle",22,TEAL),("Heading 1",21,TEAL),("Heading 2",14,NAVY),("Heading 3",11.5,NAVY)):
        style=doc.styles[name]; style.font.name="Calibri";style.font.size=Pt(size);style.font.color.rgb=RGBColor.from_string(color)
        style.paragraph_format.keep_with_next=True
        style.paragraph_format.space_before=Pt(12 if name!='Title' else 0)
        style.paragraph_format.space_after=Pt(7)
    for name in ("Caption",):
        doc.styles[name].font.size=Pt(8.5);doc.styles[name].font.color.rgb=RGBColor.from_string(GRAY)
    bibliography=doc.styles.add_style("Course References", WD_STYLE_TYPE.PARAGRAPH)
    bibliography.base_style=normal
    bibliography.font.size=Pt(9)
    bibliography.paragraph_format.line_spacing=1.03
    bibliography.paragraph_format.space_after=Pt(1)
    ref_heading=doc.styles.add_style("Course Reference Heading", WD_STYLE_TYPE.PARAGRAPH)
    ref_heading.base_style=doc.styles["Heading 2"]
    ref_heading.font.size=Pt(10.5)
    ref_heading.paragraph_format.space_before=Pt(4)
    ref_heading.paragraph_format.space_after=Pt(3)
    header=section.header.paragraphs[0]
    run=header.add_run(f"LANGGRAPH  /  {title.upper()}");run.font.size=Pt(8);run.font.color.rgb=RGBColor.from_string(GRAY)
    footer=section.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    run=footer.add_run("Version 1.1  |  3 November 2026  |  ");run.font.size=Pt(8)
    add_field(footer,"PAGE")
    doc.core_properties.title=f"LangGraph Python Training — {title}"
    doc.core_properties.author="Manus AI"
    doc.core_properties.subject="Complete beginner Python course with verified exercises and evidence"
    return doc


def word_document(markdown: str, output_path: Path, title: str) -> None:
    doc = configure_document(title)
    tokens = MD.parse(markdown)
    paragraph = None; first_h1=True; page_break=False; quote=False
    lists=[]; item_new=False; bookmark=1; references_mode=False
    for index, token in enumerate(tokens):
        kind=token.type
        if kind=="html_block":
            if "PAGEBREAK" in token.content: page_break=True
        elif kind=="heading_open":
            level=int(token.tag[1:])
            content=tokens[index+1].content if index+1<len(tokens) else ""
            style="Title" if first_h1 and level==1 else ("Subtitle" if level==2 and content==title else f"Heading {min(level,3)}")
            references_mode=level>=2 and bool(re.search(r"references?|sources", content, re.I))
            if references_mode:
                style="Course Reference Heading"
            paragraph=doc.add_paragraph(style=style)
            if page_break:paragraph.paragraph_format.page_break_before=True;page_break=False
            if first_h1 and level==1:
                paragraph.paragraph_format.space_before=Pt(28)
                first_h1=False
            content=tokens[index+1].content if index+1<len(tokens) else ""
            match=re.match(r"(P00|L\d\d|U[12]|S[12]|C01)\b",content)
            anchor=match.group(1).lower() if match else ("appendices" if content=="Appendices" else None)
            if anchor:
                start=OxmlElement("w:bookmarkStart");start.set(qn("w:id"),str(bookmark));start.set(qn("w:name"),anchor)
                end=OxmlElement("w:bookmarkEnd");end.set(qn("w:id"),str(bookmark));bookmark+=1
                paragraph._p.append(start);paragraph._p.append(end)
        elif kind=="paragraph_open":
            paragraph=doc.add_paragraph(style="Course References" if references_mode else None)
            if page_break:paragraph.paragraph_format.page_break_before=True;page_break=False
            if lists:
                paragraph.paragraph_format.left_indent=Cm(.4*len(lists))
                if item_new:
                    entry=lists[-1]
                    prefix="• " if entry["kind"]=="bullet" else f"{entry['next']}. "
                    paragraph.add_run(prefix);entry["next"]+=1;item_new=False
            if quote:
                paragraph.paragraph_format.left_indent=Cm(.5)
                paragraph.paragraph_format.right_indent=Cm(.3)
        elif kind=="inline":
            if paragraph is None:paragraph=doc.add_paragraph()
            inline(doc,paragraph,token.children,output_path.parent)
            if token.children and all(c.type in ("em_open","em_close","text","softbreak","link_open","link_close","code_inline") for c in token.children) and token.content.startswith("*"):
                paragraph.style="Caption"
        elif kind in ("heading_close","paragraph_close"):
            paragraph=None
        elif kind=="fence" or kind=="code_block":
            paragraph=doc.add_paragraph()
            paragraph.paragraph_format.line_spacing=1.0
            paragraph.paragraph_format.space_before=Pt(4);paragraph.paragraph_format.space_after=Pt(7)
            paragraph.paragraph_format.left_indent=Cm(.15);paragraph.paragraph_format.right_indent=Cm(.15)
            paragraph.paragraph_format.keep_together=False
            shade=OxmlElement("w:shd");shade.set(qn("w:fill"),"F0F4F7");paragraph._p.get_or_add_pPr().append(shade)
            run=paragraph.add_run(token.content.rstrip());run.font.name="Consolas";run.font.size=Pt(8.5);run.font.color.rgb=RGBColor.from_string("17324D")
            paragraph=None
        elif kind in ("bullet_list_open","ordered_list_open"):
            lists.append({"kind":"bullet" if kind=="bullet_list_open" else "ordered","next":int(token.attrGet("start") or 1)})
        elif kind in ("bullet_list_close","ordered_list_close"):
            lists.pop();item_new=False
        elif kind=="list_item_open":item_new=True
        elif kind=="blockquote_open":quote=True
        elif kind=="blockquote_close":quote=False
        elif kind=="hr":doc.add_paragraph("—"*24)
        elif kind in ("table_open","thead_open","tbody_open","tr_open","th_open","td_open","th_close","td_close","tr_close","thead_close","tbody_close","table_close"):
            # Chapters default to prose/lists; retain uncommon table cells as readable text.
            if kind in ("th_open","td_open"):paragraph=doc.add_paragraph()
    doc.save(output_path)


def html_document(markdown: str, output_path: Path, title: str) -> None:
    body=MD.render(markdown)
    pattern=re.compile(r'<img src="([^\"]+)"')
    def embed(match):
        path=(output_path.parent/html.unescape(match.group(1))).resolve()
        if not path.is_file():raise FileNotFoundError(path)
        data=base64.b64encode(path.read_bytes()).decode()
        mime=mimetypes.guess_type(path.name)[0] or "image/png"
        return f'<img src="data:{mime};base64,{data}"'
    body=pattern.sub(embed,body)
    document=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LangGraph — {html.escape(title)}</title><style>
:root{{--ink:#17324d;--teal:#087f8c;--muted:#536477;--paper:#fff;--back:#edf2f7}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:var(--back);color:var(--ink);font:18px/1.65 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}main{{max-width:1060px;margin:30px auto;padding:55px 65px;background:var(--paper);box-shadow:0 12px 45px #17324d12}}h1,h2,h3{{line-height:1.25}}h1{{font-size:2.1rem;color:var(--teal);margin-top:2.5em;padding-top:.5em;border-top:1px solid #dce8ed}}h1:first-child{{font-size:2.6rem;color:var(--ink);margin-top:0;border:0}}h2{{font-size:1.5rem;margin-top:1.8em}}h3{{font-size:1.16rem}}a{{color:#087f8c;text-underline-offset:3px}}p,li{{overflow-wrap:anywhere}}pre{{padding:22px;background:#112338;color:#eef6ff;border-radius:8px;overflow:auto;font:14px/1.55 Consolas,"SFMono-Regular",monospace}}code{{font-family:Consolas,"SFMono-Regular",monospace}}p code,li code{{font-size:.9em;background:#edf4f7;padding:.12em .28em;border-radius:3px}}img{{display:block;max-width:100%;max-height:780px;height:auto;margin:24px auto 8px;object-fit:contain}}p:has(>em:only-child){{font-size:.86em;color:var(--muted)}}blockquote{{margin:18px 0;padding:8px 22px;border-left:4px solid var(--teal);background:#edf6f8}}table{{border-collapse:collapse;width:100%}}td,th{{padding:8px;border:1px solid #dbe5ec;text-align:left}}.top{{position:fixed;right:20px;bottom:20px;background:#087f8c;color:white;padding:8px 14px;border-radius:6px;text-decoration:none;font-size:14px}}@media(max-width:700px){{body{{font-size:17px}}main{{margin:0;padding:28px 22px}}h1{{font-size:1.8rem}}pre{{font-size:12px}}}}@media print{{body{{background:white;font-size:11pt}}main{{margin:0;padding:0;max-width:none;box-shadow:none}}h1{{page-break-before:always}}h1:first-child{{page-break-before:auto}}.top{{display:none}}pre{{white-space:pre-wrap;font-size:8pt}}img{{max-height:600px}}}}
</style></head><body><main id="top">{body}</main><a class="top" href="#top">Contents / top</a></body></html>'''
    output_path.write_text(document,encoding="utf-8")


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,default=ROOT/"docs")
    parser.add_argument("--only",choices=list(BOOKS),nargs="*")
    args=parser.parse_args();output=args.output_dir.resolve();output.mkdir(parents=True,exist_ok=True)
    results=[]
    for kind,(basename,title) in BOOKS.items():
        if args.only and kind not in args.only:continue
        markdown=assemble(kind,output)
        md_path=output/f"{basename}.md";md_path.write_text(markdown,encoding="utf-8")
        word_document(markdown,output/f"{basename}.docx",title)
        html_document(markdown,output/f"{basename}.html",title)
        stats={"book":kind,"words":len(markdown.split()),"images":markdown.count("!["),"code_blocks":markdown.count("```python"),"markdown":str(md_path)}
        results.append(stats);print(json.dumps(stats),flush=True)
    (ROOT/"course/validation/book_build.json").write_text(json.dumps(results,indent=2))


if __name__=="__main__":main()
