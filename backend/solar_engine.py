import math
from constants import MESI, GIORNI_MESE, COSTANTE_SOLARE, CO2_EMISSION_FACTOR, ELECTRICITY_PRICE
from models import Impianto_SP, RisultatoMensile_SP, SimulazioneRisultato_SP
from datetime import datetime


def calcola_irraggiamento_SP(latitudine: float, longitudine: float,
                              inclinazione: float, orientamento: float,
                              mese_idx: int) -> float:
    """
    Stima l'irraggiamento mensile su superficie inclinata (kWh/m²/mese).
    Basato su modello semplificato con correzione per latitudine, stagione,
    inclinazione e orientamento.
    """
    lat_rad = math.radians(latitudine)
    inc_rad = math.radians(inclinazione)
    ori_rad = math.radians(orientamento)

    # Declinazione solare media del mese
    giorno_anno = sum(GIORNI_MESE[:mese_idx]) + GIORNI_MESE[mese_idx] // 2
    declinazione = math.radians(23.45 * math.sin(math.radians(360 * (284 + giorno_anno) / 365)))

    # Irraggiamento orizzontale giornaliero medio stimato (modello Hottel semplificato)
    cos_zenith_noon = (math.sin(lat_rad) * math.sin(declinazione) +
                       math.cos(lat_rad) * math.cos(declinazione))
    cos_zenith_noon = max(0.01, cos_zenith_noon)

    # Costante solare e fattore atmosferico
    clearness = 0.55 + 0.1 * math.sin(math.radians(180 * mese_idx / 11 - 30))
    ore_luce = 10 + 4 * math.sin(math.radians(360 * (giorno_anno - 80) / 365)) * (latitudine / 45)
    ore_luce = max(6, min(16, ore_luce))

    irr_orizzontale = (COSTANTE_SOLARE * clearness * cos_zenith_noon * ore_luce) / 1000  # kWh/m²/giorno

    # Fattore di correzione per inclinazione e orientamento
    angolo_ottimale = 90 - latitudine + math.degrees(declinazione)
    delta_inc = abs(inclinazione - angolo_ottimale)
    f_inclinazione = math.cos(math.radians(max(0, delta_inc - 5)))

    # Penalità orientamento (massimo per Sud = 0°)
    f_orientamento = math.cos(ori_rad) * 0.3 + 0.7

    irr_inclinata = irr_orizzontale * (0.9 + 0.1 * f_inclinazione) * f_orientamento

    return round(irr_inclinata * GIORNI_MESE[mese_idx], 2)


def calcola_simulazione_SP(impianto: Impianto_SP) -> SimulazioneRisultato_SP:
    """
    Calcola la simulazione annuale completa dell'impianto fotovoltaico.
    """
    dati_mensili_SP = []
    produzione_totale_SP = 0.0

    for i, mese in enumerate(MESI):
        irr = calcola_irraggiamento_SP(
            impianto.latitudine,
            impianto.longitudine,
            impianto.inclinazione,
            impianto.orientamento,
            i
        )
        produzione = round(irr * impianto.potenza_kwp * impianto.efficienza_sistema, 2)
        ore_eq = round(produzione / impianto.potenza_kwp, 2) if impianto.potenza_kwp > 0 else 0

        dati_mensili_SP.append(RisultatoMensile_SP(
            mese=mese,
            irraggiamento_kwh_m2=irr,
            produzione_kwh=produzione,
            ore_equivalenti=ore_eq
        ))
        produzione_totale_SP += produzione

    ore_annue = round(produzione_totale_SP / impianto.potenza_kwp, 1)
    pr = round(impianto.efficienza_sistema * 100, 1)
    co2 = round(produzione_totale_SP * CO2_EMISSION_FACTOR, 1)
    risparmio = round(produzione_totale_SP * ELECTRICITY_PRICE, 2)

    return SimulazioneRisultato_SP(
        nome_impianto=impianto.nome,
        potenza_kwp=impianto.potenza_kwp,
        latitudine=impianto.latitudine,
        longitudine=impianto.longitudine,
        inclinazione=impianto.inclinazione,
        orientamento=impianto.orientamento,
        efficienza_sistema=impianto.efficienza_sistema,
        indirizzo=impianto.indirizzo,
        produzione_annua_kwh=round(produzione_totale_SP, 2),
        ore_equivalenti_annue=ore_annue,
        performance_ratio=pr,
        co2_evitata_kg=co2,
        risparmio_annuo_eur=risparmio,
        dati_mensili=dati_mensili_SP,
        timestamp=datetime.now().isoformat()
    )
