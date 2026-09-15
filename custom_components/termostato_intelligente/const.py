"""Costanti per l'integrazione Termostato Intelligente FV."""

DOMAIN = "termostato_intelligente"

# --- Entità core ---
CONF_NAME = "name"
CONF_CLIMATE_ENTITY = "climate_entity"
CONF_TEMP_SENSOR = "temp_sensor"
CONF_WINDOW_SENSOR = "window_sensor"
CONF_WINDOW_DETECTION_ENABLED = "window_detection_enabled"  # se disattivato, la finestra non influisce mai sul climatizzatore
CONF_PRESENCE_SENSOR = "presence_sensor"
CONF_DOOR_SENSOR = "door_sensor"

# --- Energia (FV / batteria) ---
CONF_FV_SENSOR = "fv_sensor"
CONF_CONSUMPTION_SENSOR = "consumption_sensor"
CONF_BATTERY_SENSOR = "battery_sensor"
CONF_FV_MARGIN_W = "fv_margin_w"
CONF_SOC_MIN = "soc_min"
CONF_FV_START_TIME = "fv_start_time"
CONF_FV_END_TIME = "fv_end_time"
CONF_FV_PRIORITY = "fv_priority"
CONF_FV_STAGGER_MIN = "fv_stagger_minutes"

# --- Spegnimento diurno da FV ---
CONF_FV_SHUTOFF_ENABLED = "fv_shutoff_enabled"
CONF_FV_SHUTOFF_MANUAL = "fv_shutoff_manual"  # spegni anche se acceso manualmente
DEFAULT_FV_SHUTOFF_MANUAL = False  # default: non spegnere se acceso manualmente
CONF_FV_SHUTOFF_MANUAL_DELAY_MIN = "fv_shutoff_manual_delay_min"  # ritardo extra prima di spegnere un'accensione manuale
DEFAULT_FV_SHUTOFF_MANUAL_DELAY_MIN = 30  # minuti — consigliati almeno 30, minimo 10
CONF_FV_SHUTOFF_DELAY_MIN = "fv_shutoff_delay_min"
CONF_FV_SHUTOFF_TOTAL_MINUTES = "fv_shutoff_total_minutes"  # minuti totali di calo FV confermato prima di spegnere
CONF_FV_TURN_ON_TOTAL_MINUTES = "fv_turn_on_total_minutes"  # minuti totali di surplus FV confermato prima di accendere
CONF_FV_SENSOR_OFFLINE_SHUTOFF_ENABLED = "fv_sensor_offline_shutoff_enabled"  # spegni se il sensore FV va offline (solo climi accesi dal FV)
CONF_FV_SENSOR_OFFLINE_SHUTOFF_MIN = "fv_sensor_offline_shutoff_min"  # minuti di sensore offline prima di spegnere
CONF_FV_SENSOR_OFFLINE_NOTIFY_TTS = "fv_sensor_offline_notify_tts"  # avviso vocale per questo evento
CONF_FV_SENSOR_OFFLINE_NOTIFY_TELEGRAM = "fv_sensor_offline_notify_telegram"  # avviso Telegram per questo evento
CONF_FV_SHUTOFF_EXTRA_HOURS = "fv_shutoff_extra_hours"
CONF_FV_SHUTOFF_THRESHOLD = "fv_shutoff_threshold"

# --- Profilo di regolazione ---
CONF_PROFILE = "profile"
PRESET_BILANCIATO = "bilanciato"
PRESET_AGGRESSIVO = "aggressivo"
PRESET_DELICATO = "delicato"
PRESET_PERSONALIZZATO = "personalizzato"
DEFAULT_PROFILE = PRESET_BILANCIATO

# --- Soglie termiche / timing ---
CONF_TARGET_TEMP_DEFAULT = "target_temp_default"
CONF_EXTREME_OFFSET = "extreme_offset"
CONF_HOT_OFFSET = "hot_offset"
CONF_RANGE_OFFSET = "range_offset"
CONF_BELOW_OFFSET = "below_offset"
CONF_TURN_ON_OFFSET = "turn_on_offset"
CONF_TEMP_DELTA = "temp_delta"
CONF_EXTREME_DELTA = "extreme_delta"
CONF_PRESENCE_BOOST_ENABLED = "presence_boost_enabled"
CONF_PRESENCE_BOOST_MIN = "presence_boost_minutes"
CONF_PRESENCE_BOOST_OFFSET = "presence_boost_offset"
CONF_WINDOW_DELAY_MIN = "window_delay_minutes"
CONF_UPDATE_INTERVAL_MIN = "update_interval_minutes"

# --- Calibrazione sonda interna climatizzatore ---
CONF_CALIBRATION_MAX_OFFSET = "calibration_max_offset"
CONF_MIN_BELOW_INTERNAL = "min_below_internal"

# --- Modalità notturna ---
CONF_NIGHT_START_TIME = "night_start_time"
CONF_NIGHT_END_TIME = "night_end_time"
CONF_NIGHT_OFFSET = "night_offset"
CONF_NIGHT_TURN_ON_OFFSET = "night_turn_on_offset"
CONF_NIGHT_AC_ENABLED = "night_ac_enabled"

