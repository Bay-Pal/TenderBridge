"""
TenderBridge — MANEPS API Scraper (Malawi National Electronic Procurement System)
Queries the MANEPS OCDS (Open Contracting Data Standard) API for structured
procurement records including tenders, awards, and contracts.

API Endpoints:
  - Records: https://maneps.mw/rms/api/get-records
  - Releases: https://maneps.mw/rms/api/get-releases
  - API Docs: https://maneps.mw/rms/api/docs

The API returns JSON conforming to OCDS schema.
Note: High-offset queries (>6000 records) may timeout. Use date filtering.
"""

import os
import csv
import json
import ssl
import urllib.request
import urllib.parse
from datetime import datetime, timedelta


# ─── SSL & Headers ─────────────────────────────────────────────────────────────
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    "User-Agent": "TenderBridge/1.0 (Medical Supply Intelligence)",
    "Accept": "application/json",
}

API_BASE = "https://maneps.mw/rms/api"


def _fetch_json(url, timeout=60):
    """Fetch a URL and return parsed JSON."""
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
            return json.loads(raw)
    except Exception as e:
        print(f"  [!] Error fetching {url}: {e}")
        return None


def scrape_maneps_releases(output_csv="data/maneps_releases.csv", max_records=500):
    """
    Query MANEPS OCDS releases API.
    Each release represents a procurement event (planning, tender, award, contract).
    """
    print("\n" + "=" * 62)
    print("  🏛  MANEPS — Malawi National e-Procurement System (OCDS API)")
    print("=" * 62)

    all_records = []
    offset = 0
    batch_size = 100

    while offset < max_records:
        url = f"{API_BASE}/get-releases?offset={offset}&limit={batch_size}"
        print(f"  [*] Fetching releases {offset+1}–{offset+batch_size} ...")

        data = _fetch_json(url)
        if not data:
            print("  [!] No response or error — stopping pagination.")
            break

        # OCDS release packages contain a "releases" array
        releases = data.get("releases", data if isinstance(data, list) else [])
        if not releases:
            print("  [+] No more releases.")
            break

        for release in releases:
            record = _parse_release(release)
            if record:
                all_records.append(record)

        offset += len(releases)
        print(f"    → Parsed {len(releases)} releases (total: {len(all_records)})")

        if len(releases) < batch_size:
            break

    print(f"\n  [+] Total records extracted: {len(all_records)}")

    # Filter for health/medical
    health_keywords = [
        "health", "medical", "hospital", "pharma", "drug", "vaccine",
        "laboratory", "diagnostic", "surgical", "dental", "equipment",
        "medicine", "supplies", "consumable", "catheter", "syringe",
        "clinical", "nursing", "cmst", "central medical",
    ]
    health_records = [
        r for r in all_records
        if any(kw in (r.get("title", "") + " " + r.get("description", "") + " " + r.get("buyer", "")).lower()
               for kw in health_keywords)
    ]
    print(f"  [+] Health-sector records: {len(health_records)}")

    # Save ALL records to CSV
    if all_records:
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        fieldnames = list(all_records[0].keys())
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_records)
        print(f"  ✅ {len(all_records)} records saved to: {output_csv}")

    # Print health sector highlights
    if health_records:
        print(f"\n  📋 Health Sector Highlights:")
        for r in health_records[:10]:
            print(f"    → {r.get('title', 'N/A')[:60]}")
            if r.get("award_suppliers"):
                print(f"      Awarded to: {r['award_suppliers']}")
            if r.get("award_value"):
                print(f"      Value: {r['award_value']}")

    return all_records


def _parse_release(release):
    """Parse a single OCDS release into a flat dict."""
    if not isinstance(release, dict):
        return None

    record = {
        "source": "MANEPS API",
        "ocid": release.get("ocid", ""),
        "release_id": release.get("id", ""),
        "release_date": release.get("date", ""),
        "tag": ", ".join(release.get("tag", [])) if isinstance(release.get("tag"), list) else str(release.get("tag", "")),
    }

    # Tender info
    tender = release.get("tender", {})
    if tender:
        record["title"] = tender.get("title", "")
        record["description"] = tender.get("description", "")
        record["tender_status"] = tender.get("status", "")
        record["tender_id"] = tender.get("id", "")

        # Procurement method
        record["procurement_method"] = tender.get("procurementMethod", "")

        # Value
        value = tender.get("value", {})
        if value:
            record["tender_value"] = f"{value.get('amount', '')} {value.get('currency', '')}"

        # Tender period
        period = tender.get("tenderPeriod", {})
        if period:
            record["tender_start"] = period.get("startDate", "")
            record["tender_end"] = period.get("endDate", "")

    # Buyer info
    buyer = release.get("buyer", {})
    if buyer:
        record["buyer"] = buyer.get("name", "")
        record["buyer_id"] = buyer.get("id", "")

    # Awards
    awards = release.get("awards", [])
    if awards:
        suppliers_list = []
        values_list = []
        for award in awards:
            award_suppliers = award.get("suppliers", [])
            for s in award_suppliers:
                suppliers_list.append(s.get("name", ""))
            award_value = award.get("value", {})
            if award_value:
                values_list.append(f"{award_value.get('amount', '')} {award_value.get('currency', '')}")
            record["award_status"] = award.get("status", "")
            record["award_date"] = award.get("date", "")

        record["award_suppliers"] = "; ".join(suppliers_list)
        record["award_value"] = "; ".join(values_list)

    # Contracts
    contracts = release.get("contracts", [])
    if contracts:
        for contract in contracts:
            record["contract_id"] = contract.get("id", "")
            contract_value = contract.get("value", {})
            if contract_value:
                record["contract_value"] = f"{contract_value.get('amount', '')} {contract_value.get('currency', '')}"
            record["contract_status"] = contract.get("status", "")

    return record


def scrape_maneps_records(output_csv="data/maneps_records.csv", max_records=200):
    """
    Query MANEPS OCDS records API (compiled records, not individual releases).
    Each record represents a complete procurement process.
    """
    print("\n  [*] Trying MANEPS records endpoint ...")
    url = f"{API_BASE}/get-records?offset=0&limit={min(max_records, 100)}"
    data = _fetch_json(url)

    if not data:
        print("  [!] Records endpoint not available, use releases instead.")
        return []

    records = data.get("records", data if isinstance(data, list) else [])
    print(f"  [+] Fetched {len(records)} compiled records")
    return records


if __name__ == "__main__":
    scrape_maneps_releases()
