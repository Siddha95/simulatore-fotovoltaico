# ─── Calendar Data ────────────────────────────────────────────────────────────

MESI = [
    "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
    "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"
]

GIORNI_MESE = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

# ─── Solar Constants ──────────────────────────────────────────────────────────

COSTANTE_SOLARE = 1361  # W/m² (solar constant)

# ─── Environmental Factors ────────────────────────────────────────────────────

CO2_EMISSION_FACTOR = 0.233  # kg CO₂/kWh (mix energetico Italia)
ELECTRICITY_PRICE = 0.22  # €/kWh (media residenziale Italia 2026)

# ─── PDF Colors ───────────────────────────────────────────────────────────────

from reportlab.lib import colors

PDF_COLORS = {
    "viola": colors.HexColor("#7C3AED"),
    "arancio": colors.HexColor("#F97316"),
    "viola_chiaro": colors.HexColor("#EDE9FE"),
    "grigio": colors.HexColor("#6B7280"),
    "bianco": colors.white,
    "nero": colors.HexColor("#111827"),
    "grid": colors.HexColor("#D1D5DB"),
    "arancio_chiaro": colors.HexColor("#FFF7ED"),
    "viola_ultra_chiaro": colors.HexColor("#F5F3FF"),
}

# ─── PDF Page Setup ───────────────────────────────────────────────────────────

PDF_MARGINS = {
    "right": 2,   # cm
    "left": 2,    # cm
    "top": 2,     # cm
    "bottom": 2,  # cm
}

PDF_FONT_SIZES = {
    "title": 22,
    "subtitle": 10,
    "section": 12,
    "body": 9,
    "table": 9,
    "footer": 7,
}

# ─── Company Info ─────────────────────────────────────────────────────────────

COMPANY_INFO = "SunPark S.r.l. · Via Zoe Fontana 220, 00131 Roma · info@sunpark.it · P.IVA 12336581009"