# --- Spegnimento notturno per raggiungimento target ---
CONF_NIGHT_SHUTOFF_ENABLED = "night_shutoff_enabled"
CONF_NIGHT_SHUTOFF_DELTA = "night_shutoff_delta"
CONF_NIGHT_SHUTOFF_MIN = "night_shutoff_min"

# --- Spegnimento a fine modalità notturna ---
CONF_NIGHT_END_SHUTOFF_ENABLED = "night_end_shutoff_enabled"       # spegne sempre
CONF_NIGHT_END_SHUTOFF_AUTO_ONLY = "night_end_shutoff_auto_only"   # spegne solo se acceso automaticamente

# --- Notifiche TTS (Google / media_player) ---
CONF_TTS_PLAYERS = "tts_media_players"
CONF_TTS_ENGINE = "tts_engine_entity"
CONF_TTS_MESSAGE_OPEN = "tts_message_open"

# --- Notifiche Telegram / notify ---
CONF_NOTIFY_TARGETS = "notify_targets"
CONF_NOTIFY_CHAT_IDS = "notify_chat_ids"
CONF_NOTIFY_TEMP_CHANGE_ENABLED = "notify_temp_change_enabled"
CONF_NOTIFY_TEMP_CHANGE_MESSAGE = "notify_temp_change_message"
CONF_NOTIFY_TEMP_CHANGE_LIMIT_ENABLED = "notify_temp_change_limit_enabled"
CONF_NOTIFY_TEMP_CHANGE_LIMIT_MIN = "notify_temp_change_limit_min"

# --- Avvisi accensione/spegnimento automatico ---
CONF_NOTIFY_POWER_TTS = "notify_power_tts"
CONF_NOTIFY_POWER_NOTIFY = "notify_power_notify"

# --- Avviso spegnimento fine notte ---
CONF_NOTIFY_NIGHT_END_TTS = "notify_night_end_tts"
CONF_NOTIFY_NIGHT_END_NOTIFY = "notify_night_end_notify"

# --- Fascia di silenzio ---
CONF_QUIET_ENABLED = "quiet_enabled"
CONF_QUIET_START_TIME = "quiet_start_time"
CONF_QUIET_END_TIME = "quiet_end_time"
CONF_QUIET_TTS = "quiet_tts"
CONF_QUIET_NOTIFY = "quiet_notify"

# --- Avviso porta (selettivo per canale) ---
CONF_DOOR_ALERT_ENABLED = "door_alert_enabled"
CONF_DOOR_ALERT_MESSAGE = "door_alert_message"
CONF_DOOR_ALERT_TTS = "door_alert_tts"
CONF_DOOR_ALERT_NOTIFY = "door_alert_notify"


# --- Protezione potenza (evita distacco contatore) ---
CONF_POWER_LIMIT_ENABLED = "power_limit_enabled"
CONF_POWER_LIMIT_SENSOR = "power_limit_sensor"
CONF_POWER_LIMIT_MODE = "power_limit_mode"
CONF_POWER_LIMIT_MAX_W = "power_limit_max_w"
CONF_POWER_LIMIT_HYSTERESIS_W = "power_limit_hysteresis_w"
CONF_POWER_LIMIT_RESTORE_MIN = "power_limit_restore_min"
CONF_POWER_LIMIT_NOTIFY_TTS = "power_limit_notify_tts"
CONF_POWER_LIMIT_NOTIFY_TELEGRAM = "power_limit_notify_telegram"
CONF_POWER_LIMIT_MSG_OFF = "power_limit_msg_off"
CONF_POWER_LIMIT_MSG_ON = "power_limit_msg_on"

POWER_LIMIT_MODE_SINGLE = "unico"
POWER_LIMIT_MODE_MULTI = "multiplo"

DEFAULT_POWER_LIMIT_ENABLED = False
DEFAULT_POWER_LIMIT_MODE = POWER_LIMIT_MODE_SINGLE
DEFAULT_POWER_LIMIT_MAX_W = 3500
DEFAULT_POWER_LIMIT_HYSTERESIS_W = 800
DEFAULT_POWER_LIMIT_RESTORE_MIN = 5
DEFAULT_POWER_LIMIT_NOTIFY_TTS = False
DEFAULT_POWER_LIMIT_NOTIFY_TELEGRAM = True
DEFAULT_POWER_LIMIT_MSG_OFF = (
    "Ho spento il climatizzatore {{ name }} per evitare che vada via la luce."
)
DEFAULT_POWER_LIMIT_MSG_ON = (
    "Ho riacceso il condizionatore {{ name }} perché stai consumando meno."
)

# Anti-picco: secondi di consumo sopra soglia prima di spegnere (fisso)
POWER_LIMIT_SPIKE_SEC = 30
# Stagger riaccensione cascata multi-clima (fisso)
POWER_LIMIT_RESTORE_STAGGER_MIN = 2


# --- Emergenza caldo (solo modo semplificato FV e completo) ---
SWITCH_KEY_EMERGENCY = "emergency_heat"

CONF_EMERGENCY_HEAT_THRESHOLD = "emergency_heat_threshold"
CONF_EMERGENCY_HEAT_END_THRESHOLD = "emergency_heat_end_threshold"
CONF_EMERGENCY_NOTIFY_TTS = "emergency_notify_tts"
CONF_EMERGENCY_NOTIFY_TELEGRAM = "emergency_notify_telegram"
CONF_EMERGENCY_MSG_ON = "emergency_msg_on"
CONF_EMERGENCY_MSG_OFF = "emergency_msg_off"

