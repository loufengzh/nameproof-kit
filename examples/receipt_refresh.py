"""Offline, synthetic example: recheck a registrar receipt after its expiry."""
from datetime import datetime, timedelta, timezone

from nameproof.domain import apply_registrar_receipt, check_domain


now = datetime(2026, 10, 14, tzinfo=timezone.utc)
receipt = {
    'domain': 'example.com',
    'registrar': 'Fictional example registrar',
    'status': 'available',
    'source_url': 'https://example.com/fictional-quote',
    'observed_at': now.isoformat(),
}
fresh = apply_registrar_receipt(check_domain('example.com'), receipt, now=now)
expired = apply_registrar_receipt(fresh, receipt, now=now + timedelta(minutes=16))
assert fresh['purchase_status'] == 'registrar_reported_available'
assert expired['purchase_status'] == 'unknown'
assert expired['receipt_status'] == 'stale_or_future'
print(fresh['purchase_status'], '->', expired['purchase_status'])
