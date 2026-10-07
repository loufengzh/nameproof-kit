import json
from pathlib import Path

def no_duplicates(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError('duplicate JSON key: ' + key)
        out[key] = value
    return out

def load_json(path):
    with Path(path).open('rb') as handle:
        data = handle.read(2_000_001)
    if len(data) > 2_000_000:
        raise ValueError('input exceeds 2 MB')
    return json.loads(data, object_pairs_hook=no_duplicates, parse_constant=lambda x: (_ for _ in ()).throw(ValueError('non-finite JSON number')))