DEFAULT_EMERGENCY_HEAT_THRESHOLD = 1.5
DEFAULT_EMERGENCY_HEAT_END_THRESHOLD = 0.7
DEFAULT_EMERGENCY_NOTIFY_TTS = False
DEFAULT_EMERGENCY_NOTIFY_TELEGRAM = True
DEFAULT_EMERGENCY_MSG_ON = "Ho acceso il condizionatore {{ name }} per emergenza caldo."
DEFAULT_EMERGENCY_MSG_OFF = "Fine emergenza caldo, il condizionatore {{ name }} riprende a funzionare normalmente."
DEFAULT_EMERGENCY_WINTER_MSG_ON = "Ho acceso il riscaldamento {{ name }} per emergenza freddo."
DEFAULT_EMERGENCY_WINTER_MSG_OFF = "Fine emergenza freddo, il riscaldamento {{ name }} riprende a funzionare normalmente."

# Minuti prima della notte per spegnere e disattivare emergenza
EMERGENCY_PRE_NIGHT_MIN = 5
INSTABILITY_GRACE_PERIOD_SECONDS = 1200  # periodo dopo l'ULTIMA volta che l'entità reale è stata vista unavailable/unknown (incluso il momento in cui l'entità viene aggiunta a Home Assistant, trattato come istante di instabilità presunta) in cui non rileviamo accensioni/spegnimenti manuali — copre sia il riavvio sia qualsiasi interruzione successiva, un solo meccanismo invece di un timer fisso separato
STATE_CHANGE_DEBOUNCE_SECONDS = 15  # conferma temporale prima di considerare vera una transizione spento<->acceso del clima reale — protegge da glitch di integrazioni cloud (es. ConnectLife/Hisense)
CONFIG_WRITE_DEBOUNCE_SECONDS = 1.5  # attesa dopo l'ultima regolazione dalla card (priorità/target) prima di scrivere in configurazione — click ripetuti ravvicinati producono un solo ricaricamento, non uno per click

# --- Switch ausiliari ---
SWITCH_KEY_MASTER = "switch_master"
SWITCH_KEY_FV = "switch_fv"
SWITCH_KEY_QUICK = "switch_quick"

# --- Motivi di accensione/spegnimento ---
REASON_FV = "fv"
REASON_NIGHT = "night"
REASON_NIGHT_SHUTOFF = "night_shutoff"
REASON_NIGHT_END = "night_end"
REASON_FV_SHUTOFF = "fv_shutoff"
REASON_WINDOW = "window"

# --- Default ---
DEFAULT_NAME = "Termostato Intelligente"
DEFAULT_TARGET_TEMP = 25.0
DEFAULT_EXTREME_OFFSET = 2.0
DEFAULT_HOT_OFFSET = 1.5
DEFAULT_RANGE_OFFSET = 0.2
DEFAULT_BELOW_OFFSET = 0.1
DEFAULT_TURN_ON_OFFSET = 1.5
DEFAULT_TEMP_DELTA = 1.0
DEFAULT_EXTREME_DELTA = 2.0
DEFAULT_PRESENCE_BOOST_ENABLED = False
DEFAULT_FV_MARGIN_W = 1200
DEFAULT_SOC_MIN = 70
DEFAULT_FV_START_TIME = "10:00:00"
DEFAULT_FV_END_TIME = "16:00:00"
DEFAULT_FV_PRIORITY = 50
DEFAULT_FV_STAGGER_MIN = 5
DEFAULT_FV_SHUTOFF_ENABLED = False
DEFAULT_FV_SHUTOFF_DELAY_MIN = 5
DEFAULT_FV_SHUTOFF_TOTAL_MINUTES = 20  # minuti totali (4 campioni fissi → intervallo = totale/4)
DEFAULT_FV_TURN_ON_TOTAL_MINUTES = 15  # minuti totali di conferma prima di accendere (4 campioni fissi)
DEFAULT_FV_SENSOR_OFFLINE_SHUTOFF_ENABLED = False  # disattivato di default — l'utente lo attiva consapevolmente
DEFAULT_FV_SENSOR_OFFLINE_SHUTOFF_MIN = 45  # minuti, stesso ordine di grandezza del fallback sonda temperatura
DEFAULT_FV_SENSOR_OFFLINE_NOTIFY_TTS = True
DEFAULT_FV_SENSOR_OFFLINE_NOTIFY_TELEGRAM = True
DEFAULT_FV_SHUTOFF_EXTRA_HOURS = 1.0
DEFAULT_FV_SHUTOFF_THRESHOLD = 0
DEFAULT_PRESENCE_BOOST_MIN = 10
DEFAULT_PRESENCE_BOOST_OFFSET = 1.0
DEFAULT_WINDOW_DELAY_MIN = 5
DEFAULT_WINDOW_DETECTION_ENABLED = True  # comportamento invariato di default — l'utente lo disattiva consapevolmente
DEFAULT_UPDATE_INTERVAL_MIN = 5
DEFAULT_CALIBRATION_MAX_OFFSET = 3.0
DEFAULT_MIN_BELOW_INTERNAL = 1.0
DEFAULT_NIGHT_START_TIME = "23:00:00"
DEFAULT_NIGHT_END_TIME = "07:00:00"
DEFAULT_NIGHT_OFFSET = 0.0
DEFAULT_NIGHT_TURN_ON_OFFSET = 1.5
DEFAULT_NIGHT_AC_ENABLED = False
DEFAULT_NIGHT_SHUTOFF_ENABLED = False
DEFAULT_NIGHT_SHUTOFF_DELTA = 0.3
DEFAULT_NIGHT_SHUTOFF_MIN = 30
DEFAULT_NIGHT_END_SHUTOFF_ENABLED = False
DEFAULT_NIGHT_END_SHUTOFF_AUTO_ONLY = False
DEFAULT_NOTIFY_TEMP_CHANGE_ENABLED = True
DEFAULT_NOTIFY_TEMP_CHANGE_LIMIT_ENABLED = False
DEFAULT_NOTIFY_TEMP_CHANGE_LIMIT_MIN = 30
DEFAULT_DOOR_ALERT_ENABLED = False
DEFAULT_DOOR_ALERT_TTS = True
DEFAULT_DOOR_ALERT_NOTIFY = True
DEFAULT_DOOR_ALERT_MESSAGE = "\U0001f6aa {{ name }}: porta aperta."
DEFAULT_NOTIFY_POWER_TTS = False
DEFAULT_NOTIFY_POWER_NOTIFY = True
DEFAULT_NOTIFY_NIGHT_END_TTS = False
DEFAULT_NOTIFY_NIGHT_END_NOTIFY = True
DEFAULT_QUIET_ENABLED = False
DEFAULT_QUIET_START_TIME = "23:00:00"
DEFAULT_QUIET_END_TIME = "07:00:00"
DEFAULT_QUIET_TTS = True
DEFAULT_QUIET_NOTIFY = False

