"""
TenderBridge — World Bank Major Contract Awards Scraper
Queries the World Bank Socrata Open Data API for Malawi health sector awards.

API: https://finances.worldbank.org/resource/kdui-wcs3.json
    - 100% free, no authentication required
    - Real-time, structured JSON
    - Filterable by country, sector, date

This captures international health infrastructure and equipment contracts
where local distributors and contractors participate.
"""

import os
import csv
import json
import ssl
import urllib.request
import urllib.parse
from datetime import datetime


# ─── SSL & Headers ─────────────────────────────────────────────────────────────
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    "User-Agent": "TenderBridge/1.0 (Medical Supply Intelligence)",
    "Accept": "application/json",
}

API_BASE = "https://finances.worldbank.org/resource/kdui-wcs3.json"


def _fetch_json(url):
    """Fetch a URL and return parsed JSON."""
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
            return json.loads(raw)
    except Exception as e:
        print(f"  [!] Error fetching {url}: {e}")
        return None


def scrape_worldbank_malawi(output_csv="data/worldbank_malawi_awards.csv", limit=500):
    """
    Query World Bank Major Contract Awards API for Malawi.
    Returns all contract awards for Malawi (country code MW).
    """
    print("\n" + "=" * 62)
    print("  🏦 World Bank — Malawi Major Contract Awards")
    print("=" * 62)

    all_records = []
    offset = 0
    batch_size = 200

    while offset < limit:
        # Build query URL
        params = {
            "borrower_country_code": "MW",
            "$limit": str(min(batch_size, limit - offset)),
            "$offset": str(offset),
            "$order": "as_of_date DESC",
        }
        url = API_BASE + "?" + urllib.parse.urlencode(params)

        print(f"  [*] Fetching records {offset+1}–{offset+batch_size} ...")
        data = _fetch_json(url)

        if not data:
            print("  [!] No data returned — stopping.")
            break
        if len(data) == 0:
            print("  [+] No more records.")
            break

        for record in data:
            all_records.append({
                "source": "World Bank API",
                "project_name": record.get("project_name", ""),
                "project_id": record.get("project_id", ""),
                "supplier_name": record.get("supplier", ""),
                "supplier_country": record.get("supplier_country", ""),
                "contract_description": record.get("contract_description", ""),
                "procurement_type": record.get("procurement_type", ""),
                "procurement_method": record.get("procurement_method", ""),
                "contract_amount_usd": record.get("total_contract_amount_usd", ""),
                "contract_signing_date": record.get("contract_signing_date", ""),
                "sector": record.get("major_sector", ""),
                "borrower_country": record.get("borrower_country", ""),
                "wb_region": record.get("region", ""),
            })

        offset += len(data)
        if len(data) < batch_size:
            break

    print(f"  [+] Total records fetched: {len(all_records)}")

    # Filter for health-related contracts
    health_keywords = [
        "health", "medical", "hospital", "pharma", "drug", "vaccine",
        "laboratory", "diagnostic", "clinical", "nursing", "surgical",
        "dental", "equipment", "hiv", "malaria", "tuberculosis", "tb",
        "nutrition", "medicine", "essential health", "emergency",
    ]
    health_records = []
    for r in all_records:
        combined = (
            r.get("project_name", "") + " " +
            r.get("contract_description", "") + " " +
            r.get("sector", "")
        ).lower()
        if any(kw in combined for kw in health_keywords):
            health_records.append(r)

    print(f"  [+] Health-sector records: {len(health_records)}")

    # Save to CSV
    records_to_save = all_records  # Save all records, not just health
    if records_to_save:
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        fieldnames = list(records_to_save[0].keys())
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records_to_save)
        print(f"  ✅ {len(records_to_save)} records saved to: {output_csv}")

    # Print health sector highlights
    if health_records:
        print(f"\n  📋 Health Sector Contract Highlights:")
        for r in health_records[:10]:
            amt = r.get("contract_amount_usd", "N/A")
            print(f"    → {r['supplier_name'][:40]:40s} | ${amt:>15s} | {r['contract_description'][:50]}")

    return all_records


if __name__ == "__main__":
    scrape_worldbank_malawi()
