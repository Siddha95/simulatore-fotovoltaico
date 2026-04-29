import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from models import SimulazioneRisultato_SP
from constants import PDF_COLORS, PDF_MARGINS, PDF_FONT_SIZES, COMPANY_INFO


def _get_header_table_style() -> list:
    """Stile comune per tabelle header."""
    return [
        ("BACKGROUND", (0, 0), (-1, 0), PDF_COLORS["viola"]),
        ("TEXTCOLOR", (0, 0), (-1, 0), PDF_COLORS["bianco"]),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]


def _get_standard_table_style(header_color=PDF_COLORS["viola"]) -> list:
    """Stile standard per tabelle con header colorato."""
    return _get_header_table_style() + [
        ("FONTSIZE", (0, 0), (-1, -1), PDF_FONT_SIZES["table"]),
        ("GRID", (0, 0), (-1, -1), 0.5, PDF_COLORS["grid"]),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]


def _add_params_section(elements: list, risultato: SimulazioneRisultato_SP, styles: dict, section_style: ParagraphStyle):
    """Aggiunge sezione parametri impianto al PDF."""
    elements.append(Paragraph("Parametri Impianto", section_style))
    params_data = [
        ["Parametro", "Valore"],
        ["Nome impianto", risultato.nome_impianto],
        ["Indirizzo", risultato.indirizzo or "—"],
        ["Potenza di picco", f"{risultato.potenza_kwp} kWp"],
        ["Latitudine / Longitudine", f"{risultato.latitudine}° / {risultato.longitudine}°"],
        ["Inclinazione pannelli", f"{risultato.inclinazione}°"],
        ["Orientamento", f"{risultato.orientamento}° (0=Sud)"],
        ["Efficienza sistema", f"{risultato.efficienza_sistema * 100:.0f}%"],
    ]
    t = Table(params_data, colWidths=[7*cm, 10*cm])
    t.setStyle(TableStyle(_get_standard_table_style() + [
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [PDF_COLORS["viola_chiaro"], PDF_COLORS["bianco"]]),
    ]))
    elements.append(t)


def _add_kpi_section(elements: list, risultato: SimulazioneRisultato_SP, styles: dict, section_style: ParagraphStyle):
    """Aggiunge sezione KPI annuali al PDF."""
    elements.append(Paragraph("Risultati Annuali", section_style))
    kpi_data = [
        ["Indicatore", "Valore"],
        ["Produzione annua", f"{risultato.produzione_annua_kwh:,.0f} kWh/anno"],
        ["Ore equivalenti", f"{risultato.ore_equivalenti_annue:,.0f} h/anno"],
        ["Performance Ratio", f"{risultato.performance_ratio}%"],
        ["CO₂ evitata", f"{risultato.co2_evitata_kg:,.0f} kg/anno"],
        ["Risparmio stimato", f"€ {risultato.risparmio_annuo_eur:,.2f}/anno"],
    ]
    t2 = Table(kpi_data, colWidths=[9*cm, 8*cm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PDF_COLORS["arancio"]),
        ("TEXTCOLOR", (0, 0), (-1, 0), PDF_COLORS["bianco"]),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (1, 1), (1, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (1, 1), (1, -1), PDF_COLORS["viola"]),
        ("FONTSIZE", (0, 0), (-1, -1), PDF_FONT_SIZES["table"]),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [PDF_COLORS["arancio_chiaro"], PDF_COLORS["bianco"]]),
        ("GRID", (0, 0), (-1, -1), 0.5, PDF_COLORS["grid"]),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(t2)


def _add_monthly_section(elements: list, risultato: SimulazioneRisultato_SP, styles: dict, section_style: ParagraphStyle):
    """Aggiunge sezione dati mensili al PDF."""
    elements.append(Paragraph("Produzione Mensile", section_style))
    monthly_data = [["Mese", "Irraggiamento\n(kWh/m²)", "Produzione\n(kWh)", "Ore\nEquivalenti"]]
    for m in risultato.dati_mensili:
        monthly_data.append([
            m.mese,
            f"{m.irraggiamento_kwh_m2:.1f}",
            f"{m.produzione_kwh:.1f}",
            f"{m.ore_equivalenti:.1f}",
        ])
    monthly_data.append([
        "TOTALE",
        "",
        f"{risultato.produzione_annua_kwh:.1f}",
        f"{risultato.ore_equivalenti_annue:.1f}",
    ])
    t3 = Table(monthly_data, colWidths=[4.5*cm, 4.5*cm, 4.5*cm, 3.5*cm])
    t3.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PDF_COLORS["viola"]),
        ("TEXTCOLOR", (0, 0), (-1, 0), PDF_COLORS["bianco"]),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, -1), (-1, -1), PDF_COLORS["arancio"]),
        ("TEXTCOLOR", (0, -1), (-1, -1), PDF_COLORS["bianco"]),
        ("FONTSIZE", (0, 0), (-1, -1), PDF_FONT_SIZES["table"] - 1),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [PDF_COLORS["bianco"], PDF_COLORS["viola_ultra_chiaro"]]),
        ("GRID", (0, 0), (-1, -1), 0.4, PDF_COLORS["grid"]),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(t3)


def genera_pdf_SP(risultato: SimulazioneRisultato_SP) -> bytes:
    """Genera un report PDF completo della simulazione."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=PDF_MARGINS["right"]*cm,
        leftMargin=PDF_MARGINS["left"]*cm,
        topMargin=PDF_MARGINS["top"]*cm,
        bottomMargin=PDF_MARGINS["bottom"]*cm,
        title=f"Simulazione - {risultato.nome_impianto}"
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleSP",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=PDF_FONT_SIZES["title"],
        textColor=PDF_COLORS["viola"],
        spaceAfter=4,
        alignment=TA_CENTER
    )
    subtitle_style = ParagraphStyle(
        "SubtitleSP",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=PDF_FONT_SIZES["subtitle"],
        textColor=PDF_COLORS["grigio"],
        spaceAfter=16,
        alignment=TA_CENTER
    )
    section_style = ParagraphStyle(
        "SectionSP",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=PDF_FONT_SIZES["section"],
        textColor=PDF_COLORS["viola"],
        spaceBefore=14,
        spaceAfter=6
    )

    elements = []

    # Header
    elements.append(Paragraph("☀ SunPark Solar Simulator", title_style))
    elements.append(Paragraph(f"Report di Simulazione — {risultato.nome_impianto}", subtitle_style))
    elements.append(Paragraph(f"Generato il: {risultato.timestamp[:10]}", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=PDF_COLORS["arancio"], spaceAfter=12))

    # Sezioni contenuto
    _add_params_section(elements, risultato, styles, section_style)
    _add_kpi_section(elements, risultato, styles, section_style)
    _add_monthly_section(elements, risultato, styles, section_style)

    # Footer
    elements.append(Spacer(1, 0.5*cm))
    elements.append(HRFlowable(width="100%", thickness=1, color=PDF_COLORS["viola"]))
    elements.append(Paragraph(
        COMPANY_INFO,
        ParagraphStyle(
            "FooterSP",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=PDF_FONT_SIZES["footer"],
            textColor=PDF_COLORS["grigio"],
            alignment=TA_CENTER,
            spaceBefore=6
        )
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()
