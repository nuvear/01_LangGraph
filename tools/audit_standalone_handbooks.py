"""Verify the standalone handbook editions without contacting external services."""
from __future__ import annotations
import argparse
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from xml.etree import ElementTree as ET
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
BOOKS = ('LangGraph_Student_Handbook', 'LangGraph_Teacher_Handbook', 'LangGraph_Exercise_Workbook')
PATTERN = re.compile(r'youtube|youtu\.be|vaibhav|freecodecamp|jGg_1h0qzaM|\bvideo\b|video[- ]aligned|source[- ]viewing', re.I)
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

class VisibleHTML(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []
    def handle_data(self, data):
        self.parts.append(data)
    def handle_starttag(self, tag, attrs):
        self.parts.extend(value for key, value in attrs
                          if value and key in ('href', 'alt', 'title', 'src')
                          and not value.startswith('data:'))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=ROOT / 'docs')
    args = parser.parse_args()
    old_art = {sha256(p.read_bytes()).hexdigest() for p in (ROOT / 'assets/video').glob('*.png')}
    concepts = {sha256(p.read_bytes()).hexdigest() for p in (ROOT / 'assets/diagrams').glob('*-concept.png')}
    evidence = json.loads((ROOT / 'course/validation/execution_manifest.json').read_text())['records']
    shots = {sha256((ROOT / r['screenshot']).read_bytes()).hexdigest() for r in evidence}
    expected = ['P00'] + [f'L{i:02}' for i in range(1, 12)] + ['U1', 'U2', 'S1', 'S2', 'C01']
    results = []
    assert len(concepts) == 11 and len(shots) == 34
    for name in BOOKS:
        path = args.directory / (name + '.docx')
        with ZipFile(path) as z:
            assert z.testzip() is None
            xml_parts = [z.read(n).decode() for n in z.namelist() if n.endswith(('.xml', '.rels'))]
            assert not any(PATTERN.search(s) for s in xml_parts), f'Prohibited reference in {name}'
            images = {sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('word/media/')}
            assert not old_art.intersection(images), f'Old artwork still embedded in {name}'
            if 'Workbook' not in name:
                assert concepts <= images and shots <= images, f'Missing current figure in {name}'
            doc = ET.fromstring(z.read('word/document.xml'))
            headings = []
            for p in doc.findall('.//w:p', NS):
                style = p.find('w:pPr/w:pStyle', NS)
                text = ''.join(t.text or '' for t in p.findall('.//w:t', NS))
                if style is not None and style.get('{'+NS['w']+'}val') == 'Heading1':
                    m = re.match(r'^(P00|L\d\d|U[12]|S[12]|C01)\s+—', text)
                    if m: headings.append(m.group(1))
            assert headings == expected, f'Lesson sequence changed in {name}'
            assert not doc.findall('.//w:ins', NS) and not doc.findall('.//w:del', NS)
        markdown = (args.directory / (name + '.md')).read_text()
        assert not PATTERN.search(markdown), f'Prohibited Markdown reference in {name}'
        visible = VisibleHTML(); visible.feed((args.directory / (name + '.html')).read_text())
        assert not PATTERN.search('\n'.join(visible.parts)), f'Prohibited HTML reference in {name}'
        results.append({'book': name, 'docx_sha256': sha256(path.read_bytes()).hexdigest(),
                        'prohibited_reference_matches': 0, 'old_artwork_matches': 0,
                        'embedded_images': len(images), 'lesson_count': len(headings),
                        'original_concepts_verified': 0 if 'Workbook' in name else 11,
                        'execution_screenshots_verified': 0 if 'Workbook' in name else 34,
                        'status': 'passed'})
    target = ROOT / 'course/validation/standalone_handbooks.json'
    target.write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    main()
