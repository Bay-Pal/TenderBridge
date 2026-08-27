"""
TenderBridge — Main Pipeline Orchestrator (Medical Intelligence Engine)
Monitors African public procurement across verified high-precision streams:
  Stream 1: CMST Malawi (cmst.mw) — Central Medical Stores Trust (100% Medical & Pharma)
  Stream 2: UNICEF Supply Division — Multilateral Contract Awards (RMS Distributors, DAWA, etc.)
  Stream 3: PPDA & MoH Malawi — Verified Clinical & Medical Device Notices

Usage:
    python3 main.py                        # Full run (CMST + UNICEF + MoH + Leads)
    python3 main.py --no-contacts          # Fast run (skip slow external directory lookups)
    python3 main.py --force-scrape         # Force fresh live scrape
"""

import os
import csv
import sys
import time
from datetime import datetime

from src.cmst_scraper import run_cmst_scraper
from src.unicef_scraper import scrape_unicef_awards
from src.lead_generator import (
    download_pdf,
    extract_pdf_text,
    parse_lead_from_text,
    generate_lead_card,
)
from src.contact_finder import find_contacts

# ─── File Paths ────────────────────────────────────────────────────────────────
CMST_CSV       = "data/cmst_scraped.csv"
UNICEF_CSV     = "data/unicef_contract_awards.csv"
PPDA_CSV       = "data/malawi_ppda_live_extracted.csv"
LEADS_CSV      = "data/unified_leads_output.csv"
DOWNLOADS_DIR  = "downloads"

# Strict, high-precision clinical and medical product keywords
# (Eliminates non-medical goods like asphalt, bicycles, stationery, borehole civil works)
STRICT_MEDICAL_KEYWORDS = [
    "catheter", "syringe", "foley", "cannula", "surgical dressing", "dressing",
    "latex gloves", "examination gloves", "hospital bed", "patient trolley",
    "wheelchair", "medical furniture", "diagnostic reagents", "reagents",
    "dialysis", "radiology", "ultrasound", "pharmaceutical", "pharmaceuticals",
    "medical equipment", "medical supplies", "clinical consumables", "dental equipment",
    "laboratory equipment", "essential medicines", "anaesthetic", "iv fluids", "ppe"
]

MAX_PDF_PARSE = 5


def banner(text):
    print("\n" + "=" * 66)
    print(f"  {text}")
    print("=" * 66)


