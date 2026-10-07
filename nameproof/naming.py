"""Transparent candidate ideation/ranking; host-agent candidates are first class."""
import re
import unicodedata

STOP = set('a an the and for with of to in that tool app helps users create build make ai platform software'.split())
THEMES = {
    'writing': ({'write', 'writing', 'editor', 'note', 'notes', 'document', 'text'}, ['Quill', 'Folio', 'Verse', 'Ink'], ['Pad', 'Nest', 'Flow', 'Bloom']),
    'developer': ({'code', 'coding', 'developer', 'test', 'deploy', 'debug', 'api'}, ['Forge', 'Patch', 'Stack', 'Trace'], ['Kit', 'Lens', 'Pilot', 'Nest']),
    'design': ({'design', 'logo', 'brand', 'image', 'visual', 'creative'}, ['Hue', 'Mark', 'Form', 'Glyph'], ['Loom', 'Nest', 'Bloom', 'Canvas']),
    'research': ({'research', 'search', 'find', 'discover', 'knowledge'}, ['Scout', 'Quest', 'Signal', 'Atlas'], ['Lens', 'Trail', 'Nest', 'Scope']),
    'workflow': ({'task', 'workflow', 'automate', 'automation', 'agent', 'schedule'}, ['Orbit', 'Relay', 'Thread', 'Pulse'], ['Flow', 'Desk', 'Weave', 'Loop']),
}

def norm(value):
    return ''.join(x for x in unicodedata.normalize('NFKD', value).casefold() if not unicodedata.combining(x))

def validate_brief(brief):
    if not isinstance(brief, dict) or not isinstance(brief.get('idea'), str) or not brief['idea'].strip():
        raise ValueError('brief requires a nonempty idea string')
    if len(brief['idea']) > 10000:
        raise ValueError('idea is too long')
    result = dict(brief)
    for key, default in [('keywords', []), ('avoid', []), ('countries', ['US']), ('nice_classes', [9, 42]), ('tlds', ['com'])]:
        value = result.setdefault(key, default)
        if not isinstance(value, list) or len(value) > 50:
            raise ValueError(key + ' must be a list of at most 50 items')
        if key != 'nice_classes' and any(not isinstance(x, str) or not x.strip() for x in value):
            raise ValueError(key + ' requires nonempty strings')
    maximum = result.setdefault('max_length', 14)
    if type(maximum) is not int or not 4 <= maximum <= 40:
        raise ValueError('max_length must be 4..40')
    for key in ('audience', 'tone'):
        if key in result and not isinstance(result[key], str):
            raise ValueError(key + ' must be text')
    for tld in result['tlds']:
        if not re.fullmatch(r'[a-zA-Z]{2,24}(?:\.[a-zA-Z]{2,24})?', tld):
            raise ValueError('tlds must be suffixes such as com or co.uk')
    from .trademark import screening
    validated = screening('BriefValidation', result['countries'], result['nice_classes'])
    result['countries'] = validated['countries']
    result['nice_classes'] = validated['classes']
    return result

def propose(brief, candidates=None, limit=12):
    brief = validate_brief(brief)
    if type(limit) is not int or not 1 <= limit <= 50:
        raise ValueError('limit must be 1..50')
    words = set(re.findall(r'[a-z]+', norm(brief['idea'] + ' ' + ' '.join(brief['keywords'])))) - STOP
    matched = [(k, v) for k, v in THEMES.items() if v[0] & words]
    if not matched:
        matched = [('general', (set(), ['Clear', 'Bright', 'Open', 'Kind'], ['Path', 'Nest', 'Loom', 'Trail']))]
    generated = []
    for theme, (_, roots, suffixes) in matched:
        for i, root in enumerate(roots):
            for j, suffix in enumerate(suffixes):
                if root.casefold() != suffix.casefold():
                    generated.append({'name': root + suffix, 'rationale': f'{root} + {suffix}: a {theme} metaphor; validate meaning with target speakers.', 'origin': 'offline_heuristic', 'theme': theme})
    for keyword in sorted(words):
        if 3 <= len(keyword) <= 7 and keyword.isascii():
            generated.append({'name': keyword.title() + 'Loom', 'rationale': f'Uses the brief term {keyword}; descriptive and potentially less distinctive.', 'origin': 'offline_heuristic', 'theme': 'brief_keyword'})
    if candidates is not None:
        if not isinstance(candidates, list) or not 1 <= len(candidates) <= 200:
            raise ValueError('candidates must be 1..200 objects')
        generated = []
        for candidate in candidates:
            if not isinstance(candidate, dict) or not isinstance(candidate.get('name'), str) or not isinstance(candidate.get('rationale'), str):
                raise ValueError('candidate requires name and rationale strings')
            generated.append({'name': candidate['name'], 'rationale': candidate['rationale'], 'origin': 'host_agent_or_user', 'theme': 'provided'})
    seen, ranked = set(), []
    for candidate in generated:
        name = candidate['name'].strip()
        if not name or len(name) > 80 or any(unicodedata.category(c).startswith('C') for c in name):
            raise ValueError('invalid candidate name')
        if len(name) > brief['max_length']:
            continue
        key = norm(name)
        if key in seen or any(norm(x) in key for x in brief['avoid']):
            continue
        seen.add(key)
        length = len(name)
        # Scores describe spelling ergonomics only, never IP safety or market success.
        components = {'length': max(0, 35 - max(0, length - 8) * 4), 'simple_spelling': 25 if name.isascii() and name.isalpha() else 10,
                      'vowel_balance': 20 if .2 <= sum(x in 'aeiou' for x in key) / max(1, len(key)) <= .6 else 5,
                      'within_requested_length': 20 if length <= brief['max_length'] else 0}
        candidate.update(name=name, spelling_score=sum(components.values()), score_components=components,
                         screening_status='not_checked', domain_labels=[unicodedata.normalize('NFC', name).lower().replace(' ', '') + '.' + tld.lower() for tld in brief['tlds']],
                         limitations=['Spelling score is not semantic fit, distinctiveness, trademark clearance or availability.'])
        ranked.append(candidate)
    ranked.sort(key=lambda x: (-x['spelling_score'], x['name'].casefold()))
    return {'idea': brief['idea'], 'method': 'host_candidates_ranked' if candidates is not None else 'offline_heuristic_ideation',
            'candidates': ranked[:limit], 'next_step': 'Have the host agent critique semantic fit, pronunciation, cultural meanings and competing brands; then screen finalists.',
            'assumptions': {'countries': brief['countries'], 'nice_classes': brief['nice_classes'], 'tlds': brief['tlds']}}

def logo_brief(name, brief):
    brief = validate_brief(brief)
    if not isinstance(name, str) or not name.strip() or len(name) > 80:
        raise ValueError('name must be 1..80 characters')
    return {'name': name, 'idea': brief['idea'], 'audience': brief.get('audience', 'not specified'), 'tone': brief.get('tone', 'not specified'),
            'status': 'brief_only_no_image_generated', 'upstream': 'https://github.com/op7418/logo-generator-skill/tree/bf4e9ac4d4428bda261afcfe981871ceb92d94e6',
            'prompt': f"Create three original logo directions for {name}. Product: {brief['idea']}. Explore silhouette, typography and a monochrome variant. Do not imitate existing marks. Ask the user to select a direction before final rendering.",
            'approval_required_before': ['sending private inputs to an external image service', 'paid generation or API calls', 'executing unreviewed third-party scripts'],
            'review': ['small-size legibility', 'monochrome contrast', 'actual word spelling', 'visual trademark similarity', 'license and provenance']}
