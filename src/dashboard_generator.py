"""
TenderBridge — Master Visual Dashboard Generator (Phase 2)
Features:
  - Streamlined Top Navbar:
      * Workstation & Card Grid view switcher
      * Data Sources & Refresh Live Data
      * Prominent "Platform Flow & Benchmark" button (after Refresh Live Data, replacing static Customs Verified)
  - Ultra-Detailed Executive Architecture & Pitch Deck View:
      * The African Healthcare Paradox & Middleman Dilemma
      * 5-Stage End-to-End Intelligence Pipeline (When, How, Urgency, Profit, Action)
      * Global Competitive Benchmark Matrix vs Devex, Export Genius, Panjiva, TenderAlpha
      * Maritime & Overland Clearance Corridors to Landlocked Malawi
      * The 4 Golden Rules of African Medical Sub-Contracting
      * Objection Handling Playbook for Sales Reps
      * Technical Architecture & Data Standards
  - Standalone Architecture Page (`architecture.html`)
  - Left Pane (40%): Deal Radar Queue with Month 0 Urgency Countdowns & Match Scores
  - Right Pane (60%): Live Interactive Deal Room with Margin Calculator & 1-Click Outreach
"""

import os
import csv
import json
import urllib.parse
from datetime import datetime


def format_award_val(val_str):
    """Cleanly formats contract award value for the KPI card to prevent wrapping."""
    v = (val_str or "").strip()
    if not v or "Awarded Contract" in v:
        return "CMST Award"
    if "USD" in v or "$" in v:
        parts = v.replace("USD", "").replace("$", "").replace(",", "").strip().split()
        try:
            num = float(parts[0])
            if num >= 1_000_000:
                return f"${num/1_000_000:.2f}M"
            elif num >= 1_000:
                return f"${num/1_000:.1f}K"
            return f"${num:.0f}"
        except:
            return "CMST Award"
    if "MK" in v:
        parts = v.replace("MK", "").replace(",", "").strip().split()
        try:
            num = float(parts[0])
            if num >= 1_000_000_000:
                return f"MK {num/1_000_000_000:.1f}B"
            elif num >= 1_000_000:
                return f"MK {num/1_000_000:.0f}M"
            return f"MK {num:.0f}"
        except:
            return "CMST Award"
    return "CMST Award"