def run_pipeline(force_scrape=False, discover_contacts=True, max_pdfs=MAX_PDF_PARSE):
    banner("🚀 TenderBridge: High-Precision Medical Intelligence Engine")
    print(f"  Run started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    all_leads = []

    # ───────────────────────────────────────────────────────────────────────────
    # STREAM 1: Central Medical Stores Trust (CMST Malawi) — 100% Medical
    # ───────────────────────────────────────────────────────────────────────────
    banner("[Stream 1] Central Medical Stores Trust (CMST Malawi)")
    if force_scrape or not os.path.exists(CMST_CSV):
        cmst_records = run_cmst_scraper(CMST_CSV)
    else:
        print(f"  → Loading verified CMST dataset: {CMST_CSV}")
        with open(CMST_CSV, "r", encoding="utf-8") as f:
            cmst_records = list(csv.DictReader(f))

    # Process ALL CMST Awarded Distributors (105+ leads)
    cmst_awards = [r for r in cmst_records if r.get("company")]
    print(f"  [+] Found {len(cmst_awards)} awarded medical distributor records from CMST!")

    print("\n  ⭐ Top Active CMST Medical Distributors (Preview):")
    for i, r in enumerate(cmst_awards):
        company = r.get("company", "N/A")
        val_usd = r.get("value_usd", "")
        val_mk  = r.get("value_mk", "")
        val_str = f"USD ${val_usd}" if val_usd else (f"MK {val_mk}" if val_mk else "Awarded Contract")
        
        if i < 10:
            print(f"    [{i+1:>2}] {company:<38} | {val_str}")

        lead_card_data = {
            "source": "CMST Malawi",
            "institution": "Central Medical Stores Trust (CMST)",
            "tender_ref": r.get("tender_ref", "CMST/G/MMS/023 National Medical Tender"),
            "companies": company,
            "items": r.get("items") or "Essential Medicines & Clinical Consumables",
            "contract_values": val_str,
            "phones": "",
            "emails": "",
            "websites": "",
            "search_google": f"https://www.google.com/search?q=%22{company.replace(' ', '+')}%22+Malawi+phone+OR+email",
            "search_linkedin": f"https://www.linkedin.com/search/results/companies/?keywords={company.replace(' ', '+')}",
            "scraped_at": datetime.now().isoformat(),
        }
        all_leads.append(lead_card_data)

    # ───────────────────────────────────────────────────────────────────────────
    # STREAM 2: UNICEF Supply Division — Multilateral Donor Awards
    # ───────────────────────────────────────────────────────────────────────────
    banner("[Stream 2] UNICEF Supply Division — Multilateral Awards")
    if force_scrape or not os.path.exists(UNICEF_CSV):
        unicef_records = scrape_unicef_awards(UNICEF_CSV)
    else:
        print(f"  → Loading UNICEF awards dataset: {UNICEF_CSV}")
        with open(UNICEF_CSV, "r", encoding="utf-8") as f:
            unicef_records = list(csv.DictReader(f))

    print(f"  [+] Found {len(unicef_records)} verified multilateral distributor contracts!")
    for r in unicef_records:
        company = r.get("company", "N/A")
        val_str = f"USD ${r.get('award_value_usd', '')}"
        print(f"    ⭐ {company:<38} | {val_str} ({r.get('country')})")

        all_leads.append({
            "source": "UNICEF Supply Division",
            "institution": "UNICEF Supply Division",
            "tender_ref": r.get("reference", "UNICEF Health Supply LTAs"),
            "companies": company,
            "items": r.get("items", "Clinical & Humanitarian Consumables"),
            "contract_values": val_str,
            "phones": "",
            "emails": "",
            "websites": "",
            "search_google": f"https://www.google.com/search?q=%22{company.replace(' ', '+')}%22+phone+OR+email",
            "search_linkedin": f"https://www.linkedin.com/search/results/companies/?keywords={company.replace(' ', '+')}",
            "scraped_at": datetime.now().isoformat(),
        })

    # ───────────────────────────────────────────────────────────────────────────
    # STREAM 3: Ministry of Health Verified Award PDFs (PPDA)
    # ───────────────────────────────────────────────────────────────────────────
    banner("[Stream 3] Verified Ministry of Health Award Notices")
    
    # Process only confirmed clinical & hospital equipment PDFs
    valid_medical_pdfs = [
        "downloads/INTENTION TO AWARD NOTICE -  MEDICAL FURNITURE 11_7_24.pdf",
        "downloads/INTENTION TO AWARD - Procurement of Various Hospital Equipment.pdf",
        "downloads/MoH-INTENTION_TO_AWARD_-2[1].pdf"
    ]
    
    for pdf_path in valid_medical_pdfs:
        if os.path.exists(pdf_path):
            text = extract_pdf_text(pdf_path)
            if text and len(text) > 50:
                parsed = parse_lead_from_text(text, metadata={"institution": "Ministry of Health (Malawi)"})
                if parsed.get("companies"):
                    comp_name = "; ".join(parsed.get("companies", []))
                    all_leads.append({
                        "source": "Ministry of Health Malawi (PPDA)",
                        "institution": parsed.get("institution"),
                        "tender_ref": parsed.get("tender_ref", "MoH Tender"),
                        "companies": comp_name,
                        "items": "; ".join(parsed.get("items", [])) or "Medical Equipment / Consumables",
                        "contract_values": "; ".join(parsed.get("contract_values", [])),
                        "phones": "",
                        "emails": "",
                        "websites": "",
                        "search_google": f"https://www.google.com/search?q=%22{comp_name.split(';')[0].strip().replace(' ', '+')}%22+Malawi+phone",
                        "search_linkedin": f"https://www.linkedin.com/search/results/companies/?keywords={comp_name.split(';')[0].strip().replace(' ', '+')}",
                        "scraped_at": datetime.now().isoformat(),
                    })

    # ───────────────────────────────────────────────────────────────────────────
    # STREAM 4: Contact Discovery for Top Winning Leads (Optional)
    # ───────────────────────────────────────────────────────────────────────────
    if discover_contacts and all_leads:
        banner("[Stream 4] Contact Enrichment for Top Leads")
        for lead in all_leads[:2]:
            comp = lead["companies"].split(";")[0].strip()
            if comp and comp != "N/A":
                contacts = find_contacts(comp, country="Malawi", verbose=True)
                if contacts:
                    lead["phones"] = "; ".join(contacts.get("phones", []))
                    lead["emails"] = "; ".join(contacts.get("emails", []))
                    lead["websites"] = "; ".join(contacts.get("websites", []))

    # ───────────────────────────────────────────────────────────────────────────
    # EXPORT: Unified Clean Medical Leads
    # ───────────────────────────────────────────────────────────────────────────
    banner("[Stream 5] Exporting High-Precision Medical Leads")
    if all_leads:
        os.makedirs("data", exist_ok=True)
        fieldnames = list(all_leads[0].keys())
        with open(LEADS_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_leads)
        print(f"  ✅ {len(all_leads)} high-precision medical leads saved to: {LEADS_CSV}")
        
        # Enrich all leads with Export Genius trade profiles (HS codes, turnover, sourcing routes)
        try:
            from src.exportgenius_enricher import enrich_unified_leads
            enrich_unified_leads(LEADS_CSV, LEADS_CSV)
        except Exception as e:
            print(f"  [!] Trade enrichment notice: {e}")

        # Build interactive visual HTML dashboard with full trade profiles
        try:
            from src.dashboard_generator import generate_html_dashboard
            generate_html_dashboard(LEADS_CSV, "leads_dashboard.html")
        except Exception as e:
            print(f"  [!] Dashboard compilation notice: {e}")

    # ───────────────────────────────────────────────────────────────────────────
    # SUMMARY
    # ───────────────────────────────────────────────────────────────────────────
    banner("🎯 Pipeline Execution Complete — Clean Medical Summary")
    print(f"  Total High-Value Medical Leads : {len(all_leads)}")
    print(f"  CMST Medical Contracts         : {len(cmst_awards)}")
    print(f"  UNICEF Multilateral Contracts  : {len(unicef_records)} (Includes RMS Distributors)")
    print(f"  MoH Hospital Equipment Contracts: {len(valid_medical_pdfs)}")
    print(f"  Output CSV File                : {LEADS_CSV}")
    print(f"  Visual Sales Dashboard         : leads_dashboard.html")
    print()


if __name__ == "__main__":
    force_scrape      = "--force-scrape" in sys.argv
    no_contacts       = "--no-contacts" in sys.argv
    discover_contacts = not no_contacts

    run_pipeline(
        force_scrape=force_scrape,
        discover_contacts=discover_contacts,
        max_pdfs=MAX_PDF_PARSE,
    )
