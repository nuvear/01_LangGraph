"""Export only Git-tracked course files; never include credentials or working data."""
from __future__ import annotations

import argparse
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import re
import shutil
import subprocess
from zipfile import ZipFile, ZIP_DEFLATED

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = {'.git', '.venv', '.work', '.manus', 'outputs', 'inputs', '__pycache__', '.pytest_cache'}
KEY_PATTERN = re.compile(rb'(?:sk-ant-|lsv2_pt_|gh[oaprsu]_)[A-Za-z0-9_-]{25,}')
BOOKS = ('LangGraph_Student_Handbook', 'LangGraph_Teacher_Handbook', 'LangGraph_Exercise_Workbook')
ARCHIVAL_FILES = {
    'docs/LangGraph_Training_Index.docx', 'course/training_index.md',
    'course/syllabus.md', 'course/video_source_map.md',
    'course/video_visual_review.md', 'course/handbook_production_notes.md',
    'tools/build_training_index.py', 'tools/extract_video_figures.py',
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'outputs/course-handbooks')
    parser.add_argument('--overwrite', action='store_true', help='Replace an earlier generated export.')
    parser.add_argument('--standalone', action='store_true', help='Omit historical planning and borrowed visual assets.')
    args = parser.parse_args()
    output = args.output_dir.resolve()
    names = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    files = [Path(name) for name in names if name]
    if args.standalone:
        files = [p for p in files if p.as_posix() not in ARCHIVAL_FILES
                 and not p.as_posix().startswith('assets/video/')
                 and not (p.as_posix().startswith('course/chapters/') and p.name == 'metadata.json')]
    secrets = [value.encode() for key, value in dotenv_values(ROOT / '.env').items()
               if value and len(value) >= 8 and re.search('API_KEY|TOKEN|PASSWORD|SECRET', key)]
    manifest = {}
    for relative in files:
        if relative.is_absolute() or '..' in relative.parts or any(part in FORBIDDEN for part in relative.parts):
            raise ValueError(f'Forbidden tracked export path: {relative}')
        if relative.name.startswith('.env') and relative.name not in ('.env.example', '.env.template'):
            raise ValueError('A private environment file is tracked; stop and repair Git staging.')
        source = ROOT / relative
        if source.is_symlink() or not source.is_file():
            raise ValueError(f'Export source is not an ordinary file: {relative}')
        content = source.read_bytes()
        blobs = [content]
        if source.suffix == '.docx':
            with ZipFile(BytesIO(content)) as document:
                assert document.testzip() is None
                blobs += [document.read(name) for name in document.namelist() if name.endswith('.xml')]
        if any(value in blob for value in secrets for blob in blobs) or any(KEY_PATTERN.search(blob) for blob in blobs):
            raise ValueError(f'Credential safety scan rejected {relative}; no value is printed.')
        manifest[relative.as_posix()] = {'bytes': len(content), 'sha256': sha256(content).hexdigest()}
    for book in BOOKS:
        assert Path('docs', book + '.docx') in files
    output.mkdir(parents=True, exist_ok=True)
    for relative in files:
        target = output / relative
        if target.exists() and not args.overwrite and sha256(target.read_bytes()).hexdigest() != manifest[relative.as_posix()]['sha256']:
            raise FileExistsError(f'Preserving changed export: {target}; use --overwrite only intentionally.')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, target)
    metadata = output / 'DELIVERY_MANIFEST.json'
    metadata.write_text(json.dumps({'files': manifest, 'credential_scan': 'passed',
                                   'private_environment_included': False,
                                   'standalone_edition': args.standalone}, indent=2))
    archive = output / 'LangGraph_Complete_Course.zip'
    with ZipFile(archive, 'w', compression=ZIP_DEFLATED, compresslevel=6) as bundle:
        for relative in files:
            bundle.write(output / relative, 'LangGraph_Course/' + relative.as_posix())
        bundle.write(metadata, 'LangGraph_Course/DELIVERY_MANIFEST.json')
    with ZipFile(archive) as bundle:
        assert bundle.testzip() is None
        assert not any(Path(name).name == '.env' for name in bundle.namelist())
    for book in BOOKS:
        target = output / 'docs' / (book + '.docx')
        with ZipFile(target) as document:
            assert document.testzip() is None
        print(target)
    print(archive)
    print(f'Export verified: {len(files)} files; archive {archive.stat().st_size / 1024**2:.1f} MiB; credentials excluded.')


if __name__ == '__main__':
    main()
