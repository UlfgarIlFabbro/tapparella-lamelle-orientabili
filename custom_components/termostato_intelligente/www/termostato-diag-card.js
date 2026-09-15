// ============================================================================
// Termostato Diag Card
// Card singola entità per Termostato Intelligente FV, con sfondo colorato in
// base allo stato del climatizzatore e un pannello configurabile di attributi
// diagnostici (notte, DRY, blocco riaccensione, FV, notifiche, ecc).
// Completamente configurabile da editor grafico — nessun YAML necessario.
// ============================================================================

// Mappa unificata icona+colore per ciascuna modalità hvac — usata sia per lo
// sfondo/cornice della card sia per i pulsanti modalità in alto, così sono
// sempre coerenti tra loro (prima erano due sistemi scollegati). Il verde è
// deliberatamente escluso: è riservato al pulsante di accensione/spegnimento.
const HVAC_MODE_STYLE = {
  cool:      { icon: "mdi:snowflake",              activeBg: "#2e6fd9", activeFg: "#fff",    cardBg: "rgba(46, 111, 217, 0.5)",  cardBorder: "#2e6fd9", cardShadow: "rgba(46, 111, 217, 0.3)" },
  dry:       { icon: "mdi:water",                  activeBg: "#f0b400", activeFg: "#4a3800", cardBg: "rgba(240, 180, 0, 0.5)",   cardBorder: "#f0b400", cardShadow: "rgba(240, 180, 0, 0.3)" },
  heat:      { icon: "mdi:fire",                   activeBg: "#e8602c", activeFg: "#fff",    cardBg: "rgba(232, 96, 44, 0.5)",   cardBorder: "#e8602c", cardShadow: "rgba(232, 96, 44, 0.3)" },
  fan_only:  { icon: "mdi:fan",                    activeBg: "#8e5fd1", activeFg: "#fff",    cardBg: "rgba(142, 95, 209, 0.5)",  cardBorder: "#8e5fd1", cardShadow: "rgba(142, 95, 209, 0.3)" },
  auto:      { icon: "mdi:alpha-a-circle",         activeBg: "#1fa8a0", activeFg: "#fff",    cardBg: "rgba(31, 168, 160, 0.5)",  cardBorder: "#1fa8a0", cardShadow: "rgba(31, 168, 160, 0.3)" },
  heat_cool: { icon: "mdi:sun-snowflake-variant",  activeBg: "#c74e8e", activeFg: "#fff",    cardBg: "rgba(199, 78, 142, 0.5)",  cardBorder: "#c74e8e", cardShadow: "rgba(199, 78, 142, 0.3)" },
};
const UNKNOWN_MODE_STYLE = { icon: "mdi:help-circle-outline", activeBg: "#8a8a8a", activeFg: "#fff", cardBg: "rgba(138, 138, 138, 0.4)", cardBorder: "#8a8a8a", cardShadow: "rgba(138, 138, 138, 0.3)" };
const OFF_COLOR = { bg: "rgba(255, 255, 255, 0.5)", border: "black", shadow: "rgba(255, 255, 255, 0.3)" };
const DEFAULT_COLOR = { bg: "rgba(255, 255, 255, 0.5)", border: "black", shadow: "rgba(255, 255, 255, 0.3)" };

function applyOpacity(rgbaString, opacity) {
  // Sostituisce solo il valore alpha di una stringa rgba() esistente,
  // mantenendo invariati i valori R/G/B — usato per rendere lo sfondo
  // della card più o meno trasparente in base alla configurazione.
  const match = rgbaString.match(/rgba?\(([^)]+)\)/);
  if (!match) return rgbaString;
  const parts = match[1].split(",").map((s) => s.trim());
  const [r, g, b] = parts;
  return `rgba(${r}, ${g}, ${b}, ${opacity})`;
}

// Elenco completo attributi diagnostici conosciuti, con etichetta e icona.
// type serve a formattare il valore: bool | timestamp | number | text | array | notify_event
const KNOWN_ATTRIBUTES = [
  { key: "finestra_aperta", label: "Finestra aperta", icon: "🪟", type: "bool", linkedEntityAttr: "finestra_entity_id" },
  { key: "porta_aperta", label: "Porta aperta", icon: "🚪", type: "bool", linkedEntityAttr: "porta_entity_id" },
  { key: "modalita_notturna_attiva", label: "Modalità notturna attiva", icon: "🌙", type: "bool" },
  { key: "target_effettivo", label: "Target effettivo", icon: "🎯", type: "number", unit: "°C" },
  { key: "accensione_notturna_automatica", label: "Acceso automaticamente di notte", icon: "🌙⚡", type: "bool" },
  { key: "accensione_notturna_abilitata", label: "Accensione notturna abilitata", icon: "🌙", type: "bool" },
  { key: "spegnimento_notturno_abilitato", label: "Spegnimento notturno abilitato", icon: "🌙", type: "bool" },
  { key: "spegnimento_fine_notte_abilitato", label: "Spegnimento fine notte abilitato", icon: "🌅", type: "bool" },
  { key: "spegnimento_fv_abilitato", label: "Spegnimento FV abilitato", icon: "☀️", type: "bool" },
  { key: "accensione_fv_abilitata", label: "Accensione FV abilitata", icon: "☀️", type: "bool" },
  { key: "termostato_abilitato", label: "Termostato abilitato (master)", icon: "🔌", type: "bool" },
  { key: "raffreddamento_rapido", label: "Raffreddamento rapido", icon: "❄️", type: "bool" },
  { key: "fascia_silenzio_attiva", label: "Fascia di silenzio attiva", icon: "🔇", type: "bool" },
  { key: "fv_surplus_buffer", label: "Buffer surplus FV", icon: "📊", type: "array" },
  { key: "dry_since", label: "DRY avviato alle", icon: "💧", type: "timestamp" },
  { key: "dry_end", label: "DRY termina alle", icon: "💧", type: "timestamp" },
  { key: "dry_elapsed_min", label: "Minuti DRY trascorsi", icon: "⏱️", type: "number", unit: "min" },
  { key: "spento_manualmente_da", label: "Spento manualmente da", icon: "✋", type: "timestamp" },
  { key: "blocco_riaccensione_attivo", label: "Blocco riaccensione attivo", icon: "🔒", type: "bool" },
  { key: "soglia_accensione_fv", label: "Soglia accensione", icon: "🌡️", type: "number", unit: "°C" },
  { key: "fv_basso_da", label: "FV insufficiente da", icon: "📉", type: "timestamp" },
  { key: "acceso_manualmente_da", label: "Acceso manualmente da (immunità FV)", icon: "✋", type: "timestamp" },
  { key: "sonda_esterna_bloccata", label: "Sonda esterna bloccata (fallback su interna)", icon: "📡", type: "bool" },
  { key: "modalita_esterna_non_gestita", label: "Modalità non gestita (caldo/ventilatore/auto)", icon: "⚠️", type: "bool" },
  { key: "ultimo_evento_notifica", label: "Ultimo evento notifica (storico espandibile)", icon: "🔔", type: "notify_event", dedicatedWidget: true },
  { key: "presenza_da", label: "Presenza rilevata da", icon: "🧍", type: "timestamp" },
  { key: "notte_sotto_target_da", label: "Sotto target notturno da", icon: "🌙", type: "timestamp" },
  { key: "snapshot_attivo", label: "Snapshot finestra attivo", icon: "📸", type: "bool" },
  { key: "climatizzatore_reale", label: "Entità climatizzatore reale", icon: "🔧", type: "text" },
  { key: "modalita_configurazione", label: "Modalità configurazione", icon: "⚙️", type: "mode_label" },
  { key: "fv_priorita", label: "Priorità FV (regolabile con frecce)", icon: "🔢", type: "number", dedicatedWidget: true },
  { key: "protezione_potenza_attiva", label: "Protezione potenza attiva", icon: "⚡", type: "bool" },
  { key: "protezione_potenza_da", label: "Protezione potenza da", icon: "⚡", type: "timestamp" },
  { key: "emergenza_caldo_attiva", label: "Emergenza caldo attiva", icon: "🔥", type: "bool" },
];

function findAttrDef(key) {
  return KNOWN_ATTRIBUTES.find((a) => a.key === key) || { key, label: key, icon: "•", type: "text" };
}

function formatTimestamp(value) {
  if (!value) return "—";
  const d = new Date(value);
  if (isNaN(d.getTime())) return String(value);
  const now = new Date();
  const sameDay = d.toDateString() === now.toDateString();
  const time = d.toLocaleTimeString("it-IT", { hour: "2-digit", minute: "2-digit" });
  if (sameDay) return time;
  const date = d.toLocaleDateString("it-IT", { day: "2-digit", month: "2-digit" });
  return `${date} ${time}`;
}

// Traduzione automatica per i valori grezzi (spesso in inglese, stile
// slug tecnico) delle opzioni di entità select esposte da integrazioni
// diverse (es. modalità "riposo" con valori come "for_old", "for_kids").
// Il dizionario copre i termini più comuni per questo tipo di funzione;
// per qualunque valore non riconosciuto, applichiamo comunque una pulizia
// meccanica (via leggibile, non più uno slug grezzo) invece di lasciarlo
// tecnico. Non è una vera traduzione universale — solo i termini elencati
// hanno una resa in italiano, il resto resta in inglese ma leggibile.
const OPTION_VALUE_LABELS = {
  for_old: "Anziano", elderly: "Anziano", old: "Anziano",
  for_kids: "Bambino", for_child: "Bambino", child: "Bambino", kids: "Bambino", baby: "Bambino",
  for_adult: "Adulto", adult: "Adulto",
  for_young: "Giovane", young: "Giovane",
  standard: "Standard", normal: "Standard", default: "Standard",
  general: "Generale",
  custom: "Personalizzato",
  off: "Spento", none: "Spento", disabled: "Spento",
  on: "Attivo", enabled: "Attivo",
  auto: "Automatico",
  low: "Basso", medium: "Medio", high: "Alto",
  follow: "Segue", no_follow: "Non segue",
  quiet: "Silenzioso", silent: "Silenzioso",
  "panel light": "Luce pannello", panel_light: "Luce pannello",
};
function humanizeOptionValue(raw) {
  if (raw === null || raw === undefined) return "";
  const key = String(raw).trim().toLowerCase();
  if (OPTION_VALUE_LABELS[key]) return OPTION_VALUE_LABELS[key];
  // Pulizia meccanica: "for_old_test" -> "For old test"
  const cleaned = key.replace(/[_\-]+/g, " ").trim();
  if (!cleaned) return String(raw);
  return cleaned.charAt(0).toUpperCase() + cleaned.slice(1);
}

function formatValue(def, value) {
  if (value === null || value === undefined || value === "") {
    if (def.type === "bool") return { text: "No", positive: false };
    return { text: "—", positive: null };
  }
  switch (def.type) {
    case "bool":
      return { text: value ? "Sì" : "No", positive: !!value };
    case "timestamp":
      return { text: formatTimestamp(value), positive: null };
    case "number": {
      const n = typeof value === "number" ? value : parseFloat(value);
      return { text: isNaN(n) ? String(value) : `${n}${def.unit ? " " + def.unit : ""}`, positive: null };
    }
    case "array": {
      if (!Array.isArray(value) || value.length === 0) return { text: "—", positive: null };
      return { text: value.map((v) => Math.round(v)).join(", "), positive: null };
    }
    case "notify_event": {
      if (typeof value === "object" && value.messaggio) {
        return { text: `${formatTimestamp(value.timestamp)} — ${value.messaggio}`, positive: null };
      }
      return { text: "—", positive: null };
    }
    case "mode_label": {
      const labels = { simple: "Semplificato", simple_fv: "Semplificato + FV", full: "Completo" };
      return { text: labels[value] || String(value), positive: null };
    }
    default:
      return { text: String(value), positive: null };
  }
}

