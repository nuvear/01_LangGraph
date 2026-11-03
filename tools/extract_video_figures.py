"""Extract short, attributed source-video stills; full media is not redistributed.

Run with a legally accessible local copy of the source video:
    python tools/extract_video_figures.py --source .work/video/source-illustrations.mp4
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FIGURES = {
    "L01": (760, "The source explanation of conditional edges"),
    "L02": (1950, "The original personalized-compliment exercise"),
    "L03": (2635, "The original one-node arithmetic exercise"),
    "L04": (3280, "The original three-node profile exercise"),
    "L05": (4405, "The original two-section conditional exercise"),
    "L06": (5370, "The original automatic higher/lower exercise"),
    "L07": (5515, "The original simple-bot objectives"),
    "L08": (6210, "The original conversation-memory objectives"),
    "L09": (7460, "The original agent–tool loop diagram"),
    "L10": (8985, "The source human–AI drafting requirements"),
    "L11": (10358, "The original model/retriever loop diagram"),
}


def extract(source: Path) -> None:
    target = ROOT / "assets" / "video"
    target.mkdir(parents=True, exist_ok=True)
    def one(item):
        lesson, (seconds, description) = item
        output = target / f"{lesson.lower()}.png"
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-threads", "1",
            "-ss", str(seconds), "-i", str(source), "-frames:v", "1",
            "-vf", "scale='min(1600,iw)':-2", str(output),
        ], check=True)
        timestamp = f"{seconds // 3600:02d}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}"
        note = ""
        if lesson in ("L07", "L08"):
            note = " Historical provider names are shown in the source; adapted executable examples use Anthropic only."
        return {"lesson": lesson, "file": f"assets/video/{output.name}",
                "seconds": seconds, "timestamp": timestamp, "description": description,
                "source_url": f"https://youtu.be/jGg_1h0qzaM?t={seconds}",
                "credit": "Vaibhav Mehra / freeCodeCamp, LangGraph Complete Course for Beginners", "note": note}
    with ThreadPoolExecutor(max_workers=3) as pool:
        records = list(pool.map(one, FIGURES.items()))
    (target / "attribution.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"Extracted {len(records)} attributed source stills to {target}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    if not args.source.is_file():
        parser.error("Supply an existing local source-video file.")
    extract(args.source.resolve())
