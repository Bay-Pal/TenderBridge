"""
TenderBridge — Contact Discovery Module (Phase 3)
Automatically finds phone numbers, email addresses, and web presence
for winning distributors using multiple free public sources.

Sources tried in order:
  1. Export Genius public company profile (free, SEO-indexed)
  2. Africa Business Directory / Yellow Pages Africa
  3. LinkedIn company search URL
  4. Malawi Business Registry
  5. Google search URL (fallback — needs manual visit)
"""

import re
import time
import ssl
import urllib.request
import urllib.parse
import json

# ─── SSL Context ───────────────────────────────────────────────────────────────
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# ─── Phone & Email Regex ───────────────────────────────────────────────────────
# Malawi: +265 prefix, 9 digits. Also Kenya +254, Tanzania +255, Uganda +256
PHONE_PATTERNS = [
    r"\+265[\s\-\.]?\d{3}[\s\-\.]?\d{3}[\s\-\.]?\d{3}",   # +265 XXX XXX XXX
    r"0265[\s\-\.]?\d{3}[\s\-\.]?\d{3}[\s\-\.]?\d{3}",    # 0265 XXX XXX XXX
    r"\b0[89]\d{2}[\s\-\.]?\d{3}[\s\-\.]?\d{3}\b",        # 08XX or 09XX (Malawi mobile)
    r"\+254[\s\-\.]?\d{3}[\s\-\.]?\d{6}",                  # Kenya
    r"\+255[\s\-\.]?\d{3}[\s\-\.]?\d{6}",                  # Tanzania
    r"\+256[\s\-\.]?\d{3}[\s\-\.]?\d{6}",                  # Uganda
    r"\+260[\s\-\.]?\d{3}[\s\-\.]?\d{6}",                  # Zambia
]

EMAIL_PATTERN = r"[a-zA-Z0-9._%+\-]{2,}@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
EMAIL_NOISE   = ["duckduckgo", "sentry", "example", "schema", "w3.org",
                 "openstreetmap", "wikimedia", "google", ".png", ".jpg"]


def _fetch(url, timeout=15):
    """Fetch a URL and return HTML text, or None on failure."""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
            raw = resp.read()
            return raw.decode("utf-8", errors="ignore")
    except Exception:
        return None


def _extract_phones(text):
    phones = set()
    for pattern in PHONE_PATTERNS:
        for m in re.findall(pattern, text):
            cleaned = re.sub(r"\s+", " ", m).strip()
            if cleaned:
                phones.add(cleaned)
    return sorted(phones)


def _extract_emails(text):
    raw = re.findall(EMAIL_PATTERN, text)
    return sorted({
        e for e in raw
        if not any(noise in e.lower() for noise in EMAIL_NOISE)
    })


def _slug(name):
    """Convert a company name to a URL slug."""
    s = name.lower()
    s = re.sub(r"[^a-z0-9\s]", "", s)
    s = re.sub(r"\s+", "-", s.strip())
    return s


# ─── Source 1: Export Genius Public Profile ────────────────────────────────────
def _try_export_genius(company_name, country="Malawi"):
    """
    Export Genius has free SEO-indexed public profiles for many African importers.
    The profile page shows the registered address and sometimes a contact hint.
    We try both the structured URL format and a search.
    """
    slug = _slug(company_name)
    # Try direct profile URL pattern (observed from RMS profile)
    url = f"https://www.exportgenius.in/company/{slug}"
    html = _fetch(url)

    phones, emails = [], []
    if html:
        phones = _extract_phones(html)
        emails = _extract_emails(html)
        # Also extract structured JSON-LD data (they embed FAQ schema with contact hints)
        json_lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
        for jld in json_lds:
            try:
                data = json.loads(jld)
                text = json.dumps(data)
                phones.extend(_extract_phones(text))
                emails.extend(_extract_emails(text))
            except Exception:
                pass

    return sorted(set(phones)), sorted(set(emails)), url if html else None


# ─── Source 2: Kompass Africa Business Directory ───────────────────────────────
def _try_kompass(company_name, country="Malawi"):
    """Kompass is a global B2B directory with some African coverage."""
    query = urllib.parse.quote(f"{company_name} {country}")
    url = f"https://www.kompass.com/a/worldwide-search/{query}/"
    html = _fetch(url)
    if not html:
        return [], [], None
    phones = _extract_phones(html)
    emails = _extract_emails(html)
    return phones, emails, url if (phones or emails) else None


# ─── Source 3: Africa Business Directory ──────────────────────────────────────
def _try_africa_directory(company_name, country="Malawi"):
    """africabizinfo.com has listings for some Malawi / East Africa companies."""
    query = urllib.parse.quote(f"{company_name}")
    url = f"https://www.africabizinfo.com/MW/search?q={query}"
    html = _fetch(url)
    if not html:
        return [], [], None
    phones = _extract_phones(html)
    emails = _extract_emails(html)
    return phones, emails, url if html else None