class TermostatoDiagCard extends HTMLElement {
  setConfig(config) {
    if (!config.entity) {
      throw new Error("Devi specificare un'entità climate");
    }
    if (this._notifyHistoryModalOpen === undefined) {
      this._notifyHistoryModalOpen = false; // sopravvive ai re-render, si azzera solo su riconfigurazione
    }
    if (this._modePickerOpen === undefined) {
      this._modePickerOpen = false;
    }
    if (this._modePickerWasOn === undefined) {
      this._modePickerWasOn = false;
    }
    if (this._timerConfirmOpen === undefined) {
      this._timerConfirmOpen = false;
    }
    if (this._presetPickerOpen === undefined) {
      this._presetPickerOpen = false;
    }
    if (this._swingPickerOpen === undefined) {
      this._swingPickerOpen = false;
    }
    if (this._priorityPopupOpen === undefined) {
      this._priorityPopupOpen = false;
    }
    if (this._seasonPickerOpen === undefined) {
      this._seasonPickerOpen = false;
    }
    if (this._extraFunctionsPopupOpen === undefined) {
      this._extraFunctionsPopupOpen = false;
    }
    this._config = {
      title: "",
      color_by_state: true,
      display_style: "rows", // rows | badges
      show_attributes: [],
      extra_entities: [],
      ...config,
    };
  }

  set hass(hass) {
    this._hass = hass;
    // Home Assistant chiama questo setter ad OGNI cambio di stato in tutta
    // la casa, non solo quando cambia qualcosa di rilevante per questa
    // card — con più istanze sulla stessa dashboard, senza questo
    // controllo si ridisegna l'intero DOM decine di volte al minuto anche
    // quando nulla di davvero utile è cambiato, causando rallentamenti
    // percepibili specialmente su dispositivi meno potenti.
    const stateObj = this._config && hass.states[this._config.entity];
    if (!stateObj) { this._render(); return; }
    const roomSensorEntity = stateObj.attributes.sonda_esterna_entity_id;
    const realClimateEntity = stateObj.attributes.climatizzatore_reale;
    const signature = JSON.stringify([
      stateObj,
      roomSensorEntity ? hass.states[roomSensorEntity] : null,
      realClimateEntity ? hass.states[realClimateEntity] : null,
    ]);
    if (signature === this._lastRenderSignature) return; // nulla di rilevante è cambiato, salta il re-render
    this._lastRenderSignature = signature;
    this._render();
  }

  getCardSize() {
    return 2 + Math.ceil((this._config.show_attributes || []).length / 2);
  }

