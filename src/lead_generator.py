"""
TenderBridge — Lead Card Generator (Phase 2)
Parses award notice PDFs and produces structured lead cards
with company, commodity, contract value, and items needed.

Patterns are tuned to actual PPDA Malawi award notice PDF text format.
"""

import re
import zlib
import os
import urllib.request
import urllib.parse
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# ─── Regex Patterns (tuned to real PPDA PDF text output) ──────────────────────

# Successful bidder patterns — match table cells in government award notices
BIDDER_PATTERNS = [
    # "Successful Bidder   Company Name Ltd" (table header + cell)
    r"Successful\s+Bidder\s+([A-Z][A-Za-z\s\-&,\.]{3,60}?(?:Ltd|Limited|LTD|Company|Dealers|Distributors|Medical|Solutions|Enterprises|Associates|General|Holdings|Group|Services|DEALERS|GENERAL|MEDICAL))[A-Za-z\s\-&,\.]{0,20}",
    # "intends to award the contract as follows: ... Company Name Ltd"
    r"intends?\s+to\s+award\s+(?:the\s+)?(?:procurement\s+)?[Cc]ontract\s+(?:[A-Za-z\s]{0,50}?)([A-Z][A-Za-z\s\-&,\.]{3,50}?(?:Ltd|Limited|LTD|Dealers|Distributors|Medical|Enterprises|Associates|General|GENERAL|DEALERS)[A-Za-z\s\-&,\.]{0,20})",
    # General company name ending in a known business suffix
    r"\b([A-Z][A-Za-z\s\-&,\.]{3,50}?(?:Ltd|Limited|LTD|Company|Dealers|Distributors|Medical Solutions|Enterprises|Associates|General|Holdings|Group|Services|DEALERS|DISTRIBUTORS|GENERAL|MEDICAL))\b",
]

# Contract value patterns — MK and USD formats seen in real Malawi PDFs
VALUE_PATTERNS = [
    r"USD\s*([\d,]+(?:\.\d{2})?)",                            # USD 1,234,567.89
    r"(?:US\$|\$)\s*([\d,]+(?:\.\d{2})?)",                   # $1,234,567.89
    r"MK\s*([\d,\s]+(?:\.\d{2})?)",                          # MK 798,388,436.38
    r"([\d,]+(?:\.\d{2})?)\s*(?:MK|MWK|USD?)\b",             # 1,234,567.89 MK
    r"Contract\s+(?:Amount|Price)\s*\(?[A-Z]+\)?\s*([\d,\s]+(?:\.\d{2})?)",
]

# Item description patterns — matches "Subject of Procurement" and inline descriptions
ITEM_PATTERNS = [
    r"Subject\s+of\s+Procurement\s+([A-Za-z][A-Za-z\s,\-&]{10,100})",
    r"supply\s+(?:and\s+)?delivery\s+of\s+([A-Za-z][A-Za-z\s,\-&]{5,80})",
    r"procurement\s+of\s+([A-Za-z][A-Za-z\s,\-&]{5,80})",
    r"Description\s+of\s+(?:the\s+)?(?:Procurement|Tender)\s+([A-Za-z][A-Za-z\s,\-&]{5,80})",
]

# Tender reference patterns — PPDA Malawi standard reference formats
REF_PATTERNS = [
    # "Reference Number   031 - 01 - HSJF - PU - 23/24 - G - ICB - 56"
    r"Reference\s+Number\s+([\d]{3}[\s\-]+\d{2}[\s\-]+[A-Z\s\-]+[\d/\-]+)",
    # "MOH/NCB/G/GF/C19RM/2025/013"
    r"(MOH\s*/\s*[A-Z]+\s*/\s*[A-Z]+\s*/\s*[A-Z0-9]+(?:\s*/\s*[A-Z0-9]+)+)",
    # "NLGFC - MoH - Works/5/2022"
    r"(NLGFC\s*-\s*MoH\s*-\s*[A-Za-z]+/[\d/]+)",
    # Generic fallback
    r"(?:Bid|Tender|Contract|Procurement)\s+(?:Ref(?:erence)?\s+)?No\.?\s*:?\s*([\w\-/\s]{6,40})",
]


