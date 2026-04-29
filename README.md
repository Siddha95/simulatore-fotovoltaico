# ☀ SunPark Solar Simulator

**Simulatore di produttività per impianti fotovoltaici residenziali**  
---

<img width="2878" height="1556" alt="image" src="https://github.com/user-attachments/assets/36d47826-8a1d-4eb2-97b8-ba03d71e5c7e" />


## Requisiti

- [Docker](https://www.docker.com/) ≥ 24
- [Docker Compose](https://docs.docker.com/compose/) ≥ 2.x (incluso in Docker Desktop)

---

## Avvio rapido

```bash
git clone <repo-url>
cd sunpark
docker compose up --build
```

Dopo la build (~1-2 minuti), i servizi saranno disponibili:

| Servizio                  | URL                         |
| ------------------------- | --------------------------- |
| 🖥 **Interfaccia utente** | http://localhost:3000       |
| 📖 **API Swagger UI**     | http://localhost:3000/docs  |
| 📄 **API ReDoc**          | http://localhost:3000/redoc |

> Per fermare: `docker compose down`

---

## Architettura

```
sunpark/
├── backend/
│   ├── main.py            # FastAPI app + motore di calcolo + generatore PDF
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html         # Single-page app (HTML + CSS + JS vanilla)
│   ├── nginx.conf         # Proxy verso il backend
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

Il **frontend** (nginx sulla porta 80, esposta come 3000) fa da reverse proxy verso il **backend** FastAPI (porta 8000 interna). Non è necessario esporre il backend direttamente.

---

## Utilizzo dell'interfaccia

1. Apri http://localhost:3000
2. Inserisci i parametri dell'impianto:
   - **Nome** e indirizzo (opzionale)
   - **Potenza di picco** in kWp
   - **Coordinate geografiche** (latitudine / longitudine) oppure usa i preset città
   - **Inclinazione** e **orientamento** dei pannelli tramite slider
   - **Efficienza sistema** (default 80%)
3. Clicca **Calcola Simulazione**
4. Visualizza KPI annuali, grafico a barre mensile e tabella di dettaglio
5. Clicca **Scarica PDF** per esportare il report

---

## API REST

La documentazione interattiva completa è disponibile su `/docs` (Swagger UI).

### `POST /simula`

Calcola la simulazione e restituisce JSON strutturato.

**Payload:**

```json
{
  "nome": "Casa Famiglia Rossi",
  "potenza_kwp": 6.0,
  "latitudine": 41.9,
  "longitudine": 12.5,
  "inclinazione": 30,
  "orientamento": 0,
  "efficienza_sistema": 0.8,
  "indirizzo": "Via Roma 1, Roma"
}
```

**Risposta (esempio parziale):**

```json
{
  "nome_impianto": "Casa Famiglia Rossi",
  "potenza_kwp": 6.0,
  "produzione_annua_kwh": 7843.2,
  "ore_equivalenti_annue": 1307.2,
  "performance_ratio": 80.0,
  "co2_evitata_kg": 1827.5,
  "risparmio_annuo_eur": 1725.5,
  "dati_mensili": [
    { "mese": "Gennaio", "irraggiamento_kwh_m2": 62.4, "produzione_kwh": 299.5, "ore_equivalenti": 49.9 },
    ...
  ],
  "timestamp": "2024-01-15T10:30:00"
}
```

### `POST /simula/pdf`

Stesso payload di `/simula` — restituisce direttamente il file PDF.

```bash
curl -X POST http://localhost:3000/simula/pdf \
  -H "Content-Type: application/json" \
  -d '{"nome":"Test","potenza_kwp":6,"latitudine":41.9,"longitudine":12.5}' \
  --output simulazione.pdf
```

### `GET /health`

Health check — restituisce `{"status": "ok"}`.

---

## Modello di calcolo

Il motore stima l'irraggiamento mensile su superficie inclinata tramite un **modello semplificato** basato su:

- Declinazione solare media mensile (formula di Cooper)
- Angolo zenitale solare a mezzogiorno
- Coefficiente di limpidezza atmosferica stagionale
- Ore di luce giornaliere in funzione di latitudine e giorno dell'anno
- Fattori correttivi per inclinazione e orientamento dei pannelli

La **produzione mensile** (kWh) viene calcolata come:

```
P_mese = Irraggiamento_mese × Potenza_picco × Efficienza_sistema
```

I valori di **CO₂ evitata** usano il fattore di emissione medio italiano (0.233 kg CO₂/kWh),  
il **risparmio economico** usa un prezzo medio residenziale di 0.22 €/kWh.

---

## Scelte tecniche

| Componente         | Tecnologia                |
| ------------------ | ------------------------- |
| Backend API        | FastAPI (Python 3.13)     |
| Generazione PDF    | ReportLab                 |
| Frontend           | HTML5 + CSS3 + JS vanilla |
| Web server / Proxy | Nginx (Alpine)            |
| Containerizzazione | Docker Compose            |

---

## Note di sviluppo

- Le variabili e classi principali hanno suffisso `_SP` (es. `Impianto_SP`, `calcola_simulazione_SP`, `VIOLA_SP`)
- Il tema grafico usa i colori viola (`#7C3AED`) e arancione (`#F97316`) del brand SunPark
- Il frontend è un singolo file `index.html` senza dipendenze esterne a runtime (solo Google Fonts)
- Il backend non richiede database né variabili d'ambiente

---

_SunPark S.r.l. · Via Zoe Fontana 220, 00131 Roma · info@sunpark.it_