  _render() {
    if (!this._hass || !this._config) return;
    const stateObj = this._hass.states[this._config.entity];
    if (!stateObj) {
      this.innerHTML = `<ha-card><div style="padding:16px;color:var(--error-color);">Entità non trovata: ${this._config.entity}</div></ha-card>`;
      return;
    }

    // Se il dispositivo reale è in una modalità che questa integrazione
    // Leggiamo il clima reale PRIMA della sezione colori, perché ora la
    // scegliamo in base allo stato REALE del dispositivo (che può essere
    // heat/fan_only/auto anche quando il nostro wrapper riporta "cool" per
    // vincolo tecnico), non solo al nostro stato riportato.
    const realClimateEntity = stateObj.attributes.climatizzatore_reale;
    const realClimateState = realClimateEntity ? this._hass.states[realClimateEntity] : null;

    // Stagione — icona/etichetta per ciascuna delle 5 modalità, usate sia
    // per il pulsante compatto che per lo sfondo grande e il popup.
    const seasonMode = stateObj.attributes.modalita_stagionale || "estate";
    const seasonMeta = {
      estate: { icon: "mdi:white-balance-sunny", label: "Estate" },
      inverno: { icon: "mdi:image-filter-hdr", label: "Inverno" },
      auto: { icon: "mdi:autorenew", label: "Auto" },
      manuale: { icon: "mdi:hand-back-right-outline", label: "Manuale" },
      off: { icon: "mdi:power-off", label: "Off" },
    };
    const currentSeasonMeta = seasonMeta[seasonMode] || seasonMeta.estate;
    const isWinterManaged = seasonMode === "inverno" || (seasonMode === "auto" && realClimateState && realClimateState.state === "heat"); // in inverno (o auto+attualmente in heat) gestiamo heat, non cool/dry
    const realHvacState = realClimateState ? realClimateState.state : stateObj.state;

    const unmanagedMode = !!stateObj.attributes.modalita_esterna_non_gestita;
    const isOff = realHvacState === "off" || realHvacState === "unknown" || realHvacState === "unavailable";
    const modeStyle = isOff ? null : (HVAC_MODE_STYLE[realHvacState] || UNKNOWN_MODE_STYLE);
    const colors = this._config.color_by_state
      ? (isOff ? OFF_COLOR : { bg: modeStyle.cardBg, border: modeStyle.cardBorder, shadow: modeStyle.cardShadow })
      : null;
    const title = this._config.title || stateObj.attributes.friendly_name || this._config.entity;

    // Trasparenza dello sfondo, regolabile dalla configurazione della card
    // (0.1 = quasi trasparente, 1 = colore pieno) — si applica sia allo
    // sfondo colorato per stato che a quello neutro quando il clima è spento.
    const bgOpacity = this._config.background_opacity !== undefined ? this._config.background_opacity : 0.5;
    const cardStyle = colors
      ? `position:relative;background-color:${applyOpacity(colors.bg, bgOpacity)};border:2px solid ${colors.border};box-shadow:0 2px 30px ${colors.shadow};border-radius:20px;padding:12px;`
      : `position:relative;background-color:var(--card-background-color, #fff);border-radius:20px;padding:12px;`;

    const temp = stateObj.attributes.temperature;
    const curTemp = stateObj.attributes.current_temperature;
    const fanMode = stateObj.attributes.fan_mode;
    const fvPriorita = stateObj.attributes.fv_priorita;
    const isSimpleMode = ["semplificato", "semplificato_fv"].includes(stateObj.attributes.modalita_configurazione);
    const isSimpleFvMode = stateObj.attributes.modalita_configurazione === "semplificato_fv";

    // Temperatura "stanza" (sonda esterna, se configurata) e "clima" (sonda
    // interna del climatizzatore reale) mostrate separatamente — utile per
    // capire a colpo d'occhio se le due letture divergono molto, o durante
    // il fallback quando current_temperature mostra la sonda interna.
    const roomSensorEntity = stateObj.attributes.sonda_esterna_entity_id;
    const roomTempState = roomSensorEntity ? this._hass.states[roomSensorEntity] : null;
    const roomTemp = roomTempState && !isNaN(parseFloat(roomTempState.state)) ? parseFloat(roomTempState.state) : null;
    const climaTemp = realClimateState && realClimateState.attributes.current_temperature !== undefined
      ? realClimateState.attributes.current_temperature : null;

    // "ultimo_evento_notifica" e "fv_priorita" restano selezionabili come
    // prima, ma invece di una riga generica ora controllano la visibilità
    // dei rispettivi widget dedicati (storico espandibile, frecce +/-).
    const showAttrs = this._config.show_attributes || [];
    const showNotifyHistoryWidget = showAttrs.includes("ultimo_evento_notifica");
    const showPriorityWidget = showAttrs.includes("fv_priorita");
    const hideInactive = this._config.hide_inactive !== false; // default true

    // Storico notifiche — calcoliamo qui solo i DATI (ultimo messaggio,
    // presenza di storico), non ancora l'HTML del badge: quello va
    // costruito DENTRO il ciclo degli attributi più sotto, per poter
    // partecipare allo stesso sistema di ordinamento/riserva-spazio degli
    // altri badge (porta, finestra, ecc.) invece di essere sempre
    // aggiunta in coda a prescindere da tutto il resto.
    const notifyHistory = Array.isArray(stateObj.attributes.storico_notifiche) ? stateObj.attributes.storico_notifiche : [];
    let notifyHistoryHtml = "";
    let notifyHistoryModalHtml = "";
    const isBadgeStyle = this._config.display_style === "badges";
    const hasNotifyHistory = notifyHistory.length > 0;
    if (hasNotifyHistory && showNotifyHistoryWidget && !isBadgeStyle) {
      // Stile righe: qui la campanella resta una riga a piena larghezza a
      // sé stante (comportamento invariato), non entra nel sistema badge.
      const latest = notifyHistory[0];
      const latestTime = latest.timestamp ? new Date(latest.timestamp).toLocaleTimeString("it-IT", { hour: "2-digit", minute: "2-digit" }) : "";
      notifyHistoryHtml = `
        <div style="border-top:0.5px solid rgba(128,128,128,0.25);padding-top:8px;margin-top:10px;">
          <button data-open-notify-history="1" style="width:100%;display:flex;justify-content:space-between;align-items:center;padding:8px 10px;background:rgba(0,0,0,0.04);border-radius:10px;border:none;text-align:left;cursor:pointer;">
            <span style="font-size:12px;opacity:0.8;">🔔 ultimo evento: ${latestTime} — ${latest.messaggio || ""}</span>
            <ha-icon icon="mdi:open-in-new" style="--mdc-icon-size:14px;opacity:0.6;flex-shrink:0;margin-left:6px;"></ha-icon>
          </button>
        </div>`;
    }
    if (showNotifyHistoryWidget && this._notifyHistoryModalOpen) {
        const allRows = notifyHistory.map((ev) => {
          const t = ev.timestamp ? new Date(ev.timestamp).toLocaleTimeString("it-IT", { hour: "2-digit", minute: "2-digit" }) : "";
          return `<div style="font-size:13px;padding:6px 0;border-bottom:0.5px solid rgba(128,128,128,0.15);">${t} — ${ev.messaggio || ""}</div>`;
        }).join("");
        notifyHistoryModalHtml = `
          <div data-notify-history-backdrop="1" style="position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);z-index:1000;display:flex;align-items:center;justify-content:center;padding:20px;box-sizing:border-box;">
            <div style="background:var(--card-background-color, #fff);border-radius:12px;padding:16px;max-width:360px;width:100%;max-height:70vh;overflow-y:auto;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                <div style="font-size:14px;font-weight:700;">🔔 Storico notifiche</div>
                <button data-close-notify-history="1" style="border:none;background:none;cursor:pointer;padding:4px;">
                  <ha-icon icon="mdi:close" style="--mdc-icon-size:18px;"></ha-icon>
                </button>
              </div>
              ${allRows}
            </div>
          </div>`;
      }

    // Swing — lettura diretta dal climatizzatore reale. Icona barrata
    // quando lo swing è spento/assente, verde quando è attivo qualsiasi
    // valore diverso da quello di "spento". Calcolato qui, prima del
    // blocco badge, perché va inserito nella stessa riga (a destra).
    //
    // IMPORTANTE: non tutti i dispositivi usano "off" per rappresentare
    // "swing spento" — molti Gree/Hisense usano "default" o non hanno
    // affatto un valore di "spento" esplicito. Aggiungere "off"
    // artificialmente alla lista, quando il dispositivo reale non lo
    // supporta, genera un errore se l'utente lo seleziona (il comando
    // verrebbe rifiutato dal dispositivo). Usiamo SOLO i valori
    // realmente supportati, mai valori inventati.
    const swingModesRaw = (realClimateState && Array.isArray(realClimateState.attributes.swing_modes)) ? realClimateState.attributes.swing_modes : [];
    const swingModes = swingModesRaw;
    const swingOffValue = swingModesRaw.includes("off") ? "off" : (swingModesRaw.includes("default") ? "default" : null);
    const currentSwing = (realClimateState && realClimateState.attributes.swing_mode) || swingOffValue || "";
    const swingActive = swingOffValue !== null ? currentSwing !== swingOffValue : swingModesRaw.length > 0;
    const swingLabels = { off: "spento", default: "spento", vertical: "verticale", horizontal: "orizzontale", both: "entrambi", on: "attivo" };
    const swingLabel = (s) => swingLabels[s] || s;

    const priorityIconHtml = (isSimpleFvMode && fvPriorita !== undefined && showPriorityWidget) ? `
      <button data-open-priority-popup="1" aria-label="Priorità FV: ${fvPriorita} — tocca per regolare" title="Priorità ${fvPriorita}"
        style="width:28px;height:28px;border-radius:50%;border:none;background:#378add;color:#fff;display:flex;align-items:center;justify-content:center;cursor:pointer;padding:0;font-size:13px;font-weight:700;flex-shrink:0;">
        ${fvPriorita}
      </button>` : "";

    // "Altre funzioni" — entità extra configurate manualmente nella card
    // stessa (non nell'integrazione), tipicamente switch/select esposti
    // dall'integrazione ufficiale del climatizzatore reale (es. Fresh Air,
    // Quiet, XFan, Panel Light su Gree). Ogni entità è letta dal suo stato
    // reale corrente; il badge segnala se almeno uno switch configurato
    // risulta acceso, per un colpo d'occhio senza aprire il popup.
    const extraEntityIds = Array.isArray(this._config.extra_entities) ? this._config.extra_entities : [];
    const extraEntityStates = extraEntityIds
      .map((id) => this._hass && this._hass.states[id])
      .filter((s) => s !== undefined && s !== null);
    const extraFunctionsAnyOn = extraEntityStates.some((s) => s.entity_id.startsWith("switch.") && s.state === "on");
    const extraFunctionsIconHtml = extraEntityStates.length > 0 ? `
      <button data-open-extra-functions="1" aria-label="Altre funzioni — tocca per aprire" title="Altre funzioni"
        style="width:28px;height:28px;border-radius:50%;border:none;background:${extraFunctionsAnyOn ? "#2e9c4f" : "var(--card-background-color, #fff)"};color:${extraFunctionsAnyOn ? "#fff" : "var(--secondary-text-color)"};border:${extraFunctionsAnyOn ? "none" : "1px solid var(--divider-color, #ccc)"};box-sizing:border-box;display:flex;align-items:center;justify-content:center;cursor:pointer;padding:0;flex-shrink:0;">
        <ha-icon icon="mdi:dots-grid" style="--mdc-icon-size:15px;"></ha-icon>
      </button>` : "";

    const swingIconHtml = swingModesRaw.length > 0 ? `
      <button data-open-swing-picker="1" aria-label="Swing: ${swingLabel(currentSwing)} — tocca per cambiare" title="Swing: ${swingLabel(currentSwing)}"
        style="width:28px;height:28px;border-radius:50%;border:none;background:${swingActive ? "#2e9c4f" : "var(--card-background-color, #fff)"};color:${swingActive ? "#fff" : "var(--secondary-text-color)"};border:${swingActive ? "none" : "1px solid var(--divider-color, #ccc)"};box-sizing:border-box;display:flex;align-items:center;justify-content:center;cursor:pointer;padding:0;flex-shrink:0;">
        <ha-icon icon="${swingActive ? "mdi:arrow-oscillating" : "mdi:arrow-oscillating-off"}" style="--mdc-icon-size:15px;"></ha-icon>
      </button>` : "";

    const prioritySwingIconsHtml = extraFunctionsIconHtml + swingIconHtml + priorityIconHtml;

    let attrsHtml = "";
    if (showAttrs.length > 0) {
      // Tipi che hanno un concetto naturale di "attivo/presente" — se
      // hideInactive è true, li nascondiamo quando sono false/vuoti/null.
      // Numeri e testo semplice non hanno uno stato "inattivo", restano
      // sempre visibili.
      const hasActiveState = (type) => ["bool", "timestamp", "array", "notify_event"].includes(type);

      const visibleKeys = showAttrs.filter((key) => !findAttrDef(key).dedicatedWidget);

      const items = visibleKeys.map((key) => {
        const def = findAttrDef(key);
        const raw = stateObj.attributes[key];
        const val = formatValue(def, raw);
        const colorStyle =
          val.positive === true ? "color:#2e7d32;font-weight:600;" :
          val.positive === false ? "color:var(--secondary-text-color);" : "";

        // "Inattivo" = attributi con hideInactive attivo che risultano
        // false/vuoti in questo momento. Invece di OMETTERE la riga (che
        // farebbe cambiare l'altezza della card — un problema quando più
        // card della stessa integrazione sono affiancate sul dashboard e
        // solo alcune hanno quell'attributo attivo), la manteniamo nel
        // markup ma invisibile: lo spazio resta riservato, l'altezza
        // della card è sempre la stessa indipendentemente da cosa è
        // attivo in ciascuna istanza.
        let isInactive = false;
        if (hideInactive && hasActiveState(def.type)) {
          if (def.type === "bool") isInactive = !raw;
          else if (def.type === "array") isInactive = !(Array.isArray(raw) && raw.length > 0);
          else if (def.type === "notify_event") isInactive = !(raw && raw.messaggio);
          else isInactive = raw === null || raw === undefined || raw === "";
        }
        const visibilityStyle = isInactive ? "visibility:hidden;" : "";

        const linkedEntity = def.linkedEntityAttr ? stateObj.attributes[def.linkedEntityAttr] : null;
        const clickableAttr = linkedEntity ? ` data-more-info-entity="${linkedEntity}"` : "";
        let html;
        if (this._config.display_style === "badges") {
          const bg = val.positive === true ? "rgba(46,125,50,0.15)" : "rgba(120,120,120,0.12)";
          const content = def.type === "bool"
            ? `<span title="${def.label}">${def.icon}</span>`
            : `<span title="${def.label}">${def.icon}</span><span>${val.text}</span>`;
          html = `<span${clickableAttr} style="display:inline-flex;align-items:center;gap:4px;background:${bg};border-radius:12px;padding:4px 10px;margin:3px;font-size:12px;${colorStyle}${visibilityStyle}${linkedEntity ? "cursor:pointer;" : ""}">
            ${content}
          </span>`;
        } else {
          html = `<div${clickableAttr} style="display:flex;justify-content:space-between;padding:3px 0;font-size:13px;border-bottom:1px solid rgba(128,128,128,0.15);${visibilityStyle}${linkedEntity ? "cursor:pointer;" : ""}">
          <span>${def.icon} ${def.label}</span><span style="${colorStyle}">${val.text}</span>
        </div>`;
        }
        return { html, isInactive };
      });

      // Campanella storico notifiche — solo in stile badge, e solo se
      // l'utente l'ha selezionata. Aggiunta come un item NORMALE
      // dell'array (non appesa in coda dopo), così partecipa allo stesso
      // ordinamento degli altri: si compatta in prima fila se c'è
      // storico da mostrare, resta invisibile ma riserva spazio se non
      // c'è ancora nessun evento — esattamente come porta/finestra.
      if (isBadgeStyle && showNotifyHistoryWidget) {
        const latest = notifyHistory[0];
        const latestTime = latest && latest.timestamp ? new Date(latest.timestamp).toLocaleTimeString("it-IT", { hour: "2-digit", minute: "2-digit" }) : "";
        const bellTitle = hasNotifyHistory ? `Ultimo evento: ${latestTime} — ${latest.messaggio || ""}` : "Nessun evento";
        const bellVisibility = hasNotifyHistory ? "" : "visibility:hidden;";
        items.push({
          html: `<span data-open-notify-history="1" title="${bellTitle}"
            style="display:inline-flex;align-items:center;justify-content:center;background:rgba(120,120,120,0.12);border-radius:12px;padding:4px 8px;margin:3px;font-size:12px;cursor:pointer;${bellVisibility}">
            🔔
          </span>`,
          isInactive: !hasNotifyHistory,
        });
      }

      // Nello stile badge, le icone attive si compattano all'inizio (senza
      // "buchi" tra loro) e quelle invisibili — che occupano comunque lo
      // stesso spazio per mantenere l'altezza coerente tra card affiancate
      // — vengono spostate in coda, dopo tutte le attive. .sort() è
      // stabile, quindi l'ordine relativo tra elementi dello stesso tipo
      // (attivo/inattivo) resta quello di configurazione originale.
      const orderedItems = this._config.display_style === "badges"
        ? [...items].sort((a, b) => (a.isInactive === b.isInactive) ? 0 : (a.isInactive ? 1 : -1))
        : items;
      const itemsHtml = orderedItems.map((it) => it.html);
      const badgesContent = itemsHtml.join("");
      const hasPrioritySwing = !!prioritySwingIconsHtml;
      const wrapper = this._config.display_style === "badges"
        ? `<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;margin-top:10px;gap:4px;">
            <div style="display:flex;flex-wrap:wrap;">${badgesContent}</div>
            ${hasPrioritySwing ? `<div style="display:flex;gap:8px;flex-shrink:0;">${prioritySwingIconsHtml}</div>` : ""}
          </div>`
        : `<div style="display:flex;justify-content:space-between;align-items:center;margin-top:10px;">
            <div>${badgesContent}</div>
            ${hasPrioritySwing ? `<div style="display:flex;gap:8px;flex-shrink:0;">${prioritySwingIconsHtml}</div>` : ""}
          </div>`;
      attrsHtml = (items.length > 0 || hasPrioritySwing) ? wrapper : "";
    } else if (prioritySwingIconsHtml) {
      // Nessun attributo badge selezionato, ma priorità/swing sì —
      // mostriamo comunque la riga, solo con questi due allineati a destra.
      attrsHtml = `<div style="display:flex;justify-content:flex-end;gap:8px;margin-top:10px;">${prioritySwingIconsHtml}</div>`;
    }


    // Pulsanti modalità dinamici: costruiti dagli hvac_modes REALI del
    // climatizzatore sottostante (letti da realClimateState), non più
    // limitati ai 3 fissi che il nostro wrapper gestisce automaticamente.
    // Se il dispositivo supporta anche caldo/ventilazione/auto, compaiono
    // qui come pulsanti cliccabili — restano un controllo MANUALE diretto
    // (nessuna logica di temperatura nostra in quelle modalità), da cui il
    // badge di avviso che li accompagna quando sono quelli attivi.
    const realHvacModes = (realClimateState && Array.isArray(realClimateState.attributes.hvac_modes))
      ? realClimateState.attributes.hvac_modes
      : ["cool", "dry"]; // fallback prudente se il clima reale non è ancora disponibile
    const managedModes = isWinterManaged ? ["heat"] : ["cool", "dry"]; // in inverno gestiamo solo heat, il contrario dell'estate
    const modeLabel = (mode) => mode === "cool" ? "Raffreddamento" : mode === "dry" ? "Deumidificatore"
      : mode === "heat" ? "Riscaldamento" : mode === "fan_only" ? "Solo ventilazione"
      : mode === "auto" ? "Auto" : mode === "heat_cool" ? "Caldo/freddo" : mode;

    // Icona modalità: SOLO quella attualmente attiva (non più tutta la
    // fila) — stessa dimensione grande del pulsante accensione, per dargli
    // pari peso visivo. Se spento, non c'è nessuna modalità "attiva" da
    // mostrare qui.
    const isReallyOff = realHvacState === "off";
    let activeModeIconHtml = "";
    if (!isReallyOff) {
      const style = HVAC_MODE_STYLE[realHvacState] || UNKNOWN_MODE_STYLE;
      activeModeIconHtml = `<span title="${modeLabel(realHvacState)}"
        style="width:38px;height:38px;border-radius:50%;background:${style.activeBg};color:${style.activeFg};display:flex;align-items:center;justify-content:center;box-sizing:border-box;flex-shrink:0;">
        <ha-icon icon="${style.icon}" style="--mdc-icon-size:20px;"></ha-icon>
      </span>`;
    }
    const unmanagedBadge = unmanagedMode
      ? `<span title="Modalità attiva, ma non regolata automaticamente da questa integrazione (nessuna logica di temperatura per questo modo)"
          style="width:16px;height:16px;border-radius:50%;background:#f0b400;color:#4a3800;display:flex;align-items:center;justify-content:center;box-sizing:border-box;flex-shrink:0;margin-left:-10px;margin-top:-26px;border:1.5px solid var(--card-background-color, #fff);">
          <ha-icon icon="mdi:alert" style="--mdc-icon-size:9px;"></ha-icon>
        </span>`
      : "";

    // Pulsante stagione — icona compatta, un tocco apre il popup di
    // selezione (5 opzioni). Posizionato subito prima del power, come
    // richiesto.
    const seasonBtn = `<button data-open-season-picker="1" aria-label="Stagione: ${currentSeasonMeta.label} — tocca per cambiare" title="Stagione: ${currentSeasonMeta.label}"
      style="width:38px;height:38px;border-radius:50%;border:none;background:${seasonMode === "off" ? "#d9302e" : "#2e9c4f"};color:#fff;display:flex;align-items:center;justify-content:center;cursor:pointer;padding:0;box-sizing:border-box;flex-shrink:0;">
      <ha-icon icon="${currentSeasonMeta.icon}" style="--mdc-icon-size:20px;"></ha-icon>
    </button>`;

    // Pulsante accensione/spegnimento — ingrandito, stessa dimensione
    // dell'icona modalità. Da acceso spegne direttamente (invariato). Da
    // spento, invece di accendere subito in raffreddamento, apre un popup
    // per scegliere con quale modalità accendere.
    const powerBtn = `<button data-power-toggle="1" aria-label="${isReallyOff ? "Spento — tocca per scegliere una modalità" : "Acceso — tocca per spegnere"}" title="${isReallyOff ? "Spento" : "Acceso"}"
      style="width:38px;height:38px;border-radius:50%;border:none;background:${isReallyOff ? "#d9302e" : "#2e9c4f"};color:#fff;display:flex;align-items:center;justify-content:center;cursor:pointer;padding:0;box-sizing:border-box;flex-shrink:0;">
      <ha-icon icon="mdi:power" style="--mdc-icon-size:20px;"></ha-icon>
    </button>`;

    const modeButtonsHtml = `<div style="display:flex;align-items:center;gap:8px;height:38px;position:relative;">
      ${activeModeIconHtml}
      ${seasonBtn}
      ${powerBtn}
      ${unmanagedBadge}
    </div>`;

    // Popup di selezione modalità — si apre cliccando il power da spento.
    // Stesso stile (backdrop scuro + pannello bianco arrotondato) del
    // popup storico notifiche, per coerenza visiva tra i due popup della
    // card. Le icone qui sono grandi quanto power/modalità in alto.
    // Dati preset letti subito, prima di qualsiasi popup che li usi.
    const presetModesRaw = (realClimateState && Array.isArray(realClimateState.attributes.preset_modes)) ? realClimateState.attributes.preset_modes : [];
    const presetModes = presetModesRaw.includes("none") ? presetModesRaw : ["none", ...presetModesRaw];
    const currentPreset = (realClimateState && realClimateState.attributes.preset_mode) || "none";
    const presetLabels = {
      none: "No", eco: "eco", away: "fuoricasa", boost: "boost",
      sleep: "sonno", comfort: "comfort", home: "casa", activity: "attività",
    };
    const presetLabel = (p) => presetLabels[p] || p;

    let modePickerModalHtml = "";
    if (this._modePickerOpen) {
      const pickerButtons = realHvacModes.filter((m) => m !== "off").map((mode) => {
        const style = HVAC_MODE_STYLE[mode] || UNKNOWN_MODE_STYLE;
        const isManaged = managedModes.includes(mode);
        const targetAttr = isManaged ? "" : ` data-mode-target="real"`;
        return `<button data-mode="${mode}"${targetAttr} aria-label="${modeLabel(mode)}"
          style="display:flex;flex-direction:column;align-items:center;gap:6px;border:none;background:none;cursor:pointer;padding:8px;">
          <span style="width:44px;height:44px;border-radius:50%;background:${style.activeBg};color:${style.activeFg};display:flex;align-items:center;justify-content:center;">
            <ha-icon icon="${style.icon}" style="--mdc-icon-size:22px;"></ha-icon>
          </span>
          <span style="font-size:11px;color:var(--primary-text-color);">${modeLabel(mode)}</span>
        </button>`;
      }).join("");
      // Pulsante spegni — compare SOLO se il popup è stato aperto da
      // acceso (il power era verde). Se era già spento (rosso), il popup
      // serve solo a scegliere con quale modalità accendere — mostrare
      // "Spegni" in quel caso non avrebbe senso, dato che è già spento.
      const offButton = this._modePickerWasOn ? `<button data-mode="off" aria-label="Spegni"
        style="display:flex;flex-direction:column;align-items:center;gap:6px;border:none;background:none;cursor:pointer;padding:8px;">
        <span style="width:44px;height:44px;border-radius:50%;background:#d9302e;color:#fff;display:flex;align-items:center;justify-content:center;">
          <ha-icon icon="mdi:power" style="--mdc-icon-size:22px;"></ha-icon>
        </span>
        <span style="font-size:11px;color:var(--primary-text-color);">Spegni</span>
      </button>` : "";
      modePickerModalHtml = `
        <div data-mode-picker-backdrop="1" style="position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);z-index:1000;display:flex;align-items:center;justify-content:center;padding:20px;box-sizing:border-box;">
          <div style="background:var(--card-background-color, #fff);border-radius:20px;padding:16px;max-width:320px;width:100%;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
              <div style="font-size:14px;font-weight:700;">Scegli modalità</div>
              <button data-close-mode-picker="1" style="border:none;background:none;cursor:pointer;padding:4px;">
                <ha-icon icon="mdi:close" style="--mdc-icon-size:18px;"></ha-icon>
              </button>
            </div>
            <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:4px;">
              ${pickerButtons}
              ${offButton}
            </div>
          </div>
        </div>`;
    }

    // Popup selezione preset — griglia con tutte le modalità che il
    // climatizzatore reale espone (sonno/eco/fuoricasa/boost/...), sempre
    // con "nessuna" tra le opzioni anche se il dispositivo non la elenca
    // esplicitamente.
    let presetPickerModalHtml = "";
    if (this._presetPickerOpen && presetModesRaw.length > 0) {
      const presetIcons = {
        none: "mdi:circle-off-outline", eco: "mdi:leaf", away: "mdi:home-export-outline",
        boost: "mdi:rocket-launch-outline", sleep: "mdi:power-sleep", comfort: "mdi:sofa-outline",
        home: "mdi:home-outline", activity: "mdi:run",
      };
      const presetButtons = presetModes.map((p) => {
        const active = p === currentPreset;
        const bg = active ? "#2e9c4f" : "var(--card-background-color, #fff)";
        const fg = active ? "#fff" : "var(--secondary-text-color)";
        const border = active ? "none" : "1px solid var(--divider-color, #ccc)";
        return `<button data-preset="${p}" aria-label="${presetLabel(p)}"
          style="display:flex;flex-direction:column;align-items:center;gap:6px;border:none;background:none;cursor:pointer;padding:8px;">
          <span style="width:44px;height:44px;border-radius:50%;background:${bg};color:${fg};border:${border};box-sizing:border-box;display:flex;align-items:center;justify-content:center;">
            <ha-icon icon="${presetIcons[p] || "mdi:tune-variant"}" style="--mdc-icon-size:22px;"></ha-icon>
          </span>
          <span style="font-size:11px;color:var(--primary-text-color);">${presetLabel(p)}</span>
        </button>`;
      }).join("");
      presetPickerModalHtml = `
        <div data-preset-picker-backdrop="1" style="position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);z-index:1000;display:flex;align-items:center;justify-content:center;padding:20px;box-sizing:border-box;">
          <div style="background:var(--card-background-color, #fff);border-radius:20px;padding:16px;max-width:320px;width:100%;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
              <div style="font-size:14px;font-weight:700;">Scegli modalità</div>
              <button data-close-preset-picker="1" style="border:none;background:none;cursor:pointer;padding:4px;">
                <ha-icon icon="mdi:close" style="--mdc-icon-size:18px;"></ha-icon>
              </button>
            </div>
            <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:4px;">
              ${presetButtons}
            </div>
          </div>
        </div>`;
    }

    let presetPopupPlaceholder = ""; // solo per leggibilità, non usato

    let swingPickerModalHtml = "";
    if (this._swingPickerOpen && swingModesRaw.length > 0) {
      const swingButtons = swingModes.map((s) => {
        const active = s === currentSwing;
        const bg = active ? "#2e9c4f" : "var(--card-background-color, #fff)";
        const fg = active ? "#fff" : "var(--secondary-text-color)";
        const border = active ? "none" : "1px solid var(--divider-color, #ccc)";
        const icon = s === "off" ? "mdi:arrow-oscillating-off" : "mdi:arrow-oscillating";
        return `<button data-swing="${s}" aria-label="${swingLabel(s)}"
          style="display:flex;flex-direction:column;align-items:center;gap:6px;border:none;background:none;cursor:pointer;padding:8px;">
          <span style="width:44px;height:44px;border-radius:50%;background:${bg};color:${fg};border:${border};box-sizing:border-box;display:flex;align-items:center;justify-content:center;">
            <ha-icon icon="${icon}" style="--mdc-icon-size:22px;"></ha-icon>
          </span>
          <span style="font-size:11px;color:var(--primary-text-color);">${swingLabel(s)}</span>
        </button>`;
      }).join("");
      swingPickerModalHtml = `
        <div data-swing-picker-backdrop="1" style="position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);z-index:1000;display:flex;align-items:center;justify-content:center;padding:20px;box-sizing:border-box;">
          <div style="background:var(--card-background-color, #fff);border-radius:20px;padding:16px;max-width:320px;width:100%;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
              <div style="font-size:14px;font-weight:700;">Scegli swing</div>
              <button data-close-swing-picker="1" style="border:none;background:none;cursor:pointer;padding:4px;">
                <ha-icon icon="mdi:close" style="--mdc-icon-size:18px;"></ha-icon>
              </button>
            </div>
            <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:4px;">
              ${swingButtons}
            </div>
          </div>
        </div>`;
    }

    let extraFunctionsPopupModalHtml = "";
    if (this._extraFunctionsPopupOpen && extraEntityStates.length > 0) {
      const rowsHtml = extraEntityStates.map((s) => {
        const domain = s.entity_id.split(".")[0];
        const rawName = s.attributes.friendly_name || s.entity_id;
        // Il nome dell'entità spesso include per intero il nome del
        // climatizzatore come prefisso (es. "Condizionatore Sala
        // Oscillazione verticale") — lo togliamo per avere etichette
        // corte, altrimenti i pulsanti finiscono uno per riga invece di
        // stare affiancati come nello swing.
        const climateDeviceName = realClimateEntity && this._hass && this._hass.states[realClimateEntity]
          ? this._hass.states[realClimateEntity].attributes.friendly_name
          : null;
        let friendlyName = rawName;
        if (climateDeviceName && rawName.toLowerCase().startsWith(climateDeviceName.toLowerCase())) {
          friendlyName = rawName.slice(climateDeviceName.length).replace(/^[\s\-_:]+/, "");
          if (!friendlyName) friendlyName = rawName; // non lasciare l'etichetta vuota se il nome combacia per intero
        }
        friendlyName = humanizeOptionValue(friendlyName);
        const icon = s.attributes.icon || "mdi:toggle-switch-outline";
        if (domain === "switch") {
          const active = s.state === "on";
          const bg = active ? "#2e9c4f" : "#c0392b";
          return `<button data-extra-switch="${s.entity_id}" aria-label="${friendlyName}"
            style="display:flex;flex-direction:column;align-items:center;gap:6px;border:none;background:none;cursor:pointer;padding:8px;">
            <span style="width:44px;height:44px;border-radius:50%;background:${bg};color:#fff;box-sizing:border-box;display:flex;align-items:center;justify-content:center;">
              <ha-icon icon="${icon}" style="--mdc-icon-size:22px;"></ha-icon>
            </span>
            <span style="font-size:11px;color:var(--primary-text-color);">${friendlyName}</span>
          </button>`;
        }
        if (domain === "select") {
          const options = Array.isArray(s.attributes.options) ? s.attributes.options : [];
          const optionButtons = options.map((opt) => {
            const active = opt === s.state;
            const bg = active ? "#2e9c4f" : "#c0392b";
            return `<button data-extra-select="${s.entity_id}" data-extra-select-option="${opt}" aria-label="${humanizeOptionValue(opt)}"
              style="display:flex;flex-direction:column;align-items:center;gap:6px;border:none;background:none;cursor:pointer;padding:8px;">
              <span style="width:44px;height:44px;border-radius:50%;background:${bg};color:#fff;box-sizing:border-box;display:flex;align-items:center;justify-content:center;">
                <ha-icon icon="mdi:menu" style="--mdc-icon-size:22px;"></ha-icon>
              </span>
              <span style="font-size:11px;color:var(--primary-text-color);">${humanizeOptionValue(opt)}</span>
            </button>`;
          }).join("");
          return `
            <div style="width:100%;">
              <div style="font-size:12px;opacity:0.6;margin-bottom:6px;text-align:center;">${friendlyName}</div>
              <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:4px;">${optionButtons}</div>
            </div>`;
        }
        return "";
      }).join("");

      extraFunctionsPopupModalHtml = `
        <div data-extra-functions-backdrop="1" style="position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);z-index:1000;display:flex;align-items:center;justify-content:center;padding:20px;box-sizing:border-box;">
          <div style="background:var(--card-background-color, #fff);border-radius:20px;padding:16px;max-width:320px;width:100%;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
              <div style="font-size:14px;font-weight:700;">Altre funzioni</div>
              <button data-close-extra-functions="1" style="border:none;background:none;cursor:pointer;padding:4px;">
                <ha-icon icon="mdi:close" style="--mdc-icon-size:18px;"></ha-icon>
              </button>
            </div>
            <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:4px;">
              ${rowsHtml}

            </div>
          </div>
        </div>`;
    }

    let seasonPickerModalHtml = "";
    if (this._seasonPickerOpen) {
      const seasonOrder = ["estate", "inverno", "auto", "manuale", "off"];
      const seasonButtons = seasonOrder.map((s) => {
        const meta = seasonMeta[s];
        const active = s === seasonMode;
        const bg = active ? "#2e9c4f" : "var(--card-background-color, #fff)";
        const fg = active ? "#fff" : "var(--secondary-text-color)";
        const border = active ? "none" : "1px solid var(--divider-color, #ccc)";
        return `<button data-season="${s}" aria-label="${meta.label}"
          style="display:flex;flex-direction:column;align-items:center;gap:6px;border:none;background:none;cursor:pointer;padding:8px;">
          <span style="width:44px;height:44px;border-radius:50%;background:${bg};color:${fg};border:${border};box-sizing:border-box;display:flex;align-items:center;justify-content:center;">
            <ha-icon icon="${meta.icon}" style="--mdc-icon-size:22px;"></ha-icon>
          </span>
          <span style="font-size:11px;color:var(--primary-text-color);">${meta.label}</span>
        </button>`;
      }).join("");
      seasonPickerModalHtml = `
        <div data-season-picker-backdrop="1" style="position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);z-index:1000;display:flex;align-items:center;justify-content:center;padding:20px;box-sizing:border-box;">
          <div style="background:var(--card-background-color, #fff);border-radius:20px;padding:16px;max-width:320px;width:100%;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
              <div style="font-size:14px;font-weight:700;">Scegli stagione</div>
              <button data-close-season-picker="1" style="border:none;background:none;cursor:pointer;padding:4px;">
                <ha-icon icon="mdi:close" style="--mdc-icon-size:18px;"></ha-icon>
              </button>
            </div>
            <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:4px;">
              ${seasonButtons}
            </div>
          </div>
        </div>`;
    }

    // Target con frecce — regola immediatamente (step di 1°), disponibile
    // solo nel modo Semplice/Semplice+FV (dove il target è sempre
    // ricalcolato da configurazione + eventuale regolazione da card).
    const tempDisplay = temp !== undefined ? (Math.round(temp * 10) / 10) + "°" : "—";
    const targetCellHtml = isSimpleMode ? `
      <div style="flex:1;text-align:center;padding:8px 4px;">
        <div style="font-size:10px;opacity:0.6;margin-bottom:2px;">target</div>
        <div style="display:flex;align-items:center;justify-content:center;gap:4px;">
          <button data-target-delta="-0.1" aria-label="Diminuisci target" title="Diminuisci target"
            style="width:16px;height:16px;border-radius:50%;border:1px solid var(--divider-color, #ccc);background:var(--card-background-color, #fff);display:flex;align-items:center;justify-content:center;cursor:pointer;padding:0;box-sizing:border-box;flex-shrink:0;">
            <ha-icon icon="mdi:minus" style="--mdc-icon-size:10px;"></ha-icon>
          </button>
          <div style="font-size:18px;font-weight:700;line-height:1;min-width:40px;">${tempDisplay}</div>
          <button data-target-delta="0.1" aria-label="Aumenta target" title="Aumenta target"
            style="width:16px;height:16px;border-radius:50%;border:1px solid var(--divider-color, #ccc);background:var(--card-background-color, #fff);display:flex;align-items:center;justify-content:center;cursor:pointer;padding:0;box-sizing:border-box;flex-shrink:0;">
            <ha-icon icon="mdi:plus" style="--mdc-icon-size:10px;"></ha-icon>
          </button>
        </div>
      </div>` : `
      <div style="flex:1;text-align:center;padding:8px 4px;">
        <div style="font-size:10px;opacity:0.6;margin-bottom:2px;">target</div>
        <div style="font-size:18px;font-weight:700;line-height:1;">${tempDisplay}</div>
      </div>`;


    // Popup priorità — solo +/- grandi, dato che è un numero continuo (non
    // un set fisso di opzioni come preset/swing).
    let priorityPopupModalHtml = "";
    if (this._priorityPopupOpen && priorityIconHtml) {
      priorityPopupModalHtml = `
        <div data-priority-popup-backdrop="1" style="position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);z-index:1000;display:flex;align-items:center;justify-content:center;padding:20px;box-sizing:border-box;">
          <div style="background:var(--card-background-color, #fff);border-radius:16px;padding:20px;max-width:260px;width:100%;text-align:center;">
            <div style="font-size:14px;font-weight:700;margin-bottom:16px;">Priorità FV</div>
            <div style="display:flex;align-items:center;justify-content:center;gap:16px;">
              <button data-priority-delta="-1" aria-label="Diminuisci priorità" style="width:36px;height:36px;border-radius:50%;border:1px solid var(--divider-color, #ccc);background:var(--card-background-color, #fff);cursor:pointer;padding:0;display:flex;align-items:center;justify-content:center;">
                <ha-icon icon="mdi:minus" style="--mdc-icon-size:16px;"></ha-icon>
              </button>
              <span style="font-size:24px;font-weight:700;min-width:32px;">${fvPriorita}</span>
              <button data-priority-delta="1" aria-label="Aumenta priorità" style="width:36px;height:36px;border-radius:50%;border:1px solid var(--divider-color, #ccc);background:var(--card-background-color, #fff);cursor:pointer;padding:0;display:flex;align-items:center;justify-content:center;">
                <ha-icon icon="mdi:plus" style="--mdc-icon-size:16px;"></ha-icon>
              </button>
            </div>
          </div>
        </div>`;
    }

    // Ventola con frecce esplicite (prima era un click nascosto sull'icona
    // che ciclava le velocità — poco scopribile, sostituito con lo stesso
    // stile di controllo già usato per target e priorità).
    const fanOrder = ["low", "medium", "high"];
    const fanLabels = { low: "bassa", medium: "media", high: "alta" };
    const fanLabel = fanLabels[fanMode] || fanMode || "—";
    const fanControlHtml = fanMode !== undefined ? `
      <div style="flex:1;display:flex;align-items:center;justify-content:center;padding:4px 6px;min-width:0;gap:6px;">
        <span style="font-size:11px;opacity:0.75;display:flex;align-items:center;flex-shrink:0;">
          <ha-icon icon="mdi:fan" style="--mdc-icon-size:14px;"></ha-icon>
        </span>
        <div style="display:flex;align-items:center;gap:3px;">
          <button data-fan-delta="-1" aria-label="Diminuisci ventola" title="Diminuisci ventola"
            style="width:18px;height:18px;border-radius:50%;border:1px solid var(--divider-color, #ccc);background:var(--card-background-color, #fff);display:flex;align-items:center;justify-content:center;cursor:pointer;padding:0;flex-shrink:0;">
            <ha-icon icon="mdi:minus" style="--mdc-icon-size:10px;"></ha-icon>
          </button>
          <span style="font-size:11px;font-weight:700;min-width:26px;text-align:center;flex-shrink:0;">${fanLabel}</span>
          <button data-fan-delta="1" aria-label="Aumenta ventola" title="Aumenta ventola"
            style="width:18px;height:18px;border-radius:50%;border:1px solid var(--divider-color, #ccc);background:var(--card-background-color, #fff);display:flex;align-items:center;justify-content:center;cursor:pointer;padding:0;flex-shrink:0;">
            <ha-icon icon="mdi:plus" style="--mdc-icon-size:10px;"></ha-icon>
          </button>
        </div>
      </div>` : "";

    // Ventola, priorità e minuti del timer condividono la stessa riga,
    // divisa in 3 colonne — quelle assenti vengono semplicemente omesse,
    // le altre si dividono lo spazio rimanente.
    const timerMinutesConfigured = stateObj.attributes.timer_manuale_minuti_configurati;
    const timerEnabled = !!stateObj.attributes.timer_manuale_attivo;
    const timerMinutesControlHtml = (timerMinutesConfigured && timerMinutesConfigured > 0) ? `
      <div style="flex:1;display:flex;align-items:center;justify-content:center;padding:4px 6px;min-width:0;gap:6px;">
        <button data-open-timer-confirm="1" aria-label="${timerEnabled ? "Timer acceso — tocca per disattivare" : "Timer spento — tocca per attivare"}" title="${timerEnabled ? "Timer acceso" : "Timer spento"}"
          style="width:20px;height:20px;border-radius:50%;border:none;background:${timerEnabled ? "#2e9c4f" : "#d9302e"};color:#fff;display:flex;align-items:center;justify-content:center;cursor:pointer;padding:0;flex-shrink:0;">
          <ha-icon icon="mdi:clock-outline" style="--mdc-icon-size:12px;"></ha-icon>
        </button>
        <div style="display:flex;align-items:center;gap:2px;">
          <button data-timer-minutes-delta="-5" aria-label="Diminuisci minuti" title="Diminuisci minuti"
            style="width:18px;height:18px;border-radius:50%;border:1px solid var(--divider-color, #ccc);background:var(--card-background-color, #fff);display:flex;align-items:center;justify-content:center;cursor:pointer;padding:0;flex-shrink:0;">
            <ha-icon icon="mdi:minus" style="--mdc-icon-size:10px;"></ha-icon>
          </button>
          <span title="Minuti" style="font-size:11px;font-weight:700;min-width:20px;text-align:center;flex-shrink:0;">${Math.round(timerMinutesConfigured)}</span>
          <button data-timer-minutes-delta="5" aria-label="Aumenta minuti" title="Aumenta minuti"
            style="width:18px;height:18px;border-radius:50%;border:1px solid var(--divider-color, #ccc);background:var(--card-background-color, #fff);display:flex;align-items:center;justify-content:center;cursor:pointer;padding:0;flex-shrink:0;">
            <ha-icon icon="mdi:plus" style="--mdc-icon-size:10px;"></ha-icon>
          </button>
        </div>
      </div>` : "";

    // Le 3 celle diventano un'unica scatola bordata con divisori interni
    // (stesso stile della riga stanza/clima/target sopra) invece di 3
    // scatole separate — più compatta, e visivamente coerente col resto
    // della card. Solo le celle effettivamente presenti vengono unite, e
    // il bordo destro si applica a tutte tranne l'ultima.
    // Modalità preset (sonno/eco/fuoricasa/boost/nessuna...) — sostituisce
    // la priorità in questa riga. Le frecce non ciclano direttamente (i
    // preset possono essere numerosi) — aprono lo stesso popup a griglia
    // già usato per lo swing/le modalità hvac. Compare solo se il
    // climatizzatore reale espone davvero dei preset (es. lo scaldotto
    // non li espone, quindi qui non compare nulla).
    const presetControlHtml = presetModesRaw.length > 0 ? `
      <div style="flex:1;display:flex;align-items:center;justify-content:center;padding:4px 6px;min-width:0;gap:6px;">
        <ha-icon icon="mdi:tune-variant" style="--mdc-icon-size:14px;color:var(--secondary-text-color);flex-shrink:0;"></ha-icon>
        <div style="display:flex;align-items:center;gap:3px;">
          <button data-open-preset-picker="1" aria-label="Cambia modalità preset" title="Diminuisci/scegli modalità"
            style="width:18px;height:18px;border-radius:50%;border:1px solid var(--divider-color, #ccc);background:var(--card-background-color, #fff);display:flex;align-items:center;justify-content:center;cursor:pointer;padding:0;flex-shrink:0;">
            <ha-icon icon="mdi:minus" style="--mdc-icon-size:10px;"></ha-icon>
          </button>
          <span data-open-preset-picker="1" style="font-size:11px;font-weight:700;min-width:36px;text-align:center;flex-shrink:0;cursor:pointer;">${presetLabel(currentPreset)}</span>
          <button data-open-preset-picker="1" aria-label="Cambia modalità preset" title="Aumenta/scegli modalità"
            style="width:18px;height:18px;border-radius:50%;border:1px solid var(--divider-color, #ccc);background:var(--card-background-color, #fff);display:flex;align-items:center;justify-content:center;cursor:pointer;padding:0;flex-shrink:0;">
            <ha-icon icon="mdi:plus" style="--mdc-icon-size:10px;"></ha-icon>
          </button>
        </div>
      </div>` : "";

    const fanPriorityCells = [fanControlHtml, presetControlHtml, timerMinutesControlHtml].filter(Boolean);
    const dividerBorderColor = colors ? colors.border : "#000";
    const fanPriorityRowHtml = fanPriorityCells.length > 0
      ? `<div style="display:flex;border:2px solid ${dividerBorderColor};border-radius:10px;overflow:hidden;margin-top:12px;">
          ${fanPriorityCells.map((cell, i) => i < fanPriorityCells.length - 1
            ? cell.replace('min-width:0;', `min-width:0;border-right:2px solid ${dividerBorderColor};`)
            : cell
          ).join("")}
        </div>`
      : "";

    // Popup di conferma per il timer — messaggio diverso a seconda che tu
    // stia per attivarlo o disattivarlo, così è sempre chiaro cosa sta per
    // succedere prima di confermare.
    let timerConfirmModalHtml = "";
    if (this._timerConfirmOpen && timerMinutesConfigured) {
      const question = timerEnabled
        ? "Il timer verrà disattivato: il clima non si spegnerà più automaticamente dopo un'accensione manuale. Continuare?"
        : `Il clima si spegnerà sempre ${Math.round(timerMinutesConfigured)} minuti dopo un'accensione manuale. Attivare?`;
      timerConfirmModalHtml = `
        <div data-timer-confirm-backdrop="1" style="position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);z-index:1000;display:flex;align-items:center;justify-content:center;padding:20px;box-sizing:border-box;">
          <div style="background:var(--card-background-color, #fff);border-radius:16px;padding:20px;max-width:300px;width:100%;text-align:center;">
            <ha-icon icon="mdi:clock-outline" style="--mdc-icon-size:28px;color:var(--secondary-text-color);margin-bottom:8px;"></ha-icon>
            <div style="font-size:14px;margin-bottom:16px;">${question}</div>
            <div style="display:flex;gap:8px;">
              <button data-timer-confirm-no="1" style="flex:1;padding:8px;border-radius:10px;border:1px solid var(--divider-color, #ccc);background:var(--card-background-color, #fff);cursor:pointer;">No</button>
              <button data-timer-confirm-yes="1" style="flex:1;padding:8px;border-radius:10px;border:none;background:#2e9c4f;color:#fff;cursor:pointer;">Sì</button>
            </div>
          </div>
        </div>`;
    }

    const masterTimerRowHtml = "";

    this.innerHTML = `
      <ha-card style="overflow:hidden;background:transparent;--ha-card-background:transparent;border-radius:20px;">
        <div style="${cardStyle}">
          <ha-icon icon="${currentSeasonMeta.icon}" style="--mdc-icon-size:min(70%, 220px);position:absolute;top:50%;left:55%;transform:translate(-50%, -50%);opacity:0.3;pointer-events:none;z-index:0;color:${colors ? colors.border : "var(--secondary-text-color)"};"></ha-icon>
          <div style="position:relative;z-index:1;">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <div style="font-size:16px;font-weight:700;letter-spacing:0.5px;">${title}</div>
            ${modeButtonsHtml}
          </div>
          <div style="margin-top:14px;">
            <div style="display:flex;border:2px solid ${colors ? colors.border : "#000"};border-radius:10px;overflow:hidden;">
              ${roomSensorEntity ? `
              <div data-more-info-entity="${roomSensorEntity}" style="flex:1;text-align:center;padding:8px 4px;border-right:2px solid ${colors ? colors.border : "#000"};cursor:pointer;">
                <div style="font-size:10px;opacity:0.6;margin-bottom:2px;">stanza</div>
                <div style="font-size:18px;font-weight:700;line-height:1;">${roomTemp !== null ? (Math.round(roomTemp * 10) / 10) + "°" : "—"}</div>
              </div>` : ""}
              <div style="flex:1;text-align:center;padding:8px 4px;border-right:2px solid ${colors ? colors.border : "#000"};">
                <div style="font-size:10px;opacity:0.6;margin-bottom:2px;">clima</div>
                <div style="font-size:18px;font-weight:700;line-height:1;">${climaTemp !== null ? (Math.round(climaTemp * 10) / 10) + "°" : "—"}</div>
              </div>
              ${targetCellHtml}
            </div>
          </div>
          ${fanPriorityRowHtml}
          ${masterTimerRowHtml}
          ${attrsHtml}
          ${notifyHistoryHtml}
          </div>
        </div>
      </ha-card>
      ${notifyHistoryModalHtml}
      ${modePickerModalHtml}
      ${timerConfirmModalHtml}
      ${presetPickerModalHtml}
      ${swingPickerModalHtml}
      ${priorityPopupModalHtml}
      ${seasonPickerModalHtml}
      ${extraFunctionsPopupModalHtml}
    `;

    this._attachControlListeners(stateObj);
  }

