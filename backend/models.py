from pydantic import BaseModel, Field
from typing import Optional


class Impianto_SP(BaseModel):
    """Dati di input per un impianto fotovoltaico."""
    nome: str = Field(..., description="Nome dell'impianto")
    potenza_kwp: float = Field(..., gt=0, description="Potenza di picco in kWp")
    latitudine: float = Field(..., ge=-90, le=90, description="Latitudine in gradi decimali")
    longitudine: float = Field(..., ge=-180, le=180, description="Longitudine in gradi decimali")
    inclinazione: float = Field(default=30.0, ge=0, le=90, description="Inclinazione dei pannelli in gradi")
    orientamento: float = Field(default=0.0, ge=-180, le=180, description="Orientamento (0=Sud, -90=Est, 90=Ovest)")
    efficienza_sistema: float = Field(default=0.80, ge=0.5, le=1.0, description="Efficienza del sistema (0-1)")
    indirizzo: Optional[str] = Field(default=None, description="Indirizzo dell'impianto")


class RisultatoMensile_SP(BaseModel):
    """Risultato mensile della simulazione."""
    mese: str
    irraggiamento_kwh_m2: float
    produzione_kwh: float
    ore_equivalenti: float


class SimulazioneRisultato_SP(BaseModel):
    """Risultato completo della simulazione annuale."""
    nome_impianto: str
    potenza_kwp: float
    latitudine: float
    longitudine: float
    inclinazione: float
    orientamento: float
    efficienza_sistema: float
    indirizzo: Optional[str]
    produzione_annua_kwh: float
    ore_equivalenti_annue: float
    performance_ratio: float
    co2_evitata_kg: float
    risparmio_annuo_eur: float
    dati_mensili: list[RisultatoMensile_SP]
    timestamp: str