# ─── Source 4: Malawi Yellow Pages ────────────────────────────────────────────
def _try_malawi_yp(company_name):
    """Malawi Yellow Pages / local directories."""
    query = urllib.parse.quote(company_name)
    urls_to_try = [
        f"https://www.yellowpages.mw/search?q={query}",
        f"https://malawi.businesslist.africa/?q={query}",
    ]
    for url in urls_to_try:
        html = _fetch(url)
        if html:
            phones = _extract_phones(html)
            emails = _extract_emails(html)
            if phones or emails:
                return phones, emails, url
    return [], [], None


# ─── Source 5: Generate Manual Search Links ────────────────────────────────────
def _generate_search_links(company_name, country="Malawi"):
    """
    Generate manual search URLs for the sales team to check.
    These open in browser and don't need scraping.
    """
    q = urllib.parse.quote(f'"{company_name}" {country}')
    return {
        "google":   f"https://www.google.com/search?q={q}+phone+OR+email+OR+contact",
        "linkedin": f"https://www.linkedin.com/search/results/companies/?keywords={urllib.parse.quote(company_name)}",
        "export_genius_search": f"https://www.exportgenius.in/search-companies?query={urllib.parse.quote(company_name)}",
    }


# ─── Main Entry Point ──────────────────────────────────────────────────────────
def find_contacts(company_name, country="Malawi", verbose=True):
    """
    Main entry point. Given a company name and country, search multiple
    free public sources for: phone numbers, emails, website.

    Returns a dict with all discovered contact information plus manual search links.
    """
    if verbose:
        print(f"    🔍 Searching contacts for: {company_name} ({country})...")

    all_phones   = set()
    all_emails   = set()
    found_urls   = {}

    # ── Source 1: Export Genius ────────────────────────────────────────────────
    if verbose: print("       → Checking Export Genius profile...")
    phones, emails, eg_url = _try_export_genius(company_name, country)
    all_phones.update(phones)
    all_emails.update(emails)
    if eg_url: found_urls["export_genius"] = eg_url
    time.sleep(1)

    # ── Source 2: Africa Business Directory ───────────────────────────────────
    if verbose: print("       → Checking Africa Business Directory...")
    phones, emails, afd_url = _try_africa_directory(company_name, country)
    all_phones.update(phones)
    all_emails.update(emails)
    if afd_url: found_urls["africa_directory"] = afd_url
    time.sleep(1)

    # ── Source 3: Malawi Yellow Pages ─────────────────────────────────────────
    if country.lower() == "malawi":
        if verbose: print("       → Checking Malawi Yellow Pages...")
        phones, emails, yp_url = _try_malawi_yp(company_name)
        all_phones.update(phones)
        all_emails.update(emails)
        if yp_url: found_urls["yellow_pages"] = yp_url
        time.sleep(1)

    # ── Source 4: Kompass ─────────────────────────────────────────────────────
    if verbose: print("       → Checking Kompass directory...")
    phones, emails, kp_url = _try_kompass(company_name, country)
    all_phones.update(phones)
    all_emails.update(emails)
    if kp_url: found_urls["kompass"] = kp_url
    time.sleep(1)

    # ── Always: Generate manual search links ──────────────────────────────────
    search_links = _generate_search_links(company_name, country)

    # Determine if any mobile (WhatsApp-capable) number was found
    has_mobile = any(
        re.search(r"\+265|0[89]\d{2}", p) for p in all_phones
    )

    result = {
        "company":      company_name,
        "country":      country,
        "phones":       sorted(all_phones),
        "emails":       sorted(all_emails),
        "sources_hit":  found_urls,
        "search_links": search_links,
        "whatsapp_note": (
            "Mobile numbers found above are likely WhatsApp-capable."
            if has_mobile
            else "No mobile found automatically — use Google/LinkedIn links below."
        ),
    }
    return result


def format_contact_result(contact):
    """Pretty-print a contact result dict for terminal display."""
    phones  = contact.get("phones", [])
    emails  = contact.get("emails", [])
    links   = contact.get("search_links", {})
    lines = [
        f"  📞 Phones  : {', '.join(phones) if phones else 'Not found automatically'}",
        f"  📧 Emails  : {', '.join(emails) if emails else 'Not found automatically'}",
        f"  💬 WhatsApp: {contact.get('whatsapp_note', '')}",
        f"  🔗 Manual Search Links:",
        f"       Google  → {links.get('google', 'N/A')}",
        f"       LinkedIn → {links.get('linkedin', 'N/A')}",
        f"       ExportGenius → {links.get('export_genius_search', 'N/A')}",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    test_companies = [
        ("Mohammed Moshin RMS Distributors", "Malawi"),
        ("Opco Limited", "Malawi"),
        ("Sieman Bio-Medical Solution Company", "Malawi"),
        ("DRZ General Dealers", "Malawi"),
    ]
    for name, country in test_companies:
        print(f"\n{'='*62}")
        print(f"  Company: {name}")
        result = find_contacts(name, country, verbose=True)
        print(format_contact_result(result))