  _callService(domain, service, data) {
    if (this._hass && this._hass.callService) {
      this._hass.callService(domain, service, data);
    }
  }

  _attachControlListeners(stateObj) {
    const entityId = this._config.entity;
    const realClimateEntity = stateObj.attributes.climatizzatore_reale;
    const realClimateStateObj = realClimateEntity ? this._hass.states[realClimateEntity] : null;
    const realHvacState = realClimateStateObj ? realClimateStateObj.state : stateObj.state;
    const fanOrder = ["low", "medium", "high"];
    const fanMode = stateObj.attributes.fan_mode;

    this.querySelectorAll("[data-mode]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const mode = btn.getAttribute("data-mode");
        // I modi extra (heat/fan_only/auto/...) non sono tra quelli che il
        // nostro wrapper dichiara di supportare — mandiamo il comando
        // direttamente al climatizzatore reale sottostante, altrimenti
        // Home Assistant rifiuterebbe la richiesta come hvac_mode non
        // valido per l'entità target.
        const target = btn.getAttribute("data-mode-target") === "real" && realClimateEntity ? realClimateEntity : entityId;
        this._callService("climate", "set_hvac_mode", { entity_id: target, hvac_mode: mode });
        if (this._modePickerOpen) {
          this._modePickerOpen = false;
          this._render();
        }
      });
    });

    const powerToggleBtn = this.querySelector("[data-power-toggle]");
    if (powerToggleBtn) {
      powerToggleBtn.addEventListener("click", () => {
        // Apriamo sempre il popup di selezione modalità, sia da acceso
        // che da spento — così chi vuole solo cambiare modalità (senza
        // passare per uno spegnimento) può farlo con un tocco. Lo
        // spegnimento diretto resta disponibile dentro il popup stesso,
        // ma solo se il dispositivo era davvero acceso all'apertura —
        // se era già spento, mostrare "Spegni" non avrebbe senso.
        this._modePickerWasOn = realHvacState !== "off";
        this._modePickerOpen = true;
        this._render();
      });
    }

    const closeModePickerBtn = this.querySelector("[data-close-mode-picker]");
    if (closeModePickerBtn) {
      closeModePickerBtn.addEventListener("click", () => {
        this._modePickerOpen = false;
        this._render();
      });
    }
    const modePickerBackdrop = this.querySelector("[data-mode-picker-backdrop]");
    if (modePickerBackdrop) {
      modePickerBackdrop.addEventListener("click", (e) => {
        if (e.target === modePickerBackdrop) {
          this._modePickerOpen = false;
          this._render();
        }
      });
    }

    this.querySelectorAll("[data-open-preset-picker]").forEach((btn) => {
      btn.addEventListener("click", () => {
        this._presetPickerOpen = true;
        this._render();
      });
    });
    const closePresetPickerBtn = this.querySelector("[data-close-preset-picker]");
    if (closePresetPickerBtn) {
      closePresetPickerBtn.addEventListener("click", () => {
        this._presetPickerOpen = false;
        this._render();
      });
    }
    const presetPickerBackdrop = this.querySelector("[data-preset-picker-backdrop]");
    if (presetPickerBackdrop) {
      presetPickerBackdrop.addEventListener("click", (e) => {
        if (e.target === presetPickerBackdrop) {
          this._presetPickerOpen = false;
          this._render();
        }
      });
    }
    this.querySelectorAll("[data-preset]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const preset = btn.getAttribute("data-preset");
        if (realClimateEntity) {
          this._callService("climate", "set_preset_mode", { entity_id: realClimateEntity, preset_mode: preset });
        }
        this._presetPickerOpen = false;
        this._render();
      });
    });

    const openSwingPickerBtn = this.querySelector("[data-open-swing-picker]");
    if (openSwingPickerBtn) {
      openSwingPickerBtn.addEventListener("click", () => {
        this._swingPickerOpen = true;
        this._render();
      });
    }
    const closeSwingPickerBtn = this.querySelector("[data-close-swing-picker]");
    if (closeSwingPickerBtn) {
      closeSwingPickerBtn.addEventListener("click", () => {
        this._swingPickerOpen = false;
        this._render();
      });
    }
    const swingPickerBackdrop = this.querySelector("[data-swing-picker-backdrop]");
    if (swingPickerBackdrop) {
      swingPickerBackdrop.addEventListener("click", (e) => {
        if (e.target === swingPickerBackdrop) {
          this._swingPickerOpen = false;
          this._render();
        }
      });
    }
    this.querySelectorAll("[data-swing]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const swing = btn.getAttribute("data-swing");
        if (realClimateEntity) {
          this._callService("climate", "set_swing_mode", { entity_id: realClimateEntity, swing_mode: swing });
        }
        this._swingPickerOpen = false;
        this._render();
      });
    });

    const openExtraFunctionsBtn = this.querySelector("[data-open-extra-functions]");
    if (openExtraFunctionsBtn) {
      openExtraFunctionsBtn.addEventListener("click", () => {
        this._extraFunctionsPopupOpen = true;
        this._render();
      });
    }
    const closeExtraFunctionsBtn = this.querySelector("[data-close-extra-functions]");
    if (closeExtraFunctionsBtn) {
      closeExtraFunctionsBtn.addEventListener("click", () => {
        this._extraFunctionsPopupOpen = false;
        this._render();
      });
    }
    const extraFunctionsBackdrop = this.querySelector("[data-extra-functions-backdrop]");
    if (extraFunctionsBackdrop) {
      extraFunctionsBackdrop.addEventListener("click", (e) => {
        if (e.target === extraFunctionsBackdrop) {
          this._extraFunctionsPopupOpen = false;
          this._render();
        }
      });
    }
    this.querySelectorAll("[data-extra-switch]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const entityId = btn.getAttribute("data-extra-switch");
        this._callService("switch", "toggle", { entity_id: entityId });
      });
    });
    this.querySelectorAll("[data-extra-select]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const entityId = btn.getAttribute("data-extra-select");
        const option = btn.getAttribute("data-extra-select-option");
        this._callService("select", "select_option", { entity_id: entityId, option: option });
      });
    });

    const openPriorityPopupBtn = this.querySelector("[data-open-priority-popup]");
    if (openPriorityPopupBtn) {
      openPriorityPopupBtn.addEventListener("click", () => {
        this._priorityPopupOpen = true;
        this._render();
      });
    }
    const priorityPopupBackdrop = this.querySelector("[data-priority-popup-backdrop]");
    if (priorityPopupBackdrop) {
      priorityPopupBackdrop.addEventListener("click", (e) => {
        if (e.target === priorityPopupBackdrop) {
          this._priorityPopupOpen = false;
          this._render();
        }
      });
    }

    const openSeasonPickerBtn = this.querySelector("[data-open-season-picker]");
    if (openSeasonPickerBtn) {
      openSeasonPickerBtn.addEventListener("click", () => {
        this._seasonPickerOpen = true;
        this._render();
      });
    }
    const closeSeasonPickerBtn = this.querySelector("[data-close-season-picker]");
    if (closeSeasonPickerBtn) {
      closeSeasonPickerBtn.addEventListener("click", () => {
        this._seasonPickerOpen = false;
        this._render();
      });
    }
    const seasonPickerBackdrop = this.querySelector("[data-season-picker-backdrop]");
    if (seasonPickerBackdrop) {
      seasonPickerBackdrop.addEventListener("click", (e) => {
        if (e.target === seasonPickerBackdrop) {
          this._seasonPickerOpen = false;
          this._render();
        }
      });
    }
    this.querySelectorAll("[data-season]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const season = btn.getAttribute("data-season");
        this._callService("termostato_intelligente", "set_season_mode", { entity_id: entityId, season });
        this._seasonPickerOpen = false;
        this._render();
      });
    });

    const openTimerConfirmBtn = this.querySelector("[data-open-timer-confirm]");
    if (openTimerConfirmBtn) {
      openTimerConfirmBtn.addEventListener("click", () => {
        this._timerConfirmOpen = true;
        this._render();
      });
    }
    const timerConfirmYesBtn = this.querySelector("[data-timer-confirm-yes]");
    if (timerConfirmYesBtn) {
      timerConfirmYesBtn.addEventListener("click", () => {
        const currentlyEnabled = !!stateObj.attributes.timer_manuale_attivo;
        this._callService("termostato_intelligente", "toggle_manual_shutoff_timer", { entity_id: entityId, enabled: !currentlyEnabled });
        this._timerConfirmOpen = false;
        this._render();
      });
    }
    const timerConfirmNoBtn = this.querySelector("[data-timer-confirm-no]");
    if (timerConfirmNoBtn) {
      timerConfirmNoBtn.addEventListener("click", () => {
        this._timerConfirmOpen = false;
        this._render();
      });
    }
    const timerConfirmBackdrop = this.querySelector("[data-timer-confirm-backdrop]");
    if (timerConfirmBackdrop) {
      timerConfirmBackdrop.addEventListener("click", (e) => {
        if (e.target === timerConfirmBackdrop) {
          this._timerConfirmOpen = false;
          this._render();
        }
      });
    }
    this.querySelectorAll("[data-timer-minutes-delta]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const delta = parseFloat(btn.getAttribute("data-timer-minutes-delta"));
        this._callService("termostato_intelligente", "adjust_manual_shutoff_timer_minutes", { entity_id: entityId, delta });
      });
    });

    this.querySelectorAll("[data-target-delta]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const delta = parseFloat(btn.getAttribute("data-target-delta"));
        this._callService("termostato_intelligente", "adjust_target", { entity_id: entityId, delta });
      });
    });

    this.querySelectorAll("[data-priority-delta]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const delta = parseFloat(btn.getAttribute("data-priority-delta"));
        this._callService("termostato_intelligente", "adjust_priority", { entity_id: entityId, delta });
      });
    });

    this.querySelectorAll("[data-fan-delta]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const delta = parseInt(btn.getAttribute("data-fan-delta"), 10);
        const currentIdx = fanOrder.indexOf(fanMode);
        // Se il valore attuale non è tra i 3 noti (es. "auto"), partiamo
        // da "bassa" invece di un indice negativo che sballerebbe il calcolo.
        const baseIdx = currentIdx === -1 ? 0 : currentIdx;
        const nextIdx = (baseIdx + delta + fanOrder.length) % fanOrder.length;
        this._callService("climate", "set_fan_mode", { entity_id: entityId, fan_mode: fanOrder[nextIdx] });
      });
    });

    // Righe/badge con un'entità collegata (porta, finestra) — al click
    // apriamo il dialog informazioni nativo di Home Assistant su quella
    // entità specifica, usando l'evento standard che tutte le card native
    // e custom usano per questo scopo.
    this.querySelectorAll("[data-more-info-entity]").forEach((el) => {
      el.addEventListener("click", () => {
        const targetEntityId = el.getAttribute("data-more-info-entity");
        this.dispatchEvent(new CustomEvent("hass-more-info", {
          detail: { entityId: targetEntityId },
          bubbles: true,
          composed: true,
        }));
      });
    });

    const notifyOpenBtn = this.querySelector("[data-open-notify-history]");
    if (notifyOpenBtn) {
      notifyOpenBtn.addEventListener("click", () => {
        this._notifyHistoryModalOpen = true;
        this._render();
      });
    }
    const notifyCloseBtn = this.querySelector("[data-close-notify-history]");
    if (notifyCloseBtn) {
      notifyCloseBtn.addEventListener("click", () => {
        this._notifyHistoryModalOpen = false;
        this._render();
      });
    }
    const notifyBackdrop = this.querySelector("[data-notify-history-backdrop]");
    if (notifyBackdrop) {
      // Chiude solo se si clicca esattamente sullo sfondo scuro, non sul
      // pannello interno (altrimenti qualsiasi tocco dentro il popup lo chiuderebbe).
      notifyBackdrop.addEventListener("click", (e) => {
        if (e.target === notifyBackdrop) {
          this._notifyHistoryModalOpen = false;
          this._render();
        }
      });
    }
  }

  static getConfigElement() {
    return document.createElement("termostato-diag-card-editor");
  }

  static getStubConfig(hass) {
    const climateEntities = Object.keys(hass.states).filter(
      (e) => e.startsWith("climate.") && hass.states[e].attributes.modalita_configurazione !== undefined
    );
    return {
      entity: climateEntities[0] || "",
      title: "",
      color_by_state: true,
      display_style: "rows",
      hide_inactive: true,
      show_attributes: ["modalita_notturna_attiva", "blocco_riaccensione_attivo", "finestra_aperta", "porta_aperta"],
    };
  }
}

