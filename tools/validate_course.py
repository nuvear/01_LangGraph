"""Execute course demos/solutions, capture genuine stdout, and screenshot it.

This is a finite validation job, not an unattended service. Live cases consume
Anthropic credit and selected tracing backends receive synthetic classroom data.
The screenshots explicitly identify themselves as browser-rendered actual output.

Run: python tools/validate_course.py --live --screenshots
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import html
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from uuid import uuid4

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def screenshot(html_path: Path, png_path: Path) -> None:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        options = {"headless": True}
        if Path(CHROME).is_file():
            options["executable_path"] = CHROME
        browser = p.chromium.launch(**options)
        page = browser.new_page(viewport={"width": 1120, "height": 1000}, device_scale_factor=1.5)
        page.goto(html_path.as_uri())
        page.locator("main").screenshot(path=str(png_path))
        browser.close()


def evidence_html(record: dict, stdout: str, stderr: str) -> str:
    # Display real captured output, never reconstructed model answers.
    output = stdout.strip() or "(No stdout; inspect stderr in the complete log.)"
    if stderr.strip():
        output += "\n\nSTDERR\n" + stderr.strip()
    return f'''<!doctype html><html lang="en"><meta charset="utf-8">
<title>{record['id']} actual execution</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#e8eef4;font-family:Arial,sans-serif;color:#16324f}}
main{{width:1120px;padding:26px;background:#f8fafc}}
.eyebrow{{font-size:15px;letter-spacing:1px;font-weight:bold;color:#087f8c}}
h1{{font-size:30px;margin:12px 0}}.meta{{font-size:16px;margin:8px 0;line-height:1.5}}
.status{{display:inline-block;padding:5px 12px;border-radius:5px;background:#d5f3e5;font-weight:bold}}
code{{font-family:Consolas,monospace;font-size:17px;overflow-wrap:anywhere}}
pre{{font-family:Consolas,monospace;font-size:20px;line-height:1.3;background:#112338;color:#ecf5ff;padding:20px;border-radius:8px;max-height:650px;overflow:auto;white-space:pre-wrap;overflow-wrap:anywhere}}
.note{{font-size:15px;color:#475569;line-height:1.4}}
</style><main><div class="eyebrow">LANGGRAPH COURSE · ACTUAL EXECUTION EVIDENCE</div>
<h1>{html.escape(record['id'])} — {html.escape(record['role'])}</h1>
<div class="meta"><span class="status">Exit {record['exit_code']} · {html.escape(record['status'].upper())}</span>
 &nbsp; {record['duration_seconds']:.2f}s · {'Real Anthropic API enabled' if record['live'] else 'Deterministic Python / offline'}</div>
<div class="meta"><code>{html.escape(record['command'])}</code><br>Captured: {html.escape(record['completed_at_utc'])}</div>
<pre>{html.escape(output)}</pre><p class="note">Genuine browser screenshot of stdout/stderr captured from the command above, not a simulated terminal or invented response. The viewport may require scrolling; the complete text log is stored beside this image. Source SHA-256: {record['source_sha256'][:20]}…</p></main></html>'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--screenshots", action="store_true")
    parser.add_argument("--only", nargs="*")
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()
    manifest = json.loads((ROOT / "course/lesson_manifest.json").read_text())
    selected = [m for m in manifest if not args.only or m["id"] in args.only]
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:6]
    working = ROOT / ".work/course-validation" / run_id
    working.mkdir(parents=True, exist_ok=True)
    evidence = ROOT / "assets/execution"
    evidence.mkdir(parents=True, exist_ok=True)
    report_path = ROOT / "course/validation/execution_manifest.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    previous = json.loads(report_path.read_text()) if report_path.exists() else {"records": []}
    records = previous.get("records", [])
    config = dotenv_values(ROOT / ".env")
    secrets = [v for k, v in config.items() if v and any(s in k.upper() for s in ("KEY", "TOKEN", "SECRET", "PASSWORD"))]
    failed = False
    for module in selected:
        ident, name = module["id"], module["id"].lower()
        for role, package in (("demonstration", "course_lessons"), ("exercise-solution", "exercises.solutions")):
            if module["live"] and not args.live:
                print(f"SKIPPED {ident} {role}: --live not enabled", flush=True)
                failed = True
                continue
            source = ROOT / (package.replace(".", "/")) / f"{name}.py"
            directory = working / ident / role
            directory.mkdir(parents=True, exist_ok=True)
            command = [sys.executable, "-m", f"{package}.{name}", "--output-dir", str(directory / "artifacts")]
            if module["live"]:
                command.append("--live")
            backend = {"S1": "langsmith", "S2": "langwatch", "C01": "both"}.get(ident, "none")
            command += ["--backend", backend]
            print(f"RUN {ident} {role} (live={module['live']}, backend={backend})", flush=True)
            start = time.monotonic()
            environment = {**os.environ, "PYTHONHASHSEED": "0", "TOKENIZERS_PARALLELISM": "false"}
            try:
                completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                                           timeout=args.timeout, env=environment)
                stdout, stderr, code = completed.stdout, completed.stderr, completed.returncode
            except subprocess.TimeoutExpired as error:
                stdout = (error.stdout or b"").decode(errors="replace") if isinstance(error.stdout, bytes) else (error.stdout or "")
                stderr = "Validation process exceeded the configured timeout."
                code = 124
            if any(secret in stdout or secret in stderr for secret in secrets):
                stdout, stderr, code = "OUTPUT WITHHELD: credential value detected.", "Credential-safety gate blocked publication.", 125
            record = {"id": ident, "role": role, "live": module["live"], "backend": backend,
                      "command": " ".join(["python", *command[1:3], *command[3:]]).replace(str(directory / "artifacts"), f"<run-output>/{ident}/{role}"),
                      "run_id": run_id, "completed_at_utc": now(),
                      "duration_seconds": round(time.monotonic() - start, 2),
                      "exit_code": code, "status": "passed" if code == 0 else "failed",
                      "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                      "stdout_sha256": hashlib.sha256(stdout.encode()).hexdigest(),
                      "log": f"assets/execution/{name}-{role}.txt",
                      "screenshot": f"assets/execution/{name}-{role}.png" if args.screenshots and code == 0 else None}
            full_log = f"Command: {record['command']}\nUTC: {record['completed_at_utc']}\nExit: {code}\n\nSTDOUT\n{stdout}\nSTDERR\n{stderr}"
            (evidence / f"{name}-{role}.txt").write_text(full_log)
            page = directory / "execution.html"
            page.write_text(evidence_html(record, stdout, stderr))
            if args.screenshots and code == 0:
                screenshot(page, evidence / f"{name}-{role}.png")
            records = [r for r in records if (r["id"], r["role"]) != (ident, role)] + [record]
            report = {"generated_at_utc": now(), "platform": sys.platform,
                      "python": sys.version.split()[0], "screenshots_are_actual_captured_output": True,
                      "windows_executed": False, "records": records}
            report_path.write_text(json.dumps(report, indent=2))
            print(f"{record['status'].upper()} {ident} {role}: exit {code}, {record['duration_seconds']}s", flush=True)
            if code:
                print(stderr[-2500:] or stdout[-2500:], flush=True)
                failed = True
    starters = []
    for module in selected:
        command = [sys.executable, "-m", f"exercises.starters.{module['id'].lower()}"]
        try:
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=30)
            ok = result.returncode == 0 and "STARTER_NOT_COMPLETED" in result.stdout
            starters.append({"id": module["id"], "status": "passed" if ok else "failed", "exit_code": result.returncode})
            if not ok:
                print(f"Starter contract FAILED: {module['id']}", flush=True)
                failed = True
        except subprocess.TimeoutExpired:
            starters.append({"id": module["id"], "status": "failed", "exit_code": 124})
            failed = True
    starter_path = ROOT / "course/validation/starter_checks.json"
    previous_starters = json.loads(starter_path.read_text()) if starter_path.exists() else []
    chosen_ids = {s["id"] for s in starters}
    starter_path.write_text(json.dumps([s for s in previous_starters if s["id"] not in chosen_ids] + starters, indent=2))
    print("Validation report:", report_path, flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
