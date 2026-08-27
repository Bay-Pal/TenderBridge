# 🔍 TenderBridge — Portal Research Findings

> **Date:** August 24, 2026  
> **Purpose:** Consolidated findings from investigating CMST, MANEPS, UNICEF, World Bank, Global Fund, and UNGM portals.

---

## 🏆 KEY BREAKTHROUGH: RMS Distributors Found

**RMS Distributors was found in the UNICEF Supply Division records:**

| Source | Award Amount | Category |
| :--- | :--- | :--- |
| **UNICEF Supply Annual Report 2024 (Annex 1)** | **$284,893 USD** | Water & sanitation supplies, shelter/field equipment, clothing/footwear |
| **UNICEF Supply Annual Report 2013** (Opco Ltd) | **$487,271 USD** | Engineering and construction services |

This confirms RMS is bidding and winning international donor tenders — just not on PPDA.

---

## 📊 Source-by-Source Analysis

### 1. CMST (`cmst.mw`) — ⭐ HIGHEST VALUE SOURCE

CMST is the **central government buyer** for ALL medical supplies across Malawi's 28 district hospitals. This is where RMS and similar distributors bid most frequently.

**Key Pages to Scrape:**

| Page | URL | Data |
| :--- | :--- | :--- |
| **Contract Awards** | `cmst.mw/contracts-awards` | Winning bidder, lot, item, value, delivery period |
| **Open Tenders** | `cmst.mw/open-tenders` | Active ICB/NCB invitations with deadlines |
| **Performing Suppliers** | `cmst.mw/performing-suppliers` | Pre-qualified active distributors |
| **Non-Performing Suppliers** | `cmst.mw/non-performing-suppliers` | Blacklisted suppliers |
| **Request for Quotations** | `cmst.mw/request-for-quotations` | Minor supply contracts |

**HTML Structure:** Clean HTML tables with `table-striped table-bordered` classes. Fields: Lot No., Description, Recommended Awardee, Nationality, Contract Value (MWK/USD), Delivery Period.

---

### 2. MANEPS (`maneps.mw`) — ⭐ HAS AN OPEN API!

MANEPS is the national electronic procurement system. **It has native OCDS (Open Contracting Data Standard) JSON API endpoints.**

**API Endpoints:**

| Endpoint | Purpose |
| :--- | :--- |
| `maneps.mw/rms/api/docs` | Swagger/OpenAPI docs |
| `maneps.mw/rms/api/get-records` | OCDS Record Packages (JSON) |
| `maneps.mw/rms/api/get-releases` | OCDS Release Packages (JSON) |
| `maneps.mw/procurement-notice` | Web UI for tender listings |

**Caveat:** Pagination beyond ~6,000 records causes HTTP 504 timeouts. Must filter by date range or entity.

---

### 3. World Bank Major Contract Awards — FREE JSON API

**Endpoint:** `finances.worldbank.org/resource/kdui-wcs3.json`

| Query Parameter | Example |
| :--- | :--- |
| `borrower_country_code=MW` | Filter for Malawi |
| `$limit=100` | Pagination |
| Bulk CSV download | `finances.worldbank.org/api/views/kdui-wcs3/rows.csv?accessType=DOWNLOAD` |

---

### 4. UNICEF Supply Division — Excel Annexes

**Key URLs:**
- Contract Awards Hub: `unicef.org/supply/contract-awards`
- Annual Supply Reports: `unicef.org/supply/supply-reports`
- Price Data Portal: `unicef.org/supply/price-data`

Data is in Excel/PDF annual report annexes with granular supplier names and award amounts.

---

### 5. Global Fund — CSV Data Downloads

**Key URLs:**
- Direct CSV Downloads: `data-service.theglobalfund.org/downloads`
- Malawi Data Explorer: `data.theglobalfund.org/location/MWI`
- PQR Database: Transaction-level procurement with unit costs, manufacturers, product descriptions

---

### 6. UNGM — Developer REST API

**Key URLs:**
- Developer Portal: `ungm.org/Developer/Home` (OAuth2 API)
- Public Contract Awards Search: `ungm.org/Public/ContractAward`
- Statistics Downloads (Excel): `ungm.org/Public/KnowledgeCentre/Statistics`

---

## 🎯 Priority Order for Building Scrapers

| Priority | Source | Why | Difficulty |
| :--- | :--- | :--- | :--- |
| **1** | **CMST** (`cmst.mw/contracts-awards`) | Direct medical procurement body. Clean HTML tables. RMS bids here. | Easy |
| **2** | **MANEPS API** (`maneps.mw/rms/api/`) | Open JSON API with ALL Malawi government procurement. | Medium |
| **3** | **World Bank API** (`kdui-wcs3.json`) | Free JSON API, no auth needed. Health infrastructure awards. | Easy |
| **4** | **UNICEF Supply** (Excel annexes) | Confirmed RMS + Opco in the data. Annual reports. | Medium |
| **5** | **Global Fund** (CSV downloads) | Malawi health grant procurement data. CMST supply lines. | Easy |
| **6** | **UNGM API** | UN agency medical tenders. Requires OAuth2. | Hard |

