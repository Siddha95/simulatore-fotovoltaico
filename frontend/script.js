const API_URL_SP = '';  // same origin (proxied by nginx)

function updateOriLabel(val) {
  const v = parseInt(val);
  let dir = v === 0 ? 'Sud' : v > 0 ? 'Ovest' : 'Est';
  document.getElementById('ori-val').textContent = `${v}° (${dir})`;
}

function setCity(lat, lon, nome) {
  document.getElementById('lat').value = lat;
  document.getElementById('lon').value = lon;
  document.getElementById('nome').value = `Impianto ${nome}`;
}

function getPayload() {
  return {
    nome: document.getElementById('nome').value.trim() || 'Impianto',
    potenza_kwp: parseFloat(document.getElementById('potenza').value),
    latitudine: parseFloat(document.getElementById('lat').value),
    longitudine: parseFloat(document.getElementById('lon').value),
    inclinazione: parseFloat(document.getElementById('inclinazione').value),
    orientamento: parseFloat(document.getElementById('orientamento').value),
    efficienza_sistema: parseFloat(document.getElementById('efficienza').value) / 100,
    indirizzo: document.getElementById('indirizzo').value.trim() || null,
  };
}

async function avviaSimulazione() {
  const errEl = document.getElementById('error-msg');
  errEl.className = 'alert';
  errEl.textContent = '';

  const payload = getPayload();
  if (isNaN(payload.potenza_kwp) || payload.potenza_kwp <= 0) {
    errEl.classList.add('error'); errEl.textContent = 'Inserisci una potenza valida (> 0 kWp).'; return;
  }
  if (isNaN(payload.latitudine) || isNaN(payload.longitudine)) {
    errEl.classList.add('error'); errEl.textContent = 'Inserisci coordinate geografiche valide.'; return;
  }

  document.getElementById('btn-simula').disabled = true;
  document.getElementById('loader').classList.add('active');
  document.getElementById('empty-state').style.display = 'none';
  document.getElementById('results-content').style.display = 'none';

  try {
    const res = await fetch(`${API_URL_SP}/simula`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    renderResults(data);
  } catch (e) {
    errEl.classList.add('error');
    errEl.textContent = 'Errore di connessione al server. Verifica che il backend sia attivo.';
    document.getElementById('empty-state').style.display = 'flex';
  } finally {
    document.getElementById('btn-simula').disabled = false;
    document.getElementById('loader').classList.remove('active');
  }
}

function renderResults(d) {
  // KPI
  const kpis = [
    { icon: '⚡', val: d.produzione_annua_kwh.toLocaleString('it-IT', {maximumFractionDigits:0}), unit: 'kWh/anno', label: 'Produzione Annua', cls: 'kpi-arancio' },
    { icon: '🕐', val: d.ore_equivalenti_annue.toLocaleString('it-IT', {maximumFractionDigits:0}), unit: 'h/anno', label: 'Ore Equivalenti', cls: 'kpi-viola' },
    { icon: '📊', val: d.performance_ratio, unit: '%', label: 'Performance Ratio', cls: 'kpi-viola' },
    { icon: '🌱', val: d.co2_evitata_kg.toLocaleString('it-IT', {maximumFractionDigits:0}), unit: 'kg/anno', label: 'CO₂ Evitata', cls: 'kpi-green' },
    { icon: '💶', val: '€ ' + d.risparmio_annuo_eur.toLocaleString('it-IT', {minimumFractionDigits:2, maximumFractionDigits:2}), unit: '/anno', label: 'Risparmio Stimato', cls: 'kpi-arancio' },
  ];
  document.getElementById('kpi-grid').innerHTML = kpis.map(k =>
    `<div class="kpi-card ${k.cls}">
      <div class="kpi-icon">${k.icon}</div>
      <div class="kpi-value">${k.val}</div>
      <div class="kpi-label">${k.unit} · ${k.label}</div>
    </div>`
  ).join('');

  // Chart
  const maxProd = Math.max(...d.dati_mensili.map(m => m.produzione_kwh));
  const barColors = [
    '#7C3AED','#8B47EE','#9A54EF','#A861F0','#B76EF1',
    '#F97316','#F4811F','#EF8F28','#EA9D31','#E5AB3A',
    '#9A54EF','#7C3AED'
  ];
  document.getElementById('chart-bars').innerHTML = d.dati_mensili.map((m, i) => {
    const pct = (m.produzione_kwh / maxProd * 100).toFixed(1);
    return `<div class="bar-wrap">
      <div class="bar" style="height:${pct}%;background:${barColors[i]}">
        <div class="bar-tooltip">${m.produzione_kwh.toLocaleString('it-IT', {maximumFractionDigits:0})} kWh</div>
      </div>
      <div class="bar-label">${m.mese.substring(0,3)}</div>
    </div>`;
  }).join('');

  // Table
  document.getElementById('monthly-body').innerHTML = d.dati_mensili.map(m =>
    `<tr>
      <td>${m.mese}</td>
      <td>${m.irraggiamento_kwh_m2.toFixed(1)}</td>
      <td class="td-highlight">${m.produzione_kwh.toFixed(1)}</td>
      <td>${m.ore_equivalenti.toFixed(1)}</td>
    </tr>`
  ).join('') + `<tr style="border-top:2px solid rgba(124,58,237,0.3)">
    <td style="font-weight:700;color:var(--text)">Totale</td>
    <td>—</td>
    <td class="td-highlight" style="font-size:1rem">${d.produzione_annua_kwh.toFixed(0)}</td>
    <td>${d.ore_equivalenti_annue.toFixed(1)}</td>
  </tr>`;

  document.getElementById('results-content').style.display = 'block';
}

async function scaricaPDF() {
  const btn = document.getElementById('btn-pdf');
  btn.disabled = true; btn.textContent = '⏳ Generazione…';
  try {
    const res = await fetch(`${API_URL_SP}/simula/pdf`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(getPayload()),
    });
    if (!res.ok) throw new Error();
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'sunpark_simulazione.pdf'; a.click();
    URL.revokeObjectURL(url);
  } catch {
    alert('Errore nella generazione del PDF.');
  } finally {
    btn.disabled = false; btn.textContent = '⬇ Scarica PDF';
  }
}