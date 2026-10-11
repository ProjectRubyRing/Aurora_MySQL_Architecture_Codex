"""Package authored deliverables and evidence, preserving relative documentation links."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'deliverables' / 'Aurora_GlobalDatabase_Design_Assessment_2026-10-11_bundle.zip'
ALLOWED = {'.md', '.xlsx', '.py', '.json', '.java', '.sql', '.cli', '.png'}


def main():
    verification = json.loads((ROOT / 'validation' / 'validation_report.json').read_text(encoding='utf-8'))
    if verification['result'] != 'PASS':
        raise RuntimeError('Do not package a workbook with failing artifact checks.')
    files = [ROOT / 'README.md']
    for folder in ['deliverables', 'evidence', 'examples', 'scripts', 'validation']:
        files.extend(p for p in (ROOT / folder).rglob('*') if p.is_file() and p.suffix in ALLOWED
                     and '__pycache__' not in p.parts and 'classes' not in p.parts)
    files = sorted(set(files), key=lambda p: str(p.relative_to(ROOT)))
    manifest = {'created_at_utc': datetime.now(timezone.utc).isoformat(), 'files': []}
    with zipfile.ZipFile(OUT, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            data = path.read_bytes()
            relative = path.relative_to(ROOT).as_posix()
            manifest['files'].append({'file': relative, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
            archive.writestr(relative, data)
        archive.writestr('MANIFEST.json', json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    with zipfile.ZipFile(OUT) as archive:
        if archive.testzip() is not None:
            raise RuntimeError('ZIP integrity failure')
        for item in manifest['files']:
            if hashlib.sha256(archive.read(item['file'])).hexdigest() != item['sha256']:
                raise RuntimeError(f'Archive content mismatch: {item["file"]}')
    print(json.dumps({'result': 'PASS', 'file': str(OUT), 'entries': len(files)+1,
                      'bytes': OUT.stat().st_size, 'sha256': hashlib.sha256(OUT.read_bytes()).hexdigest()}, ensure_ascii=True))


if __name__ == '__main__':
    main()
