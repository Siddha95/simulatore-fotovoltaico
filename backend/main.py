from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import io

from models import Impianto_SP, SimulazioneRisultato_SP
from solar_engine import calcola_simulazione_SP
from pdf_generator import genera_pdf_SP

# ─── FastAPI App Setup ────────────────────────────────────────────────────────

app_SP = FastAPI(
    title="SunPark Solar Simulator API",
    description="API per la simulazione della produttività di impianti fotovoltaici residenziali",
    version="1.0.0"
)

app_SP.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── API Routes ───────────────────────────────────────────────────────────────

@app_SP.get("/", tags=["Info"])
def root():
    return {"service": "SunPark Solar Simulator", "version": "1.0.0", "status": "online"}


@app_SP.get("/health", tags=["Info"])
def health():
    return {"status": "ok"}


@app_SP.post("/simula", response_model=SimulazioneRisultato_SP, tags=["Simulazione"])
def simula(impianto: Impianto_SP):
    """Calcola la produzione energetica annuale di un impianto fotovoltaico."""
    try:
        return calcola_simulazione_SP(impianto)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app_SP.post("/simula/pdf", tags=["Simulazione"])
def simula_pdf(impianto: Impianto_SP):
    """Calcola la simulazione e restituisce un report PDF."""
    try:
        risultato = calcola_simulazione_SP(impianto)
        pdf_bytes = genera_pdf_SP(risultato)
        nome_file = f"sunpark_{impianto.nome.replace(' ', '_')}.pdf"
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{nome_file}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app_SP.get("/docs-info", tags=["Info"])
def docs_info():
    return {
        "swagger_ui": "/docs",
        "redoc": "/redoc",
        "openapi_json": "/openapi.json"
    }