"""
TenderBridge — CMST Malawi Scraper (Central Medical Stores Trust)
Scrapes http://www.cmst.mw for live contract awards, intention to award notices,
and active tenders for medical consumables, pharmaceuticals, and hospital equipment.

CMST is the central procuring trust for all 28 district hospitals in Malawi.
"""

import os
import csv
import re
import urllib.request
from html.parser import HTMLParser
from datetime import datetime

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

BASE_URL = "http://www.cmst.mw"


class TableExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables = []
        self.cur_table = []
        self.cur_row = []
        self.cur_cell = ""
        self.in_cell = False
        self.in_row = False
        self.in_table = False

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.in_table = True
            self.cur_table = []
        elif tag == "tr" and self.in_table:
            self.in_row = True
            self.cur_row = []
        elif tag in ["td", "th"] and self.in_row:
            self.in_cell = True
            self.cur_cell = ""

    def handle_endtag(self, tag):
        if tag in ["td", "th"] and self.in_cell:
            self.in_cell = False
            self.cur_row.append(re.sub(r"\s+", " ", self.cur_cell).strip())
        elif tag == "tr" and self.in_row:
            self.in_row = False
            if self.cur_row:
                self.cur_table.append(self.cur_row)
        elif tag == "table" and self.in_table:
            self.in_table = False
            if self.cur_table:
                self.tables.append(self.cur_table)

    def handle_data(self, data):
        if self.in_cell:
            self.cur_cell += " " + data.strip()


def fetch_url(url, timeout=20):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  [!] Error fetching {url}: {e}")
        return None


def scrape_cmst_awards():
    """Scrapes contract award tables from CMST."""
    url = f"{BASE_URL}/index.php/publications/contracts-awards"
    print(f"[*] Scraping CMST Contract Awards from: {url}")
    html = fetch_url(url)
    if not html:
        return []

    parser = TableExtractor()
    parser.feed(html)

    awards = []
    for table_idx, table in enumerate(parser.tables):
        if len(table) < 2:
            continue

        header = [c.lower() for c in table[0]]
        is_award_table = any(k in " ".join(header) for k in ["successful", "award", "amount", "price", "bidder"])

        # Check if table title was in previous row
        start_row = 1
        if "table" in table[0][0].lower() and len(table) > 2:
            header = [c.lower() for c in table[1]]
            start_row = 2

        for row in table[start_row:]:
            if not row or len(row) < 2:
                continue

            row_str = " | ".join(row)
            if "grand total" in row_str.lower():
                continue

            award = {
                "source": "CMST Malawi",
                "institution": "Central Medical Stores Trust (CMST)",
                "category": "Medical Consumables & Pharmaceuticals",
                "raw_record": row_str,
                "scraped_at": datetime.now().isoformat(),
            }

            # Map fields based on common column patterns
            for i, val in enumerate(row):
                if not val:
                    continue
                col_name = header[i] if i < len(header) else f"col_{i}"

                if any(k in col_name for k in ["bidder name", "supplier", "contractor"]):
                    award["company"] = val
                elif any(k in col_name for k in ["country", "nationality"]):
                    award["country"] = val
                elif any(k in col_name for k in ["usd", "price in usd"]):
                    award["value_usd"] = val
                elif any(k in col_name for k in ["mk", "mwk", "amount in mk", "price in mk"]):
                    award["value_mk"] = val
                elif any(k in col_name for k in ["items", "description"]):
                    award["items"] = val

            # Fallbacks if columns weren't explicitly named
            if "company" not in award and len(row) >= 3:
                # usually col 1 or 2 is company name
                for v in row[1:4]:
                    if any(s in v.lower() for s in ["ltd", "limited", "pharmaceutical", "medics", "healthcare", "trading", "investments", "supplies", "associates", "group"]):
                        award["company"] = v
                        break

            if "company" in award and len(award["company"]) > 3:
                awards.append(award)

    print(f"  [+] Extracted {len(awards)} awarded distributor records from CMST tables")
    return awards


def scrape_cmst_tenders():
    """Scrapes open and closed tender notices and attached PDF links."""
    tenders = []
    urls = [
        ("Open Tenders", f"{BASE_URL}/index.php/publications/open-tenders"),
        ("Old Procurements", f"{BASE_URL}/index.php/functions/procurement-notices/old-documents-and-procurements"),
        ("RFQs", f"{BASE_URL}/index.php/publications/request-for-quot")
    ]

    for category, url in urls:
        print(f"[*] Scraping {category} from: {url}")
        html = fetch_url(url)
        if not html:
            continue

        pdf_links = re.findall(r"href=[\"\x27]([^\x27\"]+\.pdf)[\"\x27]", html, re.I)
        for link in set(pdf_links):
            full_link = link if link.startswith("http") else f"{BASE_URL}{link}"
            tenders.append({
                "source": f"CMST {category}",
                "institution": "Central Medical Stores Trust (CMST)",
                "category": "Medical Tender Document",
                "title": os.path.basename(link).replace("_", " ").replace(".pdf", ""),
                "pdf_link": full_link,
                "scraped_at": datetime.now().isoformat(),
            })

    print(f"  [+] Extracted {len(tenders)} tender notice & PDF document records from CMST")
    return tenders


def run_cmst_scraper(output_csv="data/cmst_scraped.csv"):
    print("\n" + "=" * 62)
    print("  🏥 CMST Malawi — Central Medical Stores Trust Live Scraper")
    print("=" * 62)

    awards = scrape_cmst_awards()
    tenders = scrape_cmst_tenders()
    all_records = awards + tenders

    if all_records:
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        # Collect all unique fieldnames
        fieldnames = []
        for r in all_records:
            for k in r.keys():
                if k not in fieldnames:
                    fieldnames.append(k)

        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(all_records)
        print(f"\n  ✅ {len(all_records)} CMST records successfully saved to: {output_csv}")

    return all_records


if __name__ == "__main__":
    run_cmst_scraper()
