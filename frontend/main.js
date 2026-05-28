const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001/api';

let presetsData = {};
let modeInfoData = {};
let jMapData = {};
let nMax = 6;
let currentCoeffs = {}; // mode string " (n, m)" -> value

async function init() {
  try {
    const res = await fetch(`${API_BASE}/presets`);
    const data = await res.json();
    presetsData = data.presets;
    modeInfoData = data.mode_info;
    jMapData = data.j_map;
    nMax = data.n_max;

    setupPresets();
    setupModesGrid();
    setupSettings();
    setupResizer();
    
    document.getElementById('btn-run').addEventListener('click', runSimulation);
    document.getElementById('btn-reset').addEventListener('click', resetSelection);
  } catch (error) {
    console.error("Failed to load presets from backend", error);
    alert("Make sure the FastAPI backend is running on port 8001.");
  }
}

function setupPresets() {
  const select = document.getElementById('preset-select');
  for (const [name, _] of Object.entries(presetsData)) {
    const option = document.createElement('option');
    option.value = name;
    option.textContent = name;
    select.appendChild(option);
  }
  
  select.addEventListener('change', (e) => {
    const presetName = e.target.value;
    if (presetName && presetsData[presetName]) {
      applyPreset(presetName);
    }
  });
}

function applyPreset(name) {
  const coeffs = presetsData[name];
  currentCoeffs = { ...coeffs };
  renderModesGrid(); // re-render to update UI
  triggerSimulation();
}

function resetSelection() {
  currentCoeffs = {};
  document.getElementById('preset-select').value = "";
  renderModesGrid();
  // Clear the results visually or run empty sim
  document.getElementById('empty-state').classList.remove('hidden');
  document.getElementById('results-content').classList.add('hidden');
}

let simTimeout = null;
function triggerSimulation() {
  if (Object.keys(currentCoeffs).length > 0) {
    if (simTimeout) clearTimeout(simTimeout);
    simTimeout = setTimeout(() => {
      runSimulation();
    }, 500);
  }
}

function setupModesGrid() {
  renderModesGrid();
}

function getZLabel(n, m) {
  return `Z(${n},${m})`;
}

function renderModesGrid() {
  const grid = document.getElementById('modes-grid');
  grid.innerHTML = '';
  
  // Build modes list row by row (pyramid)
  for (let n = 0; n <= nMax; n++) {
    const row = document.createElement('div');
    row.className = 'mode-row';

    for (let m = -n; m <= n; m += 2) {
      const modeStr = `(${n}, ${m})`;
      const j = jMapData[modeStr] || "-";
      
      const isActive = currentCoeffs[modeStr] !== undefined;
      const val = isActive ? currentCoeffs[modeStr] : 0.0;
      const info = modeInfoData[modeStr] || "";

      const card = document.createElement('div');
      card.className = `mode-card ${isActive ? 'active' : ''}`;
      
      const defaultVal = 0.2; 
      
      const orderClass = n <= 2 ? 'order-lower' : 'order-higher';

      card.innerHTML = `
        <img class="mode-thumb" src="${API_BASE}/thumbnail/${n}/${m}" alt="Zernike ${n},${m}" />
        <div class="mode-title ${orderClass}">j=${j} ${getZLabel(n, m)}</div>
        <div class="mode-desc ${orderClass}">${info}</div>
        <div class="mode-slider-container">
          <div class="slider-val" id="val-${n}-${m}">${val.toFixed(2)} um</div>
          <input type="range" class="coeff-slider" min="-1.0" max="1.0" step="0.01" value="${val}" data-mode="${modeStr}" data-n="${n}" data-m="${m}">
        </div>
      `;

      card.addEventListener('click', (e) => {
        if (e.target.tagName.toLowerCase() === 'input') return;
        
        if (isActive) {
          delete currentCoeffs[modeStr];
        } else {
          currentCoeffs[modeStr] = defaultVal;
        }
        document.getElementById('preset-select').value = "";
        renderModesGrid();
        triggerSimulation();
      });

      const slider = card.querySelector('.coeff-slider');
      if (slider) {
        slider.addEventListener('input', (e) => {
          const v = parseFloat(e.target.value);
          currentCoeffs[modeStr] = v;
          card.querySelector(`#val-${n}-${m}`).textContent = v.toFixed(2) + ' um';
          triggerSimulation();
        });
      }

      row.appendChild(card);
    }
    grid.appendChild(row);
  }
}

function setupSettings() {
  const ids = ['pupil', 'wavelength', 'landolt', 'contrast'];
  ids.forEach(id => {
    const el = document.getElementById(id);
    const valEl = document.getElementById(`val-${id}`);
    el.addEventListener('input', (e) => {
      valEl.textContent = parseFloat(e.target.value).toFixed(id === 'wavelength' ? 0 : 2);
      triggerSimulation();
    });
  });
  document.getElementById('gap').addEventListener('change', triggerSimulation);
}

function setupResizer() {
  const resizer = document.getElementById('drag-resizer');
  const sidebar = document.getElementById('configure');

  let isDragging = false;

  resizer.addEventListener('mousedown', (e) => {
    isDragging = true;
    document.body.style.cursor = 'col-resize';
  });

  document.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    let newWidth = e.clientX;
    if (newWidth < 320) newWidth = 320;
    if (newWidth > 800) newWidth = 800;
    sidebar.style.flex = `0 0 ${newWidth}px`;
  });

  document.addEventListener('mouseup', () => {
    isDragging = false;
    document.body.style.cursor = 'default';
  });
}

