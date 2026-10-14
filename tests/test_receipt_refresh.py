"""Receipt replacement never borrows a purchase verdict from discarded evidence."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import unittest

from nameproof.domain import apply_registrar_receipt, check_domain


class ReceiptRefreshTests(unittest.TestCase):
    now = datetime(2026, 10, 14, tzinfo=timezone.utc)

    def receipt(self, age=0, status='available'):
        return dict(domain='example.com', registrar='Example registrar', status=status,
                    source_url='https://example.com/quote',
                    observed_at=(self.now - timedelta(seconds=age)).isoformat())

    def test_expired_or_future_replacement_clears_prior_registrar_verdict(self):
        for status in ('available', 'premium', 'reserved', 'unavailable'):
            for age in (901, -31):
                with self.subTest(status=status, age=age):
                    previous = apply_registrar_receipt(check_domain('example.com'),
                                                       self.receipt(status=status), now=self.now)
                    saved = deepcopy(previous)
                    incoming = self.receipt(age=age, status='unavailable')
                    result = apply_registrar_receipt(previous, incoming, now=self.now)
                    self.assertEqual(result['receipt_status'], 'stale_or_future')
                    self.assertEqual(result['purchase_status'], 'unknown')
                    self.assertEqual(result['registrar_receipt'], incoming)
                    self.assertEqual(previous, saved)

    def test_rechecking_same_receipt_after_expiry_clears_availability(self):
        receipt = self.receipt()
        previous = apply_registrar_receipt(check_domain('example.com'), receipt, now=self.now)
        result = apply_registrar_receipt(previous, receipt,
                                         now=self.now + timedelta(minutes=16))
        self.assertEqual(result['purchase_status'], 'unknown')

    def test_stale_replacement_preserves_registry_fact_not_old_conflict(self):
        observation = check_domain('example.com')
        observation.update(registration_status='registered',
                           purchase_status='not_available_for_new_registration')
        previous = apply_registrar_receipt(observation, self.receipt(), now=self.now)
        self.assertEqual(previous['purchase_status'], 'conflicting_evidence')
        result = apply_registrar_receipt(previous, self.receipt(age=901), now=self.now)
        self.assertEqual(result['purchase_status'], 'not_available_for_new_registration')
        self.assertEqual(result['registration_status'], 'registered')

    def test_fresh_replacement_uses_current_receipt(self):
        previous = apply_registrar_receipt(check_domain('example.com'), self.receipt(), now=self.now)
        result = apply_registrar_receipt(previous, self.receipt(status='reserved'), now=self.now)
        self.assertEqual(result['purchase_status'], 'registrar_reported_reserved')
        self.assertEqual(result['receipt_status'], 'recent')

    def test_freshness_boundaries_are_inclusive(self):
        for age in (900, -30):
            with self.subTest(age=age):
                result = apply_registrar_receipt(check_domain('example.com'),
                                                 self.receipt(age=age), now=self.now)
                self.assertEqual(result['purchase_status'], 'registrar_reported_available')

    def test_replacement_preserves_registry_provenance_and_resets_receipt_status(self):
        for registration in ('registered', 'no_record', 'unknown'):
            for status in ('available', 'premium', 'reserved', 'unavailable'):
                with self.subTest(registration=registration, status=status):
                    observation = check_domain('example.com')
                    observation.update(registration_status=registration,
                                       source_url='https://example.com/fictional-rdap',
                                       observed_at=self.now.isoformat(), reason='fixture')
                    previous = apply_registrar_receipt(observation, self.receipt(status=status),
                                                       now=self.now)
                    expired = apply_registrar_receipt(previous, self.receipt(age=901), now=self.now)
                    baseline = ('not_available_for_new_registration'
                                if registration == 'registered' else 'unknown')
                    self.assertEqual(expired['purchase_status'], baseline)
                    refreshed = apply_registrar_receipt(expired, self.receipt(status='reserved'),
                                                        now=self.now)
                    self.assertEqual(refreshed['receipt_status'], 'recent')
                    self.assertEqual(refreshed['purchase_status'], 'registrar_reported_reserved')
                    self.assertEqual(refreshed['receipt_verification'],
                                     'user_supplied_not_independently_authenticated')
                    for key in ('registration_status', 'source_url', 'observed_at', 'reason'):
                        self.assertEqual(refreshed[key], observation[key])