DEFAULT_TTS_MESSAGE_OPEN = (
    "Attenzione: la finestra della {{ name }} \u00e8 aperta. "
    "Il climatizzatore si spegner\u00e0 tra {{ delay }} minuti se non viene chiusa."
)
DEFAULT_TTS_MESSAGE_CLOSED = (
    "La finestra della {{ name }} \u00e8 stata chiusa. "
    "Il climatizzatore \u00e8 stato riacceso."
)
DEFAULT_NOTIFY_MESSAGE_OPEN = (
    "\U0001fa9f {{ name }}: finestra aperta. "
    "Il clima si spegner\u00e0 tra {{ delay }} minuti se non viene chiusa."
)
DEFAULT_NOTIFY_MESSAGE_CLOSED = (
    "\u2705 {{ name }}: finestra chiusa, climatizzatore riacceso."
)
DEFAULT_DOOR_ALERT_OPEN_MESSAGE = "\U0001f6aa {{ name }}: porta aperta."
DEFAULT_DOOR_ALERT_CLOSED_MESSAGE = "\u2705 {{ name }}: porta chiusa."
DEFAULT_NOTIFY_TEMP_CHANGE_MESSAGE = (
    "\U0001f321 {{ name }}: setpoint \u2192 {{ new_temp }}\u00b0C "
    "(ventola {{ fan_mode }}) \u2014 stanza {{ room_temp }}\u00b0C, target {{ target }}\u00b0C"
)
DEFAULT_POWER_ON_FV_MESSAGE = (
    "\u2600\ufe0f {{ name }}: ho acceso il climatizzatore perch\u00e9 stai producendo "
    "{{ fv }}W di fotovoltaico e la stanza \u00e8 a {{ temp }}\u00b0C "
    "(target {{ target }}\u00b0C)."
)
DEFAULT_POWER_ON_NIGHT_MESSAGE = (
    "\U0001f319 {{ name }}: ho acceso il climatizzatore in modalit\u00e0 notturna perch\u00e9 "
    "la stanza \u00e8 a {{ temp }}\u00b0C (target notte {{ target }}\u00b0C)."
)
DEFAULT_POWER_OFF_FV_MESSAGE = (
    "\u2600\ufe0f {{ name }}: ho spento il climatizzatore perch\u00e9 la produzione "
    "fotovoltaica ({{ fv }}W) \u00e8 scesa sotto il consumo attuale ({{ consumo }}W)."
)
DEFAULT_POWER_OFF_NIGHT_MESSAGE = (
    "\U0001f319 {{ name }}: ho spento il climatizzatore perch\u00e9 la stanza "
    "ha raggiunto la temperatura target notturna ({{ temp }}\u00b0C \u2264 {{ target }}\u00b0C)."
)
DEFAULT_POWER_OFF_NIGHT_END_MESSAGE = (
    "\U0001f305 {{ name }}: fine modalit\u00e0 notturna, climatizzatore spento."
)

# Limite ventola
FAN_MODES_ALLOWED = ["low", "medium", "high"]