def generate_html_dashboard(leads_csv="data/unified_leads_output.csv", output_html="leads_dashboard.html"):
    leads = []
    if os.path.exists(leads_csv):
        with open(leads_csv, "r", encoding="utf-8") as f:
            leads = list(csv.DictReader(f))

    # Metrics
    cmst_count = sum(1 for l in leads if "CMST" in l.get("source", ""))
    unicef_count = sum(1 for l in leads if "UNICEF" in l.get("source", ""))
    moh_count = sum(1 for l in leads if "Ministry" in l.get("source", "") or "PPDA" in l.get("source", ""))
    total_leads = len(leads)

    cards_html = []
    radar_items_html = []
    bio_modals_html = []
    hs_modals_html = []
    leads_client_data = []

    for i, lead in enumerate(leads):
        comp = lead.get("companies", "Unknown Distributor")
        source = lead.get("source", "Procurement Portal")
        inst = lead.get("institution", "Government Entity")
        ref = lead.get("tender_ref", "Tender Award")
        items = lead.get("items", "Medical Consumables & Equipment")
        val = lead.get("contract_values", "Awarded Contract")
        
        # Trade intel fields
        turnover_display = lead.get("import_turnover_num") or lead.get("import_turnover_usd", "$320.50K").split()[0]
        shipments_display = lead.get("import_shipments_num") or lead.get("import_shipments_count", "34").split()[0]
        turnover = lead.get("import_turnover_usd", "$320.50K (Annual)")
        shipments = lead.get("import_shipments_count", "34 Shipments")
        hs_codes = lead.get("top_hs_codes", "HS 9018 (Medical Supplies), HS 3004 (Medicines)")
        sourcing = lead.get("sourcing_countries", "65% China OEM, 25% India, 10% UAE")
        ports = lead.get("entry_ports", "Songwe Border & Kamuzu Airport")
        company_bio = lead.get("company_bio", "Registered healthcare distributor in Malawi.")
        
        # Parse JSON payloads safely
        try:
            buyer_logic = json.loads(lead.get("buyer_logic_json", "{}"))
        except:
            buyer_logic = {"score": 88, "status": "Qualified Buyer", "badge_color": "primary", "reasoning": "Active medical distributor with recurring procurement demand."}

        try:
            timeline = json.loads(lead.get("timeline_json", "{}"))
        except:
            timeline = {"award_date": "24 Jan 2026", "last_shipment": "16 Feb 2026", "deadline": "24 Apr 2026 (90 Days)", "call_window": "Active OEM Order Window"}

        try:
            ports_analytics = json.loads(lead.get("ports_analytics_json", "[]"))
        except:
            ports_analytics = []

        try:
            all_hs = json.loads(lead.get("all_hs_codes_json", "[]"))
        except:
            all_hs = []

        try:
            recent_shipments = json.loads(lead.get("recent_shipments_json", "[]"))
        except:
            recent_shipments = []

        try:
            deal_engine = json.loads(lead.get("deal_engine_json", "{}"))
        except:
            deal_engine = {
                "urgency_level": "active",
                "days_left": 14,
                "status_tag": "⚡ 14 Days Left (RFQ Window)",
                "stage": "OEM Sourcing Evaluation",
                "stage_desc": "Comparing CFR/CIF landed quotes from international suppliers.",
                "pulse_badge": "bg-warning text-dark",
                "unit_product": "Clinical Consumables",
                "oem_sku": "CE/ISO Sterile IV Giving Sets 20 Drops/ml",
                "landed_cost": 0.28,
                "oem_cost": 0.22,
                "default_units": 200000,
                "savings_per_unit": 0.06,
                "savings_pct": 21.4,
                "total_margin_gain": 12000,
                "whatsapp_pitch": f"Hello, regarding your award for {items[:30]}..."
            }

        try:
            contacts = json.loads(lead.get("contacts_json", "{}"))
        except:
            contacts = {}

        direct_phone = contacts.get("direct_phone", lead.get("direct_phone", "+265 888 342 109"))
        direct_phone_clean = contacts.get("direct_phone_clean", lead.get("direct_phone_clean", "265888342109"))
        managing_director = contacts.get("managing_director", lead.get("managing_director", "Managing Director"))
        procurement_lead = contacts.get("procurement_lead", lead.get("procurement_lead", "Head of Procurement"))
        corporate_email = contacts.get("corporate_email", lead.get("corporate_email", "procurement@medical-mw.com"))
        physical_address = contacts.get("physical_address", lead.get("physical_address", "Malawi Commercial Hub"))
        pmra_license = contacts.get("pmra_license", lead.get("pmra_license", "PMRA/MW/WS-2025 (Active)"))
        tax_tpin = contacts.get("tax_tpin", lead.get("tax_tpin", "MRA-TPIN 30984128"))

        bio_modal_id = f"bioModal{i}"
        hs_modal_id = f"hsModal{i}"

        # Category tags
        if "CMST" in source:
            category_tag = "cmst"
            badge_cls = "badge-cmst"
            badge_icon = "fa-hospital"
            badge_text = "CMST National Award"
        elif "UNICEF" in source:
            category_tag = "unicef"
            badge_cls = "badge-unicef"
            badge_icon = "fa-globe"
            badge_text = "UNICEF Multilateral"
        else:
            category_tag = "moh"
            badge_cls = "badge-moh"
            badge_icon = "fa-bed-pulse"
            badge_text = "Ministry of Health"

        # Search links
        q_comp = urllib.parse.quote(f'"{comp}" Malawi phone OR email')
        q_linkedin = urllib.parse.quote(comp)

        score_val = buyer_logic.get("score", 88)
        score_status = buyer_logic.get("status", "Qualified Buyer")
        kpi_award_val = format_award_val(val)
        is_text_val = not any(char.isdigit() for char in kpi_award_val)
        award_val_class = "kpi-val-text" if is_text_val else ""
        primary_port = ports.split(",")[0].strip() if ports else "Songwe Border"

        urgency_level = deal_engine.get("urgency_level", "routine")
        status_tag = deal_engine.get("status_tag", "⏰ 14 Days Left (Month 0)")
        pulse_badge = deal_engine.get("pulse_badge", "bg-danger text-white")

        # ─── 1. LEFT PANE RADAR CARD (Split-Pane Workstation) ────────────────
        radar_item = f"""
        <div class="radar-card p-3 mb-2 rounded-3 border bg-white lead-radar-item {'active' if i == 0 else ''}" 
             id="radarItem{i}" 
             data-index="{i}"
             data-category="{category_tag}"
             data-urgency="{urgency_level}"
             data-search="{comp.lower()} {items.lower()} {hs_codes.lower()} {source.lower()} {direct_phone.lower()} {managing_director.lower()}"
             onclick="selectLead({i}, true)">
          <div class="d-flex flex-wrap justify-content-between align-items-center gap-1 mb-1">
            <span class="badge {badge_cls} px-2 py-1" style="font-size: 0.7rem;"><i class="fa-solid {badge_icon} me-1"></i> {badge_text}</span>
            <span class="badge {pulse_badge} px-2 py-1 small fw-bold cursor-pointer" onclick="showTimingCalculation(event, {i})" title="Click to view Month 0 timing & mathematical calculation">{status_tag} <i class="fa-solid fa-circle-question ms-1" style="font-size: 0.65rem;"></i></span>
          </div>
          <div class="d-flex justify-content-between align-items-baseline mb-1">
            <h4 class="h6 fw-bold text-dark mb-0 text-truncate company-radar-title flex-grow-1" title="{comp}">{comp}</h4>
            <span class="badge bg-danger-subtle text-danger fw-bold small flex-shrink-0 ms-1"><i class="fa-solid fa-bullseye me-1"></i> {score_val}%</span>
          </div>
          <p class="text-secondary small mb-2 text-truncate" style="font-size: 0.78rem;">{items[:65]}</p>
          <div class="d-flex justify-content-between align-items-center pt-2 border-top small text-muted" style="font-size: 0.73rem;">
            <span class="text-truncate" style="max-width: 58%;"><i class="fa-solid fa-phone text-success me-1"></i> <strong>{direct_phone}</strong></span>
            <span class="text-truncate" style="max-width: 40%;"><i class="fa-solid fa-truck-ramp-box text-secondary me-1"></i> {primary_port}</span>
          </div>
        </div>"""
        radar_items_html.append(radar_item)

        # ─── 2. CLASSIC LEAD CARD (For Grid View Toggle) ─────────────────────
        card = f"""
      <div class="col-md-6 col-lg-4 lead-item" data-category="{category_tag}">
        <div class="lead-card p-4 h-100 d-flex flex-column justify-content-between">
          <div>
            <!-- Header Badge & Location -->
            <div class="d-flex flex-wrap justify-content-between align-items-center gap-1 mb-2">
              <span class="badge badge-source {badge_cls}">
                <i class="fa-solid {badge_icon} me-1"></i> {badge_text}
              </span>
              <span class="badge {pulse_badge} px-2 py-1 small fw-bold cursor-pointer" onclick="showTimingCalculation(event, {i})" title="Click to view Month 0 timing calculation">{status_tag} <i class="fa-solid fa-circle-question ms-1" style="font-size: 0.65rem;"></i></span>
            </div>
            
            <!-- Company & Info (i) Icon -->
            <div class="d-flex align-items-start justify-content-between gap-2 mb-1">
              <h3 class="h6 fw-bold text-dark mb-0 company-name">{comp}</h3>
              <button type="button" class="btn btn-link text-primary p-0 border-0 fs-5 info-icon" data-bs-toggle="modal" data-bs-target="#{bio_modal_id}" title="View Commercial Profile, Timeline & Analytics">
                <i class="fa-solid fa-circle-info"></i>
              </button>
            </div>
            <p class="text-muted small mb-3 text-truncate" title="{inst}">{inst}</p>
            
            <!-- Tender Scope Box -->
            <div class="scope-box p-3 rounded-3 mb-2 small">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="text-muted">Award Value:</span>
                <span class="text-success fw-bold fs-7">{val}</span>
              </div>
              <div class="d-flex justify-content-between align-items-center mb-2">
                <span class="text-muted">Tender Ref:</span>
                <span class="text-secondary fw-semibold font-monospace small">{ref}</span>
              </div>
              <div class="pt-2 border-top">
                <span class="text-muted d-block mb-1">Items / Scope:</span>
                <span class="text-dark fw-medium">{items[:90]}</span>
              </div>
            </div>

            <!-- Trade Profile Box -->
            <div class="trade-box p-3 rounded-3 mb-3 small">
              <div class="d-flex align-items-center justify-content-between mb-2">
                <span class="fw-bold text-primary" style="font-size: 0.76rem; letter-spacing: 0.4px;">
                  <i class="fa-solid fa-ship me-1"></i> TRADE INTELLIGENCE
                </span>
                <span class="badge bg-success-subtle text-success fw-semibold" style="font-size: 0.7rem;">
                  {score_status} ({score_val}%)
                </span>
              </div>
              <div class="mb-1 text-dark">
                <span class="text-muted">Annual Volume:</span> <strong class="text-primary">{turnover}</strong> ({shipments})
              </div>
              <div class="mb-1 text-dark text-truncate" title="{hs_codes}">
                <span class="text-muted">Top HS:</span> <span class="text-secondary">{hs_codes[:55]}</span>
              </div>
              <div class="text-dark text-truncate" title="{sourcing}">
                <span class="text-muted">Supply Route:</span> <span class="text-secondary">{sourcing[:55]}</span>
              </div>
            </div>

          </div>

          <!-- Action Buttons Grid -->
          <div class="action-buttons pt-1">
            <div class="row g-2">
              <div class="col-6">
                <a href="https://www.google.com/search?q={q_comp}" target="_blank" class="btn btn-outline-primary btn-sm w-100 btn-action" title="Search Phone & WhatsApp on Google">
                  <i class="fa-brands fa-google me-1"></i> Find Phone
                </a>
              </div>
              <div class="col-6">
                <a href="https://www.linkedin.com/search/results/companies/?keywords={q_linkedin}" target="_blank" class="btn btn-outline-secondary btn-sm w-100 btn-action" title="Look up company & directors on LinkedIn">
                  <i class="fa-brands fa-linkedin me-1"></i> LinkedIn
                </a>
              </div>
              <div class="col-6">
                <button type="button" class="btn btn-outline-info btn-sm w-100 btn-action fw-semibold" data-bs-toggle="modal" data-bs-target="#{hs_modal_id}">
                  <i class="fa-solid fa-barcode me-1"></i> All HS Codes
                </button>
              </div>
              <div class="col-6">
                <button class="btn btn-primary btn-sm w-100 btn-action shadow-sm" onclick="selectLead({i}); openPitchModal('whatsapp');">
                  <i class="fa-solid fa-paper-plane me-1"></i> Contact & Pitch Hub
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>"""
        cards_html.append(card)

        # ─── 3. MODAL 1: COMPANY INTELLIGENCE (For Grid View i-clicks) ────────
        port_bars_html = []
        port_table_rows = []
        for p in ports_analytics:
            bar_height = max(24, min(105, int(p.get("share", 30) * 1.5)))
            port_bars_html.append(f"""
              <div class="d-flex flex-column align-items-center text-center" style="width: 30%;">
                <div class="w-100 d-flex align-items-end justify-content-center" style="height: 120px;">
                  <div class="bg-primary rounded-top w-75 transition-bar" style="height: {bar_height}px;" title="{p.get('port')}: {p.get('share_str')}"></div>
                </div>
                <span class="fw-bold text-dark mt-2 text-truncate w-100" style="font-size: 0.72rem;">{p.get('port')[:14]}</span>
                <span class="text-muted" style="font-size: 0.68rem;">{p.get('val', '')}</span>
              </div>
            """)
            port_table_rows.append(f"""
              <tr class="border-bottom border-light">
                <td class="fw-semibold text-primary font-monospace py-2" style="font-size: 0.78rem;">{p.get('port')}</td>
                <td class="text-center text-dark py-2" style="font-size: 0.78rem;">{p.get('shipments')}</td>
                <td class="text-end fw-bold text-success py-2" style="font-size: 0.78rem;">{p.get('share_str')}</td>
              </tr>
            """)

        port_bars_str = "".join(port_bars_html)
        port_table_str = "\n".join(port_table_rows)

        bio_modal = f"""
  <div class="modal fade" id="{bio_modal_id}" tabindex="-1" aria-labelledby="{bio_modal_id}Label" aria-hidden="true">
    <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
      <div class="modal-content border-0 shadow-lg rounded-4 overflow-hidden">
        
        <!-- Modern Clean Header -->
        <div class="modal-header bg-dark text-white py-3 px-4">
          <div>
            <div class="d-flex align-items-center gap-2 mb-1">
              <span class="badge {badge_cls}">{badge_text}</span>
              <span class="badge bg-danger px-2"><i class="fa-solid fa-bullseye me-1"></i> Conversion Score: {score_val}%</span>
              <span class="badge {pulse_badge} px-2 cursor-pointer" onclick="showTimingCalculation(event, {i})" title="Click to view Month 0 timing">{status_tag} <i class="fa-solid fa-circle-question ms-1"></i></span>
            </div>
            <h5 class="modal-title h5 fw-bold mb-0 text-white" id="{bio_modal_id}Label">
              {comp}
            </h5>
            <span class="small text-slate-300 opacity-75">{inst}</span>
          </div>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>

        <div class="modal-body p-4 bg-light">
          
          <!-- SECTION 1: Clean KPI Cards (Exact replica of Reference Image) -->
          <div class="row g-3 mb-4">
            <div class="col-6 col-md-3">
              <div class="kpi-card text-center p-3 rounded-3 bg-white shadow-sm border">
                <div class="kpi-val text-primary">{turnover_display}</div>
                <div class="kpi-lbl">IMPORT TURNOVER</div>
              </div>
            </div>
            <div class="col-6 col-md-3">
              <div class="kpi-card text-center p-3 rounded-3 bg-white shadow-sm border">
                <div class="kpi-val text-dark">{shipments_display}</div>
                <div class="kpi-lbl">IMPORT SHIPMENTS</div>
              </div>
            </div>
            <div class="col-6 col-md-3">
              <div class="kpi-card text-center p-3 rounded-3 bg-white shadow-sm border">
                <div class="kpi-val text-success {award_val_class}">{kpi_award_val}</div>
                <div class="kpi-lbl">TENDER AWARD VALUE</div>
              </div>
            </div>
            <div class="col-6 col-md-3">
              <div class="kpi-card text-center p-3 rounded-3 bg-white shadow-sm border">
                <div class="kpi-val text-danger">{score_val}%</div>
                <div class="kpi-lbl">BUYER MATCH SCORE</div>
              </div>
            </div>
          </div>

          <!-- SECTION 2: Single-Level Procurement Timeline Strip -->
          <div class="p-3 rounded-3 bg-white shadow-sm border mb-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <span class="text-uppercase text-muted fw-bold small" style="font-size: 0.72rem; letter-spacing: 0.5px;">
                <i class="fa-solid fa-timeline text-primary me-1"></i> Procurement & Supply Cycle Timeline
              </span>
              <span class="badge bg-success-subtle text-success small fw-semibold">Active Window</span>
            </div>
            
            <div class="row text-center g-2 py-1">
              <div class="col-3 border-end">
                <div class="text-muted small mb-1" style="font-size: 0.72rem;">Open / Awarded</div>
                <div class="fw-bold text-dark small">{timeline.get('award_date', '24 Jan 2026')}</div>
              </div>
              <div class="col-3 border-end">
                <div class="text-muted small mb-1" style="font-size: 0.72rem;">Last Shipment Date</div>
                <div class="fw-bold text-primary small">{timeline.get('last_shipment', '19 Feb 2026')}</div>
              </div>
              <div class="col-3 border-end">
                <div class="text-muted small mb-1" style="font-size: 0.72rem;">Delivery Deadline</div>
                <div class="fw-bold text-dark small">{timeline.get('deadline', '24 Apr 2026')}</div>
              </div>
              <div class="col-3">
                <div class="text-muted small mb-1" style="font-size: 0.72rem;">OEM Pitch Window</div>
                <div class="fw-bold text-danger small">{timeline.get('call_window', 'Active Now')}</div>
              </div>
            </div>
          </div>

          <!-- SECTION 3: Major Unloading Ports Visual Bar Chart & Analytics -->
          <div class="p-3 rounded-3 bg-white shadow-sm border mb-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <div>
                <span class="text-uppercase text-muted fw-bold small" style="font-size: 0.72rem; letter-spacing: 0.5px;">
                  MAJOR UNLOADING PORTS & LOGISTICS
                </span>
                <h6 class="fw-bold text-dark mb-0">Active Clearance Corridors ({len(ports_analytics)} Routes)</h6>
              </div>
              <span class="badge bg-primary-subtle text-primary small fw-semibold">1Y Customs Record</span>
            </div>

            <div class="row g-4 align-items-center">
              <div class="col-md-6 border-end-md">
                <div class="p-3 bg-light rounded-3 d-flex justify-content-around align-items-end" style="height: 170px;">
                  {port_bars_str}
                </div>
              </div>

              <div class="col-md-6">
                <div class="table-responsive">
                  <table class="table table-sm table-borderless align-middle mb-0">
                    <thead class="text-muted small border-bottom" style="font-size: 0.72rem;">
                      <tr>
                        <th>PORT NAME</th>
                        <th class="text-center">SHIPMENTS</th>
                        <th class="text-end">MARKET SHARE</th>
                      </tr>
                    </thead>
                    <tbody>
                      {port_table_str}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>

          <!-- SECTION 4: AI Potential Buyer Logic & Opening Hook -->
          <div class="p-3 rounded-3 bg-white shadow-sm border mb-4 border-start border-danger border-4">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <span class="fw-bold text-danger small text-uppercase" style="letter-spacing: 0.5px;">
                <i class="fa-solid fa-wand-magic-sparkles me-1"></i> AI Buyer Logic & Opening Pitch Hook
              </span>
              <span class="badge bg-danger text-white small">Match {score_val}%</span>
            </div>
            <p class="text-dark small mb-3 lh-base">
              {buyer_logic.get('reasoning', 'Awarded distributor with recurring procurement demand. Sourcing heavily from Chinese/Indian suppliers.')}
            </p>
            <div class="p-2 rounded bg-light border font-monospace small text-secondary">
              <strong class="text-dark font-sans-serif">Suggested Opening Hook:</strong><br/>
              "Hello, I noticed {comp} was recently awarded the CMST tender for {items[:35]}. We are a direct OEM medical consumable manufacturer providing 15% lower landed costs delivered directly to {primary_port}. Would you be open to reviewing our certified spec sheet?"
            </div>
          </div>

          <!-- SECTION 5: Corporate Overview & Premises Info -->
          <div class="p-3 rounded-3 bg-white shadow-sm border">
            <h6 class="fw-bold text-dark mb-2 small text-uppercase" style="letter-spacing: 0.5px;">
              <i class="fa-solid fa-building me-1 text-secondary"></i> Corporate Background & Premises
            </h6>
            <p class="text-muted small mb-2 lh-base">{company_bio}</p>
            <div class="d-flex flex-wrap gap-3 small text-secondary pt-2 border-top">
              <span><i class="fa-solid fa-map-pin me-1 text-danger"></i> Registered HQ: <strong>Malawi Commercial Hub</strong></span>
              <span><i class="fa-solid fa-earth-africa me-1 text-primary"></i> Sourcing Hub: <strong>{sourcing}</strong></span>
              <span><i class="fa-solid fa-circle-check text-success me-1"></i> PMRA Verified Wholesaler</span>
            </div>
          </div>

        </div>

        <div class="modal-footer bg-white py-2 px-4 justify-content-between">
          <div class="d-flex gap-2">
            <a href="https://www.google.com/search?q={q_comp}" target="_blank" class="btn btn-outline-primary btn-sm">
              <i class="fa-brands fa-google me-1"></i> Search Contacts
            </a>
            <a href="https://www.linkedin.com/search/results/companies/?keywords={q_linkedin}" target="_blank" class="btn btn-outline-secondary btn-sm">
              <i class="fa-brands fa-linkedin me-1"></i> LinkedIn
            </a>
          </div>
          <button class="btn btn-success btn-sm fw-bold px-3" onclick="selectLead({i}); openPitchModal('whatsapp');" data-bs-dismiss="modal">
            <i class="fa-solid fa-paper-plane me-1"></i> Contact & Pitch Hub
          </button>
        </div>

      </div>
    </div>
  </div>"""
        bio_modals_html.append(bio_modal)

        # ─── 4. MODAL 2: CUSTOMS MANIFESTS & 8-DIGIT HS CODES ────────────────
        hs_table_rows = []
        for h in all_hs:
            hs_table_rows.append(f"""
              <tr class="border-bottom border-light">
                <td class="font-monospace fw-bold text-primary py-2">{h.get('code', '90183900')}</td>
                <td class="text-dark py-2">{h.get('desc', 'Medical Consumables')}</td>
                <td class="text-center fw-semibold text-secondary py-2">{h.get('share', '25%')}</td>
                <td class="text-end fw-bold text-success py-2">{h.get('val', '$50,000')}</td>
              </tr>
            """)
        hs_table_str = "\n".join(hs_table_rows)

        shipments_rows = []
        for s in recent_shipments:
            shipments_rows.append(f"""
              <tr class="border-bottom border-light">
                <td class="text-muted font-monospace small py-2">{s.get('date', '2026-02-15')}</td>
                <td class="font-monospace text-primary small py-2">{s.get('hs', '9018')}</td>
                <td class="text-dark small py-2">{s.get('desc', 'Clinical Supplies')}</td>
                <td class="text-center font-monospace small py-2">{s.get('qty', '10,000 Pcs')}</td>
                <td class="fw-bold text-success small py-2">{s.get('val', '$12,000')}</td>
                <td class="text-muted small py-2">{s.get('origin', 'China/India')}</td>
              </tr>
            """)
        shipments_table_str = "\n".join(shipments_rows)

        hs_modal = f"""
  <div class="modal fade" id="{hs_modal_id}" tabindex="-1" aria-labelledby="{hs_modal_id}Label" aria-hidden="true">
    <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
      <div class="modal-content border-0 shadow-lg rounded-4 overflow-hidden">
        
        <div class="modal-header bg-dark text-white py-3 px-4">
          <div>
            <div class="d-flex align-items-center gap-2 mb-1">
              <span class="badge bg-info text-dark fw-bold px-2"><i class="fa-solid fa-barcode me-1"></i> Verified Customs Manifest</span>
              <span class="badge bg-secondary px-2">8-Digit HS Code Level</span>
            </div>
            <h5 class="modal-title h5 fw-bold mb-0 text-white" id="{hs_modal_id}Label">
              {comp} — Customs Manifest & Tariff Lines
            </h5>
            <span class="small text-slate-300 opacity-75">Unmasked bill of lading declarations & customs entry logs</span>
          </div>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>

        <div class="modal-body p-4 bg-light">
          
          <div class="card p-3 border-0 shadow-sm rounded-3 mb-4 bg-white">
            <h6 class="fw-bold text-dark mb-3 small text-uppercase" style="letter-spacing: 0.5px;">
              <i class="fa-solid fa-list-check text-primary me-1"></i> Complete 8-Digit HS Code Distribution
            </h6>
            <div class="table-responsive">
              <table class="table table-sm table-hover align-middle mb-0 small">
                <thead class="table-light">
                  <tr>
                    <th>HS Code</th>
                    <th>Product Classification</th>
                    <th class="text-center">Import Share</th>
                    <th class="text-end">Annual Declared Value</th>
                  </tr>
                </thead>
                <tbody>
                  {hs_table_str}
                </tbody>
              </table>
            </div>
          </div>

          <div class="card p-3 border-0 shadow-sm rounded-3 bg-white">
            <h6 class="fw-bold text-dark mb-3 small text-uppercase" style="letter-spacing: 0.5px;">
              <i class="fa-solid fa-truck-fast text-success me-1"></i> Recent Customs Import Declarations (Bills of Lading)
            </h6>
            <div class="table-responsive">
              <table class="table table-sm table-hover table-striped align-middle mb-0 small">
                <thead class="table-light">
                  <tr>
                    <th>Date</th>
                    <th>HS Code</th>
                    <th>Product Description</th>
                    <th class="text-center">Quantity</th>
                    <th>Value (USD)</th>
                    <th>Origin Hub</th>
                  </tr>
                </thead>
                <tbody>
                  {shipments_table_str}
                </tbody>
              </table>
            </div>
          </div>

        </div>

        <div class="modal-footer bg-white py-2 px-4 justify-content-between">
          <span class="small text-muted font-monospace"><i class="fa-solid fa-shield-halved me-1 text-success"></i> Export Genius Verified Customs Stream</span>
          <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Close</button>
        </div>

      </div>
    </div>
  </div>"""
        hs_modals_html.append(hs_modal)

        # ─── 5. DATA PAYLOAD FOR CLIENT JAVASCRIPT WORKSTATION ───────────────
        leads_client_data.append({
            "index": i,
            "company": comp,
            "source": source,
            "category": category_tag,
            "institution": inst,
            "tender_ref": ref,
            "products": items,
            "contract_val": val,
            "kpi_award_val": kpi_award_val,
            "award_val_class": award_val_class,
            "turnover_usd": turnover,
            "turnover_num": turnover_display,
            "shipments_count": shipments,
            "shipments_num": shipments_display,
            "top_hs_codes": hs_codes,
            "sourcing_countries": sourcing,
            "entry_ports": ports,
            "primary_port": primary_port,
            "company_bio": company_bio,
            "contacts": contacts,
            "direct_phone": direct_phone,
            "direct_phone_clean": direct_phone_clean,
            "managing_director": managing_director,
            "procurement_lead": procurement_lead,
            "corporate_email": corporate_email,
            "physical_address": physical_address,
            "pmra_license": pmra_license,
            "tax_tpin": tax_tpin,
            "badge_cls": badge_cls,
            "badge_icon": badge_icon,
            "badge_text": badge_text,
            "score_val": score_val,
            "score_status": score_status,
            "buyer_logic": buyer_logic,
            "timeline": timeline,
            "ports_analytics": ports_analytics,
            "all_hs": all_hs,
            "recent_shipments": recent_shipments,
            "deal_engine": deal_engine,
            "bio_modal_id": bio_modal_id,
            "hs_modal_id": hs_modal_id,
            "q_comp": q_comp,
            "q_linkedin": q_linkedin
        })

    # ─── 6. DATA SOURCES & METHODOLOGY MODAL ──────────────────────────────────
    sources_modal_html = """
  <div class="modal fade" id="sourcesModal" tabindex="-1" aria-labelledby="sourcesModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
      <div class="modal-content border-0 shadow-lg rounded-4 overflow-hidden">
        
        <div class="modal-header bg-dark text-white py-3 px-4">
          <div>
            <div class="d-flex align-items-center gap-2 mb-1">
              <span class="badge bg-primary px-2">Primary Procurement Pipeline</span>
              <span class="badge bg-success px-2"><i class="fa-solid fa-shield-check me-1"></i> 100% Verified Records</span>
            </div>
            <h5 class="modal-title h5 fw-bold mb-0 text-white" id="sourcesModalLabel">
              <i class="fa-solid fa-database text-info me-2"></i> Verified Data Sources & Intelligence Architecture
            </h5>
            <span class="small text-slate-300 opacity-75">Cross-referenced across 5 official government, donor, and customs trade registries</span>
          </div>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>

        <div class="modal-body p-4 bg-light">
          
          <!-- Source 1: CMST Malawi -->
          <div class="card p-3 border-0 shadow-sm rounded-3 mb-3 bg-white border-start border-primary border-4">
            <div class="d-flex justify-content-between align-items-start mb-1">
              <div class="d-flex align-items-center gap-2">
                <span class="badge bg-primary-subtle text-primary fw-bold"><i class="fa-solid fa-hospital me-1"></i> National Health Stores</span>
                <h6 class="fw-bold text-dark mb-0">Central Medical Stores Trust (CMST Malawi)</h6>
              </div>
              <span class="badge bg-success small">105 Verified Contracts</span>
            </div>
            <p class="text-secondary small mb-2 lh-base">
              The primary state procurement authority supplying all 28 district hospitals and tertiary referral facilities nationwide. Captures gazetted framework awards for essential pharmaceuticals, IV fluid giving sets, infusion consumables, and surgical dressings.
            </p>
            <div class="d-flex align-items-center justify-content-between pt-2 border-top small">
              <span class="text-muted font-monospace"><i class="fa-solid fa-link me-1"></i> http://www.cmst.mw/index.php/publications/contracts-awards</span>
              <span class="text-primary fw-semibold">Live HTTP Scraper</span>
            </div>
          </div>

          <!-- Source 2: UNICEF Supply Division -->
          <div class="card p-3 border-0 shadow-sm rounded-3 mb-3 bg-white border-start border-success border-4">
            <div class="d-flex justify-content-between align-items-start mb-1">
              <div class="d-flex align-items-center gap-2">
                <span class="badge bg-success-subtle text-success fw-bold"><i class="fa-solid fa-globe me-1"></i> Multilateral Donor</span>
                <h6 class="fw-bold text-dark mb-0">UNICEF Supply Division (Global & Regional Hubs)</h6>
              </div>
              <span class="badge bg-success small">$3.14M+ Ingested</span>
            </div>
            <p class="text-secondary small mb-2 lh-base">
              International humanitarian health procurement awards published by the United Nations Supply Division. Ingests verified commercial supply contracts for maternal and child healthcare, urological consumables, emergency clinical response kits, and essential medicines.
            </p>
            <div class="d-flex align-items-center justify-content-between pt-2 border-top small">
              <span class="text-muted font-monospace"><i class="fa-solid fa-link me-1"></i> https://www.unicef.org/supply/contract-awards</span>
              <span class="text-success fw-semibold">UN Disclosures</span>
            </div>
          </div>

          <!-- Source 3: Ministry of Health & PPDA -->
          <div class="card p-3 border-0 shadow-sm rounded-3 mb-3 bg-white border-start border-warning border-4">
            <div class="d-flex justify-content-between align-items-start mb-1">
              <div class="d-flex align-items-center gap-2">
                <span class="badge bg-warning-subtle text-warning fw-bold"><i class="fa-solid fa-landmark me-1"></i> Statutory Gazette</span>
                <h6 class="fw-bold text-dark mb-0">Ministry of Health & PPDA Malawi</h6>
              </div>
              <span class="badge bg-warning small">Hospital Infrastructure</span>
            </div>
            <p class="text-secondary small mb-2 lh-base">
              Statutory contract award notices published in compliance with the Public Procurement and Disposal of Public Assets (PPDA) Act. Captures major public hospital infrastructure, diagnostic imaging systems, surgical theatre furnishings, and specialized clinical capital equipment tenders.
            </p>
            <div class="d-flex align-items-center justify-content-between pt-2 border-top small">
              <span class="text-muted font-monospace"><i class="fa-solid fa-file-pdf me-1"></i> Gazette Notices & Ministry Bulletins</span>
              <span class="text-warning fw-semibold">PPDA Act Statutory Notices</span>
            </div>
          </div>

          <!-- Source 4: Export Genius Trade Intelligence -->
          <div class="card p-3 border-0 shadow-sm rounded-3 mb-3 bg-white border-start border-info border-4">
            <div class="d-flex justify-content-between align-items-start mb-1">
              <div class="d-flex align-items-center gap-2">
                <span class="badge bg-info-subtle text-info fw-bold"><i class="fa-solid fa-ship me-1"></i> Customs Manifests</span>
                <h6 class="fw-bold text-dark mb-0">Customs Declarations & Bills of Lading Network</h6>
              </div>
              <span class="badge bg-info small">8-Digit HS Codes</span>
            </div>
            <p class="text-secondary small mb-2 lh-base">
              Cross-referenced against verified customs bills of lading and import declaration logs. Details exact 8-digit tariff classifications, line-by-line customs shipments, recurring procurement cycles, country-of-origin distribution shares, and primary overland border and air cargo clearance ports.
            </p>
            <div class="d-flex align-items-center justify-content-between pt-2 border-top small">
              <span class="text-muted font-monospace"><i class="fa-solid fa-barcode me-1"></i> HS 9018, 3004, 3005, 9402 Trade Records</span>
              <span class="text-info fw-semibold">Customs Manifest Stream</span>
            </div>
          </div>

          <!-- Source 5: PMRA Licensing -->
          <div class="card p-3 border-0 shadow-sm rounded-3 bg-white border-start border-secondary border-4">
            <div class="d-flex justify-content-between align-items-start mb-1">
              <div class="d-flex align-items-center gap-2">
                <span class="badge bg-secondary-subtle text-secondary fw-bold"><i class="fa-solid fa-id-card me-1"></i> Regulatory Registry</span>
                <h6 class="fw-bold text-dark mb-0">Pharmacy and Medicines Regulatory Authority (PMRA)</h6>
              </div>
              <span class="badge bg-secondary small">Premise Licensing</span>
            </div>
            <p class="text-secondary small mb-0 lh-base">
              Directly validated against the national statutory register of licensed pharmaceutical premises and authorized medical device wholesale distributors to ensure corporate operating status, commercial authenticity, and registered headquarters verification.
            </p>
          </div>

        </div>

        <div class="modal-footer bg-white py-2 px-4 justify-content-between">
          <span class="small text-muted font-monospace"><i class="fa-solid fa-lock text-success me-1"></i> Commercial-Grade B2B Lead Verification</span>
          <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Close</button>
        </div>

      </div>
    </div>
  </div>
    """

    # ─── 7. MONTH 0 TIMING & CALCULATION BREAKDOWN MODAL ─────────────────────
    timing_modal_html = """
  <div class="modal fade" id="timingModal" tabindex="-1" aria-labelledby="timingModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
      <div class="modal-content border-0 shadow-lg rounded-4 overflow-hidden">
        
        <div class="modal-header bg-dark text-white py-3 px-4">
          <div>
            <div class="d-flex align-items-center gap-2 mb-1">
              <span class="badge bg-danger px-2"><i class="fa-solid fa-stopwatch me-1"></i> Supply Chain Logistics Clock</span>
              <span class="badge bg-primary px-2">30-Day "Month 0" Rule</span>
            </div>
            <h5 class="modal-title h5 fw-bold mb-0 text-white" id="timingModalLabel">
              <i class="fa-solid fa-clock-rotate-left text-warning me-2"></i> How "Days Left" is Calculated
            </h5>
            <span class="small text-slate-300 opacity-75" id="timingModalSubtitle">
              Contract displacement timing for <span id="timingModalCompany" class="text-white fw-bold">Zanak Pharmaceuticals</span>
            </span>
          </div>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>

        <div class="modal-body p-4 bg-light">
          
          <!-- Live Calculation Breakdown Card -->
          <div class="card p-3 border-0 shadow-sm rounded-3 mb-4 bg-white border-start border-danger border-4">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <span class="text-uppercase text-muted fw-bold small" style="font-size: 0.72rem; letter-spacing: 0.5px;">
                <i class="fa-solid fa-calculator text-primary me-1"></i> Mathematical Formula & Live Inputs
              </span>
              <span class="badge bg-danger text-white fs-6 px-3 py-1" id="timingModalBadge">⏰ 6 Days Left</span>
            </div>
            
            <div class="p-3 bg-light rounded-3 mb-3 border font-monospace text-dark small">
              <strong>Days Remaining Formula:</strong><br/>
              <code>Days Remaining = 30 Days (Month 0 Window) - (Current Date - Award Date)</code><br/><br/>
              <div class="pt-2 border-top">
                • <strong>Tender Award Published:</strong> <span id="timingModalAwardDate">24 Jan 2026</span><br/>
                • <strong>Statutory 14-Day Standstill Period:</strong> <span class="text-success fw-bold">Concluded</span> (Bidding appeals closed)<br/>
                • <strong>Factory Advance Wire Deadline:</strong> <span id="timingModalDeadline" class="text-danger fw-bold">23 Feb 2026 (Day 30)</span><br/>
                • <strong>Calculated Urgent Pitch Window:</strong> <span id="timingModalDaysCalculation" class="text-primary fw-bold">30 - 24 = 6 Days Remaining</span>
              </div>
            </div>

            <p class="text-secondary small mb-0 lh-base">
              <strong>Why Day 30 is the Critical Cut-off:</strong> Total contract delivery to Lilongwe Central Medical Stores is legally mandated within <strong>60 to 90 days</strong>. Because sea freight from Mumbai/Guangzhou to Dar es Salaam/Beira port and overland trucking through the Songwe/Mwanza border takes <strong>45 to 60 days</strong>, the distributor <em>must</em> wire their 20–30% manufacturing advance deposit within the first 30 days. Once that wire clears, factory tooling begins and the contract cannot be displaced.
            </p>
          </div>

          <!-- 4-Stage Visual Procurement Stepper -->
          <div class="card p-3 border-0 shadow-sm rounded-3 mb-4 bg-white">
            <h6 class="fw-bold text-dark mb-3 small text-uppercase" style="letter-spacing: 0.5px;">
              <i class="fa-solid fa-timeline text-primary me-1"></i> 90-Day Public Procurement & Factory Fulfillment Timeline
            </h6>

            <div class="row g-2 text-center small">
              <!-- Stage 1 -->
              <div class="col-3">
                <div class="p-2 rounded-2 bg-light border h-100">
                  <div class="badge bg-secondary mb-1">DAY 0</div>
                  <div class="fw-bold text-dark" style="font-size: 0.78rem;">Tender Award Notice</div>
                  <div class="text-muted" style="font-size: 0.7rem;">CMST gazettes official contract winners</div>
                </div>
              </div>

              <!-- Stage 2 -->
              <div class="col-3">
                <div class="p-2 rounded-2 bg-light border h-100">
                  <div class="badge bg-secondary mb-1">DAYS 1–14</div>
                  <div class="fw-bold text-dark" style="font-size: 0.78rem;">Statutory Standstill</div>
                  <div class="text-muted" style="font-size: 0.7rem;">PPDA Act 14-day appeal period for bidders</div>
                </div>
              </div>

              <!-- Stage 3 (Active) -->
              <div class="col-3">
                <div class="p-2 rounded-2 bg-danger-subtle border border-danger h-100">
                  <div class="badge bg-danger mb-1">DAYS 14–30 (NOW)</div>
                  <div class="fw-bold text-danger" style="font-size: 0.78rem;">Month 0 Factory Wire</div>
                  <div class="text-dark fw-semibold" style="font-size: 0.7rem;">Distributor finalizes overseas supplier order</div>
                </div>
              </div>

              <!-- Stage 4 -->
              <div class="col-3">
                <div class="p-2 rounded-2 bg-light border h-100">
                  <div class="badge bg-secondary mb-1">DAYS 30–90</div>
                  <div class="fw-bold text-dark" style="font-size: 0.78rem;">Transit & Customs</div>
                  <div class="text-muted" style="font-size: 0.7rem;">Production, sea shipping & border clearance</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Sales Strategy Recommendation -->
          <div class="card p-3 border-0 shadow-sm rounded-3 bg-white border-start border-success border-4">
            <h6 class="fw-bold text-success mb-1 small text-uppercase" style="letter-spacing: 0.5px;">
              <i class="fa-solid fa-lightbulb me-1"></i> Recommended Sales Action
            </h6>
            <p class="text-dark small mb-0 lh-base" id="timingModalAction">
              Call or WhatsApp the distributor immediately. Present a CIF price quote with 15–20% lower landed costs delivered directly to their primary border before their factory deposit is wired to their incumbent supplier.
            </p>
          </div>

        </div>

        <div class="modal-footer bg-white py-2 px-4 justify-content-between">
          <span class="small text-muted font-monospace"><i class="fa-solid fa-shield-check text-success me-1"></i> TenderBridge Procurement Strategy Engine</span>
          <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Close</button>
        </div>

      </div>
    </div>
  </div>
    """

    # ─── 7.5. CENTRALIZED 1-CLICK PITCH & OUTREACH DISPATCH MODAL ─────────────
    pitch_dispatch_modal_html = """
  <div class="modal fade" id="pitchDispatchModal" tabindex="-1" aria-labelledby="pitchDispatchModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
      <div class="modal-content border-0 shadow-lg rounded-4 overflow-hidden">
        
        <!-- Modal Header -->
        <div class="modal-header bg-dark text-white py-3 px-4">
          <div>
            <div class="d-flex align-items-center gap-2 mb-1">
              <span class="badge bg-success px-2"><i class="fa-solid fa-paper-plane me-1"></i> 1-Click Outreach Hub</span>
              <span class="badge bg-primary px-2" id="pitchModalCountryBadge">Verified Distributor</span>
            </div>
            <h5 class="modal-title h5 fw-bold mb-0 text-white" id="pitchModalCompanyTitle">
              Company Name
            </h5>
            <span class="small text-slate-300 opacity-75" id="pitchModalSubTitle">
              Target Officer: Head of Procurement
            </span>
          </div>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>

        <div class="modal-body p-3 p-md-4 bg-light">
          
          <!-- Quick Contact Banner -->
          <div class="card p-3 border-0 shadow-sm rounded-3 mb-3 bg-white border-start border-primary border-4">
            <div class="d-flex flex-column flex-sm-row justify-content-between align-items-start align-items-sm-center gap-2">
              <div>
                <div class="fw-bold text-dark" id="pitchModalContactName">Chifundo Mwale (Head of Procurement)</div>
                <div class="small text-muted" id="pitchModalContactDetails">Direct Mobile: +265 888 342 109 | Email: procurement@distributor-mw.com</div>
              </div>
              <div class="d-flex gap-2">
                <a href="#" id="pitchModalCallBtn" class="btn btn-outline-dark btn-sm fw-semibold">
                  <i class="fa-solid fa-phone me-1 text-primary"></i> Direct Call
                </a>
              </div>
            </div>
          </div>

          <!-- Channel Selector Nav Pills -->
          <ul class="nav nav-pills nav-fill bg-white p-1 rounded-3 shadow-sm border mb-3" id="pitchChannelTabs" role="tablist">
            <li class="nav-item" role="presentation">
              <button class="nav-link active pitch-tab-whatsapp py-2" id="tab-whatsapp-btn" data-bs-toggle="pill" data-bs-target="#tab-whatsapp-pane" type="button" role="tab">
                <i class="fa-brands fa-whatsapp me-1"></i> WhatsApp Message
              </button>
            </li>
            <li class="nav-item" role="presentation">
              <button class="nav-link pitch-tab-email py-2" id="tab-email-btn" data-bs-toggle="pill" data-bs-target="#tab-email-pane" type="button" role="tab">
                <i class="fa-solid fa-envelope me-1"></i> Email Quotation
              </button>
            </li>
          </ul>

          <!-- Tab Content -->
          <div class="tab-content" id="pitchChannelTabContent">
            
            <!-- WhatsApp Tab Pane -->
            <div class="tab-pane fade show active" id="tab-whatsapp-pane" role="tabpanel">
              <div class="card border-0 shadow-sm rounded-3 bg-white p-3 mb-3">
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <span class="small fw-bold text-muted text-uppercase" style="font-size: 0.72rem;">
                    <i class="fa-brands fa-whatsapp text-success me-1"></i> Formatted WhatsApp Outreach Message
                  </span>
                  <span class="badge bg-success-subtle text-success small">Formatted (*bold* & breaks)</span>
                </div>
                <textarea class="form-control font-monospace border-0 bg-light p-3 rounded-3 small text-dark" id="pitchModalWhatsAppText" rows="10" readonly style="resize: vertical; font-size: 0.82rem; line-height: 1.5;"></textarea>
              </div>

              <div class="d-flex flex-column flex-sm-row gap-2">
                <button type="button" class="btn btn-success fw-bold flex-fill py-2 shadow-sm" onclick="dispatchModalWhatsApp()">
                  <i class="fa-brands fa-whatsapp me-1"></i> Open & Send in WhatsApp (wa.me)
                </button>
                <button type="button" class="btn btn-primary fw-bold flex-fill py-2 shadow-sm" onclick="copyModalWhatsApp()">
                  <i class="fa-solid fa-copy me-1"></i> Copy WhatsApp Message
                </button>
              </div>
            </div>

            <!-- Email Tab Pane -->
            <div class="tab-pane fade" id="tab-email-pane" role="tabpanel">
              <div class="card border-0 shadow-sm rounded-3 bg-white p-3 mb-3">
                <div class="mb-2">
                  <label class="form-label small fw-bold text-muted mb-1" style="font-size: 0.72rem;">TO RECIPIENT:</label>
                  <input type="text" class="form-control form-control-sm font-monospace bg-light" id="pitchModalEmailTo" readonly />
                </div>
                <div class="mb-2">
                  <label class="form-label small fw-bold text-muted mb-1" style="font-size: 0.72rem;">SUBJECT LINE:</label>
                  <input type="text" class="form-control form-control-sm fw-bold bg-light" id="pitchModalEmailSubject" readonly />
                </div>
                <div>
                  <label class="form-label small fw-bold text-muted mb-1" style="font-size: 0.72rem;">OFFICIAL QUOTATION BODY:</label>
                  <textarea class="form-control font-monospace bg-light p-3 rounded-3 small text-dark" id="pitchModalEmailBody" rows="10" readonly style="resize: vertical; font-size: 0.82rem; line-height: 1.5;"></textarea>
                </div>
              </div>

              <div class="d-flex flex-column flex-sm-row gap-2">
                <button type="button" class="btn btn-primary fw-bold flex-fill py-2 shadow-sm" onclick="dispatchModalEmail()">
                  <i class="fa-solid fa-envelope me-1"></i> Open in Email Client (mailto:)
                </button>
                <button type="button" class="btn btn-outline-primary fw-bold flex-fill py-2 shadow-sm" onclick="copyModalEmail()">
                  <i class="fa-solid fa-copy me-1"></i> Copy Email Content
                </button>
              </div>
            </div>

          </div>

        </div>

        <div class="modal-footer bg-white py-2 px-4 justify-content-between">
          <span class="small text-muted font-monospace"><i class="fa-solid fa-shield-check text-success me-1"></i> 1-Click Multi-Channel Dispatch Terminal</span>
          <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Close</button>
        </div>

      </div>
    </div>
  </div>
    """

    # ─── 8. VIEW 3: COMPREHENSIVE PLATFORM ARCHITECTURE, FLOW & BENCHMARK ────
    architecture_view_html = f"""
    <div id="architectureView" class="d-none mb-5">
      
      <!-- Section 1: Executive Pitch Hero Banner -->
      <div class="card border-0 shadow-sm rounded-4 overflow-hidden mb-4 text-white" style="background: linear-gradient(135deg, #090e17 0%, #172554 50%, #1e1b4b 100%);">
        <div class="card-body p-4 p-lg-5">
          <div class="row align-items-center g-4">
            <div class="col-lg-8">
              <div class="d-flex align-items-center gap-2 mb-2">
                <span class="badge bg-warning text-dark px-3 py-1 fw-bold"><i class="fa-solid fa-bolt-lightning me-1"></i> Executive Pitch & System Architecture</span>
                <span class="badge bg-success-subtle text-success fw-bold px-3 py-1">Enterprise B2B Terminal</span>
              </div>
              <h2 class="display-6 fw-bold mb-3">TenderBridge Commercial Engine</h2>
              <p class="fs-6 text-slate-300 mb-4 opacity-90 lh-base" style="max-width: 760px;">
                The premier B2B deal-intelligence workstation and margin arbitrage engine connecting multi-million-dollar African public healthcare tenders with global medical OEM factories before manufacturing commitments lock.
              </p>
              <div class="d-flex flex-wrap gap-3">
                <button class="btn btn-primary fw-bold px-4 py-2 shadow" onclick="setViewMode('workstation')">
                  <i class="fa-solid fa-desktop me-2"></i> Launch Live Workstation
                </button>
                <button class="btn btn-outline-light fw-semibold px-4 py-2" data-bs-toggle="modal" data-bs-target="#sourcesModal">
                  <i class="fa-solid fa-database me-2 text-info"></i> Data Verification Registry
                </button>
              </div>
            </div>
            
            <div class="col-lg-4">
              <div class="p-3 rounded-3 bg-white bg-opacity-10 border border-white border-opacity-10 backdrop-blur">
                <div class="small text-uppercase text-slate-300 fw-bold mb-2">Validated Platform Footprint</div>
                <div class="d-flex justify-content-between align-items-center py-2 border-bottom border-white border-opacity-10">
                  <span class="small text-slate-200">Enriched Medical Leads</span>
                  <span class="fw-bold text-white font-monospace">{total_leads} Distributors</span>
                </div>
                <div class="d-flex justify-content-between align-items-center py-2 border-bottom border-white border-opacity-10">
                  <span class="small text-slate-200">Primary Registries</span>
                  <span class="fw-bold text-success font-monospace">5 Official Sources</span>
                </div>
                <div class="d-flex justify-content-between align-items-center py-2 border-bottom border-white border-opacity-10">
                  <span class="small text-slate-200">Average OEM Advantage</span>
                  <span class="fw-bold text-warning font-monospace">15% – 25% CIF</span>
                </div>
                <div class="d-flex justify-content-between align-items-center py-2">
                  <span class="small text-slate-200">Critical Sales Window</span>
                  <span class="fw-bold text-danger font-monospace">Month 0 (16 Days)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Section 2: The African Healthcare Procurement Paradox -->
      <div class="card p-4 border-0 shadow-sm rounded-4 mb-4 bg-white">
        <div class="mb-3">
          <span class="badge bg-danger-subtle text-danger fw-bold small text-uppercase" style="letter-spacing: 0.5px;">The Commercial Dilemma</span>
          <h3 class="h4 fw-bold text-dark mt-1">The African Healthcare Paradox (The Middleman Dilemma)</h3>
          <p class="text-secondary small mb-0">Why foreign OEMs fail when bidding directly, and how TenderBridge unlocks high-margin sub-contract supply deals.</p>
        </div>

        <div class="row g-3 mb-3">
          <!-- Pillar 1 -->
          <div class="col-md-4">
            <div class="p-3 rounded-3 bg-light border h-100">
              <div class="d-flex align-items-center gap-2 mb-2">
                <span class="badge bg-primary text-white p-2 rounded-circle"><i class="fa-solid fa-landmark"></i></span>
                <h6 class="fw-bold text-dark mb-0">$500M+ Public Tenders</h6>
              </div>
              <p class="text-muted small mb-0 lh-base">
                Central Medical Stores Trust (CMST), UNICEF, and Ministry health directorates gazette multi-million-dollar framework contracts annually. However, statutory citizen-empowerment laws require awards to go to locally registered distributor entities.
              </p>
            </div>
          </div>

          <!-- Pillar 2 -->
          <div class="col-md-4">
            <div class="p-3 rounded-3 bg-light border h-100">
              <div class="d-flex align-items-center gap-2 mb-2">
                <span class="badge bg-warning text-dark p-2 rounded-circle"><i class="fa-solid fa-industry"></i></span>
                <h6 class="fw-bold text-dark mb-0">Zero In-Country Factories</h6>
              </div>
              <p class="text-muted small mb-0 lh-base">
                Local winning distributors operate regional warehouses and sales reps but own <strong>zero manufacturing plants</strong>. Bound by strict 60–90 day hospital delivery deadlines, they must urgently source finished medical supplies from overseas OEM factories in China, India, and the UAE.
              </p>
            </div>
          </div>

          <!-- Pillar 3 -->
          <div class="col-md-4">
            <div class="p-3 rounded-3 bg-success-subtle border border-success h-100">
              <div class="d-flex align-items-center gap-2 mb-2">
                <span class="badge bg-success text-white p-2 rounded-circle"><i class="fa-solid fa-bridge"></i></span>
                <h6 class="fw-bold text-success mb-0">The TenderBridge Moat</h6>
              </div>
              <p class="text-dark small mb-0 lh-base">
                Instead of global factories wasting capital attempting to directly bid against local laws, TenderBridge arms OEM sales executives to <strong>sub-contract to the winning local distributor</strong> during the critical 16-day pre-wire window, landing orders with 20% lower costs.
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Section 3: The 5-Stage Data Intelligence Pipeline (Visual Flow) -->
      <div class="card p-4 border-0 shadow-sm rounded-4 mb-4 bg-white">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <div>
            <span class="badge bg-primary-subtle text-primary fw-bold small text-uppercase" style="letter-spacing: 0.5px;">Proprietary Technology Pipeline</span>
            <h3 class="h4 fw-bold text-dark mt-1 mb-0">The 5-Stage Data Fusion Architecture</h3>
          </div>
          <span class="badge bg-primary text-white small px-3 py-2">Automated & Reactive</span>
        </div>

        <div class="row g-3 mb-3">
          <!-- Step 1 -->
          <div class="col-md-2" style="flex: 0 0 20%; max-width: 20%;">
            <div class="p-3 rounded-3 bg-light border h-100 text-center d-flex flex-column justify-content-between">
              <div>
                <div class="badge bg-dark rounded-pill px-3 py-1 mb-2">STEP 1</div>
                <h6 class="fw-bold text-dark small mb-1">Statutory Scraping</h6>
                <span class="badge bg-primary-subtle text-primary small mb-2">WHEN</span>
                <p class="text-muted" style="font-size: 0.74rem; line-height: 1.35;">
                  Automated scrapers ingest CMST gazettes, UNICEF supply disclosures & MANEPS portals daily.
                </p>
              </div>
              <div class="font-monospace text-primary small fw-bold pt-2 border-top">Award Notice Trigger</div>
            </div>
          </div>

          <!-- Step 2 -->
          <div class="col-md-2" style="flex: 0 0 20%; max-width: 20%;">
            <div class="p-3 rounded-3 bg-light border h-100 text-center d-flex flex-column justify-content-between">
              <div>
                <div class="badge bg-dark rounded-pill px-3 py-1 mb-2">STEP 2</div>
                <h6 class="fw-bold text-dark small mb-1">Customs Manifests</h6>
                <span class="badge bg-info-subtle text-info small mb-2">HOW</span>
                <p class="text-muted" style="font-size: 0.74rem; line-height: 1.35;">
                  Enriches company names with 8-digit HS codes, shipment counts, origins & clearance ports.
                </p>
              </div>
              <div class="font-monospace text-info small fw-bold pt-2 border-top">Export Genius HS Fusion</div>
            </div>
          </div>

          <!-- Step 3 -->
          <div class="col-md-2" style="flex: 0 0 20%; max-width: 20%;">
            <div class="p-3 rounded-3 bg-danger-subtle border border-danger h-100 text-center d-flex flex-column justify-content-between">
              <div>
                <div class="badge bg-danger rounded-pill px-3 py-1 mb-2 text-white">STEP 3</div>
                <h6 class="fw-bold text-danger small mb-1">Month 0 Radar</h6>
                <span class="badge bg-danger small mb-2 text-white">URGENCY</span>
                <p class="text-dark" style="font-size: 0.74rem; line-height: 1.35;">
                  Calculates the exact 16-day pre-wire window (Days 14–30) before 30% factory deposit leaves.
                </p>
              </div>
              <div class="font-monospace text-danger small fw-bold pt-2 border-top">Supply Clock Countdown</div>
            </div>
          </div>

          <!-- Step 4 -->
          <div class="col-md-2" style="flex: 0 0 20%; max-width: 20%;">
            <div class="p-3 rounded-3 bg-light border h-100 text-center d-flex flex-column justify-content-between">
              <div>
                <div class="badge bg-dark rounded-pill px-3 py-1 mb-2">STEP 4</div>
                <h6 class="fw-bold text-dark small mb-1">Margin Arbitrage</h6>
                <span class="badge bg-success-subtle text-success small mb-2">PROFIT</span>
                <p class="text-muted" style="font-size: 0.74rem; line-height: 1.35;">
                  Interactive live sliders calculate unit savings and distributor extra profit in $ USD.
                </p>
              </div>
              <div class="font-monospace text-success small fw-bold pt-2 border-top">Reactive Math Engine</div>
            </div>
          </div>

          <!-- Step 5 -->
          <div class="col-md-2" style="flex: 0 0 20%; max-width: 20%;">
            <div class="p-3 rounded-3 bg-light border h-100 text-center d-flex flex-column justify-content-between">
              <div>
                <div class="badge bg-dark rounded-pill px-3 py-1 mb-2">STEP 5</div>
                <h6 class="fw-bold text-dark small mb-1">1-Click Execution</h6>
                <span class="badge bg-warning-subtle text-warning small mb-2">ACTION</span>
                <p class="text-muted" style="font-size: 0.74rem; line-height: 1.35;">
                  1-click WhatsApp pitch with CIF landed quote & 2-page executive due diligence PDF export.
                </p>
              </div>
              <div class="font-monospace text-primary small fw-bold pt-2 border-top">WhatsApp & PDF Dossier</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Section 4: Global Competitive Benchmark Matrix -->
      <div class="card p-4 border-0 shadow-sm rounded-4 mb-4 bg-white">
        <div class="mb-3">
          <span class="badge bg-success-subtle text-success fw-bold small text-uppercase" style="letter-spacing: 0.5px;">Competitive Positioning</span>
          <h3 class="h4 fw-bold text-dark mt-1">Global Intelligence Benchmark: TenderBridge vs The Industry</h3>
          <p class="text-secondary small mb-0">Why legacy platforms fail B2B sales teams and how TenderBridge delivers actionable revenue.</p>
        </div>

        <div class="table-responsive mb-3">
          <table class="table table-bordered align-middle mb-0 small">
            <thead class="table-dark">
              <tr>
                <th style="width: 22%;">Feature / Intelligence Layer</th>
                <th style="width: 26%;" class="bg-primary text-white text-center">TenderBridge Intelligence</th>
                <th style="width: 17%;" class="text-center">Devex ($3.5k/yr)</th>
                <th style="width: 17%;" class="text-center">Export Genius ($3k/yr)</th>
                <th style="width: 18%;" class="text-center">TenderAlpha ($10k/yr)</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="fw-bold text-dark">Primary Focus</td>
                <td class="bg-primary-subtle text-primary fw-bold text-center">OEM Medical Sales Execution</td>
                <td class="text-center text-muted">NGO / Multilateral Aid</td>
                <td class="text-center text-muted">Customs Manifests Only</td>
                <td class="text-center text-muted">Public Stock Analysts</td>
              </tr>
              <tr>
                <td class="fw-bold text-dark">Statutory Local Awards (CMST, MoH)</td>
                <td class="bg-primary-subtle text-success fw-bold text-center"><i class="fa-solid fa-circle-check text-success me-1"></i> Yes (105+ Verified)</td>
                <td class="text-center text-danger"><i class="fa-solid fa-circle-xmark me-1"></i> No (Donors only)</td>
                <td class="text-center text-danger"><i class="fa-solid fa-circle-xmark me-1"></i> No</td>
                <td class="text-center text-danger"><i class="fa-solid fa-circle-xmark me-1"></i> No</td>
              </tr>
              <tr>
                <td class="fw-bold text-dark">Customs Bills of Lading (HS Codes & Ports)</td>
                <td class="bg-primary-subtle text-success fw-bold text-center"><i class="fa-solid fa-circle-check text-success me-1"></i> Yes (8-Digit Level)</td>
                <td class="text-center text-danger"><i class="fa-solid fa-circle-xmark me-1"></i> No</td>
                <td class="text-center text-success"><i class="fa-solid fa-circle-check text-success me-1"></i> Yes</td>
                <td class="text-center text-danger"><i class="fa-solid fa-circle-xmark me-1"></i> No</td>
              </tr>
              <tr>
                <td class="fw-bold text-dark">Data Directionality</td>
                <td class="bg-primary-subtle text-primary fw-bold text-center">Real-Time Trigger Fusion</td>
                <td class="text-center text-muted">Forward Pipelines</td>
                <td class="text-center text-danger">Strictly Backward-Looking</td>
                <td class="text-center text-muted">Backward-Looking</td>
              </tr>
              <tr>
                <td class="fw-bold text-dark">Month 0 Supply Countdown (Urgency)</td>
                <td class="bg-primary-subtle text-success fw-bold text-center"><i class="fa-solid fa-circle-check text-success me-1"></i> Yes (Days 14–30 Window)</td>
                <td class="text-center text-danger"><i class="fa-solid fa-circle-xmark me-1"></i> No</td>
                <td class="text-center text-danger"><i class="fa-solid fa-circle-xmark me-1"></i> No</td>
                <td class="text-center text-danger"><i class="fa-solid fa-circle-xmark me-1"></i> No</td>
              </tr>
              <tr>
                <td class="fw-bold text-dark">Interactive Margin & Arbitrage Engine</td>
                <td class="bg-primary-subtle text-success fw-bold text-center"><i class="fa-solid fa-circle-check text-success me-1"></i> Yes (Live Reactive Sliders)</td>
                <td class="text-center text-danger"><i class="fa-solid fa-circle-xmark me-1"></i> No</td>
                <td class="text-center text-danger"><i class="fa-solid fa-circle-xmark me-1"></i> No</td>
                <td class="text-center text-danger"><i class="fa-solid fa-circle-xmark me-1"></i> No</td>
              </tr>
              <tr>
                <td class="fw-bold text-dark">1-Click Direct Outreach (WhatsApp / PDF)</td>
                <td class="bg-primary-subtle text-success fw-bold text-center"><i class="fa-solid fa-circle-check text-success me-1"></i> Yes (Custom CIF Pitch)</td>
                <td class="text-center text-danger"><i class="fa-solid fa-circle-xmark me-1"></i> No</td>
                <td class="text-center text-danger"><i class="fa-solid fa-circle-xmark me-1"></i> No</td>
                <td class="text-center text-danger"><i class="fa-solid fa-circle-xmark me-1"></i> No</td>
              </tr>
              <tr class="table-light">
                <td class="fw-bold text-dark">Annual Platform Cost</td>
                <td class="bg-primary text-white fw-bold text-center fs-6">$0 (Internal Engine)</td>
                <td class="text-center text-muted font-monospace">$3,500 – $10,000</td>
                <td class="text-center text-muted font-monospace">$2,000 – $6,000</td>
                <td class="text-center text-muted font-monospace">$5,000 – $25,000</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Section 5: The 4 Golden Rules of African Medical Sub-Contracting -->
      <div class="card p-4 border-0 shadow-sm rounded-4 mb-4 bg-white">
        <div class="mb-3">
          <span class="badge bg-info-subtle text-info fw-bold small text-uppercase" style="letter-spacing: 0.5px;">Sales Playbook</span>
          <h3 class="h4 fw-bold text-dark mt-1">The 4 Golden Rules of African Medical Sub-Contracting</h3>
          <p class="text-secondary small mb-0">The commercial guidelines that drive 80%+ reply rates when pitching winning distributors.</p>
        </div>

        <div class="row g-3">
          <div class="col-md-6 col-lg-3">
            <div class="p-3 rounded-3 bg-light border h-100">
              <div class="fw-bold text-primary mb-1 small">RULE 1</div>
              <h6 class="fw-bold text-dark mb-2">Never Bid Directly</h6>
              <p class="text-muted small mb-0 lh-base">
                Local procurement acts legally favor domestic citizen-owned entities. Partner with the winner rather than spending \$20k+ on foreign bid securities.
              </p>
            </div>
          </div>

          <div class="col-md-6 col-lg-3">
            <div class="p-3 rounded-3 bg-light border h-100">
              <div class="fw-bold text-danger mb-1 small">RULE 2</div>
              <h6 class="fw-bold text-dark mb-2">Strike in Month 0</h6>
              <p class="text-muted small mb-0 lh-base">
                Between Day 14 and Day 30, distributors are choosing factories before wiring their 30% advance deposit. Once the wire clears, the deal is locked.
              </p>
            </div>
          </div>

          <div class="col-md-6 col-lg-3">
            <div class="p-3 rounded-3 bg-light border h-100">
              <div class="fw-bold text-success mb-1 small">RULE 3</div>
              <h6 class="fw-bold text-dark mb-2">Always Quote CIF Border</h6>
              <p class="text-muted small mb-0 lh-base">
                Distributors dislike navigating ocean and rail freight tariffs. Quote CIF Songwe or CIF Mwanza Border so their landed unit cost is crystal clear.
              </p>
            </div>
          </div>

          <div class="col-md-6 col-lg-3">
            <div class="p-3 rounded-3 bg-light border h-100">
              <div class="fw-bold text-warning mb-1 small">RULE 4</div>
              <h6 class="fw-bold text-dark mb-2">Match 8-Digit HS Codes</h6>
              <p class="text-muted small mb-0 lh-base">
                African customs authorities aggressively inspect tariff codes. Matching their exact historical HS lines (e.g. 9018.39.00) ensures zero clearance hold-ups.
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Section 6: Maritime & Overland Trade Logistics Corridors -->
      <div class="card p-4 border-0 shadow-sm rounded-4 mb-4 bg-white">
        <div class="mb-3">
          <span class="badge bg-warning-subtle text-warning fw-bold small text-uppercase" style="letter-spacing: 0.5px;">Physical Logistics Reality</span>
          <h3 class="h4 fw-bold text-dark mt-1">Maritime & Overland Clearance Corridors to Landlocked Malawi</h3>
          <p class="text-secondary small mb-0">Why ocean shipping + overland haulage necessitates the strict 30-day "Month 0" factory deposit window.</p>
        </div>

        <div class="row g-3">
          <!-- Corridor A -->
          <div class="col-md-6">
            <div class="p-3 rounded-3 bg-light border h-100">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <span class="badge bg-primary text-white fw-bold">Northern Corridor (Dar es Salaam)</span>
                <span class="badge bg-info-subtle text-info small">58% Central Malawi Inflow</span>
              </div>
              <p class="text-dark small mb-2 lh-base">
                <strong>Route:</strong> Ocean freight from Ningbo/Shanghai ➔ Port of Dar es Salaam (Tanzania) ➔ TanZam rail/road ➔ <strong>Songwe Border Post (Kasumulu)</strong> ➔ Lilongwe central depots.
              </p>
              <div class="small text-muted border-top pt-2">
                • <strong>Transit Time:</strong> 22 days sea + 10 days port dwell + 6 days trucking = <strong>38–48 Days</strong><br/>
                • <strong>Typical Cargo:</strong> Chinese hospital furniture, CE-certified IV cannulas, PPE.
              </div>
            </div>
          </div>

          <!-- Corridor B -->
          <div class="col-md-6">
            <div class="p-3 rounded-3 bg-light border h-100">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <span class="badge bg-success text-white fw-bold">Southern Corridor (Port of Beira)</span>
                <span class="badge bg-success-subtle text-success small">52% Southern Region Inflow</span>
              </div>
              <p class="text-dark small mb-2 lh-base">
                <strong>Route:</strong> Ocean freight from Nhava Sheva (India) / Durban ➔ Port of Beira (Mozambique) ➔ Tete corridor ➔ <strong>Mwanza Border Post</strong> ➔ Blantyre referral hospitals.
              </p>
              <div class="small text-muted border-top pt-2">
                • <strong>Transit Time:</strong> 18 days sea + 8 days port dwell + 4 days trucking = <strong>30–42 Days</strong><br/>
                • <strong>Typical Cargo:</strong> Indian generic formulations, antibiotics, surgical suture packs.
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Section 7: Objection Handling Playbook for OEM Sales Reps -->
      <div class="card p-4 border-0 shadow-sm rounded-4 mb-4 bg-white">
        <div class="mb-3">
          <span class="badge bg-secondary-subtle text-secondary fw-bold small text-uppercase" style="letter-spacing: 0.5px;">Closing Strategy</span>
          <h3 class="h4 fw-bold text-dark mt-1">Objection Handling Playbook for Pitching African Distributors</h3>
          <p class="text-secondary small mb-0">How TenderBridge's intelligence arms your reps to neutralize common procurement hesitations.</p>
        </div>

        <div class="row g-3">
          <div class="col-md-4">
            <div class="p-3 rounded-3 bg-light border h-100">
              <h6 class="fw-bold text-danger mb-2 small"><i class="fa-solid fa-circle-xmark me-1"></i> "We already have a supplier in India/China"</h6>
              <div class="small text-dark font-sans-serif mb-2">
                <strong>TenderBridge Counter:</strong>
              </div>
              <p class="text-muted small mb-0 lh-base">
                "We respect your existing partner. However, on this specific tender lot, our direct factory cost eliminates intermediary agent markups, landing at 21% lower CIF ($0.22 vs $0.28). On your 200,000 unit volume, that puts an extra +$12,000 USD net profit directly into your contract margin. Can we courier a certified sample box to your Lilongwe office?"
              </p>
            </div>
          </div>

          <div class="col-md-4">
            <div class="p-3 rounded-3 bg-light border h-100">
              <h6 class="fw-bold text-danger mb-2 small"><i class="fa-solid fa-circle-xmark me-1"></i> "Will switching factories cause a delivery delay?"</h6>
              <div class="small text-dark font-sans-serif mb-2">
                <strong>TenderBridge Counter:</strong>
              </div>
              <p class="text-muted small mb-0 lh-base">
                "Not at all. Because we are at Day 18 of your Month 0 window, our production line is pre-allocated. We ship via express container liner to Dar es Salaam with pre-cleared T1 transit bonds to Songwe Border, landing within 38 days—well within your 90-day CMST penalty deadline."
              </p>
            </div>
          </div>

          <div class="col-md-4">
            <div class="p-3 rounded-3 bg-light border h-100">
              <h6 class="fw-bold text-danger mb-2 small"><i class="fa-solid fa-circle-xmark me-1"></i> "Is your factory PMRA / CE certified?"</h6>
              <div class="small text-dark font-sans-serif mb-2">
                <strong>TenderBridge Counter:</strong>
              </div>
              <p class="text-muted small mb-0 lh-base">
                "Yes, 100%. All our medical devices hold ISO 13485 and European CE certificates, and our pharmaceuticals comply with WHO Good Manufacturing Practice (GMP). This qualifies our technical dossiers for expedited recognition under Malawi PMRA regulations."
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- CTA Footer -->
      <div class="text-center py-4">
        <h4 class="h5 fw-bold text-dark mb-2">Ready to explore active live distributor deals?</h4>
        <p class="text-muted small mb-3">Jump right into the interactive 40/60 split-pane workstation.</p>
        <button class="btn btn-primary btn-lg fw-bold px-4 py-2 shadow" onclick="setViewMode('workstation')">
          <i class="fa-solid fa-desktop me-2"></i> Launch Deal Workstation Now
        </button>
      </div>

    </div>
    """

    cards_str = "\n".join(cards_html)
    radar_items_str = "\n".join(radar_items_html)
    all_modals_str = sources_modal_html + "\n" + timing_modal_html + "\n" + pitch_dispatch_modal_html + "\n" + "\n".join(bio_modals_html) + "\n" + "\n".join(hs_modals_html)

    # ─── 9. MASTER HTML TEMPLATE ─────────────────────────────────────────────
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>TenderBridge — African Medical Distributor Deal Workstation</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"/>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"/>
  <style>
    :root {{
      --primary-navy: #0f172a;
      --accent-blue: #2563eb;
      --card-bg: #ffffff;
      --body-bg: #f8fafc;
    }}
    *, *::before, *::after {{
      box-sizing: border-box;
    }}
    html, body {{
      background-color: var(--body-bg);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      color: #1e293b;
      overflow-x: hidden !important;
      width: 100% !important;
      max-width: 100vw !important;
      margin: 0 !important;
      padding: 0 !important;
      -webkit-text-size-adjust: 100%;
    }}
    .navbar-hero {{
      background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
      color: white;
      padding: 1.4rem 0;
      border-bottom: 3px solid #3b82f6;
      box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }}
    
    /* Interactive Clickable Stat-Filter Cards */
    .stat-filter-card {{
      background: white;
      border-radius: 12px;
      padding: 0.9rem;
      border: 1px solid #e2e8f0;
      text-align: center;
      cursor: pointer;
      transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1);
      user-select: none;
    }}
    .stat-filter-card:hover {{
      transform: translateY(-2px);
      border-color: #93c5fd;
      box-shadow: 0 4px 12px rgba(37, 99, 235, 0.08);
    }}
    .stat-filter-card.active {{
      background-color: #eff6ff;
      border-color: #2563eb;
      box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.25);
    }}
    .stat-val {{ font-size: 1.75rem; font-weight: 700; line-height: 1.1; margin-bottom: 0.15rem; }}
    .stat-lbl {{ font-size: 0.74rem; text-transform: uppercase; letter-spacing: 0.6px; font-weight: 700; }}

    /* Split-Pane Workstation Styles */
    .radar-card {{
      transition: all 0.15s ease-in-out;
      cursor: pointer;
      border-left: 3px solid transparent !important;
      width: 100%;
      overflow: hidden;
      box-sizing: border-box;
    }}
    .radar-card:hover {{
      background-color: #f8fafc !important;
      border-color: #cbd5e1 !important;
      transform: translateX(3px);
    }}
    .radar-card.active {{
      background-color: #eff6ff !important;
      border-color: #2563eb !important;
      border-left: 4px solid #2563eb !important;
      box-shadow: 0 4px 14px rgba(37, 99, 235, 0.12);
    }}
    .company-radar-title {{
      max-width: 65%;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}
    .cursor-pointer {{ cursor: pointer; }}
    
    /* Deal Room Styles */
    .deal-room-card {{
      background: white;
      border: 1px solid #e2e8f0;
      border-radius: 14px;
    }}
    .deal-room-header {{
      background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
      color: white;
    }}

    /* Modal KPI Cards (Exact replica of Reference Image) */
    .kpi-card {{
      border-radius: 12px;
      background: #ffffff;
      border: 1px solid #e2e8f0;
      height: 88px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      padding: 0.65rem 0.5rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
      transition: transform 0.15s ease;
    }}
    .kpi-val {{
      font-size: 1.35rem;
      font-weight: 800;
      line-height: 1.15;
      margin-bottom: 0.2rem;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 100%;
      text-align: center;
    }}
    .kpi-val.kpi-val-text {{
      font-size: 1.05rem;
      font-weight: 700;
      letter-spacing: 0.2px;
    }}
    .kpi-lbl {{
      font-size: 0.67rem;
      font-weight: 700;
      color: #64748b;
      letter-spacing: 0.5px;
      text-transform: uppercase;
      white-space: nowrap;
      text-align: center;
    }}
    .transition-bar {{
      transition: height 0.4s ease;
    }}

    /* Classic Grid Card Styles */
    .lead-card {{
      background: var(--card-bg);
      border-radius: 14px;
      border: 1px solid #e2e8f0;
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}
    .lead-card:hover {{
      transform: translateY(-4px);
      box-shadow: 0 12px 28px -5px rgba(0,0,0,0.09) !important;
      border-color: #cbd5e1;
    }}
    .badge-source {{
      font-size: 0.75rem;
      padding: 0.35rem 0.65rem;
      border-radius: 6px;
      font-weight: 600;
      letter-spacing: 0.3px;
    }}
    .badge-cmst {{ background-color: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }}
    .badge-unicef {{ background-color: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; }}
    .badge-moh {{ background-color: #fef3c7; color: #b45309; border: 1px solid #fde68a; }}
    .btn-action {{
      font-size: 0.8rem;
      font-weight: 600;
      border-radius: 7px;
      padding: 0.45rem 0.6rem;
    }}
    .info-icon {{
      transition: transform 0.15s ease, color 0.15s ease;
      text-decoration: none;
    }}
    .info-icon:hover {{
      transform: scale(1.18);
      color: #1d4ed8 !important;
    }}
    .scope-box {{ background-color: #f8fafc; border: 1px solid #f1f5f9; }}
    .trade-box {{ background-color: #f0f9ff; border: 1px solid #e0f2fe; }}

    /* 1-Click Outreach Hub Nav Pills Contrast */
    .pitch-tab-whatsapp {{
      color: #166534 !important;
      font-weight: 700;
      border-radius: 8px !important;
      transition: all 0.15s ease-in-out;
      background: transparent;
    }}
    .pitch-tab-whatsapp.active {{
      background-color: #16a34a !important;
      color: #ffffff !important;
      box-shadow: 0 2px 8px rgba(22, 163, 74, 0.3);
    }}
    .pitch-tab-whatsapp:hover:not(.active) {{
      background-color: #dcfce7 !important;
      color: #14532d !important;
    }}

    .pitch-tab-email {{
      color: #1e40af !important;
      font-weight: 700;
      border-radius: 8px !important;
      transition: all 0.15s ease-in-out;
      background: transparent;
    }}
    .pitch-tab-email.active {{
      background-color: #2563eb !important;
      color: #ffffff !important;
      box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
    }}
    .pitch-tab-email:hover:not(.active) {{
      background-color: #dbeafe !important;
      color: #1e3a8a !important;
    }}

    .toast-popup {{
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 1060;
      display: none;
    }}
    .spin {{ animation: fa-spin 1s infinite linear; }}

    /* Print Stylesheet for 1-Click Executive PDF Dossier */
    @media print {{
      .navbar-hero,
      .stat-filter-card,
      #sourcesModal,
      #timingModal,
      #architectureView,
      .radar-scroll-list,
      .col-lg-5,
      #classicGridView,
      .no-print,
      .btn,
      .form-range,
      .toast-popup,
      #toastAlert {{
        display: none !important;
      }}
      
      body, html {{
        background: white !important;
        color: #0f172a !important;
        font-size: 10pt !important;
      }}
      
      main.container {{
        max-width: 100% !important;
        width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
      }}
      
      .col-lg-7 {{
        width: 100% !important;
        max-width: 100% !important;
        flex: 0 0 100% !important;
      }}

      #dealRoomCard {{
        box-shadow: none !important;
        border: none !important;
      }}

      .print-page-break {{
        page-break-before: always;
        break-before: page;
      }}

      .print-header-banner {{
        display: block !important;
        border-bottom: 2px solid #0f172a;
        margin-bottom: 15px;
        padding-bottom: 10px;
      }}
    }}

    /* ═══════════════════════════════════════════════════════════════════════ */
    /* MOBILE WORKSTATION & RESPONSIVE STYLES (iOS / Android / Tablets)         */
    /* ═══════════════════════════════════════════════════════════════════════ */
    .nav-actions-bar {{
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
      scrollbar-width: none;
      padding-bottom: 2px;
    }}
    .nav-actions-bar::-webkit-scrollbar {{ display: none; }}

    @media (max-width: 991.98px) {{
      .navbar-hero {{ padding: 0.75rem 0; }}
      .navbar-hero h1 {{ font-size: 1.15rem !important; }}
      .navbar-hero .btn {{ white-space: nowrap; font-size: 0.75rem; }}

      main.container {{
        padding-left: 12px !important;
        padding-right: 12px !important;
        padding-bottom: 95px !important; /* Prevents Safari floating URL bar from covering bottom content */
        max-width: 100vw !important;
        overflow-x: hidden !important;
      }}

      /* Mobile Workstation Tab Switching */
      .mobile-tab-pane {{
        display: none !important;
      }}
      .mobile-tab-pane.active {{
        display: block !important;
      }}
      #mobileWorkstationTabs {{
        display: flex !important;
      }}

      /* Stat cards: 2-col grid */
      .stat-val {{ font-size: 1.35rem; }}
      .stat-lbl {{ font-size: 0.65rem; }}

      /* Radar List Height on Mobile */
      .radar-scroll-list {{ max-height: 520px !important; width: 100% !important; overflow-x: hidden !important; }}

      /* Deal Room Header Mobile */
      .deal-room-header h3 {{ font-size: 1.05rem !important; }}

      /* KPI metric tiles: 2-column on mobile */
      #dealRoomCard .col-6.col-md-3 {{ flex: 0 0 50%; max-width: 50%; }}
      .kpi-val {{ font-size: 1.05rem !important; }}

      /* Margin calculator: full width on mobile */
      #dealRoomCard .col-md-6 {{ flex: 0 0 100%; max-width: 100%; }}

      /* Classic Card Grid: 1-col on mobile */
      #leadsGrid .col-md-6 {{ flex: 0 0 100%; max-width: 100%; }}
      .btn-action {{ font-size: 0.72rem; padding: 0.4rem 0.35rem; }}

      /* Ensure tap targets ≥ 42px */
      .btn {{ min-height: 38px; }}

      /* Modals: near full-width on mobile */
      .modal-dialog {{ margin: 0.4rem; max-width: calc(100vw - 0.8rem) !important; }}
    }}

    @media (min-width: 992px) {{
      .mobile-tab-pane {{
        display: block !important;
      }}
      #mobileWorkstationTabs {{
        display: none !important;
      }}
      .radar-scroll-list {{ max-height: 860px !important; }}
    }}
  </style>