// ============================================================================
// Editor grafico
// ============================================================================

class TermostatoDiagCardEditor extends HTMLElement {
  setConfig(config) {
    const firstTime = !this._config;
    this._config = { title: "", color_by_state: true, display_style: "rows", show_attributes: [], extra_entities: [], ...config };
    // Ridisegniamo solo al primissimo caricamento. Le chiamate successive a
    // setConfig arrivano dall'host di Home Assistant come "conferma" dopo
    // ogni nostro _emitConfig — se ridisegnassimo sempre, un campo di testo
    // come il titolo perderebbe il focus ad ogni singola lettera digitata
    // (l'intero DOM viene ricostruito da innerHTML). I controlli che
    // richiedono davvero un redraw (es. cambio entità, che cambia gli
    // attributi disponibili nei checkbox) lo chiamano già esplicitamente
    // nel proprio handler, subito sotto.
    if (firstTime) this._render();
  }

  set hass(hass) {
    const firstTime = !this._hass;
    this._hass = hass;
    // Ridisegna solo al primo arrivo di hass. Gli aggiornamenti successivi
    // (che in HA arrivano molte volte al secondo per ogni cambio di stato
    // in tutta la casa) NON devono ridisegnare l'editor, altrimenti ogni
    // tendina aperta si chiude e lo scroll si resetta a metà interazione.
    // I cambi espliciti (entità, checkbox, ecc.) chiamano già _render()
    // da soli nei rispettivi handler più sotto.
    if (firstTime) this._render();
  }