def download_pdf(pdf_url, download_dir="downloads"):
    """Download a PDF from a URL and return the local path. Caches locally."""
    os.makedirs(download_dir, exist_ok=True)
    filename = os.path.basename(urllib.parse.urlparse(pdf_url).path)
    if not filename.endswith(".pdf"):
        filename = filename + ".pdf"
    local_path = os.path.join(download_dir, filename)

    if os.path.exists(local_path):
        return local_path  # Use cached version

    parsed = urllib.parse.urlparse(pdf_url)
    encoded_path = urllib.parse.quote(parsed.path)
    full_url = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, encoded_path, "", "", ""))

    try:
        req = urllib.request.Request(full_url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            content = resp.read()
            with open(local_path, "wb") as f:
                f.write(content)
            return local_path
    except Exception as e:
        return None


def extract_pdf_text(pdf_path):
    """Extract all readable text from a PDF using pure Python zlib decompression."""
    if not os.path.exists(pdf_path):
        return ""

    with open(pdf_path, "rb") as f:
        data = f.read()

    stream_objs = re.findall(rb"stream[\r\n]+(.*?)[\r\n]+endstream", data, re.DOTALL)
    extracted = []

    for stream in stream_objs:
        try:
            decompressed = zlib.decompress(stream)
        except Exception:
            try:
                decompressed = zlib.decompress(stream, -zlib.MAX_WBITS)
            except Exception:
                decompressed = stream

        raw_str = decompressed.decode("latin1", errors="ignore")
        matches = re.findall(r"\(([^()\\]*(?:\\.[^()\\]*)*)\)\s*(?:Tj|\')", raw_str)
        if matches:
            extracted.extend(matches)
        tj_matches = re.findall(r"\[(.*?)\]\s*TJ", raw_str)
        for tj in tj_matches:
            inner = re.findall(r"\(([^()\\]*(?:\\.[^()\\]*)*)\)", tj)
            if inner:
                extracted.append("".join(inner))

    return " ".join([t.replace("\\", "") for t in extracted])


def _clean(s):
    """Normalise whitespace in a string."""
    return re.sub(r"\s+", " ", s).strip()


def parse_lead_from_text(text, metadata=None):
    """
    Parse a structured lead from PDF text.
    Returns a dict with: institution, tender_ref, companies, items, contract_values.
    """
    lead = {
        "tender_ref": None,
        "institution": metadata.get("institution", "Unknown") if metadata else "Unknown",
        "companies": [],
        "items": [],
        "contract_values": [],
        "raw_text_preview": _clean(text[:400]) if text else "",
    }

    if not text:
        return lead

    # ── Tender Reference ──────────────────────────────────────────────────────
    for pattern in REF_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            ref = _clean(matches[0])
            if len(ref) > 4:
                lead["tender_ref"] = ref
                break

    # ── Companies (successful bidders) ────────────────────────────────────────
    found_companies = set()
    for pattern in BIDDER_PATTERNS:
        for match in re.findall(pattern, text, re.IGNORECASE):
            name = _clean(match)
            # Filter out noise: too short, too long, or just "Limited" / "Company"
            if 5 < len(name) < 80 and not name.lower() in {"limited", "company", "ltd", "general"}:
                # Remove trailing junk words
                name = re.sub(r"\s+(of|in|with|and|the|for|at|by|to)\s*$", "", name, flags=re.IGNORECASE)
                name = _clean(name)
                if name:
                    found_companies.add(name)
    lead["companies"] = sorted(found_companies)

    # ── Items / Commodities ───────────────────────────────────────────────────
    found_items = set()
    for pattern in ITEM_PATTERNS:
        for match in re.findall(pattern, text, re.IGNORECASE):
            item = _clean(match).rstrip(".,;")
            if 8 < len(item) < 120:
                found_items.add(item[:100])
    lead["items"] = sorted(found_items)[:5]

    # ── Contract Values ───────────────────────────────────────────────────────
    found_values = []
    for pattern in VALUE_PATTERNS:
        for match in re.findall(pattern, text, re.IGNORECASE):
            val = _clean(match).rstrip(".,;")
            if val and len(val) > 3 and re.search(r"\d", val):
                found_values.append(val)
    # Deduplicate while preserving order
    seen = set()
    unique_values = []
    for v in found_values:
        if v not in seen:
            seen.add(v)
            unique_values.append(v)
    lead["contract_values"] = unique_values[:5]

    return lead


def generate_lead_card(lead, contact=None):
    """Format a lead dict into a human-readable lead card string."""
    W = 66  # Box width

    def row(icon, label, value):
        val_str = str(value) if value else "Not extracted"
        return f"  {icon} {label:<11}: {val_str[:W - 18]}"

    lines = [
        "╔" + "═" * W + "╗",
        "║" + "  🎯 NEW TENDER LEAD".center(W) + "║",
        "╠" + "═" * W + "╣",
        row("🏛 ", "Institution", lead.get("institution")),
        row("📄 ", "Tender Ref ", lead.get("tender_ref") or "Not found"),
        "  " + "─" * (W - 2),
    ]

    companies = lead.get("companies", [])
    if companies:
        lines.append("  🏢 Awardees  :")
        for c in companies[:4]:
            lines.append(f"       → {c[:58]}")
    else:
        lines.append("  🏢 Awardees  : Not extracted from PDF")

    items = lead.get("items", [])
    if items:
        lines.append("  📦 Items     :")
        for item in items[:3]:
            lines.append(f"       → {item[:58]}")
    else:
        lines.append("  📦 Items     : Not extracted from PDF")

    values = lead.get("contract_values", [])
    lines.append(f"  💰 Values    : {', '.join(values[:3]) if values else 'Not extracted'}")

    lines.append("  " + "─" * (W - 2))

    if contact:
        phones  = contact.get("phones", [])
        emails  = contact.get("emails", [])
        websites = contact.get("websites", [])
        lines.append(f"  📞 Phones    : {', '.join(phones[:2]) if phones else 'Not found'}")
        lines.append(f"  📧 Emails    : {', '.join(emails[:2]) if emails else 'Not found'}")
        lines.append(f"  🌐 Website   : {websites[0] if websites else 'Not found'}")
        lines.append(f"  💬 WhatsApp  : {'Try mobile numbers above' if phones else 'Not found'}")
        lines.append("  " + "─" * (W - 2))

    # Auto-generated outreach message
    company_name = companies[0][:35] if companies else "the distributor"
    item_hint    = items[0][:45] if items else "the awarded items"
    ref          = lead.get("tender_ref") or "the recent tender"
    msg = (
        f"Hi, I noticed {company_name} was awarded {ref[:30]}. "
        f"We are a direct medical equipment supplier specialising in "
        f"{item_hint}. We can offer competitive OEM pricing for your "
        f"fulfillment obligations. Would you be open to a quick call this week?"
    )
    lines.append("  📝 OUTREACH MESSAGE:")
    words = msg.split()
    line_buf = "     "
    for word in words:
        if len(line_buf) + len(word) + 1 > W:
            lines.append(line_buf)
            line_buf = "     " + word
        else:
            line_buf += " " + word
    if line_buf.strip():
        lines.append(line_buf)

    lines.append("╚" + "═" * W + "╝")
    return "\n".join(lines)


if __name__ == "__main__":
    for fname in sorted(os.listdir("downloads")):
        if fname.endswith(".pdf"):
            path = os.path.join("downloads", fname)
            print(f"\n{'─'*68}\nFILE: {fname}")
            text = extract_pdf_text(path)
            lead = parse_lead_from_text(text, {"institution": "Ministry of Health, Malawi"})
            print(generate_lead_card(lead))

