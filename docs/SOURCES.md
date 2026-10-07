# Evidence and official-source catalog

Research date: 2026-10-07. Links and API terms can change. This is an implementation
reference, not legal advice or proof that a particular name is available. Website
access does not grant permission to automate it. No accounts were created, no paid
queries or purchases made, and no blocked search was circumvented.

## Domain evidence: two different questions

1. **Registration record:** discover the registry using the [IANA RDAP bootstrap](https://data.iana.org/rdap/dns.json), not a hand-maintained `.com`-only mapping. Normalize IDNs to A-labels, preserve the original Unicode name and query the domain endpoint. A successful domain object is registration evidence. An authoritative 404 is only `not_found_in_rdap`. No endpoint, timeouts, invalid responses, rate limits and access denials are `unknown`, never “available.” See [IANA RDAP requirements](https://www.iana.org/help/rdap-requirements) and [ICANN RDAP user information](https://www.icann.org/en/contracted-parties/registry-operators/registration-data-access-protocol/information-for-rdap-users-31-08-2018-en).
2. **Purchasable now:** require a separate current registrar quote for the exact domain, TLD, currency and term. [Namecheap's official check endpoint](https://www.namecheap.com/support/api/methods/domains/check/) returns `Available`, `IsPremiumName`, premium registration/renewal prices and fees; it permits at most 50 domains per check. [Production API access](https://www.namecheap.com/support/api/intro/) has account eligibility requirements and credentials/IP configuration. Sandbox results are not production purchase evidence. A check is not a reservation or guaranteed successful checkout.

An RDAP absence cannot prove sale availability: registries have [reserved names](https://www.icann.org/en/contracted-parties/registry-operators/services/reserved-names), eligibility restrictions and other policy constraints. Premium is a pricing property, not the opposite of available. Do not infer standard pricing from missing premium fields or conflate aftermarket offers with first registration. DNS NXDOMAIN and a missing website also do not prove a domain unregistered or purchasable.

Recommended provider record: exact query, provider/endpoint, observation timestamp,
HTTP status, raw-response hash or permitted evidence excerpt, registration outcome,
registrar quote outcome, premium flag, registration/renewal totals, currency, term,
fee/tax exclusions and reason codes. Keep conflicting observations visible. Apply
bounded concurrency, timeouts, caching, `Retry-After` and provider-specific limits.
Do not follow arbitrary RDAP redirects into private networks or fetch URLs supplied
in imported evidence records.

## Trademark and company-name coverage

The machine-readable catalog is `nameproof/jurisdictions.json`. All current
trademark checks are **manual search plans plus optional imported records**. An
`account-api` label describes a possible future integration, not one implemented
or authenticated by this toolkit. No published API was verified for a portal
unless explicitly listed below; this does not claim an API does not exist.

| Region | Trademark source | Business-name source | Access and coverage limits |
| --- | --- | --- | --- |
| US | [USPTO Trademark Search](https://www.uspto.gov/trademarks/search) | [SBA state-register directory](https://www.sba.gov/counseling/launch-your-business/state-registration-lookup/) | Federal trademark search; state, local DBA and common-law use remain separate. [TSDR API](https://www.uspto.gov/sites/default/files/documents/tm-enterprise-api-user-guide-v2.pdf) is credentialed case retrieval, not a verified general name-search API. |
| EU | [EUIPO eSearch/TMview](https://www.euipo.europa.eu/search-ip), [official Trademark Search API](https://dev.euipo.europa.eu/product/trademark-search_100) | [e-Justice / BRIS](https://e-justice.europa.eu/topics/registers-business-insolvency-land/business-registers-search-company-eu_en) | EUIPO API needs sign-in/subscription and plan-specific limits; numeric quotas not verified. TMview coverage varies by participating office. National rights matter to EU plans; BRIS is not an EU-wide name reservation service. |
| UK / GB | [UK IPO](https://www.gov.uk/search-for-trademark) | [Companies House](https://find-and-update.company-information.service.gov.uk/) | [Companies House API](https://developer-specs.company-information.service.gov.uk/companies-house-public-data-api/reference/search/search-companies) uses an API key and documents legally-equivalent active-company restrictions; [limit is 600 requests/5 minutes](https://developer-specs.company-information.service.gov.uk/guides/rateLimiting). This does not establish trademark or trading-name rights. |
| VN | [IP Viet Nam](https://ipvietnam.gov.vn/), [official WIPO Publish guide](https://wipopublish.ipvietnam.gov.vn/wopublish-resources/documents/help.pdf) | [National Business Registration Portal](https://dangkykinhdoanh.gov.vn/en/Pages/default.aspx) | Manual search, check publication lag and Vietnamese spelling/diacritics; no public API authorization verified. Follow current office links rather than hardcoding obsolete NOIP endpoints. |
| CN | [CNIPA trademark services](https://english.cnipa.gov.cn/col/col2950/index.html), [public service platform](https://ggfw.cnipa.gov.cn/) | [GSXT](https://www.gsxt.gov.cn/index.html), linked by [SAMR](https://dj.samr.gov.cn/djfww/zczl/index.html) | CNIPA advertises data opening/interfaces, but access and redistribution conditions were not verified. GSXT fetch returned 403 during this research; use manual access and respect restrictions. Search Chinese, pinyin and Latin variants. |
| DE | [DPMAregister](https://www.dpma.de/english/search/dpmaregister/) | [Joint Register Portal](https://www.handelsregister.de/rp_web/) | DPMA includes German, EU and international marks protecting Germany; register data updated daily, publication schedule differs. Official automation/bulk route is DPMAconnectPlus with separate onboarding; no public unauthenticated search API verified. |
| RU | [Rospatent platform](https://searchplatform.rospatent.gov.ru/trademarks), [official coverage announcement](https://rospatent.gov.ru/ru/news/rospatent-1) | [Federal Tax Service EGRUL/EGRIP](https://egrul.nalog.ru/) | Platform describes registered, well-known and internationally protected marks. Verify pending-application coverage separately. Search Cyrillic and transliterations; no public API authorization verified. |
| SG | [IPOS Digital Hub](https://digitalhub.ipos.gov.sg/FAMN/eservice/IP4SG/MN_AdvancedSearch), [IPOS search instructions](https://ask.gov.sg/ipos/questions/clnnxj575001n4i0xnr68nc6d) | [ACRA Bizfile](https://www.bizfile.gov.sg/) | Use Similar Mark Search rather than assuming basic/prefix results cover similarity. Newly filed records may be delayed. No public search API authorization verified. |

[WIPO Global Brand Database FAQ](https://www.wipo.int/en/web/global-brand-database/faqs_branddb)
explicitly prohibits automatic querying, searches and downloading. It is therefore
manual-only here. WIPO is not a universal, instantaneous worldwide register;
participating offices supply updates on different schedules. Its FAQ recommends
national-register searches as well. Do not build a scraper around internal API
calls, rotate identities, solve challenges without authorization or treat public
browser access as a bulk-data license.

## Imported-record contract and matching limits

`screening(name, countries, classes, records=None)` accepts supported ISO codes
plus `EU`; `UK` is normalized to `GB`. Nice classes must be integer lists within
1–45. Every imported record must contain exactly:

- `mark`: nonempty mark string
- `jurisdiction`: supported jurisdiction code
- `classes`: one or more integer Nice classes
- `source_url`: HTTPS evidence link without embedded credentials
- `observed_at`: nonfuture, timezone-aware ISO timestamp
- `record_id`: identifier unique within the record jurisdiction
- `status`: source's status text, preserved without legal interpretation

URLs and timestamps are validated for form, not authenticated. Links are never
fetched. User imports can be incomplete, incorrect, stale or selectively sampled.
NFKC, casefolding and punctuation removal identify normalized exact text matches;
SequenceMatcher >= 0.8 adds fuzzy candidates. These heuristics do not cover visual,
phonetic, conceptual or transliteration similarity reliably. A non-hit is not a
clearance. Other-class and inactive-status matches are retained for review. The
[USPTO explains](https://www.uspto.gov/trademarks/search/federal-trademark-searching)
that related goods/services need not be in the same international class.

EU records are included for DE screening, and DE national records are included as
limited territorial evidence for EU plans. Other EU national rights are explicitly
unreviewed, not silently inferred covered. International registrations must be
imported by the actual designated jurisdiction supported by the record, not as
blanket worldwide rights. Business-name sources are manual plans; this module does
not evaluate business-registration eligibility or reserve any name.

## Existing work to reuse or compare

- [ICANN RDAP](https://github.com/icann/icann-rdap): official Rust CLI/client/common data libraries, dual MIT/Apache-2.0. Best foundation/reference for RDAP bootstrap, parsing and conformance rather than another WHOIS parser.
- [OpenRDAP](https://github.com/openrdap/rdap): established Go CLI/client alternative. Review license and current behavior before incorporating code.
- [available](https://github.com/bradleydwyer/available): MIT CLI/MCP combining LLM candidate generation with domain/package checks. Strong overlap with idea-to-name workflows; inspect its registration-vs-purchase semantics before reuse.
- [Domain Hunter](https://github.com/WhiteBite/Domain-Hunter): browser-first generators, bulk checks, exports and pricing UI. Useful UX reference; its own availability terminology is not a reason to equate RDAP/DNS absence with buyability.
- [BrandLab](https://github.com/scrappygmail/brandlab): explainable linguistic scoring and manual search links. Its README describes non-commercial source use; do not assume it is permissively open-source or copy into an MIT project without license review.
- [domain-finder](https://github.com/Sra1Phani/domain-finder): generation and domain/package checking, MCP interface; Elastic License 2.0 is source-available, not a permissive OSS dependency.

These are public documentation comparisons, not audits or live correctness tests.
Nameproof's intended distinction is evidence provenance, honest unknown states,
separate registrar purchase evidence and jurisdiction-specific review plans, rather
than claiming a new generator alone solves naming clearance.