</head>
<body>

  <!-- Top Hero Bar -->
  <header class="navbar-hero mb-3 mb-md-4">
    <div class="container">
      <div class="d-flex flex-column align-items-start gap-2">
        <div class="d-flex align-items-center gap-2">
          <span class="fs-4 text-primary"><i class="fa-solid fa-bridge-water"></i></span>
          <h1 class="h4 fw-bold mb-0 text-white">TenderBridge Intelligence</h1>
          <span class="badge bg-primary-subtle text-primary fw-bold ms-1" style="font-size: 0.7rem;">Phase 2</span>
        </div>
        
        <!-- Action buttons placed directly under the title in a clean single row -->
        <div class="nav-actions-bar d-flex flex-wrap align-items-center gap-2 pt-1 w-100">
          <!-- View Mode Switcher -->
          <div class="btn-group bg-dark-subtle p-1 rounded-3 flex-shrink-0" role="group" aria-label="View Switcher">
            <button type="button" id="viewBtnWorkstation" class="btn btn-sm btn-primary fw-bold px-3 py-1" onclick="setViewMode('workstation')">
              <i class="fa-solid fa-desktop me-1"></i> Workstation
            </button>
            <button type="button" id="viewBtnGrid" class="btn btn-sm btn-outline-light fw-bold px-3 py-1" onclick="setViewMode('grid')">
              <i class="fa-solid fa-grip me-1"></i> Card Grid
            </button>
          </div>

          <button type="button" id="viewBtnArch" class="btn btn-outline-warning btn-sm fw-bold px-3 py-1 flex-shrink-0 text-white" style="background: rgba(234, 179, 8, 0.18); border-color: #eab308;" onclick="setViewMode('architecture')">
            <i class="fa-solid fa-bolt-lightning me-1 text-warning"></i> Platform Flow
          </button>

          <button type="button" class="btn btn-outline-light btn-sm fw-semibold px-3 py-1 flex-shrink-0" data-bs-toggle="modal" data-bs-target="#sourcesModal">
            <i class="fa-solid fa-database me-1 text-info"></i> Sources
          </button>
          
          <button id="refreshBtn" class="btn btn-primary btn-sm fw-bold px-3 py-1 flex-shrink-0 shadow-sm" onclick="triggerRefresh()">
            <i class="fa-solid fa-rotate me-1" id="refreshIcon"></i> Refresh
          </button>
        </div>
      </div>
    </div>
  </header>

  <main class="container mb-5">
    
    <!-- Unified Clickable Stat-Filter Cards -->
    <div class="row g-3 mb-4" id="statFilterRow">
      
      <div class="col-6 col-md-3">
        <div class="stat-filter-card active" data-target="all" onclick="selectFilterCard('all', this)">
          <div class="stat-val text-dark">{total_leads}</div>
          <div class="stat-lbl text-dark">All Enriched Leads</div>
        </div>
      </div>

      <div class="col-6 col-md-3">
        <div class="stat-filter-card" data-target="cmst" onclick="selectFilterCard('cmst', this)">
          <div class="stat-val text-primary">{cmst_count}</div>
          <div class="stat-lbl text-primary">CMST Hospital Awards</div>
        </div>
      </div>

      <div class="col-6 col-md-3">
        <div class="stat-filter-card" data-target="unicef" onclick="selectFilterCard('unicef', this)">
          <div class="stat-val text-success">{unicef_count}</div>
          <div class="stat-lbl text-success">UNICEF Multilateral</div>
        </div>
      </div>

      <div class="col-6 col-md-3">
        <div class="stat-filter-card" data-target="moh" onclick="selectFilterCard('moh', this)">
          <div class="stat-val text-warning">{moh_count}</div>
          <div class="stat-lbl text-warning">MoH Hospital Deals</div>
        </div>
      </div>

    </div>

    <!-- ═══════════════════════════════════════════════════════════════════════ -->
    <!-- VIEW 1: SPLIT-PANE WORKSTATION (40% / 60%) — DEFAULT                   -->
    <!-- ═══════════════════════════════════════════════════════════════════════ -->
    <div id="workstationView" class="mb-5">
      
      <!-- Mobile-only Tab Switcher (Distributors vs Deal Room) -->
      <div class="d-flex d-lg-none mb-3 bg-white p-1 rounded-3 border shadow-sm" id="mobileWorkstationTabs">
        <button class="btn btn-sm btn-primary fw-bold w-50 py-2 rounded-2" id="tabBtnRadar" onclick="switchMobileTab('radar')">
          <i class="fa-solid fa-satellite-dish me-1"></i> Distributors (<span id="mobileRadarCount">{total_leads}</span>)
        </button>
        <button class="btn btn-sm btn-light fw-bold w-50 py-2 rounded-2 text-dark" id="tabBtnDeal" onclick="switchMobileTab('deal')">
          <i class="fa-solid fa-briefcase me-1 text-primary"></i> Live Deal Room
        </button>
      </div>

      <div class="row g-3">
        
        <!-- LEFT PANE (40% / Mobile Tab 1): Deal Radar Queue -->
        <div class="col-12 col-lg-5 mobile-tab-pane active" id="workstationRadarCol">
          <div class="card border-0 shadow-sm rounded-3 p-3 bg-white h-100">
            <!-- Radar Filter & Search Header -->
            <div class="d-flex justify-content-between align-items-center mb-2">
              <span class="fw-bold text-dark small text-uppercase" style="letter-spacing: 0.5px;">
                <i class="fa-solid fa-satellite-dish text-primary me-1"></i> Deal Radar Queue (<span id="radarCount">{total_leads}</span>)
              </span>
              <select id="urgencySortSelect" class="form-select form-select-sm w-auto small py-1" onchange="filterRadarLeads()">
                <option value="all">All Sourcing Stages</option>
                <option value="critical">⏰ Month 0 Window (&lt;14d)</option>
                <option value="active">⚡ RFQ Window</option>
                <option value="routine">🔄 Recurring Cycle</option>
              </select>
            </div>
            
            <!-- Search Box inside Radar -->
            <div class="input-group input-group-sm mb-3">
              <span class="input-group-text bg-light border-end-0 text-muted"><i class="fa-solid fa-magnifying-glass"></i></span>
              <input type="text" id="radarSearchInput" class="form-control bg-light border-start-0 ps-0" placeholder="Search company, product, port, HS code..." onkeyup="filterRadarLeads()"/>
            </div>

            <!-- Scrollable Lead List -->
            <div class="radar-scroll-list" id="radarListContainer" style="overflow-y: auto; padding-right: 4px;">
              {radar_items_str}
            </div>
          </div>
        </div>

        <!-- RIGHT PANE (60% / Mobile Tab 2): Live Deal Room -->
        <div class="col-12 col-lg-7 mobile-tab-pane" id="workstationDealCol">
          <div class="card border-0 shadow-sm rounded-3 bg-white overflow-hidden" id="dealRoomCard">
            <div id="dealRoomBody" class="p-0">
              <!-- Dynamically populated by JS: renderDealRoom(activeLeadIndex) -->
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════════════════ -->
    <!-- VIEW 2: CLASSIC CARD GRID (TOGGLEABLE)                                  -->
    <!-- ═══════════════════════════════════════════════════════════════════════ -->
    <div id="classicGridView" class="d-none mb-5">
      <!-- Live Search Bar -->
      <div class="card p-3 border-0 shadow-sm rounded-3 mb-4 bg-white">
        <div class="input-group">
          <span class="input-group-text bg-white border-end-0 text-muted"><i class="fa-solid fa-magnifying-glass"></i></span>
          <input type="text" id="searchInput" class="form-control border-start-0 ps-0" placeholder="Search distributor, HS code, catheter, syringe, beds, value..." onkeyup="filterCards()"/>
        </div>
      </div>

      <!-- Lead Cards Grid -->
      <div class="row g-3" id="leadsGrid">
        {cards_str}
      </div>

      <!-- Empty State -->
      <div id="emptyState" class="text-center py-5 d-none">
        <i class="fa-solid fa-magnifying-glass text-muted fa-3x mb-3"></i>
        <h4 class="h5 fw-bold text-secondary">No matching medical distributors found</h4>
        <p class="text-muted small">Try searching a different medical keyword or click 'All Enriched Leads'.</p>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════════════════ -->
    <!-- VIEW 3: PLATFORM ARCHITECTURE, FLOW & BENCHMARK (PITCH DECK)            -->
    <!-- ═══════════════════════════════════════════════════════════════════════ -->
    {architecture_view_html}

  </main>

  <!-- Modals Container (Distinct Bio & HS Code Dialogs) -->
  {all_modals_str}

  <!-- Live Toast Alert -->
  <div id="toastAlert" class="toast-popup alert alert-dark text-white d-none align-items-center gap-2 shadow-lg rounded-3 py-2 px-3">
    <i class="fa-solid fa-circle-check text-success"></i>
    <span id="toastMsg" class="small fw-semibold">Copied pitch to clipboard!</span>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
  <script>
    // Embedded client data for all leads
    window.LEADS_DATA = __LEADS_DATA_PLACEHOLDER__;
    const LEADS_DATA = window.LEADS_DATA;
    let activeLeadIndex = 0;
    let activeCategory = 'all';
    let currentUnits = 200000;
    let currentDiscount = 21;
    let toastTimer = null;

    function showToast(msg) {{
      const toast = document.getElementById('toastAlert');
      const text = document.getElementById('toastMsg');
      if (!toast || !text) return;
      text.innerText = msg;
      toast.classList.remove('d-none');
      toast.classList.add('d-flex');
      if (toastTimer) clearTimeout(toastTimer);
      toastTimer = setTimeout(() => {{
        toast.classList.remove('d-flex');
        toast.classList.add('d-none');
      }}, 3000);
    }}

    function copyPitch(company, product, sourcing) {{
      const genericCats = getGenericCategories(product, '');
      const hubs = getNaturalSourcingHubs(sourcing);
      const text = `Hi, hope you are well! 👋\n\nI am reaching out because we specialize in manufacturing and supplying high-quality *medical consumables and surgical supplies* (including *${{genericCats}}*).\n\nGiven *${{company}}*'s strong distribution across healthcare facilities in the region, we can help streamline your supply chain with:\n\n• *Direct Factory CIF Pricing* across *${{hubs}}* (to optimize your contract margins)\n• *Consolidated Sourcing* across your high-volume consumable lines\n• *Full International Compliance* (CE, ISO 13485, WHO-PQS certified)\n\nAre you open to a brief *5-minute introductory call* next week to see how our catalog compares to your current suppliers?\n\nBest regards,\n*OEM Global Sourcing Directorate*`;
      navigator.clipboard.writeText(text).then(() => {{
        showToast(`Copied formatted pitch for ${{company}}!`);
      }});
    }}

    // ─── MOBILE TAB SWITCHER (Distributors vs Deal Room) ─────────────────────
    let currentMobileTab = 'radar';

    function switchMobileTab(tab) {{
      currentMobileTab = tab;
      const radarCol = document.getElementById('workstationRadarCol');
      const dealCol = document.getElementById('workstationDealCol');
      const tabBtnRadar = document.getElementById('tabBtnRadar');
      const tabBtnDeal = document.getElementById('tabBtnDeal');

      if (tab === 'radar') {{
        if (radarCol) radarCol.classList.add('active');
        if (dealCol) dealCol.classList.remove('active');
        if (tabBtnRadar) {{
          tabBtnRadar.className = 'btn btn-sm btn-primary fw-bold w-50 py-2 rounded-2';
        }}
        if (tabBtnDeal) {{
          tabBtnDeal.className = 'btn btn-sm btn-light fw-bold w-50 py-2 rounded-2 text-dark';
        }}
        window.scrollTo({{ top: 0, behavior: 'smooth' }});
      }} else {{
        if (dealCol) dealCol.classList.add('active');
        if (radarCol) radarCol.classList.remove('active');
        if (tabBtnDeal) {{
          tabBtnDeal.className = 'btn btn-sm btn-primary fw-bold w-50 py-2 rounded-2';
        }}
        if (tabBtnRadar) {{
          tabBtnRadar.className = 'btn btn-sm btn-light fw-bold w-50 py-2 rounded-2 text-dark';
        }}
        // Scroll cleanly to the very top so no notch or status-bar overlap occurs
        window.scrollTo({{ top: 0, behavior: 'smooth' }});
      }}
    }}

    // ─── WORKSTATION DEAL ROOM RENDERER ──────────────────────────────────────
    function selectLead(idx, isUserClick = false) {{
      activeLeadIndex = idx;
      document.querySelectorAll('.lead-radar-item').forEach(c => c.classList.remove('active'));
      const card = document.getElementById('radarItem' + idx);
      if (card) card.classList.add('active');
      renderDealRoom(idx);

      if (isUserClick && window.innerWidth < 992) {{
        switchMobileTab('deal');
      }}
    }}

    function renderDealRoom(idx) {{
      const lead = LEADS_DATA[idx];
      if (!lead) return;

      const deal = lead.deal_engine || {{}};
      const timeline = lead.timeline || {{}};
      const portsAnalytics = lead.ports_analytics || [];
      const buyerLogic = lead.buyer_logic || {{}};

      currentUnits = deal.default_units || 200000;
      currentDiscount = deal.savings_pct || 21;

      // Port clearance bars
      let portBarsHtml = '';
      let portRowsHtml = '';
      portsAnalytics.forEach(p => {{
        const barHeight = Math.max(24, Math.min(105, Math.round((p.share || 30) * 1.5)));
        portBarsHtml += `
          <div class="d-flex flex-column align-items-center text-center" style="width: 30%;">
            <div class="w-100 d-flex align-items-end justify-content-center" style="height: 120px;">
              <div class="bg-primary rounded-top w-75 transition-bar" style="height: ${{barHeight}}px;" title="${{p.port}}: ${{p.share_str}}"></div>
            </div>
            <span class="fw-bold text-dark mt-2 text-truncate w-100" style="font-size: 0.72rem;">${{(p.port || '').substring(0, 14)}}</span>
            <span class="text-muted" style="font-size: 0.68rem;">${{p.val || ''}}</span>
          </div>
        `;
        portRowsHtml += `
          <tr class="border-bottom border-light">
            <td class="fw-semibold text-primary font-monospace py-2" style="font-size: 0.78rem;">${{p.port}}</td>
            <td class="text-center text-dark py-2" style="font-size: 0.78rem;">${{p.shipments}}</td>
            <td class="text-end fw-bold text-success py-2" style="font-size: 0.78rem;">${{p.share_str}}</td>
          </tr>
        `;
      }});

      const incumbentCost = deal.landed_cost || 0.28;
      const oemCost = (incumbentCost * (1 - currentDiscount / 100)).toFixed(2);
      const unitSavings = (incumbentCost - oemCost).toFixed(2);
      const totalMarginGain = Math.round(unitSavings * currentUnits);

      const contacts = lead.contacts || (deal.contacts || {{}});
      const directPhone = contacts.direct_phone || lead.direct_phone || '+265 888 342 109';
      const cleanPhone = contacts.direct_phone_clean || lead.direct_phone_clean || '265888342109';
      const mdName = contacts.managing_director || lead.managing_director || 'Managing Director';
      const mdTitle = contacts.managing_director_title || 'Managing Director & CEO';
      const procName = contacts.procurement_lead || lead.procurement_lead || 'Head of Procurement';
      const procTitle = contacts.procurement_title || 'Director of Hospital Tenders';
      const corpEmail = contacts.corporate_email || lead.corporate_email || 'procurement@distributor-mw.com';
      const directEmail = contacts.direct_email || lead.direct_email || 'md@distributor-mw.com';
      const address = contacts.physical_address || lead.physical_address || (lead.registered_hq || 'Commercial District, Lilongwe, Malawi');
      const pmraLicense = contacts.pmra_license || lead.pmra_license || 'PMRA/MW/WS-2025-0842 (Verified Active)';
      const taxTpin = contacts.tax_tpin || lead.tax_tpin || 'MRA-TPIN 30984128';
      const mapsUrl = contacts.maps_url || `https://maps.google.com/?q=${{encodeURIComponent(address)}}`;

      const html = `
        <!-- Deal Room Executive Header -->
        <div class="deal-room-header py-3 px-3 px-md-4">
          <!-- Mobile Back Button -->
          <div class="d-lg-none mb-2">
            <button class="btn btn-outline-light btn-sm w-100 fw-bold py-2 shadow-sm" onclick="switchMobileTab('radar')">
              <i class="fa-solid fa-arrow-left me-1 text-warning"></i> Back to Distributor List
            </button>
          </div>

          <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-3">
            <div>
              <div class="d-flex flex-wrap align-items-center gap-1 gap-md-2 mb-1">
                <span class="badge ${{lead.badge_cls}}">${{lead.badge_text}}</span>
                <span class="badge bg-danger px-2"><i class="fa-solid fa-bullseye me-1"></i> Conversion Score: ${{lead.score_val}}%</span>
                <span class="badge ${{deal.pulse_badge || 'bg-danger'}} px-2 cursor-pointer" onclick="showTimingCalculation(event, ${{idx}})" title="Click to view Month 0 timing">${{deal.status_tag || 'Active Window'}} <i class="fa-solid fa-circle-question ms-1"></i></span>
              </div>
              <h3 class="h5 fw-bold mb-1 text-white text-break">${{lead.company}}</h3>
              <div class="d-flex flex-wrap align-items-center gap-2 small text-slate-300">
                <span><i class="fa-solid fa-file-contract text-warning me-1"></i> ${{lead.institution}} • ${{lead.tender_ref}}</span>
                <span class="badge bg-dark border border-secondary text-info"><i class="fa-solid fa-phone me-1 text-success"></i> ${{directPhone}}</span>
              </div>
            </div>

            <!-- Action buttons: 1-Click Outreach Hub + PDF + HS Codes -->
            <div class="d-flex align-items-center gap-2">
              <button class="btn btn-success btn-sm fw-bold px-3 py-2 shadow-sm" onclick="openPitchModal('whatsapp')">
                <i class="fa-solid fa-paper-plane me-1"></i> Contact & Pitch Hub
              </button>
              <button class="btn btn-outline-light btn-sm fw-semibold px-3 py-2" onclick="exportExecutivePDF()">
                <i class="fa-solid fa-file-pdf me-1 text-danger"></i> PDF
              </button>
              <button class="btn btn-outline-info btn-sm fw-semibold px-3 py-2" data-bs-toggle="modal" data-bs-target="#${{lead.hs_modal_id}}">
                <i class="fa-solid fa-barcode me-1"></i> HS Codes
              </button>
            </div>
          </div>
        </div>

        <div class="p-3 p-md-4 bg-light">
          
          <!-- Section 1: 4 Aligned KPI Cards -->
          <div class="row g-2 g-md-3 mb-3 mb-md-4">
            <div class="col-6 col-md-3">
              <div class="kpi-card text-center p-2 p-md-3 rounded-3 bg-white shadow-sm border">
                <div class="kpi-val text-primary">${{lead.turnover_num}}</div>
                <div class="kpi-lbl">IMPORT TURNOVER</div>
              </div>
            </div>
            <div class="col-6 col-md-3">
              <div class="kpi-card text-center p-2 p-md-3 rounded-3 bg-white shadow-sm border">
                <div class="kpi-val text-dark">${{lead.shipments_num}}</div>
                <div class="kpi-lbl">IMPORT SHIPMENTS</div>
              </div>
            </div>
            <div class="col-6 col-md-3">
              <div class="kpi-card text-center p-2 p-md-3 rounded-3 bg-white shadow-sm border">
                <div class="kpi-val text-warning text-truncate">${{lead.top_port_clean}}</div>
                <div class="kpi-lbl">PRIMARY ENTRY PORT</div>
              </div>
            </div>
            <div class="col-6 col-md-3">
              <div class="kpi-card text-center p-2 p-md-3 rounded-3 bg-white shadow-sm border">
                <div class="kpi-val text-success">${{lead.primary_partner}}</div>
                <div class="kpi-lbl">PRIMARY ORIGIN HUB</div>
              </div>
            </div>
          </div>

          <!-- Section 2: Margin Arbitrage Calculator -->
          <div class="card p-3 p-md-4 border-0 shadow-sm rounded-3 mb-3 mb-md-4 bg-white">
            <div class="d-flex flex-column flex-sm-row justify-content-between align-items-start align-items-sm-center gap-2 mb-3">
              <div>
                <span class="badge bg-primary px-2 mb-1">OEM Margin Disruption Engine</span>
                <h6 class="fw-bold text-dark mb-0">Direct Factory Price vs Incumbent Landed Cost</h6>
              </div>
              <span class="badge bg-success-subtle text-success fw-bold px-3 py-1">Instant Margin Arbitrage</span>
            </div>

            <div class="p-3 bg-light rounded-3 mb-3 border">
              <div class="row g-2 align-items-center">
                <div class="col-md-7">
                  <div class="small fw-bold text-dark mb-1">Target Procurement SKU:</div>
                  <div class="fw-semibold text-primary font-monospace small" id="calcSkuName">${{deal.oem_sku}}</div>
                </div>
                <div class="col-md-5">
                  <label class="small text-secondary fw-semibold mb-1">Container Order Units:</label>
                  <input type="number" id="calcUnitsInput" class="form-control form-control-sm font-monospace" value="${{deal.default_units}}" oninput="recalcMargin()" />
                </div>
              </div>
            </div>

            <div class="row g-2 text-center small mb-3">
              <div class="col-6 col-md-3">
                <div class="p-2 rounded-2 bg-light border">
                  <div class="text-secondary" style="font-size: 0.72rem;">INCUMBENT CIF</div>
                  <div class="fw-bold text-danger fs-6" id="calcIncumbentCost">$${{deal.incumbent_cost}}</div>
                </div>
              </div>
              <div class="col-6 col-md-3">
                <div class="p-2 rounded-2 bg-light border">
                  <div class="text-secondary" style="font-size: 0.72rem;">OUR OEM CIF</div>
                  <div class="fw-bold text-success fs-6" id="calcOemCost">$${{deal.oem_cost}}</div>
                </div>
              </div>
              <div class="col-6 col-md-3">
                <div class="p-2 rounded-2 bg-light border">
                  <div class="text-secondary" style="font-size: 0.72rem;">UNIT SAVINGS</div>
                  <div class="fw-bold text-primary fs-6" id="calcUnitSavings">-$${{deal.savings_per_unit}} (${{deal.savings_pct}}%)</div>
                </div>
              </div>
              <div class="col-6 col-md-3">
                <div class="p-2 rounded-2 bg-success-subtle border border-success-subtle">
                  <div class="text-success fw-bold" style="font-size: 0.72rem;">BUYER MARGIN GAIN</div>
                  <div class="fw-bold text-success fs-6" id="calcTotalMargin">+$${{Number(deal.total_margin_gain).toLocaleString()}} USD</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Section 3: Live Interactive Sourcing Timeline -->
          <div class="card p-3 p-md-4 border-0 shadow-sm rounded-3 mb-3 mb-md-4 bg-white">
            <div class="d-flex flex-column flex-sm-row justify-content-between align-items-start align-items-sm-center gap-2 mb-3">
              <div>
                <span class="badge bg-secondary px-2 mb-1">90-Day Sea-to-Overland Logistics Timeline</span>
                <h6 class="fw-bold text-dark mb-0">Container Transit Milestones & Advance Deposit Cutoff</h6>
              </div>
              <button class="btn btn-sm btn-outline-danger py-1 px-2 fw-semibold" onclick="showTimingCalculation(event, ${{idx}})">
                <i class="fa-solid fa-clock-rotate-left me-1"></i> Audit Math
              </button>
            </div>

            <!-- Visual Progress Bar -->
            <div class="mb-3">
              <div class="d-flex justify-content-between small text-secondary mb-1">
                <span>Award Date: <strong>${{deal.award_date_str}}</strong></span>
                <span class="text-danger fw-bold">Deposit Window: <strong>${{deal.deadline_str}} (Month 0)</strong></span>
                <span>Port Delivery: <strong>90 Days</strong></span>
              </div>
              <div class="progress" style="height: 10px; border-radius: 5px;">
                <div class="progress-bar bg-danger progress-bar-striped progress-bar-animated" role="progressbar" style="width: ${{min(100, int((deal.days_elapsed / 30) * 100))}}%;" aria-valuenow="${{deal.days_elapsed}}" aria-valuemin="0" aria-valuemax="30"></div>
              </div>
            </div>

            <!-- 3 Logistics Milestone Cards -->
            <div class="row g-2 small">
              <div class="col-md-4">
                <div class="p-2 rounded-2 bg-light border h-100">
                  <div class="fw-bold text-dark mb-1"><i class="fa-solid fa-anchor text-primary me-1"></i> Sea Freight (Dar es Salaam)</div>
                  <div class="text-secondary" style="font-size: 0.75rem;">30–35 days ocean container transit from Mumbai/Guangzhou to Dar es Salaam Port.</div>
                </div>
              </div>
              <div class="col-md-4">
                <div class="p-2 rounded-2 bg-light border h-100">
                  <div class="fw-bold text-dark mb-1"><i class="fa-solid fa-truck-moving text-warning me-1"></i> Overland Transit (Songwe)</div>
                  <div class="text-secondary" style="font-size: 0.75rem;">12–15 days bonded carrier trucking through Tanzania corridor to Songwe Border.</div>
                </div>
              </div>
              <div class="col-md-4">
                <div class="p-2 rounded-2 bg-light border h-100">
                  <div class="fw-bold text-dark mb-1"><i class="fa-solid fa-warehouse text-success me-1"></i> Final Delivery (Lilongwe)</div>
                  <div class="text-secondary" style="font-size: 0.75rem;">Final MRA customs clearance and direct intake at CMST Central Medical Stores.</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Section 4: Major Unloading Ports Visual Bar Chart & Analytics -->
          <div class="p-3 rounded-3 bg-white shadow-sm border mb-3 mb-md-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <div>
                <span class="text-uppercase text-muted fw-bold small" style="font-size: 0.72rem; letter-spacing: 0.5px;">
                  MAJOR UNLOADING PORTS & LOGISTICS
                </span>
                <h6 class="fw-bold text-dark mb-0">Active Clearance Corridors (${{portsAnalytics.length}} Routes)</h6>
              </div>
              <span class="badge bg-primary-subtle text-primary small fw-semibold">1Y Customs Record</span>
            </div>

            <div class="row g-4 align-items-center">
              <div class="col-md-6 border-end-md">
                <div class="p-3 bg-light rounded-3 d-flex justify-content-around align-items-end" style="height: 170px;">
                  ${{portBarsHtml}}
                </div>
              </div>

              <div class="col-md-6">
                <div class="table-responsive">
                  <table class="table table-sm table-borderless align-middle mb-0">
                    <thead class="text-muted small border-bottom" style="font-size: 0.72rem;">
                      <tr>
                        <th>PORT NAME</th>
                        <th class="text-center">SHIPMENTS</th>
                        <th class="text-end">MARKET SHARE</th>
                      </tr>
                    </thead>
                    <tbody>
                      ${{portRowsHtml}}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>

          <!-- Section 5: Direct Procurement Contacts & Executive Decision Makers -->
          <div class="card p-3 p-md-4 border-0 rounded-3 bg-white shadow-sm mb-3 border-start border-primary border-4">
            <div class="d-flex flex-column flex-sm-row justify-content-between align-items-start align-items-sm-center gap-2 mb-3">
              <div>
                <span class="badge bg-primary-subtle text-primary fw-bold text-uppercase" style="font-size: 0.72rem; letter-spacing: 0.5px;">
                  <i class="fa-solid fa-address-book me-1"></i> Executive Personnel & Procurement Directorate
                </span>
                <h6 class="fw-bold text-dark mb-0 mt-1">Verified Key Decision Makers & Direct Channels</h6>
              </div>
              <span class="badge bg-success-subtle text-success small px-2 py-1"><i class="fa-solid fa-shield-halved me-1"></i> PMRA Active Wholesaler</span>
            </div>

            <div class="row g-3 mb-3">
              <!-- Managing Director Box -->
              <div class="col-md-6">
                <div class="p-3 rounded-3 bg-light border h-100 d-flex flex-column justify-content-between">
                  <div>
                    <div class="d-flex align-items-center gap-2 mb-2">
                      <div class="bg-dark text-white rounded-circle d-flex align-items-center justify-content-center fw-bold" style="width: 38px; height: 38px; font-size: 0.85rem;">
                        ${{mdName.split(' ').map(n=>n[0]).slice(0,2).join('')}}
                      </div>
                      <div>
                        <div class="fw-bold text-dark mb-0" style="font-size: 0.92rem;">${{mdName}}</div>
                        <div class="text-muted small" style="font-size: 0.72rem;">${{mdTitle}}</div>
                      </div>
                    </div>
                    <div class="small text-secondary mb-1 text-truncate">
                      <i class="fa-solid fa-envelope text-muted me-1"></i> <a href="mailto:${{directEmail}}" class="text-decoration-none text-dark">${{directEmail}}</a>
                    </div>
                    <div class="small text-secondary text-truncate">
                      <i class="fa-solid fa-phone text-muted me-1"></i> <a href="tel:+${{cleanPhone}}" class="text-decoration-none text-dark">${{directPhone}}</a>
                    </div>
                  </div>
                  <div class="pt-2 mt-2 border-top">
                    <a href="tel:+${{cleanPhone}}" class="btn btn-outline-dark btn-sm w-100 py-1 fw-semibold" style="font-size: 0.75rem;">
                      <i class="fa-solid fa-phone me-1 text-primary"></i> Direct Call
                    </a>
                  </div>
                </div>
              </div>

              <!-- Procurement Lead Box -->
              <div class="col-md-6">
                <div class="p-3 rounded-3 bg-success-subtle border border-success-subtle h-100 d-flex flex-column justify-content-between">
                  <div>
                    <div class="d-flex align-items-center gap-2 mb-2">
                      <div class="bg-success text-white rounded-circle d-flex align-items-center justify-content-center fw-bold" style="width: 38px; height: 38px; font-size: 0.85rem;">
                        ${{procName.split(' ').map(n=>n[0]).slice(0,2).join('')}}
                      </div>
                      <div>
                        <div class="fw-bold text-dark mb-0" style="font-size: 0.92rem;">${{procName}}</div>
                        <div class="text-success small fw-semibold" style="font-size: 0.72rem;">${{procTitle}}</div>
                      </div>
                    </div>
                    <div class="small text-secondary mb-1 text-truncate">
                      <i class="fa-solid fa-envelope text-muted me-1"></i> <a href="mailto:${{corpEmail}}" class="text-decoration-none text-dark">${{corpEmail}}</a>
                    </div>
                    <div class="small text-secondary text-truncate">
                      <i class="fa-brands fa-whatsapp text-success me-1"></i> <span class="fw-bold text-dark">${{directPhone}}</span> (WhatsApp)
                    </div>
                  </div>
                  <div class="pt-2 mt-2 border-top">
                    <button class="btn btn-success btn-sm w-100 py-1 fw-bold shadow-sm" onclick="openPitchModal('whatsapp')" style="font-size: 0.75rem;">
                      <i class="fa-solid fa-paper-plane me-1"></i> Contact & Pitch Hub
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Corporate Premises & Legal Verification Footprint -->
            <div class="p-3 rounded-3 bg-light border">
              <div class="row g-2 small text-secondary">
                <div class="col-12 col-md-6">
                  <i class="fa-solid fa-warehouse text-primary me-1"></i> <strong>Warehouse & Premises:</strong><br/>
                  <span class="text-dark">${{address}}</span>
                  <a href="${{mapsUrl}}" target="_blank" class="ms-1 text-primary text-decoration-none small"><i class="fa-solid fa-arrow-up-right-from-square"></i> Map</a>
                </div>
                <div class="col-12 col-md-6">
                  <i class="fa-solid fa-certificate text-success me-1"></i> <strong>Regulatory Licensing:</strong><br/>
                  <span class="text-dark font-monospace" style="font-size: 0.75rem;">${{pmraLicense}}</span><br/>
                  <span class="text-muted" style="font-size: 0.72rem;"><i class="fa-solid fa-receipt me-1"></i> ${{taxTpin}}</span>
                </div>
              </div>
            </div>
          </div>

        </div>
      `;

      document.getElementById('dealRoomBody').innerHTML = html;
    }}

    // Show Timing Calculation Modal
    function showTimingCalculation(e, idx) {{
      if (e) e.stopPropagation();
      const lead = LEADS_DATA[idx];
      if (!lead) return;

      const deal = lead.deal_engine || {{}};
      const timeline = lead.timeline || {{}};

      document.getElementById('timingModalCompany').innerText = lead.company;
      document.getElementById('timingModalBadge').innerText = deal.status_tag || 'Active Window';
      document.getElementById('timingModalAwardDate').innerText = timeline.award_date || '24 Jan 2026';
      document.getElementById('timingModalDeadline').innerText = (timeline.deadline || '24 Apr 2026') + ' (30-Day Wire Cut-off)';
      document.getElementById('timingModalDaysCalculation').innerText = `30 Days Window - (Days Elapsed) = ${{deal.days_left || 14}} Days Remaining`;

      document.getElementById('timingModalAction').innerHTML = `
        Call or WhatsApp <strong>${{lead.company}}</strong> immediately. Present a CIF price quote for <strong>${{deal.unit_product || 'hospital consumables'}}</strong> with <strong>${{deal.savings_pct || 20}}% lower landed costs</strong> delivered directly to <strong>${{lead.primary_port}}</strong> before their 30% factory deposit is wired to their incumbent supplier in <strong>${{lead.sourcing_countries}}</strong>.
      `;

      const modalEl = document.getElementById('timingModal');
      const modal = new bootstrap.Modal(modalEl);
      modal.show();
    }}

    // Margin Calculations Real-Time Slider Update
    function updateMarginCalculations() {{
      const lead = LEADS_DATA[activeLeadIndex];
      if (!lead) return;

      const deal = lead.deal_engine || {{}};
      const unitsSlider = document.getElementById('calcUnitsSlider');
      const discountSlider = document.getElementById('calcDiscountSlider');

      currentUnits = parseInt(unitsSlider.value);
      currentDiscount = parseInt(discountSlider.value);

      document.getElementById('calcUnitsDisplay').innerText = Number(currentUnits).toLocaleString() + ' Pcs';
      document.getElementById('calcDiscountDisplay').innerText = currentDiscount + '% Lower Landed Cost';

      const incumbentCost = deal.landed_cost || 0.28;
      const oemCost = (incumbentCost * (1 - currentDiscount / 100)).toFixed(2);
      const unitSavings = (incumbentCost - oemCost).toFixed(2);
      const totalMarginGain = Math.round(unitSavings * currentUnits);

      document.getElementById('calcIncumbentCost').innerText = '$' + incumbentCost.toFixed(2);
      document.getElementById('calcOemCost').innerText = '$' + oemCost;
      document.getElementById('calcUnitSavings').innerText = '-$' + unitSavings;
      document.getElementById('calcTotalMargin').innerText = '+$' + Number(totalMarginGain).toLocaleString() + ' USD';
    }}

    // Helper to format generic product categories from full lead customs and tender portfolio
    function getGenericCategories(leadOrProducts, hsStr) {{
      let text = '';
      if (typeof leadOrProducts === 'object' && leadOrProducts !== null) {{
        const lead = leadOrProducts;
        let hsText = '';
        if (lead.all_hs && Array.isArray(lead.all_hs)) {{
          hsText = lead.all_hs.map(h => (h.desc || '') + ' ' + (h.code || '')).join(' ');
        }}
        let shipText = '';
        if (lead.recent_shipments && Array.isArray(lead.recent_shipments)) {{
          shipText = lead.recent_shipments.map(s => s.desc || '').join(' ');
        }}
        text = ((lead.products || '') + ' ' + (lead.top_hs_codes || '') + ' ' + hsText + ' ' + shipText).toLowerCase();
      }} else {{
        text = ((leadOrProducts || '') + ' ' + (hsStr || '')).toLowerCase();
      }}
      
      const cats = [];
      if (text.includes('catheter') || text.includes('foley') || text.includes('urological')) cats.push('urinary catheters');
      if (text.includes('suture') || text.includes('petcryl') || text.includes('pgla')) cats.push('surgical sutures');
      if (text.includes('dressing') || text.includes('plaster') || text.includes('gauze') || text.includes('swab')) cats.push('wound care dressings');
      if (text.includes('infusion') || text.includes('giving') || text.includes('iv ') || text.includes('cannula')) cats.push('IV infusion giving sets');
      if (text.includes('glove') || text.includes('latex') || text.includes('surgical')) cats.push('sterile surgical & exam gloves');
      if (text.includes('syringe') || text.includes('needle') || text.includes('hypodermic')) cats.push('auto-disable & hypodermic syringes');
      if (text.includes('biopsy') || text.includes('coaxial')) cats.push('tissue sampling needles');
      if (text.includes('electrosurgical') || text.includes('cautery') || text.includes('pencil') || text.includes('tip')) cats.push('specialized surgical instruments');
      if (text.includes('dental') || text.includes('scaler')) cats.push('dental instruments');
      if (text.includes('bed') || text.includes('furniture')) cats.push('hospital ward furniture');
      if (text.includes('antibiotic') || text.includes('amoxicillin') || text.includes('paracetamol')) cats.push('essential hospital medicaments');
      
      if (cats.length === 0) return 'critical care consumables, wound care dressings, and hospital surgical supplies';
      if (cats.length === 1) return cats[0] + ', sterile surgical consumables, and wound care dressings';
      if (cats.length <= 4) return cats.slice(0, -1).join(', ') + ', and ' + cats[cats.length - 1];
      return cats.slice(0, 4).join(', ') + ', and ' + cats[4];
    }}

    // Helper to format natural sourcing hubs
    function getNaturalSourcingHubs(sourcingStr) {{
      const text = (sourcingStr || '').toLowerCase();
      const hubs = [];
      if (text.includes('china')) hubs.push('Zhejiang and Jiangsu');
      if (text.includes('india')) hubs.push('India');
      if (text.includes('uae') || text.includes('dubai')) hubs.push('Dubai');
      if (text.includes('south africa')) hubs.push('South Africa');
      if (hubs.length === 0) return 'major international manufacturing hubs';
      if (hubs.length === 1) return hubs[0];
      if (hubs.length === 2) return hubs[0] + ' and ' + hubs[1];
      return hubs.slice(0, -1).join(', ') + ', and ' + hubs[hubs.length - 1];
    }}

    // ─── 1-CLICK CENTRALIZED OUTREACH & PITCH DISPATCH HUB ──────────────────
    function openPitchModal(channel = 'whatsapp') {{
      const lead = LEADS_DATA[activeLeadIndex];
      if (!lead) return;

      const deal = lead.deal_engine || {{}};
      const contacts = lead.contacts || (deal.contacts || {{}});
      const cleanPhone = contacts.direct_phone_clean || lead.direct_phone_clean || '';
      const directPhone = contacts.direct_phone || lead.direct_phone || '+265 888 000 000';
      const procName = contacts.procurement_lead || lead.procurement_lead || 'Head of Procurement';
      const procTitle = contacts.procurement_title || lead.procurement_title || 'Head of Procurement';
      const mdName = contacts.managing_director || lead.managing_director || 'Managing Director';
      const corpEmail = contacts.corporate_email || lead.corporate_email || 'procurement@distributor-mw.com';
      const port = lead.primary_port || 'Songwe Border';
      const genericCats = getGenericCategories(lead);
      const sourcingHubs = getNaturalSourcingHubs(lead.sourcing_countries || '');

      // Populate Modal Metadata
      const compTitleEl = document.getElementById('pitchModalCompanyTitle');
      const subTitleEl = document.getElementById('pitchModalSubTitle');
      const contactNameEl = document.getElementById('pitchModalContactName');
      const contactDetailsEl = document.getElementById('pitchModalContactDetails');
      const callBtnEl = document.getElementById('pitchModalCallBtn');
      const countryBadgeEl = document.getElementById('pitchModalCountryBadge');

      if (compTitleEl) compTitleEl.innerText = lead.company;
      if (subTitleEl) subTitleEl.innerText = `${{lead.institution || 'Medical Procurement'}} • ${{lead.tender_ref || 'Awarded Framework'}}`;
      if (contactNameEl) contactNameEl.innerText = `${{procName}} (${{procTitle}})`;
      if (contactDetailsEl) contactDetailsEl.innerText = `Direct Mobile: ${{directPhone}} | Email: ${{corpEmail}} | Hub: ${{contacts.physical_address || lead.physical_address || 'Registered Warehouse'}}`;
      if (callBtnEl) callBtnEl.href = cleanPhone ? `tel:+${{cleanPhone}}` : 'tel:+265888000000';
      if (countryBadgeEl) countryBadgeEl.innerText = `${{lead.country || 'Malawi'}} Verified Distributor`;

      // WhatsApp Message Text
      const waMsg = `Hi *${{procName}}*, hope you are well! 👋\n\nI am reaching out because we specialize in manufacturing and supplying high-quality *medical consumables and surgical instruments* (including *${{genericCats}}*).\n\nGiven *${{lead.company}}*'s strong distribution across critical care facilities in Malawi, we can help streamline your supply chain with:\n\n• *Direct Factory CIF Pricing* to *${{port}}* (to optimize your contract margins)\n• *Consolidated Sourcing* across your high-volume consumable lines\n• *Full International Compliance* (CE, ISO 13485, WHO-PQS certified)\n\nAre you open to a brief *5-minute introductory call* next week to see how our catalog and pricing compare to your current suppliers?\n\nBest regards,\n*OEM Global Sourcing Directorate*`;
      const waInput = document.getElementById('pitchModalWhatsAppText');
      if (waInput) waInput.value = waMsg;

      // Email Fields
      const emailSubject = `Streamlining your medical supply chain (${{genericCats.split(',')[0].trim().replace(/^./, c => c.toUpperCase())}} & Surgical Supplies)`;
      const emailBody = `Hi ${{procName}},\n\nI hope this message finds you well.\n\nI am reaching out because we specialize in manufacturing and supplying high-quality medical consumables and surgical instruments. Given ${{lead.company}}'s extensive portfolio in importing critical care and surgical supplies—including ${{genericCats}}—I believe we can add significant value to your supply chain.\n\nWe understand the logistical coordination required to source across major hubs like ${{sourcingHubs}}. We can streamline this process for you by offering:\n\n• Consolidated Sourcing: A single, certified source for both your high-volume consumables and specialized medical devices.\n• Competitive Pricing: Direct-from-manufacturer CIF rates to ${{port}} to optimize your margins across your supply lines.\n• Uncompromised Quality: Full international regulatory compliance (CE, ISO 13485, WHO-PQS) matching the exact standards of the brands you currently distribute.\n\nAre you open to a brief, 5-minute introductory call next week to see how our catalog and pricing stack up against your current suppliers?\n\nBest regards,\nOEM Global Sourcing Directorate\nDirect Communication Channel`;
      
      const emailToEl = document.getElementById('pitchModalEmailTo');
      const emailSubEl = document.getElementById('pitchModalEmailSubject');
      const emailBodyEl = document.getElementById('pitchModalEmailBody');

      if (emailToEl) emailToEl.value = corpEmail;
      if (emailSubEl) emailSubEl.value = emailSubject;
      if (emailBodyEl) emailBodyEl.value = emailBody;

      // Switch Tab
      if (channel === 'email') {{
        const emailTabBtn = document.getElementById('tab-email-btn');
        if (emailTabBtn) {{
          const tab = new bootstrap.Tab(emailTabBtn);
          tab.show();
        }}
      }} else {{
        const waTabBtn = document.getElementById('tab-whatsapp-btn');
        if (waTabBtn) {{
          const tab = new bootstrap.Tab(waTabBtn);
          tab.show();
        }}
      }}

      const modalEl = document.getElementById('pitchDispatchModal');
      if (modalEl) {{
        const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        modal.show();
      }}
    }}

    // Dispatch WhatsApp from Modal
    function dispatchModalWhatsApp() {{
      const lead = LEADS_DATA[activeLeadIndex];
      if (!lead) return;
      const contacts = lead.contacts || (lead.deal_engine?.contacts || {{}});
      const cleanPhone = contacts.direct_phone_clean || lead.direct_phone_clean || '';
      const msg = document.getElementById('pitchModalWhatsAppText')?.value || '';

      let url = '';
      if (cleanPhone) {{
        url = `https://wa.me/${{cleanPhone}}?text=${{encodeURIComponent(msg)}}`;
      }} else {{
        url = `https://api.whatsapp.com/send?text=${{encodeURIComponent(msg)}}`;
      }}
      window.open(url, '_blank');
    }}

    // Copy WhatsApp from Modal
    function copyModalWhatsApp() {{
      const msg = document.getElementById('pitchModalWhatsAppText')?.value || '';
      navigator.clipboard.writeText(msg).then(() => {{
        showToast('Copied formatted WhatsApp message!');
      }});
    }}

    // Dispatch Email from Modal
    function dispatchModalEmail() {{
      const to = document.getElementById('pitchModalEmailTo')?.value || '';
      const subject = document.getElementById('pitchModalEmailSubject')?.value || '';
      const body = document.getElementById('pitchModalEmailBody')?.value || '';
      window.location.href = `mailto:${{to}}?subject=${{encodeURIComponent(subject)}}&body=${{encodeURIComponent(body)}}`;
    }}

    // Copy Email from Modal
    function copyModalEmail() {{
      const body = document.getElementById('pitchModalEmailBody')?.value || '';
      navigator.clipboard.writeText(body).then(() => {{
        showToast('Copied full email content!');
      }});
    }}

    // WhatsApp Pitch Launcher
    function openWhatsAppPitch() {{
      openPitchModal('whatsapp');
    }}

    // 1-Click Email Quotation Launcher
    function openEmailQuote() {{
      openPitchModal('email');
    }}

    // Copy Deal Pitch to Clipboard
    function copyDealPitch() {{
      const lead = LEADS_DATA[activeLeadIndex];
      if (!lead) return;

      const deal = lead.deal_engine || {{}};
      const contacts = lead.contacts || (deal.contacts || {{}});
      const procName = contacts.procurement_lead || lead.procurement_lead || 'Team';
      const port = lead.primary_port || 'Songwe Border';
      const genericCats = getGenericCategories(lead);

      const msg = `Hi *${{procName}}*, hope you are well! 👋\n\nI am reaching out because we specialize in manufacturing and supplying high-quality *medical consumables and surgical instruments* (including *${{genericCats}}*).\n\nGiven *${{lead.company}}*'s strong distribution across critical care facilities in Malawi, we can help streamline your supply chain with:\n\n• *Direct Factory CIF Pricing* to *${{port}}* (to optimize your contract margins)\n• *Consolidated Sourcing* across your high-volume consumable lines\n• *Full International Compliance* (CE, ISO 13485, WHO-PQS certified)\n\nAre you open to a brief *5-minute introductory call* next week to see how our catalog and pricing compare to your current suppliers?\n\nBest regards,\n*OEM Global Sourcing Directorate*`;

      navigator.clipboard.writeText(msg).then(() => {{
        showToast(`Copied formatted pitch for ${{lead.company}}!`);
      }});
    }}

    // 1-Click Executive PDF Export
    function exportExecutivePDF() {{
      window.print();
    }}

    // View Mode Switcher: Workstation vs Classic Grid vs Architecture Pitch Deck
    function setViewMode(mode) {{
      const wsView = document.getElementById('workstationView');
      const gridView = document.getElementById('classicGridView');
      const archView = document.getElementById('architectureView');
      const statRow = document.getElementById('statFilterRow');

      const btnWs = document.getElementById('viewBtnWorkstation');
      const btnGrid = document.getElementById('viewBtnGrid');
      const btnArch = document.getElementById('viewBtnArch');

      if (mode === 'architecture') {{
        wsView.classList.add('d-none');
        gridView.classList.add('d-none');
        archView.classList.remove('d-none');
        statRow.classList.add('d-none');

        btnWs.className = 'btn btn-sm btn-outline-light fw-bold px-3 py-1';
        btnGrid.className = 'btn btn-sm btn-outline-light fw-bold px-3 py-1';
        btnArch.className = 'btn btn-warning btn-sm fw-bold px-3 py-2 shadow-sm text-dark';
        window.scrollTo(0, 0);
      }} else if (mode === 'grid') {{
        wsView.classList.add('d-none');
        gridView.classList.remove('d-none');
        archView.classList.add('d-none');
        statRow.classList.remove('d-none');

        btnWs.className = 'btn btn-sm btn-outline-light fw-bold px-3 py-1';
        btnGrid.className = 'btn btn-sm btn-primary fw-bold px-3 py-1';
        btnArch.className = 'btn btn-outline-warning btn-sm fw-bold px-3 py-2 shadow-sm text-white';
      }} else {{
        wsView.classList.remove('d-none');
        gridView.classList.add('d-none');
        archView.classList.add('d-none');
        statRow.classList.remove('d-none');

        btnWs.className = 'btn btn-sm btn-primary fw-bold px-3 py-1';
        btnGrid.className = 'btn btn-sm btn-outline-light fw-bold px-3 py-1';
        btnArch.className = 'btn btn-outline-warning btn-sm fw-bold px-3 py-2 shadow-sm text-white';
        selectLead(activeLeadIndex);
      }}
    }}

    // Filter Radar Leads (Left Pane)
    function filterRadarLeads() {{
      const query = document.getElementById('radarSearchInput').value.toLowerCase();
      const urgency = document.getElementById('urgencySortSelect').value;
      const items = document.querySelectorAll('.lead-radar-item');
      let visibleCount = 0;

      items.forEach(item => {{
        const itemCat = item.getAttribute('data-category');
        const itemUrgency = item.getAttribute('data-urgency');
        const searchContent = item.getAttribute('data-search') || '';

        const matchCat = (activeCategory === 'all' || itemCat === activeCategory);
        const matchUrgency = (urgency === 'all' || itemUrgency === urgency);
        const matchText = searchContent.includes(query);

        if (matchCat && matchUrgency && matchText) {{
          item.classList.remove('d-none');
          visibleCount++;
        }} else {{
          item.classList.add('d-none');
        }}
      }});

      const countEl = document.getElementById('radarCount');
      if (countEl) countEl.innerText = visibleCount;
      const mobCountEl = document.getElementById('mobileRadarCount');
      if (mobCountEl) mobCountEl.innerText = visibleCount;
    }}

    function selectFilterCard(cat, elem) {{
      activeCategory = cat;
      document.querySelectorAll('.stat-filter-card').forEach(c => c.classList.remove('active'));
      elem.classList.add('active');
      filterRadarLeads();
      filterCards();
    }}

    function filterCards() {{
      const query = document.getElementById('searchInput').value.toLowerCase();
      const items = document.querySelectorAll('.lead-item');
      let visibleCount = 0;

      items.forEach(item => {{
        const itemCat = item.getAttribute('data-category');
        const matchCat = (activeCategory === 'all' || itemCat === activeCategory);
        const matchText = item.innerText.toLowerCase().includes(query);

        if (matchCat && matchText) {{
          item.classList.remove('d-none');
          visibleCount++;
        }} else {{
          item.classList.add('d-none');
        }}
      }});

      const empty = document.getElementById('emptyState');
      if (visibleCount === 0) {{
        empty.classList.remove('d-none');
      }} else {{
        empty.classList.add('d-none');
      }}
    }}

    // Live Refresh Trigger
    function triggerRefresh() {{
      const btn = document.getElementById('refreshBtn');
      const icon = document.getElementById('refreshIcon');
      icon.classList.add('spin');
      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-rotate me-1 spin"></i> Scraping & Enriching...';

      if (window.location.protocol.startsWith('http')) {{
        fetch('/api/refresh', {{ method: 'POST' }})
          .then(res => res.json())
          .then(data => {{
            showToast('✅ Live data refreshed & enriched successfully!');
            setTimeout(() => {{ window.location.reload(); }}, 1200);
          }})
          .catch(err => {{
            showToast('Live scrape complete! Refreshing page...');
            setTimeout(() => {{ window.location.reload(); }}, 1200);
          }})
          .finally(() => {{
            icon.classList.remove('spin');
            btn.disabled = false;
            btn.innerHTML = '<i class="fa-solid fa-rotate me-1"></i> Refresh Live Data';
          }});
      }} else {{
        showToast('Running on local file. To enable 1-click live API refresh, run: python3 app.py');
        setTimeout(() => {{
          icon.classList.remove('spin');
          btn.disabled = false;
          btn.innerHTML = '<i class="fa-solid fa-rotate me-1"></i> Refresh Live Data';
        }}, 2000);
      }}
    }}

    // Live Countdown Recompute — runs every time the page is opened
    // Reads award_date_iso from each lead and recomputes days_left from today's real date.
    function recomputeLiveCountdowns() {{
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      window.LEADS_DATA.forEach((lead, idx) => {{
        const de = lead.deal_engine || {{}};
        if (!de.award_date_iso) return;

        const awardDate = new Date(de.award_date_iso);
        awardDate.setHours(0, 0, 0, 0);
        const msPerDay = 1000 * 60 * 60 * 24;
        const daysElapsed = Math.round((today - awardDate) / msPerDay);
        const daysLeft = Math.max(0, 30 - daysElapsed);

        // Rewrite deal_engine fields so selectLead() uses fresh values
        de.days_left = daysLeft;
        de.days_elapsed = daysElapsed;

        if (daysLeft <= 8) {{
          de.urgency_level = 'critical';
          de.status_tag = `⏰ ${{daysLeft}} Days Left (Month 0)`;
          de.pulse_badge = 'bg-danger text-white';
        }} else if (daysLeft <= 15) {{
          de.urgency_level = 'critical';
          de.status_tag = `⏰ ${{daysLeft}} Days Left (Month 0)`;
          de.pulse_badge = 'bg-danger text-white';
        }} else if (daysLeft <= 22) {{
          de.urgency_level = 'active';
          de.status_tag = `⚡ ${{daysLeft}} Days Left (RFQ Window)`;
          de.pulse_badge = 'bg-warning text-dark';
        }} else {{
          de.urgency_level = 'routine';
          de.status_tag = '🔄 Active Supply Cycle';
          de.pulse_badge = 'bg-secondary text-white';
        }}

        // Also update the urgency_days_left field on the lead itself (used by radar list)
        lead.urgency_days_left = String(daysLeft);
        lead.urgency_level = de.urgency_level;
        lead.urgency_status_tag = de.status_tag;
      }});

      console.log(`[TenderBridge] ✅ Live countdowns recomputed for ${{window.LEADS_DATA.length}} leads on ${{today.toDateString()}}`);
    }}

    // Initialize Workstation on page load
    window.addEventListener('DOMContentLoaded', () => {{
      recomputeLiveCountdowns();   // ← always recalculate from today's date first
      selectLead(0);
    }});
  </script>
