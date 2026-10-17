"""Synthetic RDAP name evidence; no network or live registration claims."""
from nameproof.domain import BOOTSTRAP, check_domain


def observe(domain, record):
    def fetch(url):
        if url == BOOTSTRAP:
            return 200, {'services': [[['com'], ['https://rdap.example.org/']]]}
        return 200, {'objectClassName': 'domain', **record}
    return check_domain(domain, live=True, fetch=fetch)


contradictory = observe('example.com', {'ldhName': 'example.com', 'unicodeName': 'other.com'})
equivalent = observe('xn--fa-hia.com', {'ldhName': 'xn--fa-hia.com', 'unicodeName': 'faß.com'})
assert contradictory['registration_status'] == 'unknown'
assert contradictory['reason'] == 'rdap_domain_mismatch'
assert equivalent['registration_status'] == 'registered'
print('Synthetic contradiction:', contradictory['registration_status'])
print('Synthetic matching IDN:', equivalent['registration_status'])
