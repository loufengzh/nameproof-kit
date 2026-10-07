"""RDAP registration observations and separately attributed registrar receipts."""
import ipaddress
import json
import re
import socket
import unicodedata
from datetime import datetime, timezone, timedelta
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse, quote
from urllib.request import Request, build_opener, HTTPRedirectHandler

BOOTSTRAP = "https://data.iana.org/rdap/dns.json"
LIMIT = 2_000_000

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def normalize_domain(value):
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError("domain must be a bare hostname without whitespace")
    if any(c in value for c in '/:@?#\\'):
        raise ValueError("domain must not include URL, credentials, port or path")
    try:
        original = unicodedata.normalize('NFC', value.rstrip('.')).lower()
        result = original.encode('idna').decode('ascii').lower()
        if not original.isascii() and result.encode('ascii').decode('idna') != original:
            raise ValueError('IDN mapping changes spelling; provide an explicitly verified ASCII domain')
    except UnicodeError as exc:
        raise ValueError("invalid IDN") from exc
    labels = result.split('.')
    if len(result) > 253 or len(labels) < 2:
        raise ValueError("domain needs a public suffix and label")
    if any(not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', x) for x in labels):
        raise ValueError("invalid domain label")
    if labels[-1].isdigit() or labels[-1] in {'localhost', 'local', 'internal', 'test', 'invalid', 'example'}:
        raise ValueError("not a public domain")
    return result

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def fetch_json(url):
    """Bounded public HTTPS GET. Redirects fail closed; never follow to local services."""
    parsed = urlparse(url)
    if parsed.scheme != 'https' or parsed.username or parsed.password or parsed.port not in (None, 443) or not parsed.hostname:
        raise ValueError('only public HTTPS sources are supported')
    # URLs originate only in the HTTPS IANA bootstrap, never in a user-supplied endpoint.
    # Do not force local DNS resolution: HTTPS proxies may own DNS. Reject obvious
    # local/literal endpoints and redirects; trust IANA's registry endpoint list.
    host = parsed.hostname.lower()
    if '.' not in host or host.endswith(('.localhost', '.local', '.internal')):
        raise ValueError('local source is not supported')
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise ValueError('IP literal source is not supported')
    request = Request(url, headers={'User-Agent': 'nameproof-kit/0.1 (public RDAP lookup)', 'Accept': 'application/rdap+json, application/json'})
    opener = build_opener(NoRedirect)
    try:
        response = opener.open(request, timeout=8)
    except HTTPError as exc:
        response = exc
    with response:
        body = response.read(LIMIT + 1)
        if len(body) > LIMIT:
            raise ValueError('response exceeds size limit')
        return response.code, json.loads(body)

def rdap_url(domain, bootstrap):
    tld = domain.rsplit('.', 1)[-1]
    if not isinstance(bootstrap, dict) or not isinstance(bootstrap.get('services'), list):
        raise ValueError('invalid IANA bootstrap')
    for service in bootstrap['services']:
        if not isinstance(service, list) or len(service) != 2:
            continue
        suffixes, urls = service
        if isinstance(suffixes, list) and tld in suffixes and isinstance(urls, list):
            for base in urls:
                if isinstance(base, str) and base.startswith('https://'):
                    return base.rstrip('/') + '/domain/' + quote(domain, safe='')
    return None

def check_domain(value, live=False, fetch=fetch_json):
    domain = normalize_domain(value)
    out = {'domain': domain, 'registration_status': 'unknown', 'purchase_status': 'unknown', 'observed_at': None,
           'source_url': None, 'reason': 'not_checked', 'limitation': 'Registration absence is not registrar availability; recheck before buying.'}
    if not live:
        return out
    out['observed_at'] = now_iso()
    try:
        code, bootstrap = fetch(BOOTSTRAP)
        if code != 200:
            out['reason'] = 'bootstrap_unavailable'
            return out
        url = rdap_url(domain, bootstrap)
        if not url:
            out['reason'] = 'no_https_rdap_for_suffix'
            return out
        out['source_url'] = url
        code, record = fetch(url)
        if code == 200 and isinstance(record, dict) and record.get('objectClassName') == 'domain':
            returned = record.get('ldhName') or record.get('unicodeName')
            if returned and normalize_domain(returned) == domain:
                out.update(registration_status='registered', purchase_status='not_available_for_new_registration', reason='rdap_domain_record')
            else:
                out['reason'] = 'rdap_domain_mismatch'
        elif code == 404 and isinstance(record, dict) and record.get('errorCode') == 404:
            out.update(registration_status='no_record', reason='rdap_not_found')
        elif code == 429:
            out['reason'] = 'rate_limited'
        else:
            out['reason'] = 'unusable_rdap_response'
    except (ValueError, TypeError, KeyError, OSError, URLError) as exc:
        out['reason'] = 'lookup_failed:' + type(exc).__name__
    return out

def apply_registrar_receipt(observation, receipt, now=None):
    """Validate a user-imported quote; not independently authenticated by this tool."""
    required = {'domain', 'registrar', 'status', 'source_url', 'observed_at'}
    if not isinstance(receipt, dict) or not required <= receipt.keys():
        raise ValueError('receipt requires domain, registrar, status, source_url, observed_at')
    if normalize_domain(receipt['domain']) != observation['domain']:
        raise ValueError('receipt domain mismatch')
    statuses = {'available', 'unavailable', 'reserved', 'premium'}
    if receipt['status'] not in statuses or not isinstance(receipt['registrar'], str) or not receipt['registrar'].strip():
        raise ValueError('invalid registrar status or name')
    if not isinstance(receipt['source_url'], str) or any(c.isspace() for c in receipt['source_url']):
        raise ValueError('receipt source_url must be an HTTPS URL string')
    parsed = urlparse(receipt['source_url'])
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('receipt needs an HTTPS source URL without credentials')
    try:
        at = datetime.fromisoformat(receipt['observed_at'].replace('Z', '+00:00'))
        current = now or datetime.now(timezone.utc)
        if at.tzinfo is None:
            raise ValueError('receipt timestamp needs timezone')
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError('invalid receipt timestamp') from exc
    result = dict(observation)
    result['registrar_receipt'] = {key: receipt[key] for key in required}
    result['receipt_verification'] = 'user_supplied_not_independently_authenticated'
    age = current - at
    if age < -timedelta(seconds=30) or age > timedelta(minutes=15):
        result['receipt_status'] = 'stale_or_future'
    elif observation['registration_status'] == 'registered' and receipt['status'] in {'available', 'premium'}:
        result['receipt_status'] = 'conflicts_with_registration'
        result['purchase_status'] = 'conflicting_evidence'
    else:
        result['receipt_status'] = 'recent'
        result['purchase_status'] = 'registrar_reported_' + receipt['status']
    return result
