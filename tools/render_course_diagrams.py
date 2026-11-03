"""Render editable Mermaid source into handbook PNG figures.

Authoring-only prerequisites: Node, Google Chrome, and Mermaid CLI installed under
.work/tools/diagrams. Students receive PNGs and do not need these tools.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="*")
    parser.add_argument("--overview", action="store_true")
    parser.add_argument("--chrome", default="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    args = parser.parse_args()
    renderer = ROOT / ".work/tools/diagrams/node_modules/.bin/mmdc"
    if not renderer.is_file():
        raise SystemExit("Install @mermaid-js/mermaid-cli under .work/tools/diagrams first.")
    config = ROOT / ".work/handbooks/mermaid-theme.json"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text(json.dumps({"theme": "base", "themeVariables": {
        "fontFamily": "Arial", "fontSize": "20px", "primaryColor": "#e7f3f5",
        "primaryTextColor": "#17324d", "primaryBorderColor": "#087f8c",
        "lineColor": "#536477", "secondaryColor": "#edf2f7", "tertiaryColor": "#faf4df"
    }, "flowchart": {"htmlLabels": False, "curve": "linear"}}))
    puppet = ROOT / ".work/handbooks/puppeteer.json"
    if not Path(args.chrome).is_file():
        raise SystemExit("Supply the Chrome executable with --chrome /path/to/chrome.")
    puppet.write_text(json.dumps({"executablePath": args.chrome, "args": ["--no-sandbox"]}))
    folder = ROOT / "assets/diagrams"
    if args.overview:
        folder = folder / "overviews"
    files = sorted(folder.glob("*.mmd"))
    if args.only:
        files = [p for p in files if p.stem.upper() in args.only]
    def render(source: Path):
        output = source.with_suffix(".png")
        result = subprocess.run([str(renderer), "-i", str(source), "-o", str(output),
                                 "-p", str(puppet), "-c", str(config), "-b", "white",
                                 "--size", "1600", "-s", "1.5"], capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(f"{source.name}: {result.stderr[-2500:]}")
        return output
    with ThreadPoolExecutor(max_workers=3) as pool:
        for output in pool.map(render, files):
            print(output, flush=True)


if __name__ == "__main__":
    main()
