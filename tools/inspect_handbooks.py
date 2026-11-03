"""Inspect rendered Word manuals and create contact sheets for human layout QA.

Render DOCX with LibreOffice into .work/previews/handbooks first. PDFs are internal
layout proofs, not the course deliverables. Requires Poppler and authoring packages.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("LangGraph_Student_Handbook", "LangGraph_Teacher_Handbook", "LangGraph_Exercise_Workbook")


def inspect(name: str) -> dict:
    pdf = ROOT / ".work/previews/handbooks" / f"{name}.pdf"
    directory = pdf.parent / name
    directory.mkdir(parents=True, exist_ok=True)
    # A shorter new draft must not inherit old final pages or contact sheets.
    for pattern in ("page-*.png", "contact-*.png"):
        for stale in directory.glob(pattern):
            stale.unlink()
    subprocess.run(["pdftoppm", "-scale-to", "1100", "-png", str(pdf), str(directory / "page")], check=True)
    text_path = directory / "rendered.txt"
    subprocess.run(["pdftotext", "-layout", str(pdf), str(text_path)], check=True)
    bbox = directory / "bbox.html"
    subprocess.run(["pdftotext", "-bbox-layout", str(pdf), str(bbox)], check=True)
    tree = ET.parse(bbox)
    pages = [p for p in tree.iter() if p.tag.endswith("}page")]
    overflow = []
    page_word_counts = []
    for number, page in enumerate(pages, 1):
        width, height = float(page.attrib["width"]), float(page.attrib["height"])
        words = [w for w in page.iter() if w.tag.endswith("}word")]
        body = [w for w in words if 44 < float(w.attrib["yMin"]) < height-44]
        page_word_counts.append(len(body))
        if any(float(w.attrib["xMin"]) < 25 or float(w.attrib["xMax"]) > width-25 for w in body):
            overflow.append(number)
    images = sorted(directory.glob("page-*.png"))
    assert len(images) == len(pages), "Page-image count differs from the actual PDF."
    sparse = []
    for number, path in enumerate(images, 1):
        im = Image.open(path).convert("L")
        crop = im.crop((int(im.width*.07),int(im.height*.07),int(im.width*.93),int(im.height*.93)))
        histogram = crop.histogram()
        ink = sum(histogram[:220]) / (crop.width*crop.height)
        if ink < .003:
            sparse.append(number)
    sheets = []
    for start in range(0, len(images), 16):
        selected = images[start:start+16]
        thumb_w, thumb_h, gap = 270, 382, 18
        sheet = Image.new("RGB", (4*thumb_w+5*gap, 4*(thumb_h+28)+5*gap), "#dce5ee")
        draw = ImageDraw.Draw(sheet)
        for offset, path in enumerate(selected):
            image = Image.open(path).convert("RGB")
            image.thumbnail((thumb_w,thumb_h))
            x = gap+(offset%4)*(thumb_w+gap)
            y = gap+(offset//4)*(thumb_h+28+gap)
            sheet.paste(image,(x+(thumb_w-image.width)//2,y))
            draw.text((x,y+thumb_h+4),f"{start+offset+1} | {name.replace('LangGraph_','')}",fill="#17324d")
        target = directory / f"contact-{start//16+1:02d}.png"
        sheet.save(target);sheets.append(str(target))
    docx = ROOT / "docs" / f"{name}.docx"
    with ZipFile(docx) as z:
        if z.testzip() is not None:raise ValueError(f"Invalid DOCX ZIP: {docx}")
        xml = z.read("word/document.xml").decode()
        media = [n for n in z.namelist() if n.startswith("word/media/")]
        unresolved = re.findall(r"&lt;!-- (?:EXAMPLE|SOLUTION|VIDEO|ORIGINAL|EXECUTION)_[^-]+--&gt;",xml)
        if unresolved:raise ValueError(f"Unresolved source marker: {name}")
    result = {"book":name,"pages":len(pages),"embedded_images":len(media),
              "docx_sha256":sha256(docx.read_bytes()).hexdigest(),
              "pdf_sha256":sha256(pdf.read_bytes()).hexdigest(),
              "overflow_candidates":overflow,"sparse_page_candidates":sparse,
              "body_word_counts":page_word_counts,"contact_sheets":sheets,
              "text_path":str(text_path),"pdf":str(pdf)}
    print(json.dumps({k:v for k,v in result.items() if k not in ('body_word_counts','contact_sheets') }),flush=True)
    return result


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only",nargs="*",choices=NAMES)
    args=parser.parse_args()
    with ThreadPoolExecutor(max_workers=3) as pool:
        reports=list(pool.map(inspect,args.only or NAMES))
    target=ROOT/"course/validation/document_layout.json"
    target.write_text(json.dumps(reports,indent=2))
    print('Layout report:',target,flush=True)


if __name__=="__main__":main()