PRESET_VALUES: dict[str, dict] = {
    PRESET_BILANCIATO: {
        CONF_EXTREME_OFFSET: 2.0,
        CONF_HOT_OFFSET: 1.5,
        CONF_RANGE_OFFSET: 0.2,
        CONF_BELOW_OFFSET: 0.1,
        CONF_TURN_ON_OFFSET: 1.5,
        CONF_TEMP_DELTA: 1.0,
        CONF_EXTREME_DELTA: 2.0,
        CONF_CALIBRATION_MAX_OFFSET: 3.0,
        CONF_MIN_BELOW_INTERNAL: 1.0,
    },
    PRESET_AGGRESSIVO: {
        CONF_EXTREME_OFFSET: 1.6,
        CONF_HOT_OFFSET: 1.2,
        CONF_RANGE_OFFSET: 0.2,
        CONF_BELOW_OFFSET: 0.1,
        CONF_TURN_ON_OFFSET: 1.2,
        CONF_TEMP_DELTA: 1.2,
        CONF_EXTREME_DELTA: 2.4,
        CONF_CALIBRATION_MAX_OFFSET: 3.0,
        CONF_MIN_BELOW_INTERNAL: 1.2,
    },
    PRESET_DELICATO: {
        CONF_EXTREME_OFFSET: 2.4,
        CONF_HOT_OFFSET: 1.8,
        CONF_RANGE_OFFSET: 0.2,
        CONF_BELOW_OFFSET: 0.1,
        CONF_TURN_ON_OFFSET: 1.8,
        CONF_TEMP_DELTA: 0.8,
        CONF_EXTREME_DELTA: 1.6,
        CONF_CALIBRATION_MAX_OFFSET: 3.5,
        CONF_MIN_BELOW_INTERNAL: 0.8,
    },
}

# --- Modalità di configurazione ---
CONF_CONFIG_MODE = "config_mode"
CONFIG_MODE_SIMPLE = "semplificato"
CONFIG_MODE_SIMPLE_FV = "semplificato_fv"
CONFIG_MODE_FULL = "completo"
DEFAULT_CONFIG_MODE = CONFIG_MODE_SIMPLE

# --- Modo semplificato — temperature e orari ---
CONF_SIMPLE_TARGET_DAY = "simple_target_day"
CONF_SIMPLE_TARGET_NIGHT = "simple_target_night"
CONF_SIMPLE_NIGHT_START = "simple_night_start"
CONF_SIMPLE_NIGHT_END = "simple_night_end"
CONF_SIMPLE_SUNSET_ANTICIPATE_H = "simple_sunset_anticipate_h"  # ore di anticipo rispetto al tramonto

# --- Modo semplificato — notifiche Google Home (TTS) ---
CONF_SIMPLE_NOTIFY_TTS_AC_ON = "simple_notify_tts_ac_on"
CONF_SIMPLE_NOTIFY_TTS_AC_OFF = "simple_notify_tts_ac_off"
CONF_SIMPLE_NOTIFY_TTS_TEMP_CHANGE = "simple_notify_tts_temp_change"
CONF_SIMPLE_NOTIFY_TTS_WINDOW_OPEN = "simple_notify_tts_window_open"
CONF_SIMPLE_NOTIFY_TTS_WINDOW_CLOSE = "simple_notify_tts_window_close"
CONF_SIMPLE_NOTIFY_TTS_DOOR_OPEN = "simple_notify_tts_door_open"
CONF_SIMPLE_NOTIFY_TTS_DOOR_CLOSE = "simple_notify_tts_door_close"
CONF_SIMPLE_NOTIFY_TTS_NIGHT_START = "simple_notify_tts_night_start"
CONF_SIMPLE_NOTIFY_TTS_NIGHT_END = "simple_notify_tts_night_end"
CONF_SIMPLE_QUIET_NIGHT_TTS = "simple_quiet_night_tts"

# --- Modo semplificato — notifiche Telegram ---
CONF_SIMPLE_NOTIFY_TEL_AC_ON = "simple_notify_tel_ac_on"
CONF_SIMPLE_NOTIFY_TEL_AC_OFF = "simple_notify_tel_ac_off"
CONF_SIMPLE_NOTIFY_TEL_TEMP_CHANGE = "simple_notify_tel_temp_change"
CONF_SIMPLE_NOTIFY_TEL_WINDOW_OPEN = "simple_notify_tel_window_open"
CONF_SIMPLE_NOTIFY_TEL_WINDOW_CLOSE = "simple_notify_tel_window_close"
CONF_SIMPLE_NOTIFY_TEL_DOOR_OPEN = "simple_notify_tel_door_open"
CONF_SIMPLE_NOTIFY_TEL_DOOR_CLOSE = "simple_notify_tel_door_close"
CONF_SIMPLE_NOTIFY_TEL_NIGHT_START = "simple_notify_tel_night_start"
CONF_SIMPLE_NOTIFY_TEL_NIGHT_END = "simple_notify_tel_night_end"
CONF_SIMPLE_QUIET_NIGHT_NOTIFY = "simple_quiet_night_notify"

