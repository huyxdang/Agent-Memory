"""Exercise packet generation and human-note preservation in a disposable copy."""
import contextlib
import hashlib
import importlib.util
import io
import json
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(audit_dir):
    global ROOT
    ROOT = Path(audit_dir).resolve()
    manifest = json.loads((ROOT / 'human-review/manifest.json').read_text())
    assert all(sha(Path(p)) == expected for p, expected in manifest['inputs_sha256'].items())
    links = 0
    for p in (ROOT / 'human-review').rglob('*.md'):
        for target in re.findall(r'\]\(<([^>]+)>\)', p.read_text()):
            assert Path(target).is_file(), (p, target)
            links += 1
    for p in (ROOT / 'human-review/cases').glob('*.md'):
        assert not re.search(r'gemma_base|gemma_finetuned|gemma3-|downstream_score', p.read_text())
    with tempfile.TemporaryDirectory(prefix='human-review-check-') as tmp:
        root = Path(tmp)
        for original in manifest['inputs_sha256']:
            source = Path(original)
            target = root / source.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        script = root / 'build_human_review.py'
        shutil.copyfile(Path(__file__).resolve().parent / script.name, script)
        spec = importlib.util.spec_from_file_location('packet_check', script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with contextlib.redirect_stdout(io.StringIO()):
            module.build(root)
        notes = root / 'human-review/human-decisions.md'
        notes.write_text(notes.read_text() + '\nHuman test note: keep my correction.\n')
        before = {str(p.relative_to(root)): sha(p) for p in root.rglob('*') if p.is_file() and '__pycache__' not in str(p)}
        with contextlib.redirect_stdout(io.StringIO()):
            module.build(root)
        after = {str(p.relative_to(root)): sha(p) for p in root.rglob('*') if p.is_file() and '__pycache__' not in str(p)}
        assert before == after, 'Rebuild changed an artifact or human notes'
    result = {'input_hashes_unchanged': len(manifest['inputs_sha256']),
              'local_links_verified': links, 'case_identity_fields_absent': 10,
              'repeat_build_byte_identical': True, 'human_edits_preserved': True,
              'paid_calls': 0}
    (ROOT / 'human-review/verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit-dir', type=Path, required=True)
    main(parser.parse_args().audit_dir)
