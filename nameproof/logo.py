"""Explicit, pinned text-only handoff to the user-selected logo skill."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from urllib.request import Request, build_opener
from .domain import NoRedirect

REVISION = 'bf4e9ac4d4428bda261afcfe981871ceb92d94e6'
BASE = f'https://raw.githubusercontent.com/op7418/logo-generator-skill/{REVISION}/'
MANIFEST = {
    'SKILL.md': ('UPSTREAM_SKILL.md', 'dc4dfeca98af6f4f6ceeb599187e2cfd9e77db128be7a9ac886a13094dbdbe5c'),
    'references/design_patterns.md': ('references/design_patterns.md', 'f45e34afd9dfa79aa1ec7ed3e40202516f8890ae1ea4d6ec1bfeaac331e919b5'),
    'references/background_styles.md': ('references/background_styles.md', '838779bb61df0a037e0d0fb8d3568a8976f4066ae7d9688f5f0c4354a57d780e'),
}

def fetch_text(url):
    request = Request(url, headers={'User-Agent': 'nameproof-kit/0.1'})
    with build_opener(NoRedirect).open(request, timeout=15) as response:
        data = response.read(100_001)
    if len(data) > 100_000:
        raise ValueError('upstream instruction exceeds size limit')
    data.decode('utf-8')
    return data

def retrieve_logo_source(output, fetch=False, getter=fetch_text):
    manifest = {'repository': 'https://github.com/op7418/logo-generator-skill', 'revision': REVISION,
                'status': 'not_fetched', 'files': {source: {'saved_as': dest, 'sha256': digest} for source, (dest, digest) in MANIFEST.items()},
                'limitation': 'Instructions only; no scripts, dependencies, provider calls or automatic skill installation. Upstream licensing remains separate.'}
    if not fetch:
        return manifest
    target = Path(output).absolute()
    if target.exists() or target.is_symlink():
        raise ValueError('output must be a new directory; existing files are never overwritten')
    if not target.parent.is_dir():
        raise ValueError('output parent directory must exist')
    temporary = Path(tempfile.mkdtemp(prefix='.nameproof-logo-', dir=target.parent))
    try:
        for source, (dest, digest) in MANIFEST.items():
            data = getter(BASE + source)
            if not isinstance(data, bytes) or hashlib.sha256(data).hexdigest() != digest:
                raise ValueError('upstream content hash mismatch: ' + source)
            data.decode('utf-8')
            path = temporary / dest
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        manifest['status'] = 'retrieved_hash_verified_instructions_only'
        (temporary / 'provenance.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        # Refuse a target created concurrently. mkdir is atomic; populate only our new directory.
        target.mkdir()
        for entry in temporary.iterdir():
            shutil.move(str(entry), str(target / entry.name))
        temporary.rmdir()
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return {**manifest, 'output_directory': str(target)}