# --- Default modo semplificato ---
DEFAULT_SIMPLE_TARGET_DAY = 25.0
DEFAULT_SIMPLE_TARGET_NIGHT = 26.0
DEFAULT_SIMPLE_SUNSET_ANTICIPATE_H = 2  # ore di anticipo rispetto al tramonto
DEFAULT_SIMPLE_NIGHT_START = "23:00:00"
DEFAULT_SIMPLE_NIGHT_END = "07:00:00"
DEFAULT_SIMPLE_NOTIFY_TTS_AC_ON = False
DEFAULT_SIMPLE_NOTIFY_TTS_AC_OFF = False
DEFAULT_SIMPLE_NOTIFY_TTS_TEMP_CHANGE = False
DEFAULT_SIMPLE_NOTIFY_TTS_WINDOW_OPEN = True
DEFAULT_SIMPLE_NOTIFY_TTS_WINDOW_CLOSE = True
DEFAULT_SIMPLE_NOTIFY_TTS_DOOR_OPEN = True
DEFAULT_SIMPLE_NOTIFY_TTS_DOOR_CLOSE = True
DEFAULT_SIMPLE_NOTIFY_TTS_NIGHT_START = False
DEFAULT_SIMPLE_NOTIFY_TTS_NIGHT_END = False
DEFAULT_SIMPLE_NOTIFY_TEL_AC_ON = True
DEFAULT_SIMPLE_NOTIFY_TEL_AC_OFF = True
DEFAULT_SIMPLE_NOTIFY_TEL_TEMP_CHANGE = False
DEFAULT_SIMPLE_NOTIFY_TEL_WINDOW_OPEN = True
DEFAULT_SIMPLE_NOTIFY_TEL_WINDOW_CLOSE = True
DEFAULT_SIMPLE_NOTIFY_TEL_DOOR_OPEN = True
DEFAULT_SIMPLE_NOTIFY_TEL_DOOR_CLOSE = True
DEFAULT_SIMPLE_NOTIFY_TEL_NIGHT_START = False
DEFAULT_SIMPLE_NOTIFY_TEL_NIGHT_END = True
DEFAULT_SIMPLE_QUIET_NIGHT_TTS = True
DEFAULT_SIMPLE_QUIET_NIGHT_NOTIFY = False

# --- Costanti logica termica semplificata ---
# Con sonda esterna (decimale)
# La soglia di accensione è configurabile (CONF_SIMPLE_TURN_ON_OFFSET, default 0.8)
SIMPLE_EXT_HOT_OFFSET = 2.0        # ventola alta da target + 2.0
SIMPLE_EXT_WARM_OFFSET = 1.3       # ventola media da target + 1.3
SIMPLE_EXT_MILD_OFFSET = 0.3       # ventola bassa da target + 0.3
SIMPLE_EXT_SLOW_OFFSET = 0.3       # rallenta quando stanza ≤ target + 0.3
SIMPLE_EXT_SHUTOFF_OFFSET = -0.3   # spegne se sotto target - 0.3 per 15 min
SIMPLE_EXT_SETPOINT_HOT = 2.0      # sonda interna - 2 in caldo forte/estremo
SIMPLE_EXT_SETPOINT_MILD = 1.0     # sonda interna - 1 in caldo lieve
SIMPLE_EXT_SHUTOFF_MIN = 5        # minuti sotto soglia prima di spegnere

# Con sonda interna (intera)
# La soglia di accensione è configurabile (CONF_SIMPLE_TURN_ON_OFFSET, default 1.0)
SIMPLE_INT_HOT_OFFSET = 2          # ventola alta da target + 2
SIMPLE_INT_WARM_OFFSET = 1         # ventola media da target + 1
SIMPLE_INT_AT_TARGET = 0           # rallenta quando stanza ≤ target
SIMPLE_INT_SHUTOFF_OFFSET = -1     # spegne se sotto target - 1 per 15 min
SIMPLE_INT_SETPOINT_HOT = 2        # sonda interna - 2 in caldo forte/estremo
SIMPLE_INT_SETPOINT_MILD = 1       # sonda interna - 1 in caldo lieve
SIMPLE_INT_SHUTOFF_MIN = 5        # minuti sotto soglia prima di spegnere

# --- Modo semplificato — deumidificatore ---
CONF_SIMPLE_NO_AUTO_ON_NIGHT = "simple_no_auto_on_night"  # blocca accensione automatica di notte
CONF_SIMPLE_NO_REON_MANUAL_OFF = "simple_no_reon_manual_off"  # non riaccendere se spento manualmente
CONF_SIMPLE_NO_REON_MANUAL_OFF_HOURS = "simple_no_reon_manual_off_hours"  # ore di blocco riaccensione
CONF_SIMPLE_TURN_ON_OFFSET = "simple_turn_on_offset"  # soglia accensione configurabile
CONF_SIMPLE_SHUTOFF_MARGIN = "simple_shutoff_margin"  # margine sotto il target prima di spegnere
CONF_SIMPLE_ECO_DAY_ENABLED = "simple_eco_day_enabled"  # invece di spegnere di giorno al raggiungimento del target-margine, entra in modalità Eco seguendo la sonda interna fino a target+margine
CONF_SIMPLE_ECO_NIGHT_ENABLED = "simple_eco_night_enabled"  # stesso, ma per la notte
CONF_MANUAL_SHUTOFF_TIMER_MIN = "manual_shutoff_timer_min"  # minuti dopo cui spegnere automaticamente un'accensione manuale, se il timer è attivo dalla card (0 = funzione mai configurata)
CONF_MANUAL_SHUTOFF_TIMER_ENABLED = "manual_shutoff_timer_enabled"  # se True, il timer parte da solo ad ogni accensione manuale — vale sempre, anche a master switch disattivato
CONF_SIMPLE_EXTERNAL_SENSOR_STALE_MIN = "simple_external_sensor_stale_min"  # dopo quanti minuti senza aggiornamenti considerare bloccata la sonda esterna
DEFAULT_SIMPLE_EXTERNAL_SENSOR_STALE_MIN = 45  # minuti
CONF_SIMPLE_DRY_ENABLED = "simple_dry_enabled"
CONF_SIMPLE_DRY_MAX_MIN = "simple_dry_max_min"
DEFAULT_SIMPLE_NO_AUTO_ON_NIGHT = False
DEFAULT_SIMPLE_NO_REON_MANUAL_OFF = False
DEFAULT_SIMPLE_NO_REON_MANUAL_OFF_HOURS = 2
DEFAULT_SIMPLE_TURN_ON_OFFSET_EXT = 0.8  # sonda esterna: accende da target + 0.8°C
DEFAULT_SIMPLE_TURN_ON_OFFSET_INT = 1.0  # sonda interna: accende da target + 1°C
DEFAULT_SIMPLE_SHUTOFF_MARGIN = 0.2  # °C sotto il target prima di spegnere (arrotondato a 0/1 per la sonda interna)
DEFAULT_SIMPLE_ECO_DAY_ENABLED = False
DEFAULT_SIMPLE_ECO_NIGHT_ENABLED = False
DEFAULT_MANUAL_SHUTOFF_TIMER_MIN = 0  # 0 = timer non configurato/disattivato di default
DEFAULT_MANUAL_SHUTOFF_TIMER_ENABLED = True  # se configuri dei minuti, di default vuoi che il timer parta da solo
DEFAULT_SIMPLE_DRY_ENABLED = False
DEFAULT_SIMPLE_DRY_MAX_MIN = 30

