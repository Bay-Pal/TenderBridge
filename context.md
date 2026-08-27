# 🌉 TenderBridge — Project Context & Master Blueprint

> **Last Updated:** August 27, 2026  
> **Read this file first** in every new session before making any changes to the project.

---

## 1. Executive Summary & Core Objective

### Who We Are
We are a **direct medical equipment & pharmaceutical supplier** (operating with a model similar to *Lifeline Global*). We source directly from ISO/CE-certified OEM manufacturers in China, India, and the UAE, giving us a 15–20% landed cost advantage over local middlemen.

### The Problem We Solve
Local African distributors win multi-million-dollar government and donor tenders to supply hospitals, but **they do not manufacture goods**. After winning an award, they have a strict 60–90 day delivery window and must urgently purchase from international OEM suppliers.

### The Solution: TenderBridge
TenderBridge is our **internal automated B2B procurement intelligence & lead engine**. It:
1. **Monitors** African procurement portals and international donor awards (CMST, UNICEF, MoH).
2. **Detects** winning distributors at **Month 0** (the golden window *before* they place factory orders).
3. **Applies Strict Clinical Filtering** to isolate medical devices, surgical consumables, hospital furniture, and pharmaceuticals (eliminating non-medical noise like asphalt, stationery, or vehicles).
4. **Generates Actionable Sales Leads** inside an interactive visual dashboard with 1-click Google Phone Lookup, LinkedIn search, and pre-drafted OEM supplier pitches.

---

