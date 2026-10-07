"""Offline, provenance-preserving preliminary trademark evidence screening.

No network access, legal clearance, trademark-status interpretation or completeness
claim. Similarity is a triage heuristic; phonetic, semantic and script-aware review
remain manual. Importing a source URL does not authenticate the evidence.
"""
from copy import deepcopy
from datetime import datetime, timezone
from difflib import SequenceMatcher
import json
from pathlib import Path
import unicodedata
from urllib.parse import urlsplit

_REQUIRED = {'mark', 'jurisdiction', 'classes', 'source_url', 'observed_at',
             'record_id', 'status'}
DISCLAIMER = ('Preliminary evidence screening only, not legal clearance. Imported '
              'records are incomplete and unverified. No match does not establish '
              'availability, registrability or freedom to use a name.')


def catalog():
    """Return a fresh official-source catalog, not live search results."""
    return json.loads(Path(__file__).with_name('jurisdictions.json').read_text(encoding='utf-8'))


def _country(value, available):
    if not isinstance(value, str):
        raise ValueError('Jurisdiction must be a supported ISO code or EU')
    value = value.strip().upper()
    value = 'GB' if value == 'UK' else value
    if value not in available:
        raise ValueError('Unsupported jurisdiction: ' + value)
    return value


def _classes(values):
    if not isinstance(values, (list, tuple)) or not values:
        raise ValueError('Provide one or more Nice classes as an integer list')
    if any(type(v) is not int or not 1 <= v <= 45 for v in values):
        raise ValueError('Nice classes must be integers from 1 through 45')
    return sorted(set(values))


def normalize_mark(mark):
    """NFKC + casefold, keeping Unicode letters/numbers and combining marks."""
    if not isinstance(mark, str) or not mark.strip() or len(mark) > 500:
        raise ValueError('Mark must be a nonempty string of at most 500 characters')
    value = ''.join(c for c in unicodedata.normalize('NFKC', mark).casefold()
                    if unicodedata.category(c)[0] in {'L', 'N', 'M'})
    if not any(c.isalnum() for c in value):
        raise ValueError('Mark must include letters or numbers')
    return value


def _record(record, available):
    if not isinstance(record, dict) or set(record) != _REQUIRED:
        raise ValueError('Each record must contain exactly: ' + ', '.join(sorted(_REQUIRED)))
    result = deepcopy(record)
    normalize_mark(result['mark'])
    result['jurisdiction'] = _country(result['jurisdiction'], available)
    result['classes'] = _classes(result['classes'])
    for field in ('source_url', 'observed_at', 'record_id', 'status'):
        if not isinstance(result[field], str) or not result[field].strip():
            raise ValueError(field + ' must be a nonempty string')
    if any(c.isspace() for c in result['source_url']):
        raise ValueError('source_url must not contain whitespace')
    try:
        url = urlsplit(result['source_url'])
        valid_url = (url.scheme == 'https' and url.hostname and not url.username
                     and not url.password and url.port in (None, 443))
    except ValueError:
        valid_url = False
    if not valid_url:
        raise ValueError('source_url must be an HTTPS evidence URL without credentials')
    try:
        date = datetime.fromisoformat(result['observed_at'].replace('Z', '+00:00'))
        if date.tzinfo is None or date.utcoffset() is None:
            raise ValueError()
        if date > datetime.now(timezone.utc):
            raise ValueError()
    except ValueError:
        raise ValueError('observed_at must be a timezone-aware ISO timestamp, not in the future') from None
    return result


def screening(name, countries, classes, records=None):
    """Compare a name against optional user-supplied records, never live registers.

    Status is unreviewed without relevant records, no-match-in-imported-records
    with relevant records but no heuristic hit, or matches-requiring-review.
    EU records also apply when screening DE. DE records are relevant to EU-wide
    plans, with a national-territory warning, not an inferred EU registration.
    """
    normalized = normalize_mark(name)
    sources = catalog()
    if not isinstance(countries, (list, tuple)) or not countries:
        raise ValueError('Provide one or more jurisdictions as a list')
    selected = list(dict.fromkeys(_country(c, sources) for c in countries))
    wanted_classes = _classes(classes)
    if records is not None and not isinstance(records, (list, tuple)):
        raise ValueError('records must be a list of evidence records or None')
    evidence = [_record(r, sources) for r in (records or [])]
    ids = [(r['jurisdiction'], r['record_id']) for r in evidence]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate record_id in the same jurisdiction; reconcile evidence first')
    results = []
    for code in selected:
        relevant = [r for r in evidence if r['jurisdiction'] == code or
                    {r['jurisdiction'], code} == {'EU', 'DE'}]
        matches = []
        for record in relevant:
            other = normalize_mark(record['mark'])
            score = SequenceMatcher(None, normalized, other, autojunk=False).ratio()
            if normalized == other or score >= 0.8:
                overlap = sorted(set(wanted_classes) & set(record['classes']))
                hit = dict(record)
                hit.update(match_type='normalized-exact' if normalized == other else 'fuzzy',
                           similarity=round(score, 4), class_overlap=overlap,
                           class_relation='overlap' if overlap else 'different-classes-review-required',
                           evidence_verified=False)
                matches.append(hit)
        warnings = [DISCLAIMER,
                    'Exact/fuzzy text matching misses phonetic, conceptual, transliteration and visual conflicts.',
                    'Different Nice classes and inactive record statuses do not automatically eliminate risk.',
                    'Business-name, common-law, geographic and other rights require separate review.']
        if code == 'EU':
            warnings.append('EU-wide plans require relevant national-rights review. Only DE national records are mapped from this limited catalog; other EU member states remain unreviewed.')
        if any(r['jurisdiction'] != code for r in relevant):
            warnings.append('Cross-territory evidence included: EU rights may apply in DE; DE national rights matter to EU plans but are not EU-wide registrations.')
        results.append(dict(jurisdiction=code,
                            status='matches-requiring-review' if matches else
                            ('no-match-in-imported-records' if relevant else 'unreviewed'),
                            records_reviewed=len(relevant), matches=matches,
                            coverage='imported-records-only' if relevant else 'not-searched',
                            search_plan=deepcopy(sources[code]), warnings=warnings))
    return dict(name=name, countries=selected, classes=wanted_classes,
                jurisdictions=results, disclaimer=DISCLAIMER,
                live_search_performed=False, legal_clearance=False)