# Soglie dry con sonda esterna
SIMPLE_EXT_DRY_LOW = 0.3    # accende in dry se stanza > target + 0.3
SIMPLE_EXT_DRY_HIGH = 1.5   # passa a cool se stanza > target + 1.5

# Soglie dry con sonda interna
SIMPLE_INT_DRY_LOW = 1      # accende in dry se stanza > target + 1
SIMPLE_INT_DRY_HIGH = 2     # passa a cool se stanza > target + 2
SIMPLE_WINDOW_DELAY_MIN = 5

# Ore di limbo dopo fine modalità notturna (nessuna azione del termostato)
SIMPLE_NIGHT_END_LIMBO_H = 1

# Messaggi modo semplificato
DEFAULT_SIMPLE_MSG_TEMP_CHANGE = "🌡️ {{ name }}: temperatura {{ temp }}°C (target {{ target }}°C){% if eco %}, modalità eco{% elif fan %}, ventola {{ fan }}{% endif %}."
DEFAULT_SIMPLE_MSG_DOOR_OPEN = "\U0001f6aa {{ name }}: porta aperta."
DEFAULT_SIMPLE_MSG_DOOR_CLOSE = "\u2705 {{ name }}: porta chiusa."
DEFAULT_SIMPLE_MSG_WINDOW_OPEN = (
    "\U0001fa9f {{ name }}: finestra aperta. "
    "Il clima si spegnerà tra {{ delay }} minuti se non viene chiusa."
)
DEFAULT_SIMPLE_MSG_WINDOW_CLOSE = "\u2705 {{ name }}: finestra chiusa, climatizzatore riacceso."
DEFAULT_SIMPLE_MSG_WINDOW_SHUTOFF = "\u26a0\ufe0f {{ name }}: climatizzatore spento — sono passati {{ minuti }} minuti e la finestra non è stata chiusa."
DEFAULT_SIMPLE_MSG_AC_ON = "\u2600\ufe0f {{ name }}: acceso per temperatura ({{ temp }}\u00b0C, target {{ target }}\u00b0C)."
DEFAULT_SIMPLE_MSG_AC_ON_FV = "\u26a1 {{ name }}: acceso dal FV ({{ temp }}\u00b0C, FV {{ fv }}W, surplus {{ surplus }}W, batteria {{ soc }}%)."
DEFAULT_SIMPLE_MSG_AC_ON_NIGHT = "\U0001f319 {{ name }}: acceso modalità notturna ({{ temp }}\u00b0C, target {{ target }}\u00b0C)."
DEFAULT_SIMPLE_MSG_AC_ON_EMERGENCY = "\U0001f525 {{ name }}: acceso emergenza caldo ({{ temp }}\u00b0C, target {{ target }}\u00b0C)."
DEFAULT_SIMPLE_MSG_AC_OFF = "\U0001f4a4 {{ name }}: climatizzatore spento — temperatura raggiunta ({{ temp }}\u00b0C, target {{ target }}\u00b0C, sonda {{ sonda }})."
DEFAULT_SIMPLE_MSG_AC_OFF_FV = "\u26a1 {{ name }}: climatizzatore spento — produzione FV insufficiente ({{ temp }}\u00b0C, target {{ target }}\u00b0C, sonda {{ sonda }})."
DEFAULT_SIMPLE_MSG_NIGHT_START = "\U0001f319 {{ name }}: inizio modalità notturna (target {{ target }}\u00b0C)."
DEFAULT_SIMPLE_MSG_NIGHT_END = "\U0001f305 {{ name }}: fine modalità notturna, climatizzatore spento."