  _emitConfig() {
    this.dispatchEvent(new CustomEvent("config-changed", { detail: { config: this._config }, bubbles: true, composed: true }));
  }

  _render() {
    if (!this._hass) return;
    if (!this._config) return;

    const climateEntities = Object.keys(this._hass.states).filter(
      (e) => e.startsWith("climate.") && this._hass.states[e].attributes.modalita_configurazione !== undefined
    );
    const currentEntity = this._config.entity || "";

    // Attributi realmente presenti sull'entità selezionata (se ne esistono di
    // non elencati in KNOWN_ATTRIBUTES li mostriamo comunque, con etichetta grezza)
    let availableAttrs = KNOWN_ATTRIBUTES.map((a) => a.key);
    if (currentEntity && this._hass.states[currentEntity]) {
      const realAttrs = Object.keys(this._hass.states[currentEntity].attributes).filter(
        (k) => !["friendly_name", "hvac_modes", "min_temp", "max_temp", "fan_modes", "temperature", "current_temperature", "fan_mode", "supported_features", "hvac_action"].includes(k)
      );
      availableAttrs = Array.from(new Set([...availableAttrs.filter((k) => realAttrs.includes(k)), ...realAttrs]));
    }

    const entityOptions = climateEntities
      .map((e) => `<option value="${e}" ${e === currentEntity ? "selected" : ""}>${this._hass.states[e]?.attributes.friendly_name || e}</option>`)
      .join("");

    const checkboxes = availableAttrs
      .map((key) => {
        const def = findAttrDef(key);
        const checked = (this._config.show_attributes || []).includes(key);
        return `
          <label style="display:flex;align-items:center;gap:8px;padding:4px 0;font-size:14px;cursor:pointer;">
            <input type="checkbox" data-attr-key="${key}" ${checked ? "checked" : ""} />
            <span>${def.icon} ${def.label}</span>
          </label>`;
      })
      .join("");

    // Entità "extra" (switch/select) disponibili per la selezione — solo
    // quelle che appartengono allo STESSO dispositivo del climatizzatore
    // reale collegato a questa stanza, altrimenti con un filtro solo sul
    // dominio "switch" ne uscirebbero moltissime (luci, prese, altre
    // stanze...). Richiede il registro entità (this._hass.entities), non
    // sempre presente su versioni molto vecchie di Home Assistant — in
    // quel caso la sezione resta vuota invece di rompersi.
    const realClimateEntityId = currentEntity && this._hass.states[currentEntity]
      ? this._hass.states[currentEntity].attributes.climatizzatore_reale
      : null;
    const realDeviceId = (realClimateEntityId && this._hass.entities && this._hass.entities[realClimateEntityId])
      ? this._hass.entities[realClimateEntityId].device_id
      : null;
    const extraCandidateIds = realDeviceId && this._hass.entities
      ? Object.keys(this._hass.entities).filter((eid) => {
          const domain = eid.split(".")[0];
          if (domain !== "switch" && domain !== "select") return false;
          return this._hass.entities[eid].device_id === realDeviceId;
        })
      : [];
    const climateDeviceNameForEditor = realClimateEntityId && this._hass.states[realClimateEntityId]
      ? this._hass.states[realClimateEntityId].attributes.friendly_name
      : null;
    const extraEntityCheckboxes = extraCandidateIds
      .map((eid) => {
        const checked = (this._config.extra_entities || []).includes(eid);
        const rawLabel = (this._hass.states[eid] && this._hass.states[eid].attributes.friendly_name) || eid;
        let label = rawLabel;
        if (climateDeviceNameForEditor && rawLabel.toLowerCase().startsWith(climateDeviceNameForEditor.toLowerCase())) {
          label = rawLabel.slice(climateDeviceNameForEditor.length).replace(/^[\s\-_:]+/, "") || rawLabel;
        }
        return `
          <label style="display:flex;align-items:center;gap:8px;padding:4px 0;font-size:14px;cursor:pointer;">
            <input type="checkbox" data-extra-entity-key="${eid}" ${checked ? "checked" : ""} />
            <span>${label}</span>
          </label>`;
      })
      .join("");

    this.innerHTML = `
      <div style="padding:8px 0;">
        <div style="margin-bottom:14px;">
          <label style="display:block;font-size:13px;margin-bottom:4px;color:var(--secondary-text-color);">Entità climatizzatore</label>
          <select id="entity-select" style="width:100%;padding:8px;border-radius:6px;border:1px solid var(--divider-color,#ccc);background:var(--card-background-color,#fff);color:var(--primary-text-color);">
            <option value="">-- seleziona --</option>
            ${entityOptions}
          </select>
        </div>

        <div style="margin-bottom:14px;">
          <label style="display:block;font-size:13px;margin-bottom:4px;color:var(--secondary-text-color);">Titolo card (vuoto = usa nome entità)</label>
          <input id="title-input" type="text" value="${this._config.title || ""}" placeholder="es. SALA"
            style="width:100%;padding:8px;border-radius:6px;border:1px solid var(--divider-color,#ccc);background:var(--card-background-color,#fff);color:var(--primary-text-color);box-sizing:border-box;" />
        </div>

        <div style="margin-bottom:14px;">
          <label style="display:flex;align-items:center;gap:8px;font-size:14px;cursor:pointer;">
            <input id="color-toggle" type="checkbox" ${this._config.color_by_state ? "checked" : ""} />
            <span>Sfondo colorato in base allo stato (cool/dry/spento...)</span>
          </label>
        </div>

        <div style="margin-bottom:14px;">
          <label style="display:block;font-size:13px;margin-bottom:4px;color:var(--secondary-text-color);">
            Trasparenza sfondo (<span id="opacity-value">${Math.round((this._config.background_opacity !== undefined ? this._config.background_opacity : 0.5) * 100)}%</span>)
          </label>
          <input id="opacity-slider" type="range" min="0.1" max="1" step="0.05"
            value="${this._config.background_opacity !== undefined ? this._config.background_opacity : 0.5}"
            style="width:100%;" />
        </div>

        <div style="margin-bottom:14px;">
          <label style="display:block;font-size:13px;margin-bottom:6px;color:var(--secondary-text-color);">Stile visualizzazione attributi</label>
          <div style="display:flex;gap:16px;">
            <label style="display:flex;align-items:center;gap:6px;font-size:14px;cursor:pointer;">
              <input type="radio" name="display-style" value="rows" ${this._config.display_style !== "badges" ? "checked" : ""} />
              <span>Righe</span>
            </label>
            <label style="display:flex;align-items:center;gap:6px;font-size:14px;cursor:pointer;">
              <input type="radio" name="display-style" value="badges" ${this._config.display_style === "badges" ? "checked" : ""} />
              <span>Badge</span>
            </label>
          </div>
        </div>

        <div style="margin-bottom:14px;">
          <label style="display:flex;align-items:center;gap:8px;font-size:14px;cursor:pointer;">
            <input id="hide-inactive-toggle" type="checkbox" ${this._config.hide_inactive !== false ? "checked" : ""} />
            <span>Mostra solo attributi attivi/presenti (nascondi finestra chiusa, notte non attiva, DRY non in corso, ecc.)</span>
          </label>
        </div>

        <div style="margin-bottom:14px;">
          <label style="display:block;font-size:13px;margin-bottom:6px;color:var(--secondary-text-color);">"Altre funzioni" — interruttori/select extra del climatizzatore reale (es. Fresh Air, Quiet, XFan)</label>
          <div style="max-height:200px;overflow-y:auto;border:1px solid var(--divider-color,#ddd);border-radius:8px;padding:8px 12px;">
            ${extraEntityCheckboxes || '<div style="font-size:13px;opacity:0.7;">Nessuna entità switch/select trovata su questo dispositivo</div>'}
          </div>
        </div>

        <div>
          <label style="display:block;font-size:13px;margin-bottom:6px;color:var(--secondary-text-color);">Attributi da mostrare nella card</label>
          <div style="max-height:320px;overflow-y:auto;border:1px solid var(--divider-color,#ddd);border-radius:8px;padding:8px 12px;">
            ${checkboxes || '<div style="font-size:13px;opacity:0.7;">Seleziona prima un\'entità</div>'}
          </div>
        </div>
      </div>
    `;

    this.querySelector("#entity-select")?.addEventListener("change", (e) => {
      this._config = { ...this._config, entity: e.target.value };
      this._emitConfig();
      this._render();
    });

    this.querySelector("#title-input")?.addEventListener("input", (e) => {
      this._config = { ...this._config, title: e.target.value };
      this._emitConfig();
    });

    this.querySelector("#color-toggle")?.addEventListener("change", (e) => {
      this._config = { ...this._config, color_by_state: e.target.checked };
      this._emitConfig();
    });

    this.querySelector("#opacity-slider")?.addEventListener("input", (e) => {
      const value = parseFloat(e.target.value);
      this._config = { ...this._config, background_opacity: value };
      const label = this.querySelector("#opacity-value");
      if (label) label.textContent = `${Math.round(value * 100)}%`;
      this._emitConfig();
    });

    this.querySelector("#hide-inactive-toggle")?.addEventListener("change", (e) => {
      this._config = { ...this._config, hide_inactive: e.target.checked };
      this._emitConfig();
    });

    this.querySelectorAll('input[name="display-style"]').forEach((el) => {
      el.addEventListener("change", (e) => {
        if (e.target.checked) {
          this._config = { ...this._config, display_style: e.target.value };
          this._emitConfig();
        }
      });
    });

    this.querySelectorAll("input[data-attr-key]").forEach((el) => {
      el.addEventListener("change", (e) => {
        const key = e.target.getAttribute("data-attr-key");
        const current = new Set(this._config.show_attributes || []);
        if (e.target.checked) current.add(key);
        else current.delete(key);
        this._config = { ...this._config, show_attributes: Array.from(current) };
        this._emitConfig();
      });
    });

    this.querySelectorAll("input[data-extra-entity-key]").forEach((el) => {
      el.addEventListener("change", (e) => {
        const key = e.target.getAttribute("data-extra-entity-key");
        const current = new Set(this._config.extra_entities || []);
        if (e.target.checked) current.add(key);
        else current.delete(key);
        this._config = { ...this._config, extra_entities: Array.from(current) };
        this._emitConfig();
      });
    });
  }
}

customElements.define("termostato-diag-card", TermostatoDiagCard);
customElements.define("termostato-diag-card-editor", TermostatoDiagCardEditor);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "termostato-diag-card",
  name: "Termostato Diag Card",
  description: "Card per Termostato Intelligente FV con sfondo colorato in base allo stato e attributi diagnostici configurabili da UI.",
  preview: true,
});
