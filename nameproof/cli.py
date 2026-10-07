import argparse
import json
import sys
from .domain import check_domain, apply_registrar_receipt
from .io import load_json
from .naming import propose, logo_brief, validate_brief
from .trademark import screening


def report(brief, candidates=None, records=None, live=False, limit=5):
    brief = validate_brief(brief)
    result = propose(brief, candidates, limit)
    for candidate in result['candidates']:
        candidate['trademark_screen'] = screening(candidate['name'], brief['countries'], brief['nice_classes'], records)
        candidate['domains'] = []
        for domain in candidate['domain_labels']:
            try:
                candidate['domains'].append(check_domain(domain, live))
            except ValueError as exc:
                candidate['domains'].append({'domain': domain, 'registration_status': 'unknown', 'purchase_status': 'unknown', 'reason': str(exc)})
    result['limitation'] = 'Preliminary evidence workbook. No name is legally cleared. RDAP absence never means purchasable. Live requests reveal queried domains to public services.'
    return result


def markdown(result):
    lines = ['# Nameproof shortlist', '', result['idea'], '', result.get('limitation', ''), '']
    for item in result['candidates']:
        lines.extend(['## ' + item['name'].replace('\n', ' '), '', item['rationale'], '', f"Spelling ergonomics: {item['spelling_score']}/100; semantic fit needs human/agent review."])
        for domain in item.get('domains', []):
            lines.append(f"- {domain['domain']}: registration={domain['registration_status']}; purchase={domain['purchase_status']}; reason={domain['reason']}")
            lines.append(f"  Source: {domain.get('source_url') or 'not queried'}; observed: {domain.get('observed_at') or 'not checked'}")
        for jurisdiction in item.get('trademark_screen', {}).get('jurisdictions', []):
            lines.append(f"- {jurisdiction['jurisdiction']}: {jurisdiction['status']}; coverage: {jurisdiction['coverage']}")
            for hit in jurisdiction['matches']:
                lines.append(f"  Match: {hit['mark']} ({hit['match_type']}, source status: {hit['status']}, classes: {hit['classes']}, {hit['class_relation']}); {hit['source_url']}; observed {hit['observed_at']}; imported/unverified.")
            plan = jurisdiction['search_plan']
            for source in plan.get('trademark_sources', []) + plan.get('business_sources', []):
                lines.append(f"  Next check: {source['label']} — {source['url']} ({source['access']}; not performed by this report)")
            for warning in jurisdiction['warnings']:
                lines.append('  Limitation: ' + warning)
        lines.append('')
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Brand ideation with explicitly limited evidence, not legal clearance.')
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ['propose', 'report', 'logo-brief']:
        p = sub.add_parser(name)
        p.add_argument('--brief', required=True)
        if name in {'propose', 'report'}:
            p.add_argument('--candidates')
            p.add_argument('--limit', type=int, default=5)
        if name == 'report':
            p.add_argument('--records')
            p.add_argument('--live', action='store_true', help='Query public IANA/RDAP services; reveals domain names')
            p.add_argument('--format', choices=['json', 'markdown'], default='json')
        if name == 'logo-brief':
            p.add_argument('--name', required=True)
    p = sub.add_parser('domain')
    p.add_argument('domain')
    p.add_argument('--live', action='store_true')
    p.add_argument('--receipt')
    p = sub.add_parser('screen')
    p.add_argument('--name', required=True)
    p.add_argument('--countries', required=True)
    p.add_argument('--classes', required=True)
    p.add_argument('--records')
    p = sub.add_parser('logo-source', help='Retrieve pinned upstream instructions only; no scripts or installation')
    p.add_argument('--output', required=True)
    p.add_argument('--fetch', action='store_true', help='Explicitly download and hash-verify three text files')
    sub.add_parser('mcp', help='Run local JSON-RPC stdio server; no HTTP listener')
    args = parser.parse_args(argv)
    try:
        if args.command == 'mcp':
            from .mcp import serve
            return serve()
        if args.command == 'logo-source':
            from .logo import retrieve_logo_source
            result = retrieve_logo_source(args.output, args.fetch)
        elif args.command == 'domain':
            result = check_domain(args.domain, args.live)
            if args.receipt:
                result = apply_registrar_receipt(result, load_json(args.receipt))
        elif args.command == 'screen':
            result = screening(args.name, args.countries.split(','), [int(x) for x in args.classes.split(',')], load_json(args.records) if args.records else None)
        elif args.command == 'logo-brief':
            result = logo_brief(args.name, load_json(args.brief))
        elif args.command == 'propose':
            result = propose(load_json(args.brief), load_json(args.candidates) if args.candidates else None, args.limit)
        else:
            result = report(load_json(args.brief), load_json(args.candidates) if args.candidates else None, load_json(args.records) if args.records else None, args.live, args.limit)
        print(markdown(result) if getattr(args, 'format', 'json') == 'markdown' else json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        sys.stdout.flush()
        return 0
    except (ValueError, TypeError, KeyError, OSError, RecursionError) as exc:
        print('nameproof: ' + str(exc), file=sys.stderr)
        return 2