# ==========================================================================
# MODALITÀ STAGIONALE (Estate/Inverno/Manuale) — v0.9.0
# ==========================================================================
CONF_SEASON_MODE = "season_mode"  # "estate" | "inverno" | "auto" | "manuale" | "off"
SEASON_SUMMER = "estate"
SEASON_WINTER = "inverno"
SEASON_AUTO = "auto"  # entrambe le logiche attive, ciascuna con le proprie soglie
SEASON_MANUAL = "manuale"  # termica+FV disattivati, timer manuale attivo, master switch auto-disattivato
SEASON_OFF = "off"  # tutto disattivato, incluso il timer manuale — zero interferenze
DEFAULT_SEASON_MODE = SEASON_SUMMER  # chi non tocca il campo resta esattamente come oggi

# Tempo minimo tra uno spegnimento raffrescamento e un'accensione riscaldamento
# (o viceversa) in modalità Auto, per evitare cicli ravvicinati nelle giornate
# di mezza stagione (caso limite discusso e accettato, mitigato ma non eliminato
# dal timer di conferma FV già esistente)
SEASON_AUTO_SWITCH_COOLDOWN_HOURS = 20

# Campi inverno — soglie specchiate rispetto a quelle estive, separate per
# non dover ricordarsi di cambiarle ad ogni cambio stagione
CONF_WINTER_TARGET_DAY = "winter_target_day"  # sostituisce il target giorno estivo quando la stagione è inverno
CONF_WINTER_TARGET_NIGHT = "winter_target_night"  # sostituisce il target notte estivo quando la stagione è inverno
CONF_WINTER_TURN_ON_OFFSET = "winter_turn_on_offset"  # di quanti gradi SOTTO il target prima di accendere
CONF_WINTER_SHUTOFF_MARGIN = "winter_shutoff_margin"  # margine SOPRA il target prima di spegnere
CONF_WINTER_SOC_MIN = "winter_soc_min"  # soglia batteria minima per l'accensione FV in inverno (più alta di quella estiva — batteria preziosa)
CONF_WINTER_FLOOR_SENSOR = "winter_floor_sensor"  # binary_sensor dell'anello riscaldamento a pavimento (opzionale)

DEFAULT_WINTER_TARGET_DAY = 20.0
DEFAULT_WINTER_TARGET_NIGHT = 19.5
DEFAULT_WINTER_TURN_ON_OFFSET = 0.5
DEFAULT_WINTER_SHUTOFF_MARGIN = 0.2
DEFAULT_WINTER_SOC_MIN = 90.0

# Emergenza riscaldamento — nuovo, specchio di quella raffrescamento
# esistente (le cui chiavi tecniche restano invariate per compatibilità,
# solo l'etichetta visibile cambia da "Emergenza caldo" a "Emergenza
# accendi raffrescamento").
CONF_EMERGENCY_WINTER_HEAT_THRESHOLD = "emergency_winter_heat_threshold"
CONF_EMERGENCY_WINTER_HEAT_END_THRESHOLD = "emergency_winter_heat_end_threshold"
DEFAULT_EMERGENCY_WINTER_HEAT_THRESHOLD = 1.5
DEFAULT_EMERGENCY_WINTER_HEAT_END_THRESHOLD = 0.7

DEFAULT_SIMPLE_MSG_AC_ON_WINTER = "\U0001f525 {{ name }}: acceso riscaldamento ({{ temp }}\u00b0C, target {{ target }}\u00b0C)."
DEFAULT_SIMPLE_MSG_AC_ON_WINTER_FLOOR = "\U0001f525 {{ name }}: assistenza riscaldamento a pavimento ({{ temp }}\u00b0C, FV {{ fv }}W, surplus {{ surplus }}W, batteria {{ batteria }}%)."

# ==========================================================================
# Notifiche accensione/spegnimento manuale — selezionabili separatamente
# ==========================================================================
CONF_SIMPLE_NOTIFY_TTS_MANUAL_ON = "simple_notify_tts_manual_on"
CONF_SIMPLE_NOTIFY_TEL_MANUAL_ON = "simple_notify_tel_manual_on"
CONF_SIMPLE_NOTIFY_TTS_MANUAL_OFF = "simple_notify_tts_manual_off"
CONF_SIMPLE_NOTIFY_TEL_MANUAL_OFF = "simple_notify_tel_manual_off"

DEFAULT_SIMPLE_NOTIFY_TTS_MANUAL_ON = False
DEFAULT_SIMPLE_NOTIFY_TEL_MANUAL_ON = True
DEFAULT_SIMPLE_NOTIFY_TTS_MANUAL_OFF = False
DEFAULT_SIMPLE_NOTIFY_TEL_MANUAL_OFF = True

DEFAULT_SIMPLE_MSG_MANUAL_ON = "\U0001f535 {{ name }}: acceso manualmente ({{ temp }}\u00b0C, target {{ target }}\u00b0C, sonda {{ sonda }})."
DEFAULT_SIMPLE_MSG_MANUAL_OFF = "\U0001f534 {{ name }}: spento manualmente (telecomando/app esterna) — non dalla card."
DEFAULT_SIMPLE_MSG_AC_OFF_TIMER = "\u23f1\ufe0f {{ name }}: climatizzatore spento — timer di {{ minuti }} minuti scaduto ({{ temp }}\u00b0C, sonda {{ sonda }})."