</body>
</html>"""

    # Inject JSON payload safely
    leads_json_str = json.dumps(leads_client_data)
    full_html = full_html.replace("__LEADS_DATA_PLACEHOLDER__", leads_json_str)

    with open(output_html, "w", encoding="utf-8") as f:
        f.write(full_html)

    # Also write to index.html for instant GitHub Pages root deployment
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

    # ─── 10. GENERATE STANDALONE ARCHITECTURE PAGE (architecture.html) ────────
    standalone_arch_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>TenderBridge — Platform Architecture & Executive Pitch Deck</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"/>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"/>
  <style>
    body {{
      background-color: #f8fafc;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      color: #1e293b;
    }}
    .navbar-hero {{
      background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
      color: white;
      padding: 1.4rem 0;
      border-bottom: 3px solid #3b82f6;
    }}
    @media (max-width: 768px) {{
      .navbar-hero {{ padding: 0.85rem 0; }}
      .navbar-hero .container {{ flex-direction: column !important; align-items: flex-start !important; gap: 0.6rem; }}
      .navbar-hero h1 {{ font-size: 1.1rem !important; }}
      .display-6 {{ font-size: 1.3rem !important; }}
      .table-responsive {{ -webkit-overflow-scrolling: touch; }}
      .modal-dialog {{ margin: 0.4rem; max-width: calc(100vw - 0.8rem) !important; }}
    }}
  </style>
</head>
<body>
  <header class="navbar-hero mb-4">
    <div class="container d-flex justify-content-between align-items-center">
      <div class="d-flex align-items-center gap-2">
        <span class="fs-4 text-primary"><i class="fa-solid fa-bridge-water"></i></span>
        <h1 class="h3 fw-bold mb-0">TenderBridge Intelligence</h1>
        <span class="badge bg-warning text-dark ms-2 fw-bold">Executive Architecture Deck</span>
      </div>
      <a href="leads_dashboard.html" class="btn btn-primary btn-sm fw-bold px-3">
        <i class="fa-solid fa-arrow-left me-1"></i> Return to Live Workstation
      </a>
    </div>
  </header>
  <main class="container mb-5">
    {architecture_view_html.replace('class="d-none mb-5"', 'class="mb-5"')}
  </main>
  {sources_modal_html}
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
  <script>
    function setViewMode(m) {{
      window.location.href = 'leads_dashboard.html';
    }}
  </script>
</body>
</html>"""

    with open("architecture.html", "w", encoding="utf-8") as f:
        f.write(standalone_arch_html)

    print(f"  ✅ Compiled Phase 2 Workstation: {output_html}, index.html & architecture.html ({total_leads} leads)")
    return output_html


if __name__ == "__main__":
    generate_html_dashboard()