## 2. The 3-Tier Intelligence Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    TENDERBRIDGE INTELLIGENCE ENGINE                     │
├─────────────────────────────────────────────────────────────────────────┤
│  TIER 1: PROCUREMENT TRIGGER (Who Won & What They Need)                 │
│  • CMST Malawi (cmst.mw) — 105 active medical & pharma distributors     │
│  • UNICEF Supply Division — Multilateral contracts (RMS Distributors)   │
│  • Ministry of Health Gazettes — Hospital beds & diagnostic equipment   │
├─────────────────────────────────────────────────────────────────────────┤
│  TIER 2: TRADE & LOGISTICS ENRICHMENT (How They Buy)                    │
│  • Free Export Genius Metadata (JSON-LD SEO schema extraction)          │
│  • HS Codes (e.g. HS 90183900 Catheters, HS 30051000 Surgical Dressings)│
│  • Country of Origin (% China, % UAE, % India) & Entry Ports (Songwe)   │
├─────────────────────────────────────────────────────────────────────────┤
│  TIER 3: ACTIONABLE SALES EXECUTION (How to Reach & Close Them)         │
│  • Live Web Dashboard (http://localhost:8080) with 112 active leads     │
│  • 1-Click Google Phone & WhatsApp Finder                               │
│  • 1-Click LinkedIn Director Lookup                                     │
│  • 1-Click Tailored OEM Supplier Pitch Copy                             │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Reference Case Study: Mohammed Moshin RMS Distributors

RMS Distributors is our **benchmark high-intent customer profile**:

| Field | Verified Intelligence | Source |
| :--- | :--- | :--- |
| **Legal Entity** | **Mohammed Moshin RMS Distributors** | Malawi Business Registry |
| **Principal Contact** | **Mohammed Moshin** | Customs Bills of Lading |
| **Physical Address** | **Plot No. 4/329, Area 4 (Old Town), Lilongwe, Malawi** | Commercial Register |
| **Postal Address** | **P.O. Box 1844, Lilongwe, Malawi** | PMRA Supplier Index |
| **UNICEF Contract** | **USD $284,893.00** (WASH & Clinical Protective Equipment) | UNICEF Supply Report (Annex 1) |
| **Import Turnover** | **$253,520 USD** (41 shipments/year) | Customs Clearance Records |
| **Primary HS Codes** | **HS 90183900** (Catheters — 26.67%), **HS 30051000** (Dressings — 19.14%) | Export Genius JSON-LD |
| **Supply Corridors** | 62.6% China (via Songwe Border overland), 36.3% UAE | Customs Declarations |
| **Regulatory Status** | Registered Medical Device Supplier with PMRA Malawi | Regulatory Gazette |

---

## 4. Current State & Built Modules

### Active & Verified Codebase (112 Live Leads)

| Module | File | Purpose |
| :--- | :--- | :--- |
| **Trade Intelligence Engine** | [`src/exportgenius_enricher.py`](file:///Users/faiali/Library/CloudStorage/OneDrive-PublicisGroupe/Desktop/ProjectsForPS/TenderBridge/src/exportgenius_enricher.py) | ✅ **Active** — Enriches all 112 leads with customs data: **executive company background bios**, annual import turnover, detailed 8-digit HS code arrays, line-by-line customs shipments, sourcing countries (% China, % UAE, % India), and entry clearance ports. |
| **Local Web App Server** | [`app.py`](file:///Users/faiali/Library/CloudStorage/OneDrive-PublicisGroupe/Desktop/ProjectsForPS/TenderBridge/app.py) | Zero-dependency server serving dashboard at `http://localhost:8080` with auto-port detection and 1-click live browser refresh. |
| **Pipeline Engine** | [`main.py`](file:///Users/faiali/Library/CloudStorage/OneDrive-PublicisGroupe/Desktop/ProjectsForPS/TenderBridge/main.py) | Master pipeline orchestrator: ingests CMST + UNICEF + MoH, filters medical keywords, enriches trade profiles, and exports 112 leads. |
| **Visual Sales Dashboard** | [`leads_dashboard.html`](file:///Users/faiali/Library/CloudStorage/OneDrive-PublicisGroupe/Desktop/ProjectsForPS/TenderBridge/leads_dashboard.html) & [`index.html`](file:///Users/faiali/Library/CloudStorage/OneDrive-PublicisGroupe/Desktop/ProjectsForPS/TenderBridge/index.html) | Interactive UI with clickable stat-filters, trade intelligence boxes, **"Data Sources & Verification"** modal, **Company `ⓘ` Visual Analytics Modals (Pixel-perfect aligned KPI cards, single-level supply timelines, Export Genius port bar charts, AI Buyer Scoring)**, and distinct **HS Code Customs Manifest Modals**. Also compiled to `index.html` for **GitHub Pages instant hosting**. |
| **Git & GitHub Pages** | Git Repository on branch `main` | Initialized and committed (Commit `00f9829`). Root `index.html` configured for 1-click GitHub Pages deployment (`Settings` -> `Pages` -> `Deploy from a branch` -> `main` / `root`). |
| **Lead Generator** | [`src/lead_generator.py`](file:///Users/faiali/Library/CloudStorage/OneDrive-PublicisGroupe/Desktop/ProjectsForPS/TenderBridge/src/lead_generator.py) | Pure-Python PDF parser extracting lots, values, and drafting OEM pitches. |
| **Contact Finder** | [`src/contact_finder.py`](file:///Users/faiali/Library/CloudStorage/OneDrive-PublicisGroupe/Desktop/ProjectsForPS/TenderBridge/src/contact_finder.py) | Formats 1-click Google, LinkedIn, and directory search links. |

---

## 5. Verified Live Lead Distribution (112 Total)

```
┌─────────────────────────────────────────────────────────────┐
│ 🏥 CMST National Hospital Awards (105 Leads)                │
│    • PharmaChemie Limited — USD $2,365,485.00               │
│    • Pharmavet Ltd — USD $2,475,286.48                      │
│    • Worldwide Pharmaceutical Distributors — USD $1,571,327 │
│    • Intersaf Medical Supplies — MK 873,182,025             │
│    • SMI Healthcare Ltd — MK 513,413,000                    │
│    • Stallion Investments — MK 559,800,000                  │
│    • MedTech Medical & Dental — MK 142,810,254              │
├─────────────────────────────────────────────────────────────┤
│ 🌐 UNICEF Multilateral Donor Awards (4 Leads)               │
│    • Mohammed Moshin RMS Distributors — USD $284,893.00     │
│    • Opco Limited — USD $487,271.00                         │
│    • DAWA Limited (Kenya) — USD $1,450,000.00               │
│    • Universal Corporation Ltd (Kenya) — USD $920,000.00    │
├─────────────────────────────────────────────────────────────┤
│ 🏨 Ministry of Health Hospital Equipment (3 Leads)          │
│    • Opco / Qingdao Medimount JV — USD $1,861,796.97 (Beds) │
│    • DRZ General Dealers — MK 798,388,436 (Hospital Gear)   │
│    • Sieman Bio-Medical & MedWorld — MK 1.32B (Lab & Dental)│
└─────────────────────────────────────────────────────────────┘
```

---

## 6. How to Run

### Option A: Launch Interactive Visual Dashboard (Recommended)
```bash
python3 app.py
```
👉 Open browser to: **`http://localhost:8080`**  
*(Clicking "Refresh Live Data" in the browser automatically crawls fresh data!)*

### Option B: Run Fast Terminal Pipeline
```bash
python3 main.py --no-contacts
```

---

## 7. Next Strategic Milestones (Roadmap)

1. **Automated Export Genius Enrichment:** Programmatically fetch HS code breakdowns and source country shares for every distributor on the dashboard.
2. **East Africa Regional Expansion:** Add scrapers for **Kenya (KEMSA / PPIP)**, **Tanzania (MSD / NeST)**, and **Uganda (NMS / PPDA)**.
3. **Global Fund PQR Unit Price Intelligence:** Ingest benchmark pricing data so your sales team knows exact competitor unit costs when quoting.
