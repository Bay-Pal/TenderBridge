"""
PPDA Malawi Live Scraper
Extracts 'Intentions to Award', 'Award Notices', and 'Open Tenders' from PPDA Malawi.
"""
import urllib.request
import ssl
import csv
import os
from html.parser import HTMLParser

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

class TableHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables = []
        self.current_table = []
        self.current_row = []
        self.current_cell = ""
        self.in_table = False
        self.in_row = False
        self.in_cell = False
        self.row_links = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "table":
            self.in_table = True
            self.current_table = []
        elif tag == "tr" and self.in_table:
            self.in_row = True
            self.current_row = []
            self.row_links = []
        elif tag in ["td", "th"] and self.in_row:
            self.in_cell = True
            self.current_cell = ""
        elif tag == "a" and self.in_row:
            href = attrs_dict.get("href")
            if href:
                self.row_links.append(href)

    def handle_endtag(self, tag):
        if tag in ["td", "th"] and self.in_cell:
            self.in_cell = False
            self.current_row.append(self.current_cell.strip())
        elif tag == "tr" and self.in_row:
            self.in_row = False
            if self.current_row:
                self.current_table.append({
                    "data": self.current_row,
                    "links": list(self.row_links)
                })
        elif tag == "table" and self.in_table:
            self.in_table = False
            if self.current_table:
                self.tables.append(self.current_table)

    def handle_data(self, data):
        if self.in_cell:
            self.current_cell += " " + data.strip()


def scrape_ppda_notices(output_csv="data/malawi_ppda_live_extracted.csv"):
    urls = [
        ("Intentions to Award", "https://www.ppda.mw/intentions-to-award"),
        ("Award Notices", "https://www.ppda.mw/award-notices"),
        ("Open Tenders", "https://www.ppda.mw/tenders")
    ]

    all_extracted = []

    for section_name, url in urls:
        print(f"[*] Fetching {section_name} from {url}...")
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
                parser = TableHTMLParser()
                parser.feed(html)
                
                for table in parser.tables:
                    for row_obj in table:
                        cols = row_obj["data"]
                        links = row_obj["links"]
                        
                        if not cols or len(cols) < 2:
                            continue
                            
                        pdf_link = None
                        for l in links:
                            if l.endswith(".pdf") or "storage/documents" in l:
                                pdf_link = l
                                break
                        if not pdf_link and links:
                            pdf_link = links[0]
                            
                        if pdf_link and not pdf_link.startswith("http"):
                            pdf_link = "https://ppda.mw/" + pdf_link.lstrip("/")
                            
                        all_extracted.append({
                            "Section": section_name,
                            "Title": cols[1] if len(cols) > 1 else cols[0],
                            "Institution": cols[2] if len(cols) > 2 else "N/A",
                            "PDF_Link": pdf_link or "N/A",
                            "All_Columns": " | ".join(cols)
                        })
        except Exception as e:
            print(f"[!] Error fetching {url}: {e}")

    print(f"[+] Total notices extracted: {len(all_extracted)}")
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Section", "Title", "Institution", "PDF_Link", "All_Columns"])
        writer.writeheader()
        writer.writerows(all_extracted)
    print(f"[+] Successfully saved to: {output_csv}")
    return all_extracted

if __name__ == "__main__":
    scrape_ppda_notices()