async function runSimulation() {
  const reqData = {
    coeffs: currentCoeffs,
    pupil_mm: parseFloat(document.getElementById('pupil').value),
    wavelength_nm: parseInt(document.getElementById('wavelength').value),
    landolt_diameter_arcmin: parseFloat(document.getElementById('landolt').value),
    contrast: parseFloat(document.getElementById('contrast').value),
    gap_direction_deg: parseInt(document.getElementById('gap').value),
    N: 512,
    pad_factor: 2,
    lenslet_n: 13
  };

  document.getElementById('loading').classList.remove('hidden');
  document.getElementById('empty-state').classList.add('hidden');
  document.getElementById('results-content').classList.add('hidden');

  try {
    const res = await fetch(`${API_BASE}/simulate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(reqData)
    });
    
    if (!res.ok) throw new Error("Simulation failed");
    
    const data = await res.json();
    
    document.getElementById('report-img').src = `data:image/png;base64,${data.report_img_base64}`;
    document.getElementById('mode-map-img').src = `data:image/png;base64,${data.mode_map_img_base64}`;
    
    if (data.vision_images_base64 && data.vision_images_base64.length === 4) {
      for (let i = 0; i < 4; i++) {
        document.getElementById(`vision-img-${i}`).src = `data:image/jpeg;base64,${data.vision_images_base64[i]}`;
      }
    }
    
    // Build beautiful Summary HTML
    const container = document.getElementById('summary-container');
    let html = `<div class="summary-section">
      <h4 class="summary-subtitle">Active Zernike Modes</h4>
      <div class="modes-list">`;
      
    if (data.active_modes && data.active_modes.length > 0) {
      data.active_modes.forEach(mode => {
        const sign = mode.coeff >= 0 ? '+' : '';
        const bgClass = mode.n <= 2 ? 'bg-lower' : 'bg-higher';
        const textClass = mode.n <= 2 ? 'order-lower' : 'order-higher';
        html += `
          <div class="formula-card">
            <div class="formula-header">
              <span class="j-badge ${bgClass}">j${mode.j}</span>
              <span class="mode-label">${mode.label}</span>
              <span class="coeff-badge">${sign}${mode.coeff.toFixed(3)} um</span>
            </div>
            <div class="formula-body">
              <div class="math-line"><span class="math-sym ${textClass}">${mode.label}(ρ,θ)</span> = ${mode.formula_z}</div>
              <div class="math-line"><span class="math-sym ${textClass}">W(ρ,θ)</span> += (${sign}${mode.coeff.toFixed(3)} um) × ${mode.label}(ρ,θ)</div>
            </div>
          </div>
        `;
      });
    } else {
      html += `<div class="empty-modes">No aberrations selected.</div>`;
    }
    
    html += `</div></div>`; // close modes-list and summary-section
    
    // RMS Section
    html += `<div class="summary-section">
      <h4 class="summary-subtitle">RMS Calculation</h4>`;
      
    // Generate detailed theoretical RMS calculation
    let calcModes = data.active_modes ? data.active_modes.filter(m => m.j !== 1 && m.coeff !== 0) : [];
    if (calcModes.length > 0) {
      let squaresStr = calcModes.map(m => `(${m.coeff.toFixed(2)})²`).join(" + ");
      let squaresVals = calcModes.map(m => (m.coeff * m.coeff).toFixed(4)).join(" + ");
      let sumSq = calcModes.reduce((sum, m) => sum + (m.coeff * m.coeff), 0);
      let finalRms = Math.sqrt(sumSq);
      
      html += `
      <div class="rms-formula-box" style="text-align: left; padding: 16px; line-height: 1.6;">
        <div><code>RMS = √{ ${squaresStr} }</code></div>
        <div><code>    = √{ ${squaresVals} }</code></div>
        <div><code>    = √${sumSq.toFixed(4)}</code></div>
        <div style="font-weight: bold; color: #007aff; margin-top: 8px;"><code>    = ${finalRms.toFixed(4)} μm</code></div>
      </div>`;
    } else {
      html += `
      <div class="rms-formula-box">
        <code>RMS = sqrt(mean((W - mean(W))²))</code>
      </div>`;
    }

    html += `<div class="rms-cards">`;
      
    const rmsDataList = [data.rms_total, data.rms_lower, data.rms_higher];
    rmsDataList.forEach(r => {
      html += `
        <div class="rms-card">
          <div class="rms-title">${r.label}</div>
          <div class="rms-val">${r.rms.toFixed(3)} <span class="rms-unit">μm</span></div>
          <div class="rms-details">
            <div><span>Points:</span> ${r.n_points}</div>
            <div><span>Mean:</span> ${r.mean_before > 0 ? '+' : ''}${r.mean_before.toFixed(4)} μm</div>
            <div><span>Mean Sq:</span> ${r.mean_square.toFixed(4)} μm²</div>
          </div>
        </div>
      `;
    });
    
    html += `</div></div>`;
    
    container.innerHTML = html;
    
    document.getElementById('results-content').classList.remove('hidden');
    
    // scroll to results
    document.getElementById('results').scrollIntoView({behavior: 'smooth'});
  } catch (error) {
    console.error(error);
    alert("Error running simulation. Check backend logs.");
    document.getElementById('empty-state').classList.remove('hidden');
  } finally {
    document.getElementById('loading').classList.add('hidden');
  }
}

document.addEventListener('DOMContentLoaded', init);
