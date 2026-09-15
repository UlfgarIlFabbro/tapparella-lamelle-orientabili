"""Piattaforma climate: il vero e proprio 'termostato intelligente'."""

from __future__ import annotations


import asyncio
import logging
import math
from datetime import datetime, time as dt_time, timedelta
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import Event, HomeAssistant, State
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers import area_registry as ar, entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import (
    async_call_later,
    async_track_point_in_time,
    async_track_state_change_event,
    async_track_time_interval,
)
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.template import Template
from homeassistant.util import dt as dt_util

from .const import (
    CONF_BATTERY_SENSOR,
    CONF_BELOW_OFFSET,
    CONF_CALIBRATION_MAX_OFFSET,
    CONF_CLIMATE_ENTITY,
    CONF_CONSUMPTION_SENSOR,
    CONF_DOOR_ALERT_ENABLED,
    CONF_DOOR_ALERT_MESSAGE,
    CONF_DOOR_ALERT_NOTIFY,
    CONF_DOOR_ALERT_TTS,
    CONF_DOOR_SENSOR,
    CONF_EXTREME_DELTA,
    CONF_EXTREME_OFFSET,
    CONF_FV_END_TIME,
    CONF_FV_MARGIN_W,
    CONF_FV_PRIORITY,
    CONF_FV_SENSOR,
    CONF_FV_SHUTOFF_DELAY_MIN,
    CONF_FV_SHUTOFF_ENABLED,
    CONF_FV_SHUTOFF_MANUAL,
    CONF_FV_SHUTOFF_MANUAL_DELAY_MIN,
    CONF_FV_SHUTOFF_EXTRA_HOURS,
    CONF_FV_SHUTOFF_THRESHOLD,
    CONF_FV_STAGGER_MIN,
    CONF_FV_START_TIME,
    CONF_HOT_OFFSET,
    CONF_MIN_BELOW_INTERNAL,
    CONF_NAME,
    CONF_NIGHT_AC_ENABLED,
    CONF_NIGHT_END_TIME,
    CONF_NIGHT_END_SHUTOFF_AUTO_ONLY,
    CONF_NIGHT_END_SHUTOFF_ENABLED,
    CONF_NIGHT_OFFSET,
    CONF_NIGHT_SHUTOFF_DELTA,
    CONF_NIGHT_SHUTOFF_ENABLED,
    CONF_NIGHT_SHUTOFF_MIN,
    CONF_NIGHT_START_TIME,
    CONF_NIGHT_TURN_ON_OFFSET,
    CONF_NOTIFY_CHAT_IDS,
    CONF_NOTIFY_NIGHT_END_NOTIFY,
    CONF_NOTIFY_NIGHT_END_TTS,
    CONF_NOTIFY_POWER_NOTIFY,
    CONF_NOTIFY_POWER_TTS,
    CONF_NOTIFY_TARGETS,
    CONF_NOTIFY_TEMP_CHANGE_ENABLED,
    CONF_NOTIFY_TEMP_CHANGE_LIMIT_ENABLED,
    CONF_NOTIFY_TEMP_CHANGE_LIMIT_MIN,
    CONF_NOTIFY_TEMP_CHANGE_MESSAGE,
    CONF_PRESENCE_BOOST_ENABLED,
    CONF_PRESENCE_BOOST_MIN,
    CONF_PRESENCE_BOOST_OFFSET,
    CONF_PRESENCE_SENSOR,
    CONF_QUIET_ENABLED,
    CONF_QUIET_END_TIME,
    CONF_QUIET_NOTIFY,
    CONF_QUIET_START_TIME,
    CONF_QUIET_TTS,
    CONF_RANGE_OFFSET,
    CONF_SOC_MIN,
    CONF_TARGET_TEMP_DEFAULT,
    CONF_TEMP_DELTA,
    CONF_TEMP_SENSOR,
    CONF_TTS_ENGINE,
    CONF_TTS_MESSAGE_OPEN,
    CONF_TTS_PLAYERS,
    CONF_TURN_ON_OFFSET,
    CONF_UPDATE_INTERVAL_MIN,
    CONF_WINDOW_DELAY_MIN,
    CONF_WINDOW_SENSOR,
    CONF_WINDOW_DETECTION_ENABLED,
    DEFAULT_WINDOW_DETECTION_ENABLED,
    DEFAULT_BELOW_OFFSET,
    DEFAULT_CALIBRATION_MAX_OFFSET,
    DEFAULT_DOOR_ALERT_ENABLED,
    DEFAULT_DOOR_ALERT_MESSAGE,
    DEFAULT_DOOR_ALERT_NOTIFY,
    DEFAULT_DOOR_ALERT_TTS,
    DEFAULT_EXTREME_DELTA,
    DEFAULT_EXTREME_OFFSET,
    DEFAULT_FV_END_TIME,
    DEFAULT_FV_MARGIN_W,
    DEFAULT_FV_PRIORITY,
    DEFAULT_FV_SHUTOFF_DELAY_MIN,
    DEFAULT_FV_SHUTOFF_ENABLED,
    DEFAULT_FV_SHUTOFF_MANUAL,
    DEFAULT_FV_SHUTOFF_MANUAL_DELAY_MIN,
    DEFAULT_FV_SHUTOFF_EXTRA_HOURS,
    DEFAULT_FV_SHUTOFF_THRESHOLD,
    DEFAULT_FV_STAGGER_MIN,
    DEFAULT_FV_START_TIME,
    DEFAULT_HOT_OFFSET,
    DEFAULT_MIN_BELOW_INTERNAL,
    DEFAULT_NAME,
    DEFAULT_NIGHT_AC_ENABLED,
    DEFAULT_NIGHT_END_TIME,
    DEFAULT_NIGHT_END_SHUTOFF_AUTO_ONLY,
    DEFAULT_NIGHT_END_SHUTOFF_ENABLED,
    DEFAULT_NIGHT_OFFSET,
    DEFAULT_NIGHT_SHUTOFF_DELTA,
    DEFAULT_NIGHT_SHUTOFF_ENABLED,
    DEFAULT_NIGHT_SHUTOFF_MIN,
    DEFAULT_NIGHT_START_TIME,
    DEFAULT_NIGHT_TURN_ON_OFFSET,
    DEFAULT_DOOR_ALERT_CLOSED_MESSAGE,
    DEFAULT_DOOR_ALERT_OPEN_MESSAGE,
    DEFAULT_NOTIFY_MESSAGE_CLOSED,
    DEFAULT_NOTIFY_MESSAGE_OPEN,
    DEFAULT_NOTIFY_NIGHT_END_NOTIFY,
    DEFAULT_NOTIFY_NIGHT_END_TTS,
    DEFAULT_NOTIFY_POWER_NOTIFY,
    DEFAULT_NOTIFY_POWER_TTS,
    DEFAULT_NOTIFY_TEMP_CHANGE_ENABLED,
    DEFAULT_NOTIFY_TEMP_CHANGE_LIMIT_ENABLED,
    DEFAULT_NOTIFY_TEMP_CHANGE_LIMIT_MIN,
    DEFAULT_NOTIFY_TEMP_CHANGE_MESSAGE,
    DEFAULT_POWER_OFF_FV_MESSAGE,
    DEFAULT_POWER_OFF_NIGHT_END_MESSAGE,
    DEFAULT_POWER_OFF_NIGHT_MESSAGE,
    DEFAULT_POWER_ON_FV_MESSAGE,
    DEFAULT_POWER_ON_NIGHT_MESSAGE,
    DEFAULT_PRESENCE_BOOST_ENABLED,
    DEFAULT_PRESENCE_BOOST_MIN,
    DEFAULT_PRESENCE_BOOST_OFFSET,
    DEFAULT_QUIET_ENABLED,
    DEFAULT_QUIET_END_TIME,
    DEFAULT_QUIET_NOTIFY,
    DEFAULT_QUIET_START_TIME,
    DEFAULT_QUIET_TTS,
    DEFAULT_RANGE_OFFSET,
    DEFAULT_SOC_MIN,
    DEFAULT_TARGET_TEMP,
    DEFAULT_TEMP_DELTA,
    DEFAULT_TTS_MESSAGE_CLOSED,
    DEFAULT_TTS_MESSAGE_OPEN,
    DEFAULT_TURN_ON_OFFSET,
    DEFAULT_UPDATE_INTERVAL_MIN,
    DEFAULT_WINDOW_DELAY_MIN,
    DOMAIN,
    FAN_MODES_ALLOWED,
    REASON_FV,
    REASON_FV_SHUTOFF,
    REASON_NIGHT,
    REASON_NIGHT_END,
    REASON_NIGHT_SHUTOFF,
    SWITCH_KEY_FV,
    SWITCH_KEY_MASTER,
    SWITCH_KEY_QUICK,
)
from .const import (
    CONF_CONFIG_MODE,
    CONF_EMERGENCY_HEAT_END_THRESHOLD,
    CONF_EMERGENCY_HEAT_THRESHOLD,
    CONF_EMERGENCY_MSG_OFF,
    CONF_EMERGENCY_MSG_ON,
    CONF_EMERGENCY_NOTIFY_TELEGRAM,
    CONF_EMERGENCY_NOTIFY_TTS,
    CONF_POWER_LIMIT_ENABLED,
    CONF_POWER_LIMIT_HYSTERESIS_W,
    CONF_POWER_LIMIT_MAX_W,
    CONF_POWER_LIMIT_MODE,
    CONF_POWER_LIMIT_MSG_OFF,
    CONF_POWER_LIMIT_MSG_ON,
    CONF_POWER_LIMIT_NOTIFY_TELEGRAM,
    CONF_POWER_LIMIT_NOTIFY_TTS,
    CONF_POWER_LIMIT_RESTORE_MIN,
    CONF_POWER_LIMIT_SENSOR,
    CONF_SIMPLE_NIGHT_END,
    CONF_SIMPLE_NIGHT_START,
    CONF_SIMPLE_SUNSET_ANTICIPATE_H,
    CONF_SIMPLE_NOTIFY_TEL_AC_OFF,
    CONF_SIMPLE_NOTIFY_TEL_AC_ON,
    CONF_SIMPLE_NOTIFY_TEL_DOOR_CLOSE,
    CONF_SIMPLE_NOTIFY_TEL_DOOR_OPEN,
    CONF_SIMPLE_NOTIFY_TEL_NIGHT_END,
    CONF_SIMPLE_NOTIFY_TEL_NIGHT_START,
    CONF_SIMPLE_NOTIFY_TEL_TEMP_CHANGE,
    CONF_SIMPLE_NOTIFY_TEL_WINDOW_CLOSE,
    CONF_SIMPLE_NOTIFY_TEL_WINDOW_OPEN,
    CONF_SIMPLE_NOTIFY_TTS_AC_OFF,
    CONF_SIMPLE_NOTIFY_TTS_AC_ON,
    CONF_SIMPLE_NOTIFY_TTS_DOOR_CLOSE,
    CONF_SIMPLE_NOTIFY_TTS_DOOR_OPEN,
    CONF_SIMPLE_NOTIFY_TTS_NIGHT_END,
    CONF_SIMPLE_NOTIFY_TTS_NIGHT_START,
    CONF_SIMPLE_NOTIFY_TTS_TEMP_CHANGE,
    CONF_SIMPLE_NOTIFY_TTS_WINDOW_CLOSE,
    CONF_SIMPLE_NOTIFY_TTS_WINDOW_OPEN,
    CONF_SIMPLE_QUIET_NIGHT_NOTIFY,
    CONF_SIMPLE_QUIET_NIGHT_TTS,
    CONF_SIMPLE_TARGET_DAY,
    CONF_SIMPLE_TARGET_NIGHT,
    CONF_SIMPLE_DRY_ENABLED,
    CONF_SIMPLE_DRY_MAX_MIN,
    CONF_SIMPLE_NO_AUTO_ON_NIGHT,
    CONF_SIMPLE_NO_REON_MANUAL_OFF,
    CONF_FV_SHUTOFF_TOTAL_MINUTES,
    DEFAULT_FV_SHUTOFF_TOTAL_MINUTES,
    CONF_FV_TURN_ON_TOTAL_MINUTES,
    DEFAULT_FV_TURN_ON_TOTAL_MINUTES,
    CONF_FV_SENSOR_OFFLINE_SHUTOFF_ENABLED,
    DEFAULT_FV_SENSOR_OFFLINE_SHUTOFF_ENABLED,
    CONF_FV_SENSOR_OFFLINE_SHUTOFF_MIN,
    DEFAULT_FV_SENSOR_OFFLINE_SHUTOFF_MIN,
    CONF_FV_SENSOR_OFFLINE_NOTIFY_TTS,
    DEFAULT_FV_SENSOR_OFFLINE_NOTIFY_TTS,
    CONF_FV_SENSOR_OFFLINE_NOTIFY_TELEGRAM,
    DEFAULT_FV_SENSOR_OFFLINE_NOTIFY_TELEGRAM,
    CONF_SIMPLE_NO_REON_MANUAL_OFF_HOURS,
    DEFAULT_SIMPLE_NO_REON_MANUAL_OFF,
    DEFAULT_SIMPLE_NO_REON_MANUAL_OFF_HOURS,
    CONF_SIMPLE_TURN_ON_OFFSET,
    CONF_SIMPLE_SHUTOFF_MARGIN,
    CONF_SIMPLE_ECO_DAY_ENABLED,
    CONF_SIMPLE_ECO_NIGHT_ENABLED,
    DEFAULT_SIMPLE_ECO_DAY_ENABLED,
    DEFAULT_SIMPLE_ECO_NIGHT_ENABLED,
    CONF_MANUAL_SHUTOFF_TIMER_MIN,
    CONF_MANUAL_SHUTOFF_TIMER_ENABLED,
    DEFAULT_MANUAL_SHUTOFF_TIMER_ENABLED,
    CONF_SEASON_MODE,
    INSTABILITY_GRACE_PERIOD_SECONDS,
    STATE_CHANGE_DEBOUNCE_SECONDS,
    CONF_SIMPLE_NOTIFY_TTS_MANUAL_ON,
    CONF_SIMPLE_NOTIFY_TEL_MANUAL_ON,
    CONF_SIMPLE_NOTIFY_TTS_MANUAL_OFF,
    CONF_SIMPLE_NOTIFY_TEL_MANUAL_OFF,
    DEFAULT_SIMPLE_NOTIFY_TTS_MANUAL_ON,
    DEFAULT_SIMPLE_NOTIFY_TEL_MANUAL_ON,
    DEFAULT_SIMPLE_NOTIFY_TTS_MANUAL_OFF,
    DEFAULT_SIMPLE_NOTIFY_TEL_MANUAL_OFF,
    DEFAULT_SIMPLE_MSG_MANUAL_ON,
    DEFAULT_SIMPLE_MSG_MANUAL_OFF,
    DEFAULT_SIMPLE_MSG_AC_OFF_TIMER,
    SEASON_SUMMER,
    SEASON_WINTER,
    SEASON_AUTO,
    SEASON_MANUAL,
    SEASON_OFF,
    DEFAULT_SEASON_MODE,
    CONF_WINTER_TARGET_DAY,
    CONF_WINTER_TARGET_NIGHT,
    CONF_WINTER_TURN_ON_OFFSET,
    CONF_WINTER_SHUTOFF_MARGIN,
    CONF_WINTER_SOC_MIN,
    CONF_WINTER_FLOOR_SENSOR,
    DEFAULT_WINTER_TARGET_DAY,
    DEFAULT_WINTER_TARGET_NIGHT,
    DEFAULT_WINTER_TURN_ON_OFFSET,
    DEFAULT_WINTER_SHUTOFF_MARGIN,
    DEFAULT_WINTER_SOC_MIN,
    CONF_EMERGENCY_WINTER_HEAT_THRESHOLD,
    CONF_EMERGENCY_WINTER_HEAT_END_THRESHOLD,
    DEFAULT_EMERGENCY_WINTER_HEAT_THRESHOLD,
    DEFAULT_EMERGENCY_WINTER_HEAT_END_THRESHOLD,
    DEFAULT_SIMPLE_MSG_AC_ON_WINTER,
    DEFAULT_SIMPLE_MSG_AC_ON_WINTER_FLOOR,
    SEASON_AUTO_SWITCH_COOLDOWN_HOURS,
    DEFAULT_MANUAL_SHUTOFF_TIMER_MIN,
    DEFAULT_SIMPLE_SHUTOFF_MARGIN,
    CONF_SIMPLE_EXTERNAL_SENSOR_STALE_MIN,
    DEFAULT_SIMPLE_EXTERNAL_SENSOR_STALE_MIN,
    CONFIG_MODE_FULL,
    CONFIG_MODE_SIMPLE,
    DEFAULT_EMERGENCY_HEAT_END_THRESHOLD,
    DEFAULT_EMERGENCY_HEAT_THRESHOLD,
    DEFAULT_EMERGENCY_MSG_OFF,
    DEFAULT_EMERGENCY_MSG_ON,
    DEFAULT_EMERGENCY_WINTER_MSG_ON,
    DEFAULT_EMERGENCY_WINTER_MSG_OFF,
    DEFAULT_EMERGENCY_NOTIFY_TELEGRAM,
    DEFAULT_EMERGENCY_NOTIFY_TTS,
    DEFAULT_POWER_LIMIT_ENABLED,
    DEFAULT_POWER_LIMIT_HYSTERESIS_W,
    DEFAULT_POWER_LIMIT_MAX_W,
    DEFAULT_POWER_LIMIT_MODE,
    DEFAULT_POWER_LIMIT_MSG_OFF,
    DEFAULT_POWER_LIMIT_MSG_ON,
    DEFAULT_POWER_LIMIT_NOTIFY_TELEGRAM,
    DEFAULT_POWER_LIMIT_NOTIFY_TTS,
    DEFAULT_POWER_LIMIT_RESTORE_MIN,
    EMERGENCY_PRE_NIGHT_MIN,
    EMERGENCY_PRE_NIGHT_MIN,
    POWER_LIMIT_MODE_MULTI,
    SWITCH_KEY_EMERGENCY,
    POWER_LIMIT_MODE_SINGLE,
    POWER_LIMIT_RESTORE_STAGGER_MIN,
    POWER_LIMIT_SPIKE_SEC,
    CONFIG_MODE_SIMPLE_FV,
    DEFAULT_SIMPLE_DRY_ENABLED,
    DEFAULT_SIMPLE_DRY_MAX_MIN,
    DEFAULT_SIMPLE_NO_AUTO_ON_NIGHT,
    DEFAULT_SIMPLE_TURN_ON_OFFSET_EXT,
    DEFAULT_SIMPLE_TURN_ON_OFFSET_INT,
    DEFAULT_SIMPLE_TURN_ON_OFFSET_EXT,
    DEFAULT_SIMPLE_TURN_ON_OFFSET_INT,
    DEFAULT_SIMPLE_MSG_AC_OFF,
    DEFAULT_SIMPLE_MSG_AC_OFF_FV,
    DEFAULT_SIMPLE_MSG_AC_ON,
    DEFAULT_SIMPLE_MSG_AC_ON_FV,
    DEFAULT_SIMPLE_MSG_AC_ON_NIGHT,
    DEFAULT_SIMPLE_MSG_AC_ON_EMERGENCY,
    DEFAULT_SIMPLE_MSG_DOOR_CLOSE,
    DEFAULT_SIMPLE_MSG_DOOR_OPEN,
    DEFAULT_SIMPLE_MSG_NIGHT_END,
    DEFAULT_SIMPLE_MSG_NIGHT_START,
    DEFAULT_SIMPLE_MSG_WINDOW_CLOSE,
    DEFAULT_SIMPLE_MSG_WINDOW_OPEN,
    DEFAULT_SIMPLE_MSG_WINDOW_SHUTOFF,
    DEFAULT_SIMPLE_NIGHT_END,
    DEFAULT_SIMPLE_NIGHT_START,
    DEFAULT_SIMPLE_SUNSET_ANTICIPATE_H,
    DEFAULT_SIMPLE_MSG_TEMP_CHANGE,
    DEFAULT_SIMPLE_NOTIFY_TEL_AC_OFF,
    DEFAULT_SIMPLE_NOTIFY_TEL_AC_ON,
    DEFAULT_SIMPLE_NOTIFY_TEL_DOOR_CLOSE,
    DEFAULT_SIMPLE_NOTIFY_TEL_DOOR_OPEN,
    DEFAULT_SIMPLE_NOTIFY_TEL_NIGHT_END,
    DEFAULT_SIMPLE_NOTIFY_TEL_NIGHT_START,
    DEFAULT_SIMPLE_NOTIFY_TEL_TEMP_CHANGE,
    DEFAULT_SIMPLE_NOTIFY_TEL_WINDOW_CLOSE,
    DEFAULT_SIMPLE_NOTIFY_TEL_WINDOW_OPEN,
    DEFAULT_SIMPLE_NOTIFY_TTS_AC_OFF,
    DEFAULT_SIMPLE_NOTIFY_TTS_AC_ON,
    DEFAULT_SIMPLE_NOTIFY_TTS_DOOR_CLOSE,
    DEFAULT_SIMPLE_NOTIFY_TTS_DOOR_OPEN,
    DEFAULT_SIMPLE_NOTIFY_TTS_NIGHT_END,
    DEFAULT_SIMPLE_NOTIFY_TTS_NIGHT_START,
    DEFAULT_SIMPLE_NOTIFY_TTS_TEMP_CHANGE,
    DEFAULT_SIMPLE_NOTIFY_TTS_WINDOW_CLOSE,
    DEFAULT_SIMPLE_NOTIFY_TTS_WINDOW_OPEN,
    DEFAULT_SIMPLE_QUIET_NIGHT_NOTIFY,
    DEFAULT_SIMPLE_QUIET_NIGHT_TTS,
    DEFAULT_SIMPLE_TARGET_DAY,
    DEFAULT_SIMPLE_TARGET_NIGHT,
    SIMPLE_EXT_DRY_HIGH,
    SIMPLE_EXT_DRY_LOW,
    SIMPLE_EXT_HOT_OFFSET,
    SIMPLE_NIGHT_END_LIMBO_H,
    SIMPLE_EXT_MILD_OFFSET,
    SIMPLE_EXT_SETPOINT_HOT,
    SIMPLE_EXT_SETPOINT_MILD,
    SIMPLE_EXT_SHUTOFF_MIN,
    SIMPLE_EXT_SHUTOFF_OFFSET,
    SIMPLE_EXT_SLOW_OFFSET,
    SIMPLE_EXT_WARM_OFFSET,
    SIMPLE_INT_DRY_HIGH,
    SIMPLE_INT_DRY_LOW,
    SIMPLE_INT_AT_TARGET,
    SIMPLE_INT_HOT_OFFSET,
    SIMPLE_INT_SETPOINT_HOT,
    SIMPLE_INT_SETPOINT_MILD,
    SIMPLE_INT_SHUTOFF_MIN,
    SIMPLE_INT_SHUTOFF_OFFSET,
    SIMPLE_INT_WARM_OFFSET,
    SIMPLE_WINDOW_DELAY_MIN,
)
from .util import get_conf

_LOGGER = logging.getLogger(__name__)

FV_SHUTOFF_SAMPLES_FIXED = 4  # campioni fissi per la sliding window di spegnimento FV (modo semplificato)

# Stati considerati "non validi" per le transizioni sensori
_INVALID_STATES = {"unknown", "unavailable"}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([SmartFvClimate(hass, entry)])


class SmartFvClimate(ClimateEntity, RestoreEntity):
    """Termostato intelligente FV con avvisi accensione/spegnimento e fascia silenzio."""

    _attr_should_poll = False
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.COOL, HVACMode.DRY]
    _attr_fan_modes = FAN_MODES_ALLOWED
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self._attr_unique_id = entry.entry_id
        self._attr_name = get_conf(entry, CONF_NAME, DEFAULT_NAME)

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=get_conf(entry, CONF_NAME, DEFAULT_NAME),
            manufacturer="Termostato Intelligente FV",
            model="Termostato Intelligente",
        )
        self._climate_entity: str = get_conf(entry, CONF_CLIMATE_ENTITY)
        self._temp_sensor: str = get_conf(entry, CONF_TEMP_SENSOR)
        self._window_sensor: str | None = get_conf(entry, CONF_WINDOW_SENSOR)
        self._presence_sensor: str | None = get_conf(entry, CONF_PRESENCE_SENSOR)
        self._door_sensor: str | None = get_conf(entry, CONF_DOOR_SENSOR)
        self._fv_sensor: str | None = get_conf(entry, CONF_FV_SENSOR)
        self._consumption_sensor: str | None = get_conf(entry, CONF_CONSUMPTION_SENSOR)
        self._battery_sensor: str | None = get_conf(entry, CONF_BATTERY_SENSOR)
        self._target_temperature: float = float(
            get_conf(entry, CONF_TARGET_TEMP_DEFAULT, DEFAULT_TARGET_TEMP)
        )
        self._snapshot: dict[str, Any] | None = None
        self._window_cancel_timer = None
        self._shutoff_timer_cancel = None  # funzione per annullare il timer di spegnimento manuale (card), se attivo
        self._shutoff_timer_until: datetime | None = None  # quando scatterà lo spegnimento, per mostrarlo alla card
        self._shutoff_timer_remaining_seconds_paused: float | None = None  # secondi rimanenti quando il timer è stato messo in pausa (spegnimento per limite potenza), None se non in pausa
        # Timer manuale: card e configurazione sono UNA SOLA fonte di
        # verità (stesso principio già applicato a priorità e target) —
        # niente più override permanente che ignora la configurazione.
        self._pending_timer_enabled_display: bool | None = None
        self._pending_timer_minutes_display: float | None = None
        self._state_change_debounce_cancel = None  # funzione per annullare la conferma pendente di una transizione spento<->acceso del clima reale
        self._state_change_debounce_original_old: State | None = None  # stato di riferimento da PRIMA dell'intero episodio di instabilità (non aggiornato ad ogni evento intermedio)
        self._last_real_unavailable_at: datetime | None = None  # ultima volta che l'entità reale è stata vista unavailable/unknown — usato per estendere la protezione contro rilevamenti falsi oltre il semplice tempo fisso dal riavvio, adattandosi a QUALSIASI durata di instabilità (non solo al boot)
        self._eco_mode_active: bool = False  # True se siamo nella fascia "Eco" (tra target-scarto e target+scarto) invece che spenti o in raffreddamento attivo
        self._presence_since: datetime | None = None
        self._last_sent_setpoint: float | None = None  # ultimo setpoint che ABBIAMO inviato noi (modo semplice) — evita notifiche/comandi ripetuti per instabilità di lettura dal climatizzatore reale
        self._last_sent_setpoint_at: datetime | None = None  # quando lo abbiamo inviato (diagnostica)
        self._last_sent_fan: str | None = None  # ultima velocità ventola che ABBIAMO inviato noi — stesso principio del setpoint, evita comandi/beep ripetuti
        # Priorità e target giorno/notte: card e configurazione sono UNA
        # SOLA fonte di verità (niente più override separati). Il valore
        # "pending" serve SOLO per il feedback istantaneo della card nella
        # breve finestra di debounce, prima che la scrittura in
        # configurazione (con successivo reload) la renda definitiva.
        self._pending_priority_display: float | None = None
        self._pending_target_day_display: float | None = None
        self._pending_target_night_display: float | None = None
        self._config_write_debounce_cancel: dict[str, Any] = {}
        self._external_sensor_fallback_active: bool = False  # True se stiamo usando la sonda interna perché quella esterna è bloccata
        self._external_sensor_last_value: float | None = None  # ultimo valore letto dalla sonda esterna mentre era considerata viva — usato come controllo extra di ripristino
        self._pending_probe_notification: str | None = None  # evento fallback/ripristino sonda da notificare al prossimo ciclo asincrono ("triggered" o "recovered")

        # --- Sliding window FV shutoff ---
        self._fv_surplus_buffer: list[float] = []

        self._night_below_since: datetime | None = None

        # --- Fine modalità notturna ---
        # Traccia se eravamo in modalità notte al ciclo precedente
        # (per rilevare la transizione notte→giorno)
        self._was_night_mode: bool = False
        # Traccia se il clima è stato acceso automaticamente dalla modalità notturna
        self._night_auto_on: bool = False

        # --- Limite notifiche cambio temperatura ---
        self._last_temp_notify: datetime | None = None

        # --- Protezione potenza ---
        self._power_limit_high_since: datetime | None = None  # da quando il consumo è sopra soglia
        self._power_limit_off: bool = False                    # True se spento per power limit
        self._power_limit_off_at: datetime | None = None       # quando è stato spento
        self._power_limit_low_since: datetime | None = None    # da quando il consumo è sotto soglia-isteresi

        # --- Emergenza caldo ---
        self._emergency_notified: bool = False  # evita notifiche doppie

        # --- Modo semplificato ---
        self._simple_shutoff_since: datetime | None = None  # timer spegnimento per target raggiunto
        self._simple_was_night: bool = False                 # per rilevare transizione notte→giorno
        self._simple_night_auto_on: bool = False             # acceso automaticamente di notte
        self._simple_dry_since: datetime | None = None       # da quando è in modalità dry (diagnostica)
        self._simple_dry_end: datetime | None = None         # timestamp UTC di fine DRY (assoluto)
        self._programmatic_off_until: datetime | None = None  # finestra di tolleranza per distinguere spegnimento nostro da manuale
        self._manual_off_since: datetime | None = None        # da quando è stato spento manualmente (se rilevato)
        self._fv_low_since: datetime | None = None             # da quando il surplus FV è insufficiente in modo continuativo (diagnostica)
        self._fv_turnon_confirmed_since: datetime | None = None  # da quando le condizioni di accensione FV sono continuativamente favorevoli — evita riaccensioni troppo rapide dopo un proprio spegnimento
        self._manual_accension_since: datetime | None = None  # da quando è stato acceso manualmente (non da FV né da notte) — usato per ignorare lo spegnimento FV per un periodo fisso
        self._last_notify_event: dict | None = None             # ultima notifica Telegram inviata (diagnostica)
        self._notify_history: list = []                          # ultime 8 notifiche, per lo storico espandibile nella card
        self._dry_cancel_timer: callable | None = None       # cancel function async_track_point_in_time
        self._door_debounce_cancel = None                          # timer debounce porta
        self._fv_auto_on: bool = False                       # acceso automaticamente dal FV

        hass.data.setdefault(DOMAIN, {}).setdefault(entry.entry_id, {})["climate"] = self

    # ------------------------------------------------------------------
    # Proprietà
    # ------------------------------------------------------------------

    @property
    def current_temperature(self) -> float | None:
        if self._get_config_mode() in (CONFIG_MODE_SIMPLE, CONFIG_MODE_SIMPLE_FV):
            # Deve sempre corrispondere a quello che le decisioni interne
            # usano davvero (_simple_read_temp), fallback su sonda interna
            # incluso — altrimenti il grafico/dashboard mostrerebbe un
            # valore diverso da quello che ha realmente guidato accensioni
            # e regolazioni, generando confusione (es. un'accensione che
            # sembra scattare "prima del previsto" guardando lo storico).
            return self._simple_read_temp()
        return self._read_float(self._temp_sensor)

    @property
    def target_temperature(self) -> float:
        if self._get_config_mode() in (CONFIG_MODE_SIMPLE, CONFIG_MODE_SIMPLE_FV):
            # Nel modo Semplice il target reale usato dalla regolazione è
            # sempre quello calcolato da _simple_current_target() (giorno o
            # notte in base all'orario) — mostriamo sempre questo valore,
            # così l'interfaccia resta coerente con la configurazione anche
            # subito dopo averla modificata, senza dover riavviare.
            return self._simple_current_target()
        return self._target_temperature

    def _is_unmanaged_real_mode(self) -> bool:
        """True se il climatizzatore reale è in una modalità che questa
        integrazione non gestisce attivamente (riscaldamento, sola
        ventilazione, auto...) — impostata da fuori (telecomando, app
        ufficiale, altra automazione), mai da noi, dato che dichiariamo
        solo off/cool/dry come modalità supportate.

        Fondamentale per evitare che la regolazione automatica (pensata
        solo per raffreddamento/deumidificazione) applichi formule di
        raffreddamento a un dispositivo che in realtà sta riscaldando.
        """
        state = self.hass.states.get(self._climate_entity)
        if state is None:
            return False
        return state.state not in ("off", "cool", "dry", "unknown", "unavailable")

    @property
    def hvac_mode(self) -> HVACMode:
        state = self.hass.states.get(self._climate_entity)
        if state is None or state.state in ("unknown", "unavailable", "off"):
            return HVACMode.OFF
        if state.state == "dry":
            return HVACMode.DRY
        # Nota: se il dispositivo reale è in una modalità non gestita
        # (riscaldamento, ventilazione, auto...) continuiamo a riportare
        # COOL a Home Assistant per vincolo tecnico (dichiariamo solo
        # off/cool/dry come hvac_modes supportati) — ma _is_unmanaged_real_mode()
        # impedisce alla logica di regolazione di agire in quel caso, vedi
        # l'attributo diagnostico "modalita_esterna_non_gestita".
        return HVACMode.COOL

    @property
    def fan_mode(self) -> str | None:
        state = self.hass.states.get(self._climate_entity)
        if state is None:
            return None
        return state.attributes.get("fan_mode")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "finestra_aperta": self._is_window_open(),
            "porta_aperta": self._is_door_open(),
            "finestra_entity_id": self._window_sensor,
            "porta_entity_id": self._door_sensor,
            "snapshot_attivo": self._snapshot is not None,
            "presenza_da": self._presence_since.isoformat() if self._presence_since else None,
            "climatizzatore_reale": self._climate_entity,
            "termostato_abilitato": self._switch_state(SWITCH_KEY_MASTER, True),
            "master_switch_entity_id": self._switch_entity_id(SWITCH_KEY_MASTER),
            "timer_spegnimento_fino_a": self._shutoff_timer_until.isoformat() if self._shutoff_timer_until else None,
            "timer_manuale_attivo": self._manual_shutoff_timer_enabled(),
            "timer_manuale_minuti_configurati": self._manual_shutoff_timer_minutes(),
            "accensione_fv_abilitata": self._switch_state(SWITCH_KEY_FV, True),
            "acceso_da_fv": self._fv_auto_on,
            "modalita_eco_attiva": self._eco_mode_active,
            "timer_manuale_in_pausa_da": self._shutoff_timer_remaining_seconds_paused is not None,
            "auto_ultima_direzione": getattr(self, "_auto_last_hvac_direction", None),
            "auto_ultima_direzione_da": self._auto_last_hvac_direction_at.isoformat() if getattr(self, "_auto_last_hvac_direction_at", None) else None,
            "raffreddamento_rapido": self._switch_state(SWITCH_KEY_QUICK, False),
            "modalita_notturna_attiva": self._is_night_mode_active(),
            "target_effettivo": (
                self._simple_current_target()
                if self._get_config_mode() in (CONFIG_MODE_SIMPLE, CONFIG_MODE_SIMPLE_FV)
                else self._effective_target()
            ),
            "accensione_notturna_abilitata": (
                not bool(get_conf(self.entry, CONF_SIMPLE_NO_AUTO_ON_NIGHT, DEFAULT_SIMPLE_NO_AUTO_ON_NIGHT))
                if self._get_config_mode() in (CONFIG_MODE_SIMPLE, CONFIG_MODE_SIMPLE_FV)
                else bool(get_conf(self.entry, CONF_NIGHT_AC_ENABLED, DEFAULT_NIGHT_AC_ENABLED))
            ),
            "spegnimento_fv_abilitato": bool(
                get_conf(self.entry, CONF_FV_SHUTOFF_ENABLED, DEFAULT_FV_SHUTOFF_ENABLED)
            ),
            "spegnimento_notturno_abilitato": bool(
                get_conf(self.entry, CONF_NIGHT_SHUTOFF_ENABLED, DEFAULT_NIGHT_SHUTOFF_ENABLED)
            ),
            "spegnimento_fine_notte_abilitato": bool(
                get_conf(self.entry, CONF_NIGHT_END_SHUTOFF_ENABLED, DEFAULT_NIGHT_END_SHUTOFF_ENABLED)
            ),
            "accensione_notturna_automatica": (
                self._simple_night_auto_on
                if self._get_config_mode() in (CONFIG_MODE_SIMPLE, CONFIG_MODE_SIMPLE_FV)
                else self._night_auto_on
            ),
            "fv_surplus_buffer": self._fv_surplus_buffer,
            "notte_sotto_target_da": self._night_below_since.isoformat() if self._night_below_since else None,
            "fascia_silenzio_attiva": (
                self._simple_is_quiet_night()
                if self._get_config_mode() in (CONFIG_MODE_SIMPLE, CONFIG_MODE_SIMPLE_FV)
                else self._is_quiet_time()
            ),
            # --- diagnostica DRY (rilevante solo per modo Semplice/Semplice+FV) ---
            "dry_since": self._simple_dry_since.isoformat() if self._simple_dry_since else None,
            "dry_end": self._simple_dry_end.isoformat() if self._simple_dry_end else None,
            "dry_elapsed_min": round((dt_util.utcnow() - self._simple_dry_since).total_seconds() / 60, 1) if self._simple_dry_since else None,
            "spento_manualmente_da": self._manual_off_since.isoformat() if self._manual_off_since else None,
            "blocco_riaccensione_attivo": self._is_manual_off_block_active(),
            "soglia_accensione_fv": round(
                (self.target_temperature or 0) + float(
                    get_conf(self.entry, CONF_TURN_ON_OFFSET, DEFAULT_TURN_ON_OFFSET)
                    if self._get_config_mode() not in (CONFIG_MODE_SIMPLE, CONFIG_MODE_SIMPLE_FV)
                    else get_conf(
                        self.entry, CONF_SIMPLE_TURN_ON_OFFSET,
                        DEFAULT_SIMPLE_TURN_ON_OFFSET_INT if not self._temp_sensor else DEFAULT_SIMPLE_TURN_ON_OFFSET_EXT,
                    )
                ), 1,
            ),
            "fv_basso_da": self._fv_low_since.isoformat() if self._fv_low_since else None,
            "acceso_manualmente_da": self._manual_accension_since.isoformat() if self._manual_accension_since else None,
            "sonda_esterna_bloccata": self._external_sensor_fallback_active,
            "modalita_esterna_non_gestita": self._is_unmanaged_real_mode(),
            "ultimo_evento_notifica": self._last_notify_event,
            "storico_notifiche": self._notify_history,
            "sonda_esterna_entity_id": self._temp_sensor,
            # --- diagnostica specifica del modo Completo ---
            "modalita_configurazione": self._get_config_mode(),
            "modalita_stagionale": self._get_season_mode(),
            "fv_priorita": self._effective_priority(),
            "protezione_potenza_attiva": self._power_limit_off,
            "protezione_potenza_da": self._power_limit_off_at.isoformat() if self._power_limit_off_at else None,
            "emergenza_caldo_attiva": self._switch_state(SWITCH_KEY_EMERGENCY, False),
        }

    # ------------------------------------------------------------------
    # Ciclo di vita
    # ------------------------------------------------------------------

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()

        # Timestamp di avvio — usato per un breve periodo di grazia subito
        # dopo il riavvio, durante il quale NON rileviamo accensioni
        # manuali: l'integrazione del climatizzatore reale (Gree e simili)
        # può attraversare transizioni transitorie (es. off -> cool) mentre
        # si riconnette, che altrimenti verrebbero scambiate per una vera
        # accensione manuale fatta dall'utente — esattamente il bug
        # osservato: climi accesi dal FV prima del riavvio, rilevati come
        # "accesi manualmente" subito dopo.
        # Trattiamo il momento in cui l'entità viene aggiunta (avvio o
        # reload) come un istante di "instabilità presunta" — usa LO STESSO
        # meccanismo della verifica unavailable/unknown, invece di un
        # secondo sistema a tempo fisso separato: quasi ogni integrazione
        # reale passa per uno stato instabile durante la propria
        # riconnessione, quindi questo singolo meccanismo copre già il
        # caso del riavvio senza bisogno di un timer dedicato aggiuntivo.
        self._last_real_unavailable_at = dt_util.utcnow()

        last_state = await self.async_get_last_state()

        # Ripristina il flag "acceso automaticamente di notte" dopo un
        # riavvio — senza questo, un riavvio durante la notte fa perdere
        # l'informazione e la logica di spegnimento FV può erroneamente
        # spegnere un clima acceso per la notte (non c'è produzione solare
        # di notte, quindi "FV insufficiente" sarebbe sempre vero).
        if last_state and last_state.attributes.get("accensione_notturna_automatica"):
            real_state = self.hass.states.get(self._climate_entity)
            if real_state and real_state.state not in ("off", "unknown", "unavailable") and self._simple_is_night():
                self._simple_night_auto_on = True
                _LOGGER.info(
                    "%s: riavvio durante la notte — ripristinato flag accensione notturna automatica",
                    self._attr_name,
                )

        # Ripristina il flag "acceso dal FV" dopo un reload/riavvio — senza
        # questo, un clima realmente acceso dal FV perderebbe silenziosamente
        # lo spegnimento automatico per surplus insufficiente dopo un
        # reload (es. causato dalla regolazione di priorità/target dalla
        # card), restando acceso "orfano" a tempo indeterminato.
        if last_state and last_state.attributes.get("acceso_da_fv"):
            real_state = self.hass.states.get(self._climate_entity)
            if real_state and real_state.state not in ("off", "unknown", "unavailable"):
                self._fv_auto_on = True
                _LOGGER.info(
                    "%s: ripristinato flag 'acceso dal FV' dopo reload/riavvio",
                    self._attr_name,
                )

        # Ripristina il timer manuale (scaldotto) con il tempo RIMANENTE
        # ricalcolato — senza questo, un reload (es. causato dalla
        # regolazione di priorità/target dalla card) durante un conto alla
        # rovescia attivo lo farebbe perdere, disallineando la card dallo
        # stato reale (il vecchio timer orfano scatterebbe comunque, ma
        # la card non lo mostrerebbe più).
        if last_state and last_state.attributes.get("timer_spegnimento_fino_a"):
            try:
                saved_until = dt_util.parse_datetime(last_state.attributes["timer_spegnimento_fino_a"])
            except (TypeError, ValueError):
                saved_until = None
            if saved_until is not None:
                remaining = saved_until - dt_util.utcnow()
                real_state = self.hass.states.get(self._climate_entity)
                is_on = real_state and real_state.state not in ("off", "unknown", "unavailable")
                if remaining > timedelta(seconds=0) and is_on:
                    self._shutoff_timer_until = saved_until
                    self._shutoff_timer_cancel = async_call_later(
                        self.hass, remaining, self._async_shutoff_timer_expired
                    )
                    _LOGGER.info(
                        "%s: ripristinato timer di spegnimento manuale dopo reload/riavvio (%.0f minuti rimanenti)",
                        self._attr_name, remaining.total_seconds() / 60,
                    )
                elif remaining <= timedelta(seconds=0) and is_on:
                    # Il timer sarebbe già scaduto nel frattempo (reload
                    # durato più a lungo del previsto) — spegniamo subito.
                    _LOGGER.info("%s: timer di spegnimento manuale scaduto durante il reload — spengo ora", self._attr_name)
                    self.hass.async_create_task(self._async_shutoff_timer_expired())

        # Ripristina il cooldown tra cambi di direzione in modo Auto — senza
        # questo, un reload durante le 20 ore di raffreddamento lo
        # azzererebbe, permettendo un cambio di direzione immediato e
        # vanificando la protezione contro i cicli ravvicinati nelle mezze
        # stagioni.
        if last_state and last_state.attributes.get("auto_ultima_direzione") and last_state.attributes.get("auto_ultima_direzione_da"):
            try:
                self._auto_last_hvac_direction = last_state.attributes["auto_ultima_direzione"]
                self._auto_last_hvac_direction_at = dt_util.parse_datetime(last_state.attributes["auto_ultima_direzione_da"])
            except (TypeError, ValueError):
                pass

        # Ripristina il timestamp di accensione manuale dopo un riavvio —
        # senza questo, un riavvio durante il periodo di immunità (spegni
        # anche se acceso manualmente + ritardo) fa perdere l'informazione
        # e il clima rischia di essere spento subito al riavvio, perdendo
        # la protezione residua a cui l'utente ha diritto.
        if last_state and last_state.attributes.get("acceso_manualmente_da"):
            real_state = self.hass.states.get(self._climate_entity)
            if real_state and real_state.state not in ("off", "unknown", "unavailable"):
                try:
                    self._manual_accension_since = dt_util.parse_datetime(last_state.attributes["acceso_manualmente_da"])
                    _LOGGER.info(
                        "%s: riavvio — ripristinato timestamp accensione manuale (%s)",
                        self._attr_name, self._manual_accension_since,
                    )
                except Exception as exc:
                    _LOGGER.warning("%s: errore ripristino acceso_manualmente_da: %s", self._attr_name, exc)

        # Ripristina lo stato Eco dopo un riavvio — senza questo, se
        # Home Assistant si riavvia mentre una stanza è in Eco, il codice
        # "dimentica" di esserlo mentre il dispositivo reale resta
        # fisicamente nel preset — incoerenza tra il nostro stato interno
        # e quello vero. Verifichiamo anche il preset reale attuale, non
        # solo l'attributo salvato, per evitare di ripristinare Eco se nel
        # frattempo qualcuno ha già cambiato preset manualmente.
        if last_state and last_state.attributes.get("modalita_eco_attiva"):
            real_state = self.hass.states.get(self._climate_entity)
            if real_state and real_state.attributes.get("preset_mode") == "eco":
                self._eco_mode_active = True
                _LOGGER.info("%s: riavvio — ripristinato stato Eco (preset reale ancora 'eco')", self._attr_name)

        # Ripristina il blocco riaccensione dopo uno spegnimento manuale
        # rilevato — senza questo, un riavvio durante il periodo di blocco
        # (es. 2 ore configurate) lo cancella del tutto, e la stanza
        # potrebbe essere riaccesa subito dal FV appena dopo il riavvio,
        # ignorando la volontà esplicita dell'utente di tenerla spenta.
        # Non serve verificare lo stato reale qui: _is_manual_off_block_active()
        # scade da sola il blocco se il tempo configurato è già passato.
        if last_state and last_state.attributes.get("spento_manualmente_da"):
            try:
                self._manual_off_since = dt_util.parse_datetime(last_state.attributes["spento_manualmente_da"])
                _LOGGER.info(
                    "%s: riavvio — ripristinato blocco riaccensione (spento manualmente da %s)",
                    self._attr_name, self._manual_off_since,
                )
            except Exception as exc:
                _LOGGER.warning("%s: errore ripristino spento_manualmente_da: %s", self._attr_name, exc)

        # Ripristina il flag "spento per limite potenza" — bassa gravità se
        # perso (il clima resta comunque spento, letto dallo stato reale ad
        # ogni ciclo), ma senza questo il sistema di ripristino automatico
        # specifico per il limite potenza non riconosce di aver spento lui
        # stesso la stanza, ritardando la ripresa fino a quando qualche
        # altro meccanismo (FV, notte) non interviene.
        if last_state and last_state.attributes.get("protezione_potenza_attiva"):
            real_state = self.hass.states.get(self._climate_entity)
            if real_state and real_state.state in ("off", "unknown", "unavailable"):
                self._power_limit_off = True
                power_limit_off_at_str = last_state.attributes.get("protezione_potenza_da")
                if power_limit_off_at_str:
                    try:
                        self._power_limit_off_at = dt_util.parse_datetime(power_limit_off_at_str)
                    except Exception:
                        pass
                _LOGGER.info("%s: riavvio — ripristinato flag limite potenza (clima ancora spento)", self._attr_name)

        # Priorità e target giorno/notte non hanno più bisogno di essere
        # ripristinati qui — sono sempre letti direttamente dalla
        # configurazione (vedi _effective_priority/_simple_current_target),
        # niente più override separati da sincronizzare dopo un riavvio.
        # Stesso principio applicato ora al timer manuale (minuti/attivo) —
        # niente più ripristino di override, il valore vero è sempre e solo
        # quello in configurazione.
        if last_state:
            try:
                saved_history = last_state.attributes.get("storico_notifiche")
                if isinstance(saved_history, list):
                    self._notify_history = saved_history[:8]
            except Exception as exc:
                _LOGGER.warning("%s: errore ripristino storico notifiche: %s", self._attr_name, exc)

        # Recupera dry_end dall'ultimo stato salvato (RestoreEntity).
        # Se il clima era in DRY prima del riavvio, rischeduliamo il timer
        # a partire dal timestamp assoluto salvato.
        if last_state and last_state.attributes.get("dry_end"):
            try:
                dry_end = dt_util.parse_datetime(last_state.attributes["dry_end"])
                if dry_end is not None:
                    real_state = self.hass.states.get(self._climate_entity)
                    if real_state and real_state.state == "dry":
                        dry_since_str = last_state.attributes.get("dry_since")
                        if dry_since_str:
                            try:
                                self._simple_dry_since = dt_util.parse_datetime(dry_since_str)
                            except Exception:
                                self._simple_dry_since = dt_util.utcnow()
                        self._simple_dry_end = dry_end
                        # async_track_point_in_time scatta alla data indicata; se è già
                        # nel passato scatta al prossimo tick dell'event loop — perfetto
                        # per gestire il caso "HA spento durante il countdown DRY".
                        self._dry_cancel_timer = async_track_point_in_time(
                            self.hass, self._async_dry_to_cool, dry_end
                        )
                        _LOGGER.info(
                            "%s: riavvio con DRY — timer ripristinato, scade alle %s",
                            self._attr_name, dry_end.isoformat(),
                        )
            except Exception as exc:
                _LOGGER.warning("%s: errore recupero dry_end dopo riavvio: %s", self._attr_name, exc)

        interval_min = int(get_conf(self.entry, CONF_UPDATE_INTERVAL_MIN, DEFAULT_UPDATE_INTERVAL_MIN))
        self.async_on_remove(
            async_track_time_interval(self.hass, self._async_periodic_update, timedelta(minutes=interval_min))
        )
        fv_total_minutes = float(get_conf(self.entry, CONF_FV_SHUTOFF_TOTAL_MINUTES, DEFAULT_FV_SHUTOFF_TOTAL_MINUTES))
        fv_check_interval_min = max(1.0, fv_total_minutes / FV_SHUTOFF_SAMPLES_FIXED)
        self.async_on_remove(
            async_track_time_interval(self.hass, self._async_periodic_fv_check, timedelta(minutes=fv_check_interval_min))
        )
        tracked = [e for e in (self._climate_entity, self._temp_sensor, self._window_sensor, self._presence_sensor, self._door_sensor) if e]
        if tracked:
            self.async_on_remove(async_track_state_change_event(self.hass, tracked, self._async_on_state_change))

    async def _async_on_state_change(self, event: Event) -> None:
        entity_id = event.data.get("entity_id")
        new_state: State | None = event.data.get("new_state")
        old_state: State | None = event.data.get("old_state")

        if entity_id == self._window_sensor:
            await self._async_handle_window(new_state, old_state)
        elif entity_id == self._door_sensor:
            await self._async_handle_door(new_state, old_state)
        elif entity_id == self._presence_sensor:
            if new_state and new_state.state == "on":
                if old_state is None or old_state.state != "on":
                    self._presence_since = new_state.last_changed
            else:
                self._presence_since = None
        elif entity_id == self._climate_entity:
            if new_state is not None and new_state.state in ("unavailable", "unknown"):
                # Registriamo SEMPRE quando l'entità reale è vista instabile,
                # indipendentemente da cos'altro sta succedendo — questo
                # timestamp estende la protezione contro falsi rilevamenti
                # ben oltre il semplice tempo fisso dal riavvio, adattandosi
                # a QUALSIASI durata di instabilità (anche ore dopo il boot,
                # se l'integrazione cloud ha un'interruzione temporanea).
                self._last_real_unavailable_at = dt_util.utcnow()
            is_off_transition = new_state and new_state.state == "off" and (old_state is None or old_state.state != "off")
            is_on_transition = (
                new_state and new_state.state not in ("off", "unknown", "unavailable")
                and old_state is not None and old_state.state == "off"
            )
            if is_off_transition or is_on_transition:
                # Conferma temporale prima di trattare come vera una
                # transizione spento<->acceso: alcune integrazioni cloud
                # (es. ConnectLife/Hisense) possono riportare transizioni
                # spurie in pochi secondi per instabilità di connessione —
                # senza questa conferma, verrebbero scambiate per vere
                # accensioni/spegnimenti manuali, con notifiche false e
                # persino spegnimenti reali indesiderati (timer avviato su
                # una falsa accensione). Se durante la finestra arrivano
                # PIÙ eventi ravvicinati (es. off poi di nuovo cool), NON
                # aggiorniamo lo stato "originale" di riferimento — resta
                # quello del PRIMO evento della sequenza, così alla fine
                # confrontiamo lo stato REALMENTE stabile con quello da
                # PRIMA che iniziasse l'intero episodio di instabilità,
                # non con l'ultimo passo intermedio (che potrebbe essere
                # esso stesso uno stato spurio).
                if self._state_change_debounce_cancel is not None:
                    self._state_change_debounce_cancel()
                    self._state_change_debounce_cancel = None
                else:
                    self._state_change_debounce_original_old = old_state
                captured_original_old = self._state_change_debounce_original_old

                async def _confirm_and_process(_now):
                    self._state_change_debounce_cancel = None
                    # Prima di fidarci del dato (potenzialmente vecchio/
                    # cachato), forziamo un aggiornamento FRESCO dal cloud —
                    # molto più affidabile che sperare che il prossimo
                    # polling automatico dell'integrazione capiti proprio
                    # entro questa finestra. Un glitch cloud che riporta
                    # "off" senza mai passare per unavailable/unknown viene
                    # così smascherato in pochi secondi, non minuti.
                    try:
                        await self.hass.services.async_call(
                            "homeassistant", "update_entity",
                            {"entity_id": self._climate_entity},
                            blocking=True,
                        )
                        await asyncio.sleep(2)
                    except Exception as exc:
                        _LOGGER.debug("%s: aggiornamento forzato fallito, procedo con il dato disponibile: %s", self._attr_name, exc)
                    current = self.hass.states.get(self._climate_entity)
                    reference_old_state = captured_original_old.state if captured_original_old is not None else None
                    if current is None or current.state == reference_old_state:
                        _LOGGER.info(
                            "%s: episodio di instabilità concluso — stato tornato a '%s' (quello di partenza), nessuna vera transizione",
                            self._attr_name, reference_old_state,
                        )
                        return
                    await self._async_process_climate_state_change(current, captured_original_old)
                    self.async_write_ha_state()

                self._state_change_debounce_cancel = async_call_later(
                    self.hass, STATE_CHANGE_DEBOUNCE_SECONDS, _confirm_and_process
                )
                return
            await self._async_process_climate_state_change(new_state, old_state)
        self.async_write_ha_state()

    async def _async_process_climate_state_change(self, new_state: State, old_state: State | None) -> None:
        """Elabora una transizione di stato del climatizzatore reale GIÀ
        CONFERMATA come stabile (vedi _async_on_state_change per il
        debounce che precede questa chiamata sulle transizioni critiche
        spento<->acceso)."""
        if new_state and new_state.state == "off" and (old_state is None or old_state.state != "off"):
            # Spegnimento reale — VERA transizione da uno stato acceso a
            # off (non una ripubblicazione ridondante dello stesso "off",
            # es. un heartbeat periodico del dispositivo Gree). Senza
            # questo controllo, un Gree che ripubblica "off" mentre resta
            # spento azzererebbe continuamente _power_limit_low_since,
            # impedendo per sempre al timer di riaccensione di accumulare
            # i minuti consecutivi configurati.
            self._cancel_dry_timer("off_state_change")
            self._fv_surplus_buffer = []
            self._fv_low_since = None
            self._fv_turnon_confirmed_since = None
            self._manual_accension_since = None
            self._last_sent_setpoint = None
            self._last_sent_setpoint_at = None
            self._last_sent_fan = None
            self._night_below_since = None
            self._night_auto_on = False
            self._fv_auto_on = False
            self._simple_night_auto_on = False
            self._simple_shutoff_since = None
            self._power_limit_high_since = None
            self._power_limit_low_since = None
            # Se lo spegnimento NON è avvenuto entro la finestra di
            # tolleranza di un nostro _async_turn_off_climate() recente,
            # E non è il primo evento generato al boot/riavvio (old_state
            # is None), E rappresenta una VERA transizione da uno stato
            # acceso a "off" (non un secondo evento "off"→"off", es. per
            # un aggiornamento di attributi durante la risincronizzazione
            # dopo un riavvio, che non è un nuovo spegnimento), allora è
            # uno spegnimento manuale (telecomando, app Gree, altra
            # automazione) — registriamo il timestamp per l'eventuale
            # blocco riaccensione temporizzato.
            is_programmatic = (
                self._programmatic_off_until is not None
                and dt_util.utcnow() <= self._programmatic_off_until
            )
            is_initial_boot_event = old_state is None
            is_real_transition_to_off = old_state is not None and old_state.state != "off"
            is_recently_unstable_off = (
                self._last_real_unavailable_at is not None
                and (dt_util.utcnow() - self._last_real_unavailable_at).total_seconds() < INSTABILITY_GRACE_PERIOD_SECONDS
            )
            if is_recently_unstable_off and is_real_transition_to_off and not is_programmatic:
                _LOGGER.info(
                    "%s: spegnimento off ignorato — entità vista instabile di recente, probabile riconnessione dell'integrazione reale",
                    self._attr_name,
                )
            elif not is_programmatic and not is_initial_boot_event and is_real_transition_to_off:
                # Notifica lo spegnimento manuale rilevato (ora
                # selezionabile), indipendentemente dal fatto che il
                # blocco riaccensione sia configurato — l'utente vuole
                # sapere che si è spento, anche se non vuole bloccarne
                # la riaccensione.
                _LOGGER.info("%s: spegnimento manuale rilevato (telecomando/app esterna)", self._attr_name)
                await self._async_simple_notify_manual_off()
                # Lo spegnimento è una scelta esplicita dell'utente proprio
                # ora — il timer (attivo o eventualmente in pausa per un
                # precedente spegnimento da limite potenza) non ha più
                # senso: azzeriamo tutto, non deve riprendere né scadere
                # più avanti su una sessione che l'utente ha già chiuso.
                if self._shutoff_timer_cancel is not None:
                    self._shutoff_timer_cancel()
                    self._shutoff_timer_cancel = None
                self._shutoff_timer_until = None
                self._shutoff_timer_remaining_seconds_paused = None
                if bool(get_conf(self.entry, CONF_SIMPLE_NO_REON_MANUAL_OFF, DEFAULT_SIMPLE_NO_REON_MANUAL_OFF)):
                    self._manual_off_since = dt_util.utcnow()
                    _LOGGER.info(
                        "%s: spegnimento manuale rilevato — blocco riaccensione attivo",
                        self._attr_name,
                    )
            elif is_initial_boot_event:
                _LOGGER.debug(
                    "%s: climatizzatore già spento al riavvio — non considerato spegnimento manuale",
                    self._attr_name,
                )
            elif not is_real_transition_to_off:
                _LOGGER.debug(
                    "%s: evento off→off senza vera transizione (probabile risincronizzazione) — ignorato",
                    self._attr_name,
                )
        elif new_state and new_state.state in ("unknown", "unavailable"):
            # Blip transitorio — NON toccare il timer DRY, prosegue normalmente
            _LOGGER.debug(
                "%s: climatizzatore temporaneamente %s — timer DRY preservato",
                self._attr_name, new_state.state,
            )
        elif new_state and new_state.state not in ("off", "unknown", "unavailable"):
            # Qualsiasi stato "acceso" (cool, dry, auto, fan_only, heat...)
            # rimuove il blocco riaccensione manuale — non solo dry/cool,
            # per coprire anche accensioni da telecomando fisico o app Gree
            # che potrebbero finire in una modalità diversa dalle due usate
            # normalmente da questa integrazione.
            if self._manual_off_since is not None:
                self._manual_off_since = None
                _LOGGER.info("%s: climatizzatore riacceso — blocco riaccensione manuale rimosso", self._attr_name)
            # Rileva un'accensione MANUALE: vera transizione da "off" ad
            # acceso (non solo un cambio dry->cool o simili), e non
            # attribuibile alla logica FV o notturna di questa stessa
            # integrazione (che impostano i rispettivi flag PRIMA di
            # chiamare il servizio, quindi sono già True quando arriva
            # questo evento se sono stati loro ad accendere).
            is_recently_unstable = (
                self._last_real_unavailable_at is not None
                and (dt_util.utcnow() - self._last_real_unavailable_at).total_seconds() < INSTABILITY_GRACE_PERIOD_SECONDS
            )
            if old_state is not None and old_state.state == "off" and is_recently_unstable:
                _LOGGER.info(
                    "%s: transizione off->acceso ignorata — entità vista instabile di recente, probabile riconnessione dell'integrazione reale",
                    self._attr_name,
                )
            elif old_state is not None and old_state.state == "off" and not self._fv_auto_on and not self._simple_night_auto_on:
                self._manual_accension_since = dt_util.utcnow()
                _LOGGER.info("%s: accensione manuale rilevata — immunità spegnimento FV per il periodo configurato", self._attr_name)
                temp_for_notify = self._simple_read_temp()
                target_for_notify = self._simple_current_target() if self._get_season_mode() != SEASON_WINTER else self._winter_current_target()
                if temp_for_notify is not None:
                    await self._async_simple_notify_manual_on(temp_for_notify, target_for_notify)
                # Timer di spegnimento automatico dopo accensione
                # manuale — se l'utente l'ha attivato dalla card (o è
                # configurato di default), programma lo spegnimento a
                # prescindere da tutto il resto (FV, notte, finestra),
                # proprio come vuole chi usa il clima manualmente (es.
                # uno scaldotto) e vuole solo una sicurezza a tempo.
                if self._manual_shutoff_timer_enabled() and self._get_season_mode() != SEASON_OFF:
                    timer_minutes = self._manual_shutoff_timer_minutes()
                    if timer_minutes > 0:
                        if self._shutoff_timer_cancel is not None:
                            self._shutoff_timer_cancel()
                        self._shutoff_timer_until = dt_util.utcnow() + timedelta(minutes=timer_minutes)
                        self._shutoff_timer_cancel = async_call_later(
                            self.hass, timedelta(minutes=timer_minutes), self._async_shutoff_timer_expired
                        )
                        _LOGGER.info("%s: timer di spegnimento automatico avviato (%s minuti)", self._attr_name, timer_minutes)
                # Se la finestra è GIÀ aperta in questo momento (non è
                # lei a essere appena cambiata, quindi il suo stesso
                # listener non scatterebbe mai per questo caso),
                # applichiamo la stessa gestione che scatterebbe se si
                # fosse appena aperta: snapshot + spegnimento ritardato,
                # stessa notifica — invece di lasciare il clima acceso
                # senza nessun controllo finché la finestra non cambia
                # stato per conto suo.
                if (self._is_window_open()
                        and self._switch_state(SWITCH_KEY_MASTER, True)
                        and bool(get_conf(self.entry, CONF_WINDOW_DETECTION_ENABLED, DEFAULT_WINDOW_DETECTION_ENABLED))):
                    mode = self._get_config_mode()
                    if mode in (CONFIG_MODE_SIMPLE, CONFIG_MODE_SIMPLE_FV):
                        _LOGGER.info("%s: accensione manuale con finestra già aperta — avvio gestione come apertura finestra", self._attr_name)
                        await self._async_simple_notify_window(True, SIMPLE_WINDOW_DELAY_MIN, ac_was_on=True)
                        await self._async_window_opened_simple()
                    else:
                        _LOGGER.info("%s: accensione manuale con finestra già aperta — avvio gestione come apertura finestra", self._attr_name)
                        await self._async_window_opened()
            if new_state.state == "dry":
                if self._simple_dry_end is None:
                    # Tornato in DRY senza timer attivo (es. set manuale da UI/altra
                    # automazione/telecomando) — riarma subito, alla transizione
                    _LOGGER.warning("%s: [DRY-TRACE] rilevato DRY via state_change senza timer attivo — riavvio", self._attr_name)
                    self._schedule_dry_timer("dry_rilevato_su_state_change")
                else:
                    _LOGGER.warning(
                        "%s: [DRY-TRACE] state_change a DRY ma timer già attivo (dry_end=%s) — nessuna azione",
                        self._attr_name, self._simple_dry_end.isoformat(),
                    )

    async def async_will_remove_from_hass(self) -> None:
        if self._window_cancel_timer is not None:
            self._window_cancel_timer()
            self._window_cancel_timer = None
        if self._dry_cancel_timer is not None:
            self._dry_cancel_timer()
            self._dry_cancel_timer = None
        if self._state_change_debounce_cancel is not None:
            self._state_change_debounce_cancel()
            self._state_change_debounce_cancel = None
        for cancel in self._config_write_debounce_cancel.values():
            if cancel is not None:
                cancel()
        self._config_write_debounce_cancel.clear()
        if self._shutoff_timer_cancel is not None:
            self._shutoff_timer_cancel()
            self._shutoff_timer_cancel = None
            # NON azzero self._shutoff_timer_until — resta nello stato
            # salvato (già esposto come attributo), così la PROSSIMA
            # istanza (creata da un reload) può leggerlo e ricalcolare i
            # minuti rimanenti, rischedulando il timer invece di perderlo.
        data = self.hass.data.get(DOMAIN, {}).get(self.entry.entry_id, {})
        if data.get("climate") is self:
            data.pop("climate", None)

    # ------------------------------------------------------------------
    # Comandi utente
    # ------------------------------------------------------------------

    async def async_set_temperature(self, **kwargs: Any) -> None:
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        self._target_temperature = float(temperature)
        self.async_write_ha_state()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        if fan_mode not in FAN_MODES_ALLOWED:
            fan_mode = FAN_MODES_ALLOWED[0]
        await self._async_safe_climate_call("set_fan_mode", {"entity_id": self._climate_entity, "fan_mode": fan_mode})
        self.async_write_ha_state()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.OFF:
            # Un OFF che arriva QUI è per definizione un comando esplicito
            # dall'esterno (card/dashboard, servizio climate.set_hvac_mode
            # o climate.turn_off, assistente vocale...) — i cicli periodici
            # interni non passano MAI da questo metodo per spegnere, usano
            # sempre _async_turn_off_climate() direttamente. Va quindi
            # registrato come spegnimento manuale PRIMA di spegnere,
            # esattamente come lo spegnimento rilevato da telecomando/app
            # reale — altrimenti _async_turn_off_climate() lo marca come
            # "programmatico" e _async_on_state_change salta la
            # registrazione, vanificando il blocco riaccensione anche con
            # l'opzione abilitata (bug reale osservato: spegnimento dalla
            # card sempre bypassato, mentre da telecomando fisico
            # funzionava).
            self._set_manual_off_block("spegnimento_esplicito_da_ui_o_servizio")
            await self._async_turn_off_climate()
        elif hvac_mode == HVACMode.DRY:
            await self._async_safe_climate_call("set_hvac_mode", {"entity_id": self._climate_entity, "hvac_mode": "dry"})
            self._schedule_dry_timer("set_hvac_mode_manuale_da_ui")
            self._reset_manual_off_block("accensione_dry_manuale_da_ui")
        else:
            await self._async_safe_climate_call("set_hvac_mode", {"entity_id": self._climate_entity, "hvac_mode": "cool"})
            self._reset_manual_off_block("accensione_cool_manuale_da_ui")
        self.async_write_ha_state()

    def _set_manual_off_block(self, reason: str = "n/d") -> None:
        """Registra esplicitamente uno spegnimento come manuale, imponendo
        il blocco riaccensione se l'opzione è abilitata.

        Simmetrico a _reset_manual_off_block: usato quando l'utente spegne
        direttamente dal termostato (wrapper) tramite async_set_hvac_mode,
        senza dover dipendere dal listener di stato del climatizzatore
        reale (che classificherebbe erroneamente questo spegnimento come
        "programmato", dato che passa comunque da _async_turn_off_climate()
        per l'esecuzione vera e propria).
        """
        if self._shutoff_timer_cancel is not None:
            self._shutoff_timer_cancel()
            self._shutoff_timer_cancel = None
        self._shutoff_timer_until = None
        self._shutoff_timer_remaining_seconds_paused = None
        if bool(get_conf(self.entry, CONF_SIMPLE_NO_REON_MANUAL_OFF, DEFAULT_SIMPLE_NO_REON_MANUAL_OFF)):
            self._manual_off_since = dt_util.utcnow()
            _LOGGER.info(
                "%s: spegnimento manuale registrato — motivo: %s — blocco riaccensione attivo",
                self._attr_name, reason,
            )

    def _reset_manual_off_block(self, reason: str = "n/d") -> None:
        """Rimuove esplicitamente il blocco riaccensione manuale.

        Usato quando l'utente accende direttamente dal termostato (wrapper),
        senza dipendere dal listener di stato del climatizzatore reale — più
        robusto nel caso in cui il dispositivo reale finisca in una modalità
        diversa da dry/cool (es. "auto") che il listener non intercetta.
        """
        if self._manual_off_since is not None:
            self._manual_off_since = None
            _LOGGER.info("%s: blocco riaccensione manuale rimosso — motivo: %s", self._attr_name, reason)

    # ------------------------------------------------------------------
    # Loop periodico
    # ------------------------------------------------------------------

    async def _async_periodic_update(self, now: datetime | None = None) -> None:
        if not self._switch_state(SWITCH_KEY_MASTER, True):
            return
        if self._is_window_open():
            return

        mode = self._get_config_mode()

        if mode in (CONFIG_MODE_SIMPLE, CONFIG_MODE_SIMPLE_FV):
            await self._async_periodic_update_simple(now)
        else:
            await self._async_periodic_update_full(now)

        self.async_write_ha_state()

    async def _async_periodic_update_full(self, now: datetime | None = None) -> None:
        """Loop periodico per il modo completo."""
        temp = self.current_temperature
        if temp is None:
            return
        target = self._effective_target()

        # Protezione potenza — ha precedenza su tutto
        await self._async_handle_power_limit()

        # Se spento per power limit non fare altro
        if self._power_limit_off:
            return
        temp = self.current_temperature
        if temp is None:
            return
        target = self._effective_target()

        # Rileva transizione notte → giorno PRIMA di aggiornare _was_night_mode
        night_now = self._is_night_mode_active()
        night_just_ended = self._was_night_mode and not night_now
        self._was_night_mode = night_now

        await self._async_handle_thermal(temp, target)

        if self._switch_state(SWITCH_KEY_FV, True) and self._within_fv_window():
            await self._async_handle_fv_turn_on(temp, target)

        if night_now and bool(get_conf(self.entry, CONF_NIGHT_AC_ENABLED, DEFAULT_NIGHT_AC_ENABLED)):
            await self._async_handle_night_turn_on(temp, target)

        if bool(get_conf(self.entry, CONF_FV_SHUTOFF_ENABLED, DEFAULT_FV_SHUTOFF_ENABLED)):
            await self._async_handle_fv_shutoff(temp, target)

        if night_now and bool(get_conf(self.entry, CONF_NIGHT_SHUTOFF_ENABLED, DEFAULT_NIGHT_SHUTOFF_ENABLED)):
            await self._async_handle_night_shutoff(temp, target)

        await self._async_handle_fv_sensor_offline_shutoff()

        # Spegnimento a fine modalità notturna
        if night_just_ended:
            await self._async_handle_night_end_shutoff()

        await self._async_handle_presence_boost(temp, target)

    # ------------------------------------------------------------------
    # Loop periodico — Modo semplificato
    # ------------------------------------------------------------------

    async def _async_periodic_update_simple(self, now: datetime | None = None) -> None:
        """Loop periodico per modo semplificato e semplificato con FV."""
        season = self._get_season_mode()
        if season == SEASON_MANUAL:
            # In Manuale il master switch deve restare sempre disattivato —
            # se per qualche motivo risultasse acceso (es. riacceso per
            # errore, o residuo da prima del cambio stagione), lo forziamo
            # spento ad ogni ciclo, così l'automazione non riparte mai
            # finché la stagione resta su Manuale.
            if self._switch_state(SWITCH_KEY_MASTER, True):
                master_entity = self._switch_entity_id(SWITCH_KEY_MASTER)
                if master_entity:
                    _LOGGER.info("%s: stagione Manuale — disattivo automaticamente il master switch", self._attr_name)
                    try:
                        await self.hass.services.async_call("switch", "turn_off", {"entity_id": master_entity}, blocking=True)
                    except Exception as exc:
                        _LOGGER.warning("%s: impossibile disattivare il master switch: %s", self._attr_name, exc)
        if season == SEASON_OFF or season == SEASON_MANUAL:
            return  # nessuna regolazione — solo il timer manuale resta attivo (Manuale) o nulla del tutto (Off)

        # --- Fallback DRY→COOL ---
        # Il meccanismo primario è async_track_point_in_time schedulato da _schedule_dry_timer.
        # Questo fallback copre il caso raro in cui il Gree era unavailable al momento
        # esatto dello scatto del timer (il callback ha trovato stato != "dry" e non ha
        # transitato). Ogni 5 minuti verifichiamo: se dry_end è nel passato e il clima
        # è ancora in DRY, transitiamo a COOL adesso.
        if self._simple_dry_end is not None:
            real_state_dry = self.hass.states.get(self._climate_entity)
            if real_state_dry and real_state_dry.state == "dry":
                if dt_util.utcnow() >= self._simple_dry_end:
                    _LOGGER.warning(
                        "%s: [DRY-TRACE] fallback polling — timer già scaduto, transizione ora (set_hvac_mode cool)",
                        self._attr_name,
                    )
                    await self._async_safe_climate_call("set_hvac_mode", {"entity_id": self._climate_entity, "hvac_mode": "cool"})
                    self._cancel_dry_timer("fallback_polling_dry_end_scaduto")

        use_internal = self._should_use_internal_probe()
        if self._pending_probe_notification is not None:
            event = self._pending_probe_notification
            self._pending_probe_notification = None
            if event == "triggered":
                await self._async_simple_notify(f"📡 {self._get_display_name()}: sonda esterna bloccata, passo alla sonda interna del climatizzatore.")
            elif event == "recovered":
                await self._async_simple_notify(f"📡 {self._get_display_name()}: sonda esterna ripristinata, torno a usarla.")
        temp = self._simple_read_temp()
        if temp is None:
            return
        self._record_temp_reading(temp)

        # Protezione potenza — ha precedenza su tutto
        await self._async_handle_power_limit()
        if self._power_limit_off:
            return

        night_now = self._simple_is_night()
        night_just_ended = self._simple_was_night and not night_now
        night_just_started = not self._simple_was_night and night_now
        self._simple_was_night = night_now

        # Il target mostrato nella notifica notte, e la regolazione termica
        # che segue, dipendono dalla stagione — in Auto seguono lo stesso
        # criterio già usato nel ciclo FV (cosa è già acceso ora).
        real_state = self.hass.states.get(self._climate_entity)
        real_hvac = real_state.state if real_state else "off"
        use_winter_target = season == SEASON_WINTER or (season == SEASON_AUTO and real_hvac == "heat")
        target = self._winter_current_target() if use_winter_target else self._simple_current_target()

        # Notifica inizio modalità notturna
        if night_just_started:
            await self._async_simple_notify_night_start(target)

        # Spegnimento fine notte — deve avvenire PRIMA del check limbo, perché
        # il limbo scatta subito dopo night_end e bloccherebbe questo blocco
        # per l'intera ora successiva (bug: lo spegnimento non avveniva mai).
        if night_just_ended:
            self._simple_night_auto_on = False  # reset — non è più notte
            await self._async_handle_night_end_shutoff()
            await self._async_simple_notify_night_end()

        # Ora di limbo dopo fine notte — non fare altro (accensioni/regolazioni)
        if self._simple_is_in_limbo():
            _LOGGER.debug("%s: [semplificato] ora di limbo post-notte — nessuna azione", self._attr_name)
            return

        # Regolazione termica — solo per un clima già acceso nella direzione
        # coerente (l'accensione da spento è gestita dal ciclo FV dedicato)
        if use_winter_target:
            await self._async_handle_thermal_winter_simple(temp, target, use_internal)
        else:
            await self._async_handle_thermal_simple(temp, target, use_internal)

        # NOTA: accensione/spegnimento FV (emergenza, turn-on, shutoff) non è
        # più gestita qui — ha un ciclo dedicato più veloce, vedi
        # _async_periodic_fv_check() e CONF_FV_SHUTOFF_TOTAL_MINUTES.

    async def _async_periodic_fv_check(self, now: datetime | None = None) -> None:
        """Ciclo dedicato e più rapido per la logica FV (emergenza, accensione,
        spegnimento). Separato dal loop principale (regolazione termica, DRY,
        notte) che gira più lentamente — così il rilevamento di un surplus
        insufficiente può essere confermato in pochi minuti invece di dover
        aspettare N cicli lunghi del loop generale.

        Comportamento per stagione:
        - Off: nulla, mai (anche il timer manuale è disattivato altrove)
        - Manuale: nulla — solo il timer manuale resta attivo (gestito altrove)
        - Estate: comportamento originale, invariato
        - Inverno: equivalente specchiato, target/soglie invernali
        - Auto: entrambe le logiche, mai in contemporanea sullo stesso stato,
          con un raffreddamento di ore tra un cambio di direzione e l'altro
        """
        mode = self._get_config_mode()
        if mode != CONFIG_MODE_SIMPLE_FV:
            return
        if not self._switch_state(SWITCH_KEY_MASTER, True):
            return
        season = self._get_season_mode()
        if season == SEASON_OFF or season == SEASON_MANUAL:
            return
        if self._is_window_open():
            return
        if self._power_limit_off:
            return

        use_internal = self._should_use_internal_probe()
        temp = self._simple_read_temp()
        if temp is None:
            return
        self._record_temp_reading(temp)

        real_state = self.hass.states.get(self._climate_entity)
        real_hvac = real_state.state if real_state else "off"
        dry_enabled = bool(get_conf(self.entry, CONF_SIMPLE_DRY_ENABLED, DEFAULT_SIMPLE_DRY_ENABLED))

        run_summer = season == SEASON_SUMMER
        run_winter = season == SEASON_WINTER
        already_on_direction = None  # "cool"/"dry" o "heat" se il clima è già acceso in una direzione specifica
        if season == SEASON_AUTO:
            if real_hvac == "heat":
                run_winter = True
                already_on_direction = "heat"
            elif real_hvac in ("cool", "dry"):
                run_summer = True
                already_on_direction = "cool"
            else:
                # Clima spento — proviamo le direzioni ammesse IN SEQUENZA
                # nello stesso ciclo, non solo la prima: altrimenti se il
                # primo ramo ammesso non produce alcuna accensione (es.
                # temperatura non abbastanza calda per l'estate, ma
                # abbastanza fredda per l'inverno), il secondo ramo non
                # verrebbe mai valutato in questo ciclo.
                run_summer = self._auto_mode_direction_allowed("cool")
                run_winter = self._auto_mode_direction_allowed("heat")

        if run_summer:
            target = self._simple_current_target()
            await self._async_handle_emergency_heat(temp, target, use_internal, dry_enabled)
            if self._switch_state(SWITCH_KEY_EMERGENCY, False):
                return
            if self._switch_state(SWITCH_KEY_FV, True) and self._simple_within_fv_window():
                real_before = self.hass.states.get(self._climate_entity)
                was_off = real_before is None or real_before.state in ("off", "unknown", "unavailable")
                await self._async_handle_fv_turn_on_simple(temp, target)
                if was_off and season == SEASON_AUTO:
                    real_after = self.hass.states.get(self._climate_entity)
                    if real_after and real_after.state in ("cool", "dry"):
                        self._auto_mode_record_direction("cool")
                        already_on_direction = "cool"  # ha appena acceso — non provare più anche l'inverno in questo ciclo
            if bool(get_conf(self.entry, CONF_FV_SHUTOFF_ENABLED, DEFAULT_FV_SHUTOFF_ENABLED)):
                await self._async_handle_fv_shutoff_simple(temp, target)
            await self._async_handle_fv_sensor_offline_shutoff()
            if already_on_direction is not None:
                return  # clima già acceso (prima o dopo questo ramo) — non ha senso valutare anche l'inverno ora

        if run_winter:
            target = self._winter_current_target()
            await self._async_handle_emergency_heat(temp, target, use_internal, dry_enabled)
            if self._switch_state(SWITCH_KEY_EMERGENCY, False):
                return
            if self._switch_state(SWITCH_KEY_FV, True):
                real_before = self.hass.states.get(self._climate_entity)
                was_off = real_before is None or real_before.state in ("off", "unknown", "unavailable")
                await self._async_handle_winter_turn_on_simple(temp, target)
                if was_off and season == SEASON_AUTO:
                    real_after = self.hass.states.get(self._climate_entity)
                    if real_after and real_after.state == "heat":
                        self._auto_mode_record_direction("heat")
            await self._async_handle_winter_shutoff_simple(temp, target)
            await self._async_handle_fv_sensor_offline_shutoff()
            return

    def _is_fv_sensor_offline(self, threshold_min: float) -> bool:
        """True se il sensore di produzione FV è offline (letteralmente
        unavailable/unknown) o non si aggiorna da almeno threshold_min
        minuti — stesso principio già usato per la sonda di temperatura
        (last_updated, non last_changed, per evitare falsi positivi con
        valori stabili ma sensore comunque vivo).
        """
        if not self._fv_sensor:
            return False
        state = self.hass.states.get(self._fv_sensor)
        if state is None or state.state in ("unknown", "unavailable"):
            return True
        last_updated = state.last_updated
        if last_updated is None:
            return False
        return (dt_util.utcnow() - last_updated) > timedelta(minutes=threshold_min)

    async def _async_handle_fv_sensor_offline_shutoff(self) -> None:
        """Spegne un clima acceso dal FV se il sensore di produzione va
        offline per troppo tempo — senza quel dato non possiamo più sapere
        se il sole c'è davvero, quindi lasciarlo acceso indefinitamente
        rischierebbe uno spreco energetico silenzioso dalla rete.

        Si applica SOLO ai climi accesi dal FV (mai a quelli accesi
        manualmente — un'accensione manuale non dipende dal fotovoltaico,
        spegnerla solo perché il sensore è muto non avrebbe senso).

        Una notifica iniziale condivisa avvisa appena il problema viene
        rilevato (pochi minuti), indipendentemente da quale stanza lo nota
        per prima; lo spegnimento vero avviene poi singolarmente per ogni
        istanza, dopo il proprio tempo configurato.
        """
        if not bool(get_conf(self.entry, CONF_FV_SENSOR_OFFLINE_SHUTOFF_ENABLED, DEFAULT_FV_SENSOR_OFFLINE_SHUTOFF_ENABLED)):
            return
        if not self._fv_auto_on:
            return  # solo climi accesi dal FV, mai quelli manuali
        real_state = self.hass.states.get(self._climate_entity)
        if real_state is None or real_state.state in ("off", "unknown", "unavailable"):
            return  # già spento, nulla da fare

        coord = self.hass.data.setdefault(DOMAIN, {}).setdefault("_coordination", {})

        # Rilevamento immediato (2 minuti, giusto per escludere un singolo
        # ciclo di polling saltato) — usato solo per la notifica di allerta.
        if not self._is_fv_sensor_offline(threshold_min=2):
            coord["fv_sensor_offline_notified"] = False  # il sensore è vivo, resettiamo per il prossimo eventuale episodio
            return

        notify_tts = bool(get_conf(self.entry, CONF_FV_SENSOR_OFFLINE_NOTIFY_TTS, DEFAULT_FV_SENSOR_OFFLINE_NOTIFY_TTS))
        notify_telegram = bool(get_conf(self.entry, CONF_FV_SENSOR_OFFLINE_NOTIFY_TELEGRAM, DEFAULT_FV_SENSOR_OFFLINE_NOTIFY_TELEGRAM))

        if not coord.get("fv_sensor_offline_notified"):
            coord["fv_sensor_offline_notified"] = True
            shutoff_min_for_msg = float(get_conf(self.entry, CONF_FV_SENSOR_OFFLINE_SHUTOFF_MIN, DEFAULT_FV_SENSOR_OFFLINE_SHUTOFF_MIN))
            alert_msg = (
                f"📡 Sensore produzione fotovoltaica offline. Se non torna disponibile entro "
                f"{shutoff_min_for_msg:.0f} minuti, i climatizzatori accesi dal fotovoltaico verranno spenti per sicurezza."
            )
            _LOGGER.warning("%s: sensore FV offline rilevato — notifica di allerta inviata", self._attr_name)
            if notify_tts:
                await self._async_simple_speak(alert_msg)
            if notify_telegram:
                await self._async_simple_notify(alert_msg)

        # Spegnimento vero — dopo il tempo configurato PER QUESTA istanza
        shutoff_min = float(get_conf(self.entry, CONF_FV_SENSOR_OFFLINE_SHUTOFF_MIN, DEFAULT_FV_SENSOR_OFFLINE_SHUTOFF_MIN))
        if not self._is_fv_sensor_offline(threshold_min=shutoff_min):
            return  # non ancora scaduto il tempo configurato per questa stanza

        _LOGGER.warning("%s: spegnimento — sensore FV offline da oltre %s minuti", self._attr_name, shutoff_min)
        await self._async_turn_off_climate()
        self._fv_surplus_buffer = []
        self._fv_low_since = None
        own_msg = (
            f"⚠️ {self._get_display_name()}: climatizzatore spento — sensore produzione fotovoltaica "
            f"offline da oltre {shutoff_min:.0f} minuti."
        )
        if notify_tts:
            await self._async_simple_speak(own_msg)
        if notify_telegram:
            await self._async_simple_notify(own_msg)

    def _external_sensor_is_stale(self) -> bool:
        """True se la sonda esterna è configurata ma non si aggiorna da
        troppo tempo (probabile problema di connettività — es. sensori MQTT
        che dipendono da un server esterno che può andare offline).

        Usiamo last_updated, non last_changed: quest'ultimo si aggiorna
        SOLO quando il valore riportato cambia davvero, mentre last_updated
        si aggiorna ad ogni singolo report del sensore anche se il valore è
        identico al precedente. Con una stanza che si raffredda lentamente,
        il valore può restare invariato per lunghi periodi pur continuando
        a funzionare — usare last_changed avrebbe fatto scattare falsi
        allarmi di "sonda bloccata" anche con il sensore perfettamente vivo.
        """
        if not self._temp_sensor:
            return False
        state = self.hass.states.get(self._temp_sensor)
        if state is None or state.state in ("unknown", "unavailable"):
            return True
        last_updated = state.last_updated
        if last_updated is None:
            return False
        stale_after_min = float(get_conf(self.entry, CONF_SIMPLE_EXTERNAL_SENSOR_STALE_MIN, DEFAULT_SIMPLE_EXTERNAL_SENSOR_STALE_MIN))
        return (dt_util.utcnow() - last_updated) > timedelta(minutes=stale_after_min)

    def _should_use_internal_probe(self) -> bool:
        """Decide se usare la sonda interna del climatizzatore.

        True se non è configurata nessuna sonda esterna, OPPURE se è
        configurata ma risulta bloccata da troppo tempo — in quel caso si
        passa automaticamente alla sonda interna, e si torna alla esterna
        da sola non appena questa riprende ad aggiornarsi.

        Controllo extra di sicurezza: anche quando il timestamp indica
        "bloccata", se il valore GREZZO attuale della sonda esterna risulta
        diverso dall'ultimo che avevamo registrato mentre era viva, la
        consideriamo comunque tornata online — un segnale indipendente dal
        timestamp, utile come rete di sicurezza in caso di sensori MQTT che
        non aggiornano last_updated in modo affidabile a parità di valore.
        """
        if not self._temp_sensor:
            return True
        is_stale = self._external_sensor_is_stale()

        if is_stale:
            fresh_value = self._read_float(self._temp_sensor)
            if fresh_value is not None and self._external_sensor_last_value is not None and fresh_value != self._external_sensor_last_value:
                is_stale = False  # controllo extra: il valore è cambiato, la sonda è viva

        if not is_stale:
            fresh_value = self._read_float(self._temp_sensor)
            if fresh_value is not None:
                self._external_sensor_last_value = fresh_value

        if is_stale != self._external_sensor_fallback_active:
            self._external_sensor_fallback_active = is_stale
            if is_stale:
                _LOGGER.warning(
                    "%s: sonda esterna bloccata — passaggio automatico alla sonda interna del climatizzatore",
                    self._attr_name,
                )
                self._pending_probe_notification = "triggered"
            else:
                _LOGGER.warning(
                    "%s: sonda esterna ripristinata — torno a usarla normalmente",
                    self._attr_name,
                )
                self._pending_probe_notification = "recovered"
        return is_stale

    def _simple_read_temp(self) -> float | None:
        """Legge la temperatura: sonda esterna se configurata e aggiornata,
        altrimenti sonda interna del clima (anche come fallback automatico
        se la sonda esterna smette di aggiornarsi)."""
        if self._temp_sensor and not self._should_use_internal_probe():
            return self._read_float(self._temp_sensor)
        # Usa current_temperature dagli attributi del climatizzatore reale
        state = self.hass.states.get(self._climate_entity)
        if state is None:
            return None
        raw = state.attributes.get("current_temperature")
        if raw is None:
            return None
        try:
            return float(raw)
        except (TypeError, ValueError):
            return None

    def _get_config_mode(self) -> str:
        """Restituisce config_mode corretto, deducendolo dal fv_sensor se necessario.
        
        Tabella conversione valori vecchi → nuovi:
        - "semplificato_fv" → CONFIG_MODE_SIMPLE_FV
        - "semplificato"    → CONFIG_MODE_SIMPLE
        - None / altro      → deduce da fv_sensor
        """
        VALID = (CONFIG_MODE_SIMPLE, CONFIG_MODE_SIMPLE_FV, CONFIG_MODE_FULL)
        # Tabella conversione vecchi valori
        CONVERSION = {
            "semplificato_fv": CONFIG_MODE_SIMPLE_FV,
            "semplificato": CONFIG_MODE_SIMPLE,
            "simple": CONFIG_MODE_SIMPLE,
            "simple_fv": CONFIG_MODE_SIMPLE_FV,
            "full": CONFIG_MODE_FULL,
        }
        mode = get_conf(self.entry, CONF_CONFIG_MODE, None)
        if mode in CONVERSION:
            return CONVERSION[mode]
        # Valore sconosciuto — deduce dalla presenza del sensore FV
        return CONFIG_MODE_SIMPLE_FV if self._fv_sensor else CONFIG_MODE_SIMPLE

    def _simple_is_night(self) -> bool:
        return self._in_time_window(
            get_conf(self.entry, CONF_SIMPLE_NIGHT_START, DEFAULT_SIMPLE_NIGHT_START),
            get_conf(self.entry, CONF_SIMPLE_NIGHT_END, DEFAULT_SIMPLE_NIGHT_END),
        )

    def _simple_is_in_limbo(self) -> bool:
        """True nell'ora dopo la fine della modalità notturna.

        Durante questo periodo il termostato non fa nulla — non accende,
        non spegne, non regola. Evita accensioni indesiderate causate dal
        cambio brusco di target (da notte a giorno).
        L'ora di limbo è fissa (SIMPLE_NIGHT_END_LIMBO_H = 1h).
        """
        if self._simple_is_night():
            return False
        night_end_str = get_conf(self.entry, CONF_SIMPLE_NIGHT_END, DEFAULT_SIMPLE_NIGHT_END)
        try:
            night_end_t = dt_time.fromisoformat(str(night_end_str))
        except ValueError:
            return False
        now_local = dt_util.now()
        night_end_dt = now_local.replace(
            hour=night_end_t.hour, minute=night_end_t.minute, second=0, microsecond=0
        )
        limbo_end_dt = night_end_dt + timedelta(hours=SIMPLE_NIGHT_END_LIMBO_H)
        return night_end_dt <= now_local < limbo_end_dt

    def _simple_can_control_manual(self) -> bool:
        """Restituisce True se l'automazione può spegnere il clima acceso manualmente.

        Condizioni:
        - Il sole è sopra l'orizzonte (sun.sun == above_horizon)
        - Siamo almeno X ore prima del tramonto (configurabile, min 2h)
        """
        sun_state = self.hass.states.get("sun.sun")
        if sun_state is None:
            return False  # sun.sun non disponibile → non intervenire

        # Sole sotto l'orizzonte → non intervenire
        if sun_state.state != "above_horizon":
            return False

        # Calcola orario tramonto
        next_setting_str = sun_state.attributes.get("next_setting")
        if not next_setting_str:
            return False
        try:
            next_setting = dt_util.parse_datetime(str(next_setting_str))
            if next_setting is None:
                return False
            sunset_local = dt_util.as_local(next_setting)
        except (ValueError, TypeError):
            return False

        anticipate_h = float(get_conf(self.entry, CONF_SIMPLE_SUNSET_ANTICIPATE_H, DEFAULT_SIMPLE_SUNSET_ANTICIPATE_H))
        cutoff = sunset_local - timedelta(hours=anticipate_h)
        now_local = dt_util.now()

        return now_local < cutoff

    def _simple_within_fv_window(self) -> bool:
        """Finestra di accensione FV nel modo semplificato.

        Inizia alla fine della modalità notturna (night_end)
        e termina al tramonto - anticipate_h ore.
        Non richiede configurazione oraria — usa sun.sun e la fascia notturna.
        """
        # Controlla che il sole sia sopra l'orizzonte
        sun_state = self.hass.states.get("sun.sun")
        if sun_state is None or sun_state.state != "above_horizon":
            return False

        now_local = dt_util.now()

        # Inizio finestra = fine modalità notturna
        night_end_str = get_conf(self.entry, CONF_SIMPLE_NIGHT_END, DEFAULT_SIMPLE_NIGHT_END)
        try:
            night_end_t = dt_time.fromisoformat(str(night_end_str))
        except ValueError:
            return False
        night_end_dt = now_local.replace(
            hour=night_end_t.hour, minute=night_end_t.minute, second=0, microsecond=0
        )

        # Fine finestra = tramonto - anticipate_h
        next_setting_str = sun_state.attributes.get("next_setting")
        if not next_setting_str:
            return False
        try:
            sunset_dt = dt_util.as_local(dt_util.parse_datetime(str(next_setting_str)))
        except (ValueError, TypeError):
            return False
        anticipate_h = float(get_conf(self.entry, CONF_SIMPLE_SUNSET_ANTICIPATE_H, DEFAULT_SIMPLE_SUNSET_ANTICIPATE_H))
        cutoff_dt = sunset_dt - timedelta(hours=anticipate_h)

        return night_end_dt <= now_local <= cutoff_dt

    def _effective_priority(self) -> float:
        """Priorità FV effettiva: il valore 'pending' (durante la breve
        finestra di debounce dopo una regolazione dalla card, prima che la
        scrittura in configurazione sia definitiva) se presente, altrimenti
        quello configurato — un'unica fonte di verità, niente più override
        separati da tenere sincronizzati."""
        if self._pending_priority_display is not None:
            return self._pending_priority_display
        return float(get_conf(self.entry, CONF_FV_PRIORITY, DEFAULT_FV_PRIORITY))

    def _simple_current_target(self) -> float:
        if self._simple_is_night():
            if self._pending_target_night_display is not None:
                return self._pending_target_night_display
            return float(get_conf(self.entry, CONF_SIMPLE_TARGET_NIGHT, DEFAULT_SIMPLE_TARGET_NIGHT))
        if self._pending_target_day_display is not None:
            return self._pending_target_day_display
        return float(get_conf(self.entry, CONF_SIMPLE_TARGET_DAY, DEFAULT_SIMPLE_TARGET_DAY))

    def _simple_is_quiet_night(self) -> bool:
        """Fascia di silenzio notturna semplificata = stessa fascia notturna."""
        return self._simple_is_night()

    def _get_season_mode(self) -> str:
        return get_conf(self.entry, CONF_SEASON_MODE, DEFAULT_SEASON_MODE)

    def _winter_current_target(self) -> float:
        """Equivalente di _simple_current_target() ma per l'inverno — nessun
        override runtime dalla card per ora (non richiesto), solo i valori
        configurati nella schermata Inverno."""
        if self._simple_is_night():
            return float(get_conf(self.entry, CONF_WINTER_TARGET_NIGHT, DEFAULT_WINTER_TARGET_NIGHT))
        return float(get_conf(self.entry, CONF_WINTER_TARGET_DAY, DEFAULT_WINTER_TARGET_DAY))

    def _record_temp_reading(self, temp: float | None) -> None:
        """Registra una lettura di temperatura con timestamp, per poter poi
        rilevare se la temperatura è in discesa (accensione invernale
        opportunistica). Mantiene solo gli ultimi 20 minuti di storico —
        margine oltre i 10 richiesti, per tollerare cicli saltati."""
        if temp is None:
            return
        if not hasattr(self, "_winter_temp_history"):
            self._winter_temp_history: list[tuple[datetime, float]] = []
        now = dt_util.utcnow()
        self._winter_temp_history.append((now, temp))
        cutoff = now - timedelta(minutes=20)
        self._winter_temp_history = [(t, v) for t, v in self._winter_temp_history if t >= cutoff]

    def _is_temp_descending(self, minutes: float = 10) -> bool:
        """True se la temperatura attuale è più bassa di quella registrata
        circa N minuti fa (la lettura disponibile più vicina a quel
        momento). Se non c'è ancora abbastanza storico, restituisce False
        per prudenza (meglio aspettare un ciclo in più che accendere sulla
        base di un dato incompleto)."""
        history = getattr(self, "_winter_temp_history", [])
        if len(history) < 2:
            return False
        now = dt_util.utcnow()
        target_time = now - timedelta(minutes=minutes)
        # Trovo la lettura più vicina (per timestamp) a "minutes fa"
        past_reading = min(history, key=lambda item: abs((item[0] - target_time).total_seconds()))
        current_reading = history[-1]
        return current_reading[1] < past_reading[1]

    def _auto_mode_direction_allowed(self, wanting: str) -> bool:
        """Solo per la modalità Auto: impedisce di passare da raffrescamento
        a riscaldamento (o viceversa) troppo ravvicinati nelle giornate di
        mezza stagione. `wanting` è 'cool' o 'heat' — la direzione che si
        vorrebbe accendere ora. Non blocca mai la PRIMA accensione (nessuna
        direzione precedente registrata)."""
        last_dir = getattr(self, "_auto_last_hvac_direction", None)
        last_at = getattr(self, "_auto_last_hvac_direction_at", None)
        if last_dir is None or last_at is None or last_dir == wanting:
            return True
        elapsed = dt_util.utcnow() - last_at
        return elapsed >= timedelta(hours=SEASON_AUTO_SWITCH_COOLDOWN_HOURS)

    def _auto_mode_record_direction(self, direction: str) -> None:
        """Registra la direzione appena accesa, per il controllo cooldown
        sopra. Da chiamare ad ogni accensione automatica riuscita in modo Auto."""
        self._auto_last_hvac_direction = direction
        self._auto_last_hvac_direction_at = dt_util.utcnow()

    async def _async_handle_thermal_simple(
        self, temp: float, target: float, use_internal: bool
    ) -> None:
        """Logica termica per il modo semplificato.

        use_internal=True  → sonda interna (valori interi, soglie intere)
        use_internal=False → sonda esterna (valori decimali, soglie decimali)

        Nel modo semplificato con FV: se il clima è spento non accende —
        ci pensa solo la logica FV. La logica termica regola solo se già acceso.
        """
        real_state = self.hass.states.get(self._climate_entity)
        internal_temp: float | None = None
        if real_state is not None:
            raw = real_state.attributes.get("current_temperature")
            if raw is not None:
                try:
                    internal_temp = float(raw)
                except (TypeError, ValueError):
                    pass

        dry_enabled = bool(get_conf(self.entry, CONF_SIMPLE_DRY_ENABLED, DEFAULT_SIMPLE_DRY_ENABLED))
        no_auto_on_night = bool(get_conf(self.entry, CONF_SIMPLE_NO_AUTO_ON_NIGHT, DEFAULT_SIMPLE_NO_AUTO_ON_NIGHT))

        config_mode = self._get_config_mode()
        current_state = real_state.state if real_state else "off"
        is_on = self.hvac_mode == HVACMode.COOL or current_state == "dry"
        is_night = self._simple_is_night()
        if config_mode == CONFIG_MODE_SIMPLE_FV and not is_on and not is_night:
            return
        if no_auto_on_night and is_night and not is_on:
            return

        if use_internal:
            await self._async_thermal_simple_internal(temp, target, internal_temp, real_state, dry_enabled, is_night)
        else:
            await self._async_thermal_simple_external(temp, target, internal_temp, real_state, dry_enabled, is_night)

    async def _async_thermal_simple_internal(
        self, temp: float, target: float, internal_temp: float | None, real_state, dry_enabled: bool, is_night: bool = False
    ) -> None:
        """Logica termica con sonda interna (interi).

        Soglia accensione: target + turn_on_offset (default +1°C).
        All accensione: DRY 30 min (se abilitato), poi fascia COOL.
        Mai tornare in DRY quando già in COOL.

        Fasce COOL (target es. 25°C):
          temp ≥ target+3 (28°C) → ventola alta,  setpoint = internal-3
          temp ≥ target+2 (27°C) → ventola media, setpoint = internal-2
          temp ≥ target+1 (26°C) → ventola media, setpoint = internal-1
          temp = target   (25°C) → ventola bassa, setpoint = internal
          temp < target          → ventola bassa, setpoint = internal per 15 min → spegne
        """
        turn_on_offset = float(get_conf(self.entry, CONF_SIMPLE_TURN_ON_OFFSET, DEFAULT_SIMPLE_TURN_ON_OFFSET_INT))
        # NOTA: turn_on_offset NON viene arrotondato esplicitamente come
        # shutoff_margin — è INTENZIONALE. Dato che la sonda interna legge
        # solo interi, la condizione "temp >= target + turn_on_offset" (con
        # turn_on_offset decimale) scatta solo al primo intero che la
        # supera per davvero — garantendo SEMPRE almeno 1°C di isteresi tra
        # accensione e spegnimento. Se venisse arrotondato esplicitamente
        # come il margine di spegnimento, con margini piccoli (es. 0.4 e
        # 0.2, entrambi arrotondano a 0) le due soglie coinciderebbero,
        # azzerando l'isteresi e rischiando cicli di accensione/spegnimento
        # rapidi — verificato e scartato dopo un tentativo di "correzione"
        # che introduceva esattamente questo rischio.
        shutoff_margin_raw = float(get_conf(self.entry, CONF_SIMPLE_SHUTOFF_MARGIN, DEFAULT_SIMPLE_SHUTOFF_MARGIN))
        shutoff_margin_int = self._round_setpoint(shutoff_margin_raw)  # la sonda interna legge solo interi: arrotondiamo con la stessa regola già usata per i setpoint (≤0.5 → 0, >0.5 → 1)
        now = dt_util.utcnow()
        current_mode = real_state.state if real_state else "off"
        is_on = (self.hvac_mode == HVACMode.COOL or current_mode == "dry") and not self._is_unmanaged_real_mode()

        # --- Gestione modalità Eco attiva (invece di spento) ---
        if self._eco_mode_active:
            real_preset = real_state.attributes.get("preset_mode") if real_state else None
            really_off = current_mode in ("off", "unknown", "unavailable") and real_preset != "eco"
            if really_off:
                self._eco_mode_active = False  # spento davvero da altrove (manuale, timer, ecc.) — usciamo da Eco
                return
            if temp >= target + shutoff_margin_int:
                _LOGGER.info("%s: [semplificato] uscita da Eco, temperatura risalita (int, temp=%.0f >= target+margine=%.0f)", self._attr_name, temp, target + shutoff_margin_int)
                if await self._async_safe_climate_call("set_preset_mode", {"entity_id": self._climate_entity, "preset_mode": "none"}):
                    self._eco_mode_active = False
                    self._last_sent_setpoint = None
                    self._last_sent_fan = None
                    return
            if internal_temp is not None:
                eco_setpoint = self._round_setpoint(internal_temp)
                current_sp = real_state.attributes.get("temperature") if real_state else None
                if current_sp != eco_setpoint:
                    await self._async_safe_climate_call("set_temperature", {"entity_id": self._climate_entity, "temperature": eco_setpoint})
                    await self._async_simple_notify_temp_change(temp, target, eco=True)
            return

        # --- Spegnimento per target raggiunto ---
        if is_on:
            if temp <= target - shutoff_margin_int:
                if self._simple_shutoff_since is None:
                    self._simple_shutoff_since = now
                elif (now - self._simple_shutoff_since) >= timedelta(minutes=SIMPLE_INT_SHUTOFF_MIN):
                    eco_enabled = bool(get_conf(
                        self.entry,
                        CONF_SIMPLE_ECO_NIGHT_ENABLED if is_night else CONF_SIMPLE_ECO_DAY_ENABLED,
                        DEFAULT_SIMPLE_ECO_NIGHT_ENABLED if is_night else DEFAULT_SIMPLE_ECO_DAY_ENABLED,
                    ))
                    if eco_enabled:
                        _LOGGER.info("%s: [semplificato] ingresso in Eco invece di spegnere (int, temp=%.0f <= target-margine=%.0f)", self._attr_name, temp, target - shutoff_margin_int)
                        if await self._async_safe_climate_call("set_preset_mode", {"entity_id": self._climate_entity, "preset_mode": "eco"}):
                            self._eco_mode_active = True
                            self._simple_shutoff_since = None
                            return
                    _LOGGER.info("%s: [semplificato] spegnimento target (int, temp=%.0f <= target-margine=%.0f)", self._attr_name, temp, target - shutoff_margin_int)
                    await self._async_turn_off_climate()
                    self._simple_shutoff_since = None
                    self._cancel_dry_timer("spegnimento_target_int")
                    self._simple_night_auto_on = False
                    self._fv_auto_on = False
                    await self._async_simple_notify_ac_off(temp, target, use_internal=True)
                    return
            else:
                self._simple_shutoff_since = None

        # --- In DRY: il timer async_track_point_in_time gestisce il passaggio a COOL ---
        if current_mode == "dry":
            if self._simple_dry_end is None:
                _LOGGER.warning("%s: [int] DRY senza timer schedulato — riavvio timer", self._attr_name)
                self._schedule_dry_timer("safety_dry_senza_timer_internal")
            return

        # --- Accensione (clima spento) ---
        if not is_on:
            if self._is_manual_off_block_active():
                _LOGGER.debug("%s: accensione (int) bloccata — spento manualmente di recente", self._attr_name)
                return
            if self._temp_sensor and self._external_sensor_fallback_active:
                # La sonda esterna è configurata ma bloccata: la lettura
                # "temp" qui è quella della sonda INTERNA del Gree, che può
                # non corrispondere alla temperatura reale della stanza
                # (posizione/calibrazione diverse). Decidere una NUOVA
                # accensione su questo dato ha un costo concreto (consumo
                # inutile se sbagliato) — meglio aspettare che la sonda
                # esterna torni prima di accendere. La regolazione di un
                # clima GIÀ acceso continua invece a usare il fallback
                # normalmente, qui sotto.
                _LOGGER.debug(
                    "%s: accensione (int) sospesa — sonda esterna bloccata, non decido su dato incerto",
                    self._attr_name,
                )
                return
            if temp >= target + turn_on_offset:
                self._simple_night_auto_on = self._simple_is_night()
                self._fv_auto_on = False
                if dry_enabled:
                    _LOGGER.info("%s: [semplificato] accensione DRY (int, temp=%.0f)", self._attr_name, temp)
                    await self._async_safe_climate_call("set_hvac_mode", {"entity_id": self._climate_entity, "hvac_mode": "dry"})
                    self._schedule_dry_timer("accensione_dry_internal")
                else:
                    _LOGGER.info("%s: [semplificato] accensione COOL (int, temp=%.0f)", self._attr_name, temp)
                    await self._async_safe_climate_call("turn_on", {"entity_id": self._climate_entity})
                ac_type_int = "notturna" if self._simple_is_night() else "termica"
                await self._async_simple_notify_ac_on(temp, target, ac_type=ac_type_int)
            return

        # --- Regolazione COOL ---
        if internal_temp is None:
            return

        internal_int = int(internal_temp)

        if temp >= target + 3:
            new_setpoint = internal_int - 4
            fan = "high"
        elif temp >= target + 2:
            new_setpoint = internal_int - 3
            fan = "medium"
        elif temp >= target + 1:
            new_setpoint = internal_int - 2
            fan = "medium"
        else:
            # Sotto target+1: fascia unica fino al punto di spegnimento
            # (target - margine) — stessa spinta costante, senza il vecchio
            # salto indietro a "setpoint = interna" che rallentava proprio
            # nell'ultimo tratto prima di raggiungere il target.
            new_setpoint = internal_int - 1
            fan = "low"

        current_sp = real_state.attributes.get("temperature") if real_state else None
        current_fan = real_state.attributes.get("fan_mode") if real_state else None
        try:
            current_sp = int(float(current_sp)) if current_sp is not None else None
        except (TypeError, ValueError):
            current_sp = None

        # Confrontiamo con l'ultimo valore che ABBIAMO calcolato e inviato
        # noi, non con la lettura del dispositivo — che può restare
        # temporaneamente disallineata per un ritardo di sincronizzazione
        # (comune sui climatizzatori WiFi), causando altrimenti un nuovo
        # comando (e il relativo beep) ad ogni ciclo anche se il valore
        # desiderato non è affatto cambiato. Unico costo accettato: un
        # cambio fatto dal telecomando non viene rilevato finché il nostro
        # calcolo automatico non produce un valore diverso da quello già
        # in memoria — scelta esplicitamente richiesta per evitare i beep
        # ripetuti di notte o durante il riposo.
        # Se non abbiamo ancora memoria in questa sessione (es. subito dopo
        # un riavvio di Home Assistant col clima già acceso), usiamo la
        # lettura del dispositivo come riferimento iniziale, per non
        # forzare un invio/beep inutile se il valore era già corretto.
        reference_sp = self._last_sent_setpoint if self._last_sent_setpoint is not None else current_sp
        setpoint_needs_update = reference_sp != new_setpoint

        reference_fan = self._last_sent_fan if self._last_sent_fan is not None else current_fan
        fan_needs_update = reference_fan != fan

        if setpoint_needs_update:
            if await self._async_safe_climate_call("set_temperature", {"entity_id": self._climate_entity, "temperature": new_setpoint}):
                self._last_sent_setpoint = new_setpoint
                self._last_sent_setpoint_at = dt_util.utcnow()
            # Se il comando fallisce, NON aggiorniamo la memoria — così il
            # prossimo ciclo riprova automaticamente, invece di credere
            # (erroneamente) che il valore sia già stato applicato al
            # dispositivo reale e smettere di correggerlo per sempre.
        if fan_needs_update:
            if await self._async_safe_climate_call("set_fan_mode", {"entity_id": self._climate_entity, "fan_mode": fan}):
                self._last_sent_fan = fan
        if setpoint_needs_update or fan_needs_update:
            await self._async_simple_notify_temp_change(temp, target, fan)

    async def _async_thermal_simple_external(
        self, temp: float, target: float, internal_temp: float | None, real_state, dry_enabled: bool, is_night: bool = False
    ) -> None:
        """Logica termica con sonda esterna (decimali).

        Soglia accensione: target + turn_on_offset (default +0.8°C).
        All accensione: DRY 30 min (se abilitato), poi fascia COOL.
        Mai tornare in DRY quando già in COOL.

        Fasce COOL (target es. 25°C):
          temp ≥ target+3.1 (28.1°C) → ventola alta,  setpoint = internal-3
          temp ≥ target+1.7 (26.7°C) → ventola media, setpoint = internal-2
          temp ≥ target+0.7 (25.7°C) → ventola media, setpoint = internal-1
          temp ≥ target+0.1 (25.1°C) → ventola bassa, setpoint = internal-1
          temp = target    (25.0°C)  → ventola bassa, setpoint = internal
          temp < target              → ventola bassa, setpoint = internal per 15 min → spegne
        """
        turn_on_offset = float(get_conf(self.entry, CONF_SIMPLE_TURN_ON_OFFSET, DEFAULT_SIMPLE_TURN_ON_OFFSET_EXT))
        shutoff_margin = float(get_conf(self.entry, CONF_SIMPLE_SHUTOFF_MARGIN, DEFAULT_SIMPLE_SHUTOFF_MARGIN))
        now = dt_util.utcnow()
        current_mode = real_state.state if real_state else "off"
        is_on = (self.hvac_mode == HVACMode.COOL or current_mode == "dry") and not self._is_unmanaged_real_mode()

        # --- Gestione modalità Eco attiva (invece di spento) ---
        if self._eco_mode_active:
            real_preset = real_state.attributes.get("preset_mode") if real_state else None
            really_off = current_mode in ("off", "unknown", "unavailable") and real_preset != "eco"
            if really_off:
                self._eco_mode_active = False  # spento davvero da altrove (manuale, timer, ecc.) — usciamo da Eco
                return
            if temp >= target + shutoff_margin:
                # Risalito abbastanza — usciamo da Eco e ripartiamo come una
                # vera accensione, ricalcolando la fascia corretta (non
                # lasciamo residui della modalità Eco).
                _LOGGER.info("%s: [semplificato] uscita da Eco, temperatura risalita (temp=%.1f >= target+margine=%.1f)", self._attr_name, temp, target + shutoff_margin)
                if await self._async_safe_climate_call("set_preset_mode", {"entity_id": self._climate_entity, "preset_mode": "none"}):
                    self._eco_mode_active = False
                    self._last_sent_setpoint = None  # forza il ricalcolo della fascia al prossimo ciclo, senza cache residua
                    self._last_sent_fan = None
                    return
            # Restiamo in Eco — seguiamo la sonda interna del clima stesso,
            # senza nessuna spinta (né aggressiva né passiva), ricalcolato
            # ad ogni ciclo. Notifichiamo solo quando il setpoint cambia
            # davvero (stesso principio anti-spam della regolazione
            # normale) — altrimenti la stanza resterebbe "silenziosa" per
            # tutta la permanenza in Eco, senza nessun segnale che il
            # sistema sta ancora seguendo la temperatura.
            if internal_temp is not None:
                eco_setpoint = round(internal_temp, 1)
                current_sp = real_state.attributes.get("temperature") if real_state else None
                if current_sp != eco_setpoint:
                    await self._async_safe_climate_call("set_temperature", {"entity_id": self._climate_entity, "temperature": eco_setpoint})
                    await self._async_simple_notify_temp_change(temp, target, eco=True)
            return

        # --- Spegnimento per target raggiunto ---
        if is_on:
            if temp <= target - shutoff_margin:
                if self._simple_shutoff_since is None:
                    self._simple_shutoff_since = now
                elif (now - self._simple_shutoff_since) >= timedelta(minutes=SIMPLE_EXT_SHUTOFF_MIN):
                    eco_enabled = bool(get_conf(
                        self.entry,
                        CONF_SIMPLE_ECO_NIGHT_ENABLED if is_night else CONF_SIMPLE_ECO_DAY_ENABLED,
                        DEFAULT_SIMPLE_ECO_NIGHT_ENABLED if is_night else DEFAULT_SIMPLE_ECO_DAY_ENABLED,
                    ))
                    if eco_enabled:
                        _LOGGER.info("%s: [semplificato] ingresso in Eco invece di spegnere (temp=%.1f <= target-margine=%.1f)", self._attr_name, temp, target - shutoff_margin)
                        if await self._async_safe_climate_call("set_preset_mode", {"entity_id": self._climate_entity, "preset_mode": "eco"}):
                            self._eco_mode_active = True
                            self._simple_shutoff_since = None
                            return
                    _LOGGER.info("%s: [semplificato] spegnimento target (ext, temp=%.1f <= target-margine=%.1f)", self._attr_name, temp, target - shutoff_margin)
                    await self._async_turn_off_climate()
                    self._simple_shutoff_since = None
                    self._cancel_dry_timer("spegnimento_target_ext")
                    self._simple_night_auto_on = False
                    self._fv_auto_on = False
                    await self._async_simple_notify_ac_off(temp, target, use_internal=False)
                    return
            else:
                self._simple_shutoff_since = None

        # --- Passaggio da DRY a COOL dopo timer ---
        if current_mode == "dry":
            if self._simple_dry_end is None:
                _LOGGER.warning("%s: [ext] DRY senza timer schedulato — riavvio timer", self._attr_name)
                self._schedule_dry_timer("safety_dry_senza_timer_external")
            return

        # --- Accensione (clima spento) ---
        if not is_on:
            if self._is_manual_off_block_active():
                _LOGGER.debug("%s: accensione (ext) bloccata — spento manualmente di recente", self._attr_name)
                return
            if temp >= target + turn_on_offset:
                self._simple_night_auto_on = self._simple_is_night()
                self._fv_auto_on = False
                if dry_enabled:
                    _LOGGER.info("%s: [semplificato] accensione DRY (ext, temp=%.1f)", self._attr_name, temp)
                    await self._async_safe_climate_call("set_hvac_mode", {"entity_id": self._climate_entity, "hvac_mode": "dry"})
                    self._schedule_dry_timer("accensione_dry_external")
                else:
                    _LOGGER.info("%s: [semplificato] accensione COOL (ext, temp=%.1f)", self._attr_name, temp)
                    await self._async_safe_climate_call("turn_on", {"entity_id": self._climate_entity})
                ac_type_ext = "notturna" if self._simple_is_night() else "termica"
                await self._async_simple_notify_ac_on(temp, target, ac_type=ac_type_ext)
            return

        # --- Regolazione COOL ---
        if internal_temp is None:
            return

        if temp >= target + 3.1:
            new_setpoint = internal_temp - 4.0
            fan = "high"
        elif temp >= target + 1.7:
            new_setpoint = internal_temp - 3.0
            fan = "medium"
        elif temp >= target + 0.4:
            new_setpoint = internal_temp - 2.0
            fan = "medium"
        else:
            # Sotto target+0.4, fino al punto di spegnimento (target -
            # margine): fascia unica con spinta costante — non c'è più il
            # vecchio salto a "setpoint = interna" quando si raggiungeva
            # esattamente il target, che rallentava proprio nell'ultimo
            # tratto prima di stabilizzarsi.
            new_setpoint = internal_temp - 1.0
            fan = "low"

        new_setpoint_r = self._round_setpoint(new_setpoint)
        current_sp = real_state.attributes.get("temperature") if real_state else None
        current_fan = real_state.attributes.get("fan_mode") if real_state else None
        try:
            current_sp_r = self._round_setpoint(float(current_sp)) if current_sp is not None else None
        except (TypeError, ValueError):
            current_sp_r = None

        # Vedi commento nella versione "interna" — confronto puro col nostro
        # ultimo valore inviato (nessun limite di tempo), con fallback alla
        # lettura del dispositivo solo se non abbiamo ancora memoria in
        # questa sessione (es. subito dopo un riavvio di Home Assistant).
        reference_sp_r = self._last_sent_setpoint if self._last_sent_setpoint is not None else current_sp_r
        setpoint_needs_update = reference_sp_r != new_setpoint_r

        reference_fan = self._last_sent_fan if self._last_sent_fan is not None else current_fan
        fan_needs_update = reference_fan != fan

        if setpoint_needs_update:
            if await self._async_safe_climate_call("set_temperature", {"entity_id": self._climate_entity, "temperature": new_setpoint_r}):
                self._last_sent_setpoint = new_setpoint_r
                self._last_sent_setpoint_at = dt_util.utcnow()
        if fan_needs_update:
            if await self._async_safe_climate_call("set_fan_mode", {"entity_id": self._climate_entity, "fan_mode": fan}):
                self._last_sent_fan = fan
        if setpoint_needs_update or fan_needs_update:
            await self._async_simple_notify_temp_change(temp, target, fan)


    async def _async_handle_fv_turn_on_simple(self, temp: float, target: float) -> None:
        """Accensione FV per il modo semplificato.

        Accende solo se:
        1. Clima completamente spento (non in DRY, non in COOL)
        2. Temperatura ≥ soglia configurata
        3. FV surplus > margine E SOC > minimo
        4. Priorità e stagger rispettati
        5. Non siamo in limbo post-notte
        """
        # Non intervenire se il clima è già acceso in qualsiasi modalità (COOL o DRY)
        real_state = self.hass.states.get(self._climate_entity)
        if real_state and real_state.state not in ("off", "unknown", "unavailable"):
            return
        if self._simple_is_in_limbo():
            return
        if self._is_manual_off_block_active():
            _LOGGER.debug("%s: accensione FV bloccata — spento manualmente di recente", self._attr_name)
            return

        # Check temperatura
        use_internal = self._should_use_internal_probe()
        turn_on_offset = float(get_conf(self.entry, CONF_SIMPLE_TURN_ON_OFFSET,
            DEFAULT_SIMPLE_TURN_ON_OFFSET_INT if use_internal else DEFAULT_SIMPLE_TURN_ON_OFFSET_EXT))
        if temp < target + turn_on_offset:
            return  # non fa abbastanza caldo

        # Check FV
        if not (self._fv_sensor and self._consumption_sensor and self._battery_sensor):
            return
        fv = self._read_float(self._fv_sensor)
        consumo = self._read_float(self._consumption_sensor)
        if fv is None or consumo is None:
            return

        # Check temperatura — deve fare abbastanza caldo per giustificare l'accensione
        use_internal = self._should_use_internal_probe()
        turn_on_offset = float(get_conf(self.entry, CONF_SIMPLE_TURN_ON_OFFSET,
            DEFAULT_SIMPLE_TURN_ON_OFFSET_INT if use_internal else DEFAULT_SIMPLE_TURN_ON_OFFSET_EXT))
        if temp < target + turn_on_offset:
            return  # non fa abbastanza caldo

        margin = float(get_conf(self.entry, CONF_FV_MARGIN_W, DEFAULT_FV_MARGIN_W))
        soc_min = float(get_conf(self.entry, CONF_SOC_MIN, DEFAULT_SOC_MIN))

        # Check SOC solo se la batteria è configurata
        if self._battery_sensor:
            soc = self._read_float(self._battery_sensor)
            if soc is None:
                return  # Sensore batteria non disponibile — aspetta
            if soc < soc_min:
                return  # Batteria sotto soglia — riprova al prossimo ciclo

        if not (fv > consumo + margin):
            self._fv_turnon_confirmed_since = None  # condizione non soddisfatta, azzero il timer di conferma
            return  # FV insufficiente — riprova al prossimo ciclo

        # Conferma temporale — stesso principio della riaccensione, per
        # evitare che condizioni favorevoli solo momentanee (es. subito
        # dopo che un'altra istanza si è spenta, liberando surplus) portino
        # a un'accensione troppo rapida che potrebbe rivelarsi ingiustificata.
        now_confirm = dt_util.utcnow()
        if self._fv_turnon_confirmed_since is None:
            self._fv_turnon_confirmed_since = now_confirm
            return  # primo ciclo favorevole, aspettiamo la conferma
        turn_on_total_minutes = float(get_conf(self.entry, CONF_FV_TURN_ON_TOTAL_MINUTES, DEFAULT_FV_TURN_ON_TOTAL_MINUTES))
        if (now_confirm - self._fv_turnon_confirmed_since) < timedelta(minutes=turn_on_total_minutes):
            return  # non ancora confermato abbastanza a lungo

        # Priorità PRIMA dello stagger: la ricerca tra le sorelle deve
        # sempre poter avvenire, anche se lo stagger bloccherebbe LA MIA
        # accensione — altrimenti, con più stanze pronte contemporaneamente
        # (il caso più comune), vince semplicemente chi completa per prima
        # il PROPRIO timer di conferma personale, un fattore indipendente
        # dalla priorità configurata — vanificando il coordinamento.
        coord = self.hass.data.setdefault(DOMAIN, {}).setdefault("_coordination", {})
        stagger_min = float(get_conf(self.entry, CONF_FV_STAGGER_MIN, DEFAULT_FV_STAGGER_MIN))

        # Priorità: se un'altra istanza (sorella) ha priorità più alta (numero
        # più basso) ed è ANCH'ESSA pronta ad accendersi in questo momento
        # (clima spento, non in limbo, non bloccata manualmente, temperatura
        # sopra la sua soglia), le cedo il turno rimandando la mia accensione
        # al ciclo successivo.
        my_priority = self._effective_priority()
        for entry_data in self.hass.data.get(DOMAIN, {}).values():
            if not isinstance(entry_data, dict):
                continue
            sibling = entry_data.get("climate")
            if sibling is None or sibling is self:
                continue
            if sibling._get_config_mode() != CONFIG_MODE_SIMPLE_FV:
                continue
            sib_real_state = self.hass.states.get(sibling._climate_entity)
            if sib_real_state is None or sib_real_state.state not in ("off", "unknown", "unavailable"):
                continue
            if not sibling._switch_state(SWITCH_KEY_MASTER, True):
                continue  # sibling disabilitato — non può mai accendersi, non gli cedo il turno
            if not sibling._switch_state(SWITCH_KEY_FV, True):
                continue  # sibling con FV disattivato — non si accenderà mai da FV, non gli cedo il turno
            if sibling._simple_is_in_limbo() or sibling._is_manual_off_block_active():
                continue
            if sibling._power_limit_off:
                continue  # spenta per limite potenza — non aggirare quella protezione riaccendendola qui
            sib_temp = sibling._simple_read_temp()
            if sib_temp is None:
                continue
            sib_target = sibling._simple_current_target()
            sib_use_internal = not bool(sibling._temp_sensor)
            sib_offset = float(get_conf(sibling.entry, CONF_SIMPLE_TURN_ON_OFFSET,
                DEFAULT_SIMPLE_TURN_ON_OFFSET_INT if sib_use_internal else DEFAULT_SIMPLE_TURN_ON_OFFSET_EXT))
            if sib_temp < sib_target + sib_offset:
                continue  # il sibling non è comunque pronto ad accendersi ora

            # Non basta che il sibling abbia la temperatura giusta — deve
            # avere anche LE SUE condizioni FV/batteria soddisfatte,
            # altrimenti non è realmente pronto e non ha senso aspettarlo
            # indefinitamente. Bug reale osservato: una stanza a priorità
            # più bassa ma soglia batteria più permissiva restava bloccata
            # in attesa di una sorella a priorità più alta ma soglia più
            # severa, anche quando quella sorella non poteva ancora
            # accendersi per conto suo.
            if sibling._fv_sensor and sibling._consumption_sensor:
                sib_fv = sibling._read_float(sibling._fv_sensor)
                sib_consumo = sibling._read_float(sibling._consumption_sensor)
                if sib_fv is None or sib_consumo is None:
                    continue  # dati FV del sibling non disponibili — non è verificabile come pronto
                sib_margin = float(get_conf(sibling.entry, CONF_FV_MARGIN_W, DEFAULT_FV_MARGIN_W))
                if not (sib_fv > sib_consumo + sib_margin):
                    continue  # il sibling non ha comunque abbastanza surplus FV — non è pronto
                if sibling._battery_sensor:
                    sib_soc = sibling._read_float(sibling._battery_sensor)
                    sib_soc_min = float(get_conf(sibling.entry, CONF_SOC_MIN, DEFAULT_SOC_MIN))
                    if sib_soc is None or sib_soc < sib_soc_min:
                        continue  # il sibling non ha raggiunto la SUA soglia batteria — non è pronto
            sib_priority = sibling._effective_priority()
            if sib_priority < my_priority:
                # Invece di limitarci a cedere il turno e aspettare (il che
                # farebbe restare ENTRAMBE spente finché anche la sorella
                # non completa il SUO timer di conferma personale, anche se
                # le SUE condizioni sono già dimostrate stabili ADESSO),
                # la accendiamo direttamente noi stessi in questo ciclo —
                # simmetrico a quanto già facciamo per lo spegnimento.
                # Ricontrolliamo lo stato reale subito prima di agire, per
                # ridurre (non eliminare del tutto, l'asincronia lo rende
                # intrinsecamente possibile) il rischio di una doppia
                # accensione se il suo stesso ciclo la accende in parallelo.
                #
                # Controllo dello stagger ANCHE qui — bug reale osservato:
                # questo ramo di delega non lo controllava mai (solo il
                # ramo "accendo me stesso" più sotto lo faceva), quindi più
                # istanze che trovavano ciascuna una sorella pronta DIVERSA
                # nello stesso ciclo si accendevano tutte insieme, senza
                # mai vedersi a vicenda e senza rispettare la pausa tra
                # un'accensione e l'altra.
                last_on_check = coord.get("last_fv_turn_on")
                if last_on_check is not None and (dt_util.utcnow() - last_on_check) < timedelta(minutes=stagger_min):
                    return
                sib_state_recheck = self.hass.states.get(sibling._climate_entity)
                if sib_state_recheck is None or sib_state_recheck.state not in ("off", "unknown", "unavailable"):
                    continue  # si è già accesa nel frattempo (dal suo ciclo, o da un'altra cessione) — non rifare nulla
                _LOGGER.info(
                    "%s: [semplificato FV] accendo %s al posto mio (priorità %s < %s, sue condizioni già soddisfatte)",
                    self._attr_name, sibling._attr_name, sib_priority, my_priority,
                )
                sib_dry_enabled = bool(get_conf(sibling.entry, CONF_SIMPLE_DRY_ENABLED, DEFAULT_SIMPLE_DRY_ENABLED))
                sibling._fv_auto_on = True
                # Prenotazione IMMEDIATA (prima dell'await bloccante) —
                # altrimenti più stanze che raggiungono il proprio timer di
                # conferma quasi in contemporanea vedrebbero tutte lo
                # stagger ancora "libero" e si accenderebbero insieme,
                # ignorando lo scaglionamento (stesso bug già corretto per
                # lo spegnimento).
                coord["last_fv_turn_on"] = dt_util.utcnow()
                if sib_dry_enabled:
                    await sibling._async_safe_climate_call("set_hvac_mode", {"entity_id": sibling._climate_entity, "hvac_mode": "dry"})
                    sibling._schedule_dry_timer("accensione_fv_turn_on_simple_ceduta")
                else:
                    await sibling._async_safe_climate_call("turn_on", {"entity_id": sibling._climate_entity})
                    sibling._cancel_dry_timer("accensione_fv_cool_no_dry_ceduta")
                sibling._fv_turnon_confirmed_since = None
                sibling._simple_night_auto_on = False
                sib_soc_val = sibling._read_float(sibling._battery_sensor) or 0 if sibling._battery_sensor else 0
                sib_fv_val = sibling._read_float(sibling._fv_sensor) or 0 if sibling._fv_sensor else 0
                sib_consumo_val = sibling._read_float(sibling._consumption_sensor) or 0 if sibling._consumption_sensor else 0
                await sibling._async_simple_notify_ac_on(sib_temp, sib_target, ac_type="fv", fv=sib_fv_val, consumo=sib_consumo_val, soc=sib_soc_val)
                sibling.async_write_ha_state()
                return

        # Nessuna sorella con priorità più alta pronta — verifico lo stagger
        # solo ora, per LA MIA accensione (non per la ricerca appena fatta).
        last_on = coord.get("last_fv_turn_on")
        if last_on is not None and (dt_util.utcnow() - last_on) < timedelta(minutes=stagger_min):
            return

        # Accensione — sempre DRY prima (se abilitato)
        dry_enabled = bool(get_conf(self.entry, CONF_SIMPLE_DRY_ENABLED, DEFAULT_SIMPLE_DRY_ENABLED))
        now = dt_util.utcnow()
        self._fv_auto_on = True
        coord["last_fv_turn_on"] = now
        if dry_enabled:
            _LOGGER.info("%s: [semplificato FV] accensione DRY (fv=%.0fW, consumo=%.0fW)", self._attr_name, fv, consumo)
            await self._async_safe_climate_call("set_hvac_mode", {"entity_id": self._climate_entity, "hvac_mode": "dry"})
            self._schedule_dry_timer("accensione_fv_turn_on_simple")
        else:
            _LOGGER.info("%s: [semplificato FV] accensione COOL (fv=%.0fW, consumo=%.0fW)", self._attr_name, fv, consumo)
            await self._async_safe_climate_call("turn_on", {"entity_id": self._climate_entity})
            self._cancel_dry_timer("accensione_fv_cool_no_dry")

        self._fv_turnon_confirmed_since = None
        self._simple_night_auto_on = False
        soc_val = self._read_float(self._battery_sensor) or 0
        await self._async_simple_notify_ac_on(temp, target, ac_type="fv", fv=fv, consumo=consumo, soc=soc_val)

    async def _async_handle_winter_turn_on_simple(self, temp: float, target: float) -> None:
        """Accensione invernale (riscaldamento) da FV — sempre basata sulla
        temperatura in DISCESA, con o senza sensore anello pavimento.

        Accende solo se:
        1. Clima completamente spento
        2. Temperatura in discesa rispetto a 10 minuti fa
        3. Temperatura dentro la zona [target-scarto ; target)
        4. Se configurato, l'anello del pavimento non è già acceso (evita spreco)
        5. FV surplus > margine E SOC > soglia inverno (più restrittiva)
        6. Priorità e stagger rispettati (solo tra sorelle anch'esse in inverno)
        7. Timer di conferma 15 minuti (stesso principio anti-oscillazione dell'estate)
        """
        real_state = self.hass.states.get(self._climate_entity)
        if real_state and real_state.state not in ("off", "unknown", "unavailable"):
            return
        if self._simple_is_in_limbo():
            return
        if self._is_manual_off_block_active():
            return

        winter_offset = float(get_conf(self.entry, CONF_WINTER_TURN_ON_OFFSET, DEFAULT_WINTER_TURN_ON_OFFSET))
        if not (target - winter_offset <= temp < target):
            return  # fuori dalla zona di intervento

        if not self._is_temp_descending(minutes=10):
            return  # non sta scendendo — nessun bisogno di anticipare l'impianto principale

        floor_sensor = get_conf(self.entry, CONF_WINTER_FLOOR_SENSOR)
        if floor_sensor:
            floor_state = self.hass.states.get(floor_sensor)
            if floor_state is None or floor_state.state in ("unknown", "unavailable"):
                return  # non verificabile — prudenza, aspetto che torni disponibile
            if floor_state.state == "on":
                return  # l'anello sta già scaldando questa stanza, nessun bisogno di assistenza

        if not (self._fv_sensor and self._consumption_sensor and self._battery_sensor):
            return
        fv = self._read_float(self._fv_sensor)
        consumo = self._read_float(self._consumption_sensor)
        if fv is None or consumo is None:
            return

        margin = float(get_conf(self.entry, CONF_FV_MARGIN_W, DEFAULT_FV_MARGIN_W))
        soc_min = float(get_conf(self.entry, CONF_WINTER_SOC_MIN, DEFAULT_WINTER_SOC_MIN))

        if self._battery_sensor:
            soc = self._read_float(self._battery_sensor)
            if soc is None:
                return
            if soc < soc_min:
                return

        if not (fv > consumo + margin):
            self._fv_turnon_confirmed_since = None
            return

        now_confirm = dt_util.utcnow()
        if self._fv_turnon_confirmed_since is None:
            self._fv_turnon_confirmed_since = now_confirm
            return
        turn_on_total_minutes = float(get_conf(self.entry, CONF_FV_TURN_ON_TOTAL_MINUTES, DEFAULT_FV_TURN_ON_TOTAL_MINUTES))
        if (now_confirm - self._fv_turnon_confirmed_since) < timedelta(minutes=turn_on_total_minutes):
            return

        coord = self.hass.data.setdefault(DOMAIN, {}).setdefault("_coordination", {})
        stagger_min = float(get_conf(self.entry, CONF_FV_STAGGER_MIN, DEFAULT_FV_STAGGER_MIN))

        # Priorità — solo tra sorelle anch'esse in modalità Inverno o Auto,
        # stessa logica già corretta per l'estate (verifica anche le
        # condizioni reali del sibling, non solo la temperatura).
        my_priority = self._effective_priority()
        for entry_data in self.hass.data.get(DOMAIN, {}).values():
            if not isinstance(entry_data, dict):
                continue
            sibling = entry_data.get("climate")
            if sibling is None or sibling is self:
                continue
            if sibling._get_config_mode() != CONFIG_MODE_SIMPLE_FV:
                continue
            if sibling._get_season_mode() not in (SEASON_WINTER, SEASON_AUTO):
                continue
            sib_real_state = self.hass.states.get(sibling._climate_entity)
            if sib_real_state is None or sib_real_state.state not in ("off", "unknown", "unavailable"):
                continue
            if not sibling._switch_state(SWITCH_KEY_MASTER, True):
                continue
            if not sibling._switch_state(SWITCH_KEY_FV, True):
                continue
            if sibling._simple_is_in_limbo() or sibling._is_manual_off_block_active():
                continue
            if sibling._power_limit_off:
                continue  # spenta per limite potenza — non aggirare quella protezione riaccendendola qui
            sib_temp = sibling._simple_read_temp()
            if sib_temp is None:
                continue
            sib_target = sibling._winter_current_target()
            sib_offset = float(get_conf(sibling.entry, CONF_WINTER_TURN_ON_OFFSET, DEFAULT_WINTER_TURN_ON_OFFSET))
            if not (sib_target - sib_offset <= sib_temp < sib_target):
                continue
            if not sibling._is_temp_descending(minutes=10):
                continue
            if sibling._fv_sensor and sibling._consumption_sensor:
                sib_fv = sibling._read_float(sibling._fv_sensor)
                sib_consumo = sibling._read_float(sibling._consumption_sensor)
                if sib_fv is None or sib_consumo is None:
                    continue
                sib_margin = float(get_conf(sibling.entry, CONF_FV_MARGIN_W, DEFAULT_FV_MARGIN_W))
                if not (sib_fv > sib_consumo + sib_margin):
                    continue
                if sibling._battery_sensor:
                    sib_soc = sibling._read_float(sibling._battery_sensor)
                    sib_soc_min = float(get_conf(sibling.entry, CONF_WINTER_SOC_MIN, DEFAULT_WINTER_SOC_MIN))
                    if sib_soc is None or sib_soc < sib_soc_min:
                        continue
            sib_priority = sibling._effective_priority()
            if sib_priority < my_priority:
                # Stesso controllo dello stagger aggiunto anche qui — vedi
                # commento nel ramo estivo equivalente.
                last_on_check = coord.get("last_fv_turn_on")
                if last_on_check is not None and (dt_util.utcnow() - last_on_check) < timedelta(minutes=stagger_min):
                    return
                sib_state_recheck = self.hass.states.get(sibling._climate_entity)
                if sib_state_recheck is None or sib_state_recheck.state not in ("off", "unknown", "unavailable"):
                    continue  # si è già accesa nel frattempo — non rifare nulla
                _LOGGER.info(
                    "%s: [inverno FV] accendo %s al posto mio (priorità %s < %s, sue condizioni già soddisfatte)",
                    self._attr_name, sibling._attr_name, sib_priority, my_priority,
                )
                sibling._fv_auto_on = True
                coord["last_fv_turn_on"] = dt_util.utcnow()
                await sibling._async_safe_climate_call("set_hvac_mode", {"entity_id": sibling._climate_entity, "hvac_mode": "heat"})
                sibling._fv_turnon_confirmed_since = None
                sibling._simple_night_auto_on = False
                sib_soc_val = sibling._read_float(sibling._battery_sensor) or 0 if sibling._battery_sensor else 0
                sib_fv_val_notify = sibling._read_float(sibling._fv_sensor) or 0 if sibling._fv_sensor else 0
                sib_consumo_val_notify = sibling._read_float(sibling._consumption_sensor) or 0 if sibling._consumption_sensor else 0
                await sibling._async_simple_notify_ac_on(sib_temp, sib_target, ac_type="fv_winter", fv=sib_fv_val_notify, consumo=sib_consumo_val_notify, soc=sib_soc_val)
                sibling.async_write_ha_state()
                return

        # Nessuna sorella con priorità più alta pronta — verifico lo stagger
        # solo ora, per LA MIA accensione.
        last_on = coord.get("last_fv_turn_on")
        if last_on is not None and (dt_util.utcnow() - last_on) < timedelta(minutes=stagger_min):
            return

        # Accensione — solo riscaldamento, niente equivalente del DRY
        now = dt_util.utcnow()
        self._fv_auto_on = True
        coord["last_fv_turn_on"] = now
        _LOGGER.info("%s: [inverno FV] accensione HEAT (fv=%.0fW, consumo=%.0fW, temp in discesa)", self._attr_name, fv, consumo)
        await self._async_safe_climate_call("set_hvac_mode", {"entity_id": self._climate_entity, "hvac_mode": "heat"})
        self._fv_turnon_confirmed_since = None
        self._simple_night_auto_on = False
        soc_val = self._read_float(self._battery_sensor) or 0
        await self._async_simple_notify_ac_on(temp, target, ac_type="fv_winter", fv=fv, consumo=consumo, soc=soc_val)

    async def _async_handle_thermal_winter_simple(
        self, temp: float, target: float, use_internal: bool
    ) -> None:
        """Regolazione termica invernale per un clima già acceso in HEAT
        (es. durante l'emergenza riscaldamento). Fasce ventola/setpoint
        speculari all'estate (spinta verso l'ALTO invece che verso il
        basso), spegnimento quando il target è raggiunto con margine."""
        real_state = self.hass.states.get(self._climate_entity)
        if real_state is None or real_state.state != "heat":
            return
        shutoff_margin = float(get_conf(self.entry, CONF_WINTER_SHUTOFF_MARGIN, DEFAULT_WINTER_SHUTOFF_MARGIN))
        if temp >= target + shutoff_margin:
            _LOGGER.info("%s: [inverno] spegnimento target (temp=%.1f >= target+margine=%.1f)", self._attr_name, temp, target + shutoff_margin)
            await self._async_simple_notify_ac_off(temp, target, use_internal=use_internal)
            await self._async_turn_off_climate()
            self._fv_auto_on = False
            return
        internal_temp = self._read_float(self._climate_entity, attr="current_temperature")
        if internal_temp is None:
            internal_temp = temp

        # Fasce speculari all'estate: più siamo LONTANI (sotto) dal target,
        # più la spinta è aggressiva e la ventola alta.
        if use_internal:
            internal_int = int(internal_temp)
            if temp <= target - 3:
                new_setpoint = internal_int + 4
                fan = "high"
            elif temp <= target - 2:
                new_setpoint = internal_int + 3
                fan = "medium"
            elif temp <= target - 1:
                new_setpoint = internal_int + 2
                fan = "medium"
            else:
                new_setpoint = internal_int + 1
                fan = "low"
            new_setpoint = self._round_setpoint(new_setpoint)
        else:
            if temp <= target - 3.1:
                new_setpoint = internal_temp + 4.0
                fan = "high"
            elif temp <= target - 1.7:
                new_setpoint = internal_temp + 3.0
                fan = "medium"
            elif temp <= target - 0.4:
                new_setpoint = internal_temp + 2.0
                fan = "medium"
            else:
                new_setpoint = internal_temp + 1.0
                fan = "low"
            new_setpoint = round(new_setpoint, 1)

        current_sp = real_state.attributes.get("temperature")
        current_fan = real_state.attributes.get("fan_mode")
        reference_sp = self._last_sent_setpoint if self._last_sent_setpoint is not None else current_sp
        setpoint_needs_update = reference_sp != new_setpoint
        reference_fan = self._last_sent_fan if self._last_sent_fan is not None else current_fan
        fan_needs_update = reference_fan != fan

        if setpoint_needs_update:
            if await self._async_safe_climate_call("set_temperature", {"entity_id": self._climate_entity, "temperature": new_setpoint}):
                self._last_sent_setpoint = new_setpoint
                self._last_sent_setpoint_at = dt_util.utcnow()
        if fan_needs_update:
            if await self._async_safe_climate_call("set_fan_mode", {"entity_id": self._climate_entity, "fan_mode": fan}):
                self._last_sent_fan = fan

    async def _async_handle_winter_shutoff_simple(self, temp: float, target: float) -> None:
        """Spegnimento invernale — ora equivalente all'estate: buffer di 4
        campioni consecutivi prima di spegnere per surplus insufficiente
        (non più il primo ciclo), e coordinamento di priorità (spegne la
        sorella con priorità più bassa se la SUA soglia è già raggiunta dal
        surplus attuale). Il caso "target raggiunto" resta invariato, senza
        bisogno di conferma né coordinamento — è un evento diverso."""
        if not self._fv_auto_on:
            return  # non è stato acceso da noi per FV — non tocchiamo nulla
        current_state = self.hass.states.get(self._climate_entity)
        is_heat_on = current_state is not None and current_state.state == "heat"
        if not is_heat_on:
            return

        if temp >= target:
            _LOGGER.info("%s: [inverno FV] spegnimento — target raggiunto (temp=%.1f >= target=%.1f)", self._attr_name, temp, target)
            await self._async_simple_notify_ac_off(temp, target)
            await self._async_turn_off_climate()
            self._fv_auto_on = False
            return

        if not (self._fv_sensor and self._consumption_sensor):
            return
        fv = self._read_float(self._fv_sensor)
        consumo = self._read_float(self._consumption_sensor)
        if fv is None or consumo is None:
            return

        surplus = fv - consumo
        threshold = float(get_conf(self.entry, CONF_FV_SHUTOFF_THRESHOLD, DEFAULT_FV_SHUTOFF_THRESHOLD))
        delay_min = FV_SHUTOFF_SAMPLES_FIXED

        if surplus < threshold:
            if self._fv_low_since is None:
                self._fv_low_since = dt_util.utcnow()
        else:
            self._fv_low_since = None

        self._fv_surplus_buffer.append(surplus)
        if len(self._fv_surplus_buffer) > delay_min:
            self._fv_surplus_buffer.pop(0)

        should_shutoff = (
            len(self._fv_surplus_buffer) >= delay_min
            and all(s < threshold for s in self._fv_surplus_buffer)
        )
        if not should_shutoff:
            return

        # Stesso coordinamento di priorità già applicato all'estate: prima
        # di spegnere ME STESSO, verifico se una sorella con priorità PIÙ
        # BASSA ha la SUA soglia già raggiunta dal surplus attuale — se sì,
        # spengo LEI al posto mio.
        target_to_shutoff = self
        target_temp = temp
        target_target = target
        my_priority = self._effective_priority()
        best_candidate = None
        best_priority = my_priority
        for entry_data in self.hass.data.get(DOMAIN, {}).values():
            if not isinstance(entry_data, dict):
                continue
            sibling = entry_data.get("climate")
            if sibling is None or sibling is self:
                continue
            if not sibling._fv_auto_on:
                continue
            sib_real_state = self.hass.states.get(sibling._climate_entity)
            if sib_real_state is None or sib_real_state.state in ("off", "unknown", "unavailable"):
                continue
            sib_threshold = float(get_conf(sibling.entry, CONF_FV_SHUTOFF_THRESHOLD, DEFAULT_FV_SHUTOFF_THRESHOLD))
            if surplus >= sib_threshold:
                continue
            sib_priority = sibling._effective_priority()
            if sib_priority > best_priority:
                best_priority = sib_priority
                best_candidate = sibling
        if best_candidate is not None:
            _LOGGER.debug(
                "%s: [inverno FV] spengo %s al posto mio (priorità %s > %s, soglia sua già raggiunta dal surplus attuale %.0fW)",
                self._attr_name, best_candidate._attr_name, best_priority, my_priority, surplus,
            )
            target_to_shutoff = best_candidate
            sib_temp_val = target_to_shutoff._simple_read_temp()
            target_temp = sib_temp_val if sib_temp_val is not None else temp
            target_target = target_to_shutoff._winter_current_target()

        _LOGGER.info("%s: [inverno FV] spegnimento — surplus insufficiente", target_to_shutoff._attr_name)
        await target_to_shutoff._async_simple_notify_ac_off(target_temp, target_target, fv_shutoff=True)
        await target_to_shutoff._async_turn_off_climate()
        target_to_shutoff._fv_auto_on = False
        target_to_shutoff._fv_surplus_buffer = []
        target_to_shutoff._fv_low_since = None
        target_to_shutoff.async_write_ha_state()

    # ------------------------------------------------------------------
    # Notifiche modo semplificato
    # ------------------------------------------------------------------

    async def _async_simple_speak(self, message: str) -> None:
        """TTS per modo semplificato — silenzia di notte se configurato.

        Distanziatore vocale: se un'altra istanza ha parlato negli ultimi
        20 secondi, aspettiamo il tempo rimanente prima di parlare a nostra
        volta, per evitare che due annunci si sovrappongano su Google Home
        quando più stanze generano eventi quasi nello stesso momento (es.
        porte multiple, o il nuovo controllo sensore FV offline).
        """
        players = get_conf(self.entry, CONF_TTS_PLAYERS, [])
        if not players:
            return
        if self._simple_is_quiet_night() and bool(get_conf(self.entry, CONF_SIMPLE_QUIET_NIGHT_TTS, DEFAULT_SIMPLE_QUIET_NIGHT_TTS)):
            _LOGGER.debug("%s: [semplificato] TTS soppresso (notte)", self._attr_name)
            return

        coord = self.hass.data.setdefault(DOMAIN, {}).setdefault("_coordination", {})
        voice_gap = timedelta(seconds=20)
        last_voice_at = coord.get("last_voice_notify_at")
        now = dt_util.utcnow()
        if last_voice_at is not None:
            elapsed = now - last_voice_at
            if elapsed < voice_gap:
                wait_seconds = (voice_gap - elapsed).total_seconds()
                _LOGGER.debug("%s: [semplificato] TTS in coda, attendo %.1fs per non sovrappormi", self._attr_name, wait_seconds)
                await asyncio.sleep(wait_seconds)

        engine = get_conf(self.entry, CONF_TTS_ENGINE)
        if not engine:
            tts_states = self.hass.states.async_all("tts")
            if not tts_states:
                return
            engine = tts_states[0].entity_id
        await self.hass.services.async_call(
            "tts", "speak",
            {"entity_id": engine, "media_player_entity_id": players, "message": message, "cache": True},
            blocking=True,
        )
        coord["last_voice_notify_at"] = dt_util.utcnow()

    async def _async_simple_notify(self, message: str, bypass_quiet: bool = False) -> None:
        """Notifica Telegram per modo semplificato — silenzia di notte se configurato."""
        targets = get_conf(self.entry, CONF_NOTIFY_TARGETS, [])
        chat_ids = get_conf(self.entry, CONF_NOTIFY_CHAT_IDS)
        if not targets and not chat_ids:
            return
        if not bypass_quiet and self._simple_is_quiet_night() and bool(get_conf(self.entry, CONF_SIMPLE_QUIET_NIGHT_NOTIFY, DEFAULT_SIMPLE_QUIET_NIGHT_NOTIFY)):
            _LOGGER.debug("%s: [semplificato] notifica soppressa (notte)", self._attr_name)
            return
        if targets:
            await self.hass.services.async_call("notify", "send_message", {"entity_id": targets, "message": message}, blocking=True)
        elif chat_ids:
            ids = [c.strip() for c in str(chat_ids).split(",") if c.strip()]
            await self.hass.services.async_call("telegram_bot", "send_message", {"target": ids, "message": message}, blocking=True)
        else:
            return
        self._last_notify_event = {
            "timestamp": dt_util.utcnow().isoformat(),
            "messaggio": message,
        }
        self._notify_history.insert(0, self._last_notify_event)
        self._notify_history = self._notify_history[:8]  # solo gli ultimi 8, per non far crescere lo stato all'infinito

    async def _async_handle_fv_shutoff_simple(self, temp: float, target: float) -> None:
        """Spegnimento e riaccensione FV per il modo semplificato.

        4 casi per spegnimento:
        1. Acceso di notte automaticamente → non spegnere mai per FV
        2. Acceso dal FV → spegne sempre se FV insufficiente, riaccende quando torna
        3. Acceso manualmente prima di tramonto-Xh → spegne se FV insufficiente
        4. Acceso manualmente dopo tramonto-Xh → non toccare

        Riaccensione: se il clima è spento per FV e la produzione torna
        sufficiente + temperatura ancora sopra soglia → riaccende da DRY.
        """
        if not (self._fv_sensor and self._consumption_sensor):
            return

        fv = self._read_float(self._fv_sensor)
        consumo = self._read_float(self._consumption_sensor)
        if fv is None or consumo is None:
            return

        current_state = self.hass.states.get(self._climate_entity)
        is_on = self.hvac_mode == HVACMode.COOL or (
            current_state and current_state.state == "dry"
        )
        if not is_on and self._fv_auto_on:
            _LOGGER.info(
                "%s: [semplificato FV] rilevato is_on=False con _fv_auto_on=True — stato reale attuale = %s (entra nel ramo riaccensione anche se potrebbe essere già accesa)",
                self._attr_name, current_state.state if current_state else "None",
            )

        # --- Riaccensione dopo spegnimento FV ---
        # Se il clima è spento, era stato acceso dal FV, e il FV è tornato sufficiente
        if not is_on and self._fv_auto_on:
            margin = float(get_conf(self.entry, CONF_FV_MARGIN_W, DEFAULT_FV_MARGIN_W))
            soc_min = float(get_conf(self.entry, CONF_SOC_MIN, DEFAULT_SOC_MIN))
            soc = self._read_float(self._battery_sensor)
            use_internal = self._should_use_internal_probe()
            turn_on_offset = float(get_conf(self.entry, CONF_SIMPLE_TURN_ON_OFFSET,
                DEFAULT_SIMPLE_TURN_ON_OFFSET_INT if use_internal else DEFAULT_SIMPLE_TURN_ON_OFFSET_EXT))
            fv_ok = fv > consumo + margin and (soc is None or soc > soc_min)
            temp_ok = temp >= target + turn_on_offset
            conditions_ok = fv_ok and temp_ok and not self._simple_is_in_limbo() and not self._is_manual_off_block_active()
            now = dt_util.utcnow()

            if not conditions_ok:
                # Le condizioni non sono (più) favorevoli in questo ciclo —
                # azzeriamo il timer di conferma, si riparte da zero la
                # prossima volta che tornano favorevoli.
                self._fv_turnon_confirmed_since = None
                return

            # Le condizioni sono favorevoli — verifichiamo che lo siano state
            # in modo CONTINUATIVO per il tempo configurato prima di
            # riaccendere davvero. Senza questa conferma, spegnersi per FV
            # insufficiente riduce il consumo della casa, il che può far
            # apparire il surplus improvvisamente sufficiente al ciclo
            # successivo — un'oscillazione spegni/riaccendi in pochissimo
            # tempo (visto in produzione: meno di un minuto tra i due).
            if self._fv_turnon_confirmed_since is None:
                self._fv_turnon_confirmed_since = now
                return  # primo ciclo favorevole, aspettiamo la conferma
            turn_on_total_minutes = float(get_conf(self.entry, CONF_FV_TURN_ON_TOTAL_MINUTES, DEFAULT_FV_TURN_ON_TOTAL_MINUTES))
            if (now - self._fv_turnon_confirmed_since) < timedelta(minutes=turn_on_total_minutes):
                return  # non ancora confermato abbastanza a lungo

            # Stesso principio già applicato all'accensione principale:
            # prima di accendere ME STESSO, verifico le sorelle con
            # priorità PIÙ ALTA (numero più basso) le cui condizioni
            # ISTANTANEE sono già soddisfatte — se sì, accendo LEI al
            # posto mio, senza farla aspettare il suo timer personale.
            my_priority = self._effective_priority()
            for entry_data in self.hass.data.get(DOMAIN, {}).values():
                if not isinstance(entry_data, dict):
                    continue
                sibling = entry_data.get("climate")
                if sibling is None or sibling is self:
                    continue
                if sibling._get_config_mode() != CONFIG_MODE_SIMPLE_FV:
                    continue
                sib_real_state = self.hass.states.get(sibling._climate_entity)
                if sib_real_state is None or sib_real_state.state not in ("off", "unknown", "unavailable"):
                    continue
                if not sibling._switch_state(SWITCH_KEY_MASTER, True):
                    continue
                if not sibling._switch_state(SWITCH_KEY_FV, True):
                    continue
                if sibling._simple_is_in_limbo() or sibling._is_manual_off_block_active():
                    continue
                if sibling._power_limit_off:
                    continue
                sib_temp = sibling._simple_read_temp()
                if sib_temp is None:
                    continue
                sib_target = sibling._simple_current_target()
                sib_use_internal = not bool(sibling._temp_sensor)
                sib_offset = float(get_conf(sibling.entry, CONF_SIMPLE_TURN_ON_OFFSET,
                    DEFAULT_SIMPLE_TURN_ON_OFFSET_INT if sib_use_internal else DEFAULT_SIMPLE_TURN_ON_OFFSET_EXT))
                if sib_temp < sib_target + sib_offset:
                    continue
                if sibling._fv_sensor and sibling._consumption_sensor:
                    sib_fv = sibling._read_float(sibling._fv_sensor)
                    sib_consumo = sibling._read_float(sibling._consumption_sensor)
                    if sib_fv is None or sib_consumo is None:
                        continue
                    sib_margin = float(get_conf(sibling.entry, CONF_FV_MARGIN_W, DEFAULT_FV_MARGIN_W))
                    if not (sib_fv > sib_consumo + sib_margin):
                        continue
                    if sibling._battery_sensor:
                        sib_soc = sibling._read_float(sibling._battery_sensor)
                        sib_soc_min = float(get_conf(sibling.entry, CONF_SOC_MIN, DEFAULT_SOC_MIN))
                        if sib_soc is None or sib_soc < sib_soc_min:
                            continue
                sib_priority = sibling._effective_priority()
                if sib_priority < my_priority:
                    sib_state_recheck = self.hass.states.get(sibling._climate_entity)
                    if sib_state_recheck is None or sib_state_recheck.state not in ("off", "unknown", "unavailable"):
                        continue
                    if sibling._is_manual_off_block_active():
                        continue
                    _LOGGER.info(
                        "%s: [semplificato FV] accendo %s al posto mio (riaccensione fuori finestra, priorità %s < %s)",
                        self._attr_name, sibling._attr_name, sib_priority, my_priority,
                    )
                    sib_dry_enabled = bool(get_conf(sibling.entry, CONF_SIMPLE_DRY_ENABLED, DEFAULT_SIMPLE_DRY_ENABLED))
                    sibling._fv_auto_on = True
                    if sib_dry_enabled:
                        await sibling._async_safe_climate_call("set_hvac_mode", {"entity_id": sibling._climate_entity, "hvac_mode": "dry"})
                        sibling._schedule_dry_timer("riaccensione_fv_dopo_calo_ceduta")
                    else:
                        await sibling._async_safe_climate_call("turn_on", {"entity_id": sibling._climate_entity})
                        sibling._cancel_dry_timer("riaccensione_fv_cool_no_dry_ceduta")
                    sibling._fv_surplus_buffer = []
                    sibling._fv_low_since = None
                    sibling._manual_accension_since = None
                    sibling._fv_turnon_confirmed_since = None
                    sib_soc_val = sibling._read_float(sibling._battery_sensor) or 0 if sibling._battery_sensor else 0
                    sib_fv_val = sibling._read_float(sibling._fv_sensor) or 0 if sibling._fv_sensor else 0
                    sib_consumo_val = sibling._read_float(sibling._consumption_sensor) or 0 if sibling._consumption_sensor else 0
                    await sibling._async_simple_notify_ac_on(sib_temp, sib_target, ac_type="fv", fv=sib_fv_val, consumo=sib_consumo_val, soc=sib_soc_val)
                    sibling.async_write_ha_state()
                    return

            if self._is_manual_off_block_active():
                return

            dry_enabled = bool(get_conf(self.entry, CONF_SIMPLE_DRY_ENABLED, DEFAULT_SIMPLE_DRY_ENABLED))
            self._fv_auto_on = True
            if dry_enabled:
                _LOGGER.info("%s: [semplificato FV] riaccensione DRY dopo calo FV (confermata %s min)", self._attr_name, turn_on_total_minutes)
                await self._async_safe_climate_call("set_hvac_mode", {"entity_id": self._climate_entity, "hvac_mode": "dry"})
                self._schedule_dry_timer("riaccensione_fv_dopo_calo")
            else:
                _LOGGER.info("%s: [semplificato FV] riaccensione COOL dopo calo FV (confermata %s min)", self._attr_name, turn_on_total_minutes)
                await self._async_safe_climate_call("turn_on", {"entity_id": self._climate_entity})
                self._cancel_dry_timer("riaccensione_fv_cool_no_dry")
            self._fv_surplus_buffer = []
            self._fv_low_since = None
            self._manual_accension_since = None
            self._fv_turnon_confirmed_since = None
            soc_val2 = self._read_float(self._battery_sensor) or 0
            fv2 = self._read_float(self._fv_sensor) or 0
            consumo2 = self._read_float(self._consumption_sensor) or 0
            await self._async_simple_notify_ac_on(temp, target, ac_type="fv", fv=fv2, consumo=consumo2, soc=soc_val2)
            return

        if not is_on:
            self._fv_surplus_buffer = []
            self._fv_low_since = None
            self._manual_accension_since = None
            return

        # Caso 1: acceso dalla modalità notturna → FV non interviene
        if self._simple_night_auto_on:
            self._fv_surplus_buffer = []
            self._fv_low_since = None
            self._manual_accension_since = None
            return

        # Protezione SEMPRE ATTIVA, indipendente da "shutoff_manual": se il
        # sole è genuinamente sotto l'orizzonte (notte vera, non solo
        # "vicino al tramonto"), lo spegnimento per FV insufficiente non ha
        # senso — di notte il FV è sempre a zero per definizione, quindi
        # "spegni per FV insufficiente" non è una decisione basata sulla
        # produzione, sarebbe solo uno spegnimento a orario mascherato da
        # logica FV. L'opzione "shutoff_manual" estende lo spegnimento alle
        # accensioni manuali fatte DI GIORNO (vicino al tramonto, prima
        # della soglia di anticipo configurata) — non deve mai bypassare
        # questa protezione notturna.
        if not self._fv_auto_on:
            sun_state = self.hass.states.get("sun.sun")
            if sun_state is not None and sun_state.state != "above_horizon":
                self._fv_surplus_buffer = []
                self._fv_low_since = None
                self._manual_accension_since = None
                return

        # Caso 2/3/4: verifica se può spegnere
        shutoff_manual = bool(get_conf(self.entry, CONF_FV_SHUTOFF_MANUAL, DEFAULT_FV_SHUTOFF_MANUAL))
        if not self._fv_auto_on and not self._simple_can_control_manual() and not shutoff_manual:
            self._fv_surplus_buffer = []
            self._fv_low_since = None
            self._manual_accension_since = None
            return

        # Sliding window — campioni fissi a 4 (il tempo totale è regolato
        # tramite l'intervallo del ciclo dedicato, calcolato da CONF_FV_SHUTOFF_TOTAL_MINUTES)
        # Usata SOLO per lo spegnimento di un'accensione fatta dal FV stesso.
        surplus = fv - consumo
        threshold = float(get_conf(self.entry, CONF_FV_SHUTOFF_THRESHOLD, DEFAULT_FV_SHUTOFF_THRESHOLD))
        delay_min = FV_SHUTOFF_SAMPLES_FIXED

        # Traccia da quando il surplus è insufficiente in modo continuativo.
        # Si azzera appena il surplus torna sopra soglia anche per un solo
        # campione — questo stesso timestamp è anche il riferimento per il
        # ritardo di spegnimento di un'accensione MANUALE (vedi sotto): se
        # resta impostato per tutta la durata configurata, vuol dire che il
        # FV non si è mai ripreso nel frattempo.
        if surplus < threshold:
            if self._fv_low_since is None:
                self._fv_low_since = dt_util.utcnow()
        else:
            self._fv_low_since = None

        self._fv_surplus_buffer.append(surplus)
        if len(self._fv_surplus_buffer) > delay_min:
            self._fv_surplus_buffer.pop(0)

        _LOGGER.debug(
            "%s: [semplificato FV] shutoff buffer %s (soglia=%.0f)",
            self._attr_name, [round(s) for s in self._fv_surplus_buffer], threshold,
        )

        now = dt_util.utcnow()

        # Se l'accensione era MANUALE (non fatta dal FV) e l'opzione "spegni
        # anche se acceso manualmente" è attiva: per un periodo fisso dal
        # momento dell'accensione (non da quando si rileva il calo FV),
        # qualsiasi spegnimento automatico viene semplicemente IGNORATO —
        # non rimandato, proprio ignorato, come se questa logica non
        # esistesse per quella finestra di tempo. Passato quel periodo,
        # il controllo standard riprende a funzionare normalmente, da capo,
        # sui campioni più recenti.
        if shutoff_manual and not self._fv_auto_on and self._manual_accension_since is not None:
            manual_delay_min = float(get_conf(self.entry, CONF_FV_SHUTOFF_MANUAL_DELAY_MIN, DEFAULT_FV_SHUTOFF_MANUAL_DELAY_MIN))
            elapsed = now - self._manual_accension_since
            if elapsed < timedelta(minutes=manual_delay_min):
                return  # dentro la finestra di immunità — ignora completamente

        # Verifica standard: FV insufficiente confermato da 4 campioni pieni
        # (lo stesso identico controllo usato per un'accensione fatta dal FV,
        # e usato anche per un'accensione manuale una volta scaduta la
        # finestra di immunità qui sopra).
        should_shutoff = (
            len(self._fv_surplus_buffer) >= delay_min
            and all(s < threshold for s in self._fv_surplus_buffer)
        )
        if not should_shutoff:
            return

        # Prima di spegnere ME STESSO, verifico le sorelle con priorità PIÙ
        # BASSA (numero più alto): se la SOGLIA CONFIGURATA di una di loro
        # è già raggiunta/superata dal surplus ATTUALE (indipendentemente
        # dal fatto che il SUO buffer di conferma sia già pieno), spengo
        # LEI al posto mio — la meno prioritaria va sempre spenta per
        # prima, indipendentemente dai tempi di conferma individuali.
        target_to_shutoff = self
        target_temp = temp
        target_target = target
        my_priority = self._effective_priority()
        best_candidate = None
        best_priority = my_priority
        _LOGGER.info("%s: [semplificato FV] valuto le sorelle per il coordinamento spegnimento (mia priorità=%s, surplus attuale=%.0fW)", self._attr_name, my_priority, surplus)
        for entry_data in self.hass.data.get(DOMAIN, {}).values():
            if not isinstance(entry_data, dict):
                continue
            sibling = entry_data.get("climate")
            if sibling is None or sibling is self:
                continue
            if not sibling._fv_auto_on:
                _LOGGER.info("%s: [semplificato FV]   %s scartata: non risulta accesa dal FV (_fv_auto_on=False)", self._attr_name, sibling._attr_name)
                continue  # non è stata accesa dal FV, non è nella stessa "gara" di spegnimento
            sib_real_state = self.hass.states.get(sibling._climate_entity)
            if sib_real_state is None or sib_real_state.state in ("off", "unknown", "unavailable"):
                _LOGGER.info("%s: [semplificato FV]   %s scartata: stato reale = %s", self._attr_name, sibling._attr_name, sib_real_state.state if sib_real_state else "None")
                continue  # già spenta, non è più un candidato
            sib_threshold = float(get_conf(sibling.entry, CONF_FV_SHUTOFF_THRESHOLD, DEFAULT_FV_SHUTOFF_THRESHOLD))
            if surplus >= sib_threshold:
                _LOGGER.info("%s: [semplificato FV]   %s scartata: surplus attuale %.0fW ancora sufficiente per la sua soglia %.0fW", self._attr_name, sibling._attr_name, surplus, sib_threshold)
                continue  # la sua soglia configurata non è ancora raggiunta dal surplus attuale
            sib_priority = sibling._effective_priority()
            if sib_priority > best_priority:
                _LOGGER.info("%s: [semplificato FV]   %s ACCETTATA come candidata (priorità %s > %s finora migliore, surplus attuale %.0fW < sua soglia %.0fW)", self._attr_name, sibling._attr_name, sib_priority, best_priority, surplus, sib_threshold)
                best_priority = sib_priority
                best_candidate = sibling
            else:
                _LOGGER.info("%s: [semplificato FV]   %s scartata: priorità %s non più bassa della migliore finora (%s)", self._attr_name, sibling._attr_name, sib_priority, best_priority)
        if best_candidate is not None:
            _LOGGER.info(
                "%s: [semplificato FV] spengo %s al posto mio (priorità %s > %s, soglia sua %.0fW già raggiunta dal surplus attuale %.0fW)",
                self._attr_name, best_candidate._attr_name, best_priority, my_priority,
                float(get_conf(best_candidate.entry, CONF_FV_SHUTOFF_THRESHOLD, DEFAULT_FV_SHUTOFF_THRESHOLD)), surplus,
            )
            target_to_shutoff = best_candidate
            sib_temp = target_to_shutoff._simple_read_temp()
            target_temp = sib_temp if sib_temp is not None else temp
            is_winter_sib = target_to_shutoff._get_season_mode() == SEASON_WINTER
            target_target = target_to_shutoff._winter_current_target() if is_winter_sib else target_to_shutoff._simple_current_target()

        # Coordinamento cascata
        coord = self.hass.data.setdefault(DOMAIN, {}).setdefault("_coordination", {})
        stagger_min = float(get_conf(self.entry, CONF_FV_STAGGER_MIN, DEFAULT_FV_STAGGER_MIN))
        last_off = coord.get("last_fv_shutoff")
        if last_off is not None and (now - last_off) < timedelta(minutes=stagger_min):
            return

        _LOGGER.info("%s: [semplificato FV] spegnimento per FV (fv=%.0fW, consumo=%.0fW)", target_to_shutoff._attr_name, fv, consumo)

        # Stessa opzione Eco della regolazione termica generale — prima
        # NON veniva mai controllata qui, quindi una stanza accesa dal FV
        # (con _fv_auto_on rimasto True) veniva SEMPRE spenta secco da
        # QUESTA funzione (es. di notte, surplus sempre insufficiente),
        # senza mai passare per Eco, anche con l'opzione attivata.
        target_is_night = target_to_shutoff._simple_is_night()
        target_eco_enabled = bool(get_conf(
            target_to_shutoff.entry,
            CONF_SIMPLE_ECO_NIGHT_ENABLED if target_is_night else CONF_SIMPLE_ECO_DAY_ENABLED,
            DEFAULT_SIMPLE_ECO_NIGHT_ENABLED if target_is_night else DEFAULT_SIMPLE_ECO_DAY_ENABLED,
        ))
        if target_eco_enabled:
            coord["last_fv_shutoff"] = now
            if await target_to_shutoff._async_safe_climate_call("set_preset_mode", {"entity_id": target_to_shutoff._climate_entity, "preset_mode": "eco"}):
                _LOGGER.info("%s: [semplificato FV] ingresso in Eco invece di spegnere per FV insufficiente", target_to_shutoff._attr_name)
                target_to_shutoff._eco_mode_active = True
                target_to_shutoff._fv_surplus_buffer = []
                target_to_shutoff._fv_low_since = None
                target_to_shutoff._manual_accension_since = None
                target_to_shutoff.async_write_ha_state()
                return

        await target_to_shutoff._async_turn_off_climate()
        coord["last_fv_shutoff"] = now
        target_to_shutoff._fv_surplus_buffer = []
        target_to_shutoff._fv_low_since = None
        target_to_shutoff._manual_accension_since = None
        target_to_shutoff._own_fv_shutoff_at = now  # per impedire una riaccensione troppo rapida della STESSA istanza
        # NON resettiamo _fv_auto_on così la riaccensione sa che era il FV ad averlo acceso
        await target_to_shutoff._async_simple_notify_ac_off(target_temp, target_target, fv_shutoff=True)
        target_to_shutoff.async_write_ha_state()


    async def _async_simple_notify_ac_on(
        self, temp: float, target: float = 0,
        ac_type: str = "termica",
        fv: float = 0, consumo: float = 0, soc: float = 0
    ) -> None:
        """Notifica accensione con parametri distinti per tipo.

        ac_type: 'termica', 'fv', 'notturna', 'emergenza'
        """
        surplus = round(fv - consumo) if fv and consumo else 0
        if ac_type == "fv":
            tpl = DEFAULT_SIMPLE_MSG_AC_ON_FV
            vars = {"name": self._get_display_name(), "temp": round(temp, 1), "target": round(target, 1),
                    "fv": round(fv), "surplus": surplus, "soc": round(soc, 1)}
        elif ac_type == "notturna":
            tpl = DEFAULT_SIMPLE_MSG_AC_ON_NIGHT
            vars = {"name": self._get_display_name(), "temp": round(temp, 1), "target": round(target, 1)}
        elif ac_type == "emergenza":
            tpl = DEFAULT_SIMPLE_MSG_AC_ON_EMERGENCY
            vars = {"name": self._get_display_name(), "temp": round(temp, 1), "target": round(target, 1)}
        elif ac_type == "fv_winter":
            tpl = DEFAULT_SIMPLE_MSG_AC_ON_WINTER_FLOOR
            vars = {"name": self._get_display_name(), "temp": round(temp, 1), "target": round(target, 1),
                    "fv": round(fv), "surplus": surplus, "batteria": round(soc, 1)}
        else:
            tpl = DEFAULT_SIMPLE_MSG_AC_ON
            vars = {"name": self._get_display_name(), "temp": round(temp, 1), "target": round(target, 1)}
        msg = await self._async_render(tpl, vars)
        if bool(get_conf(self.entry, CONF_SIMPLE_NOTIFY_TTS_AC_ON, DEFAULT_SIMPLE_NOTIFY_TTS_AC_ON)):
            await self._async_simple_speak(msg)
        if bool(get_conf(self.entry, CONF_SIMPLE_NOTIFY_TEL_AC_ON, DEFAULT_SIMPLE_NOTIFY_TEL_AC_ON)):
            await self._async_simple_notify(msg)

    async def _async_simple_notify_ac_off(self, temp: float, target: float, fv_shutoff: bool = False, use_internal: bool | None = None) -> None:
        tpl = DEFAULT_SIMPLE_MSG_AC_OFF_FV if fv_shutoff else DEFAULT_SIMPLE_MSG_AC_OFF
        if use_internal is None:
            use_internal = self._should_use_internal_probe()  # fallback per i chiamanti che non lo specificano ancora
        probe_label = "interna" if use_internal else "esterna"
        msg = await self._async_render(tpl, {"name": self._get_display_name(), "temp": round(temp, 1), "target": round(target, 1), "sonda": probe_label})
        if bool(get_conf(self.entry, CONF_SIMPLE_NOTIFY_TTS_AC_OFF, DEFAULT_SIMPLE_NOTIFY_TTS_AC_OFF)):
            await self._async_simple_speak(msg)
        if bool(get_conf(self.entry, CONF_SIMPLE_NOTIFY_TEL_AC_OFF, DEFAULT_SIMPLE_NOTIFY_TEL_AC_OFF)):
            await self._async_simple_notify(msg)

    async def _async_simple_notify_ac_off_timer(self, temp: float, minuti: float, use_internal: bool | None = None) -> None:
        """Notifica DEDICATA per lo spegnimento causato dal timer manuale
        scaduto — messaggio diverso da quello standard, per distinguere
        chiaramente il motivo dello spegnimento (non temperatura raggiunta,
        non FV insufficiente: è scaduto il tempo impostato)."""
        if use_internal is None:
            use_internal = self._should_use_internal_probe()
        probe_label = "interna" if use_internal else "esterna"
        msg = await self._async_render(DEFAULT_SIMPLE_MSG_AC_OFF_TIMER, {"name": self._get_display_name(), "temp": round(temp, 1), "minuti": round(minuti), "sonda": probe_label})
        if bool(get_conf(self.entry, CONF_SIMPLE_NOTIFY_TTS_AC_OFF, DEFAULT_SIMPLE_NOTIFY_TTS_AC_OFF)):
            await self._async_simple_speak(msg)
        if bool(get_conf(self.entry, CONF_SIMPLE_NOTIFY_TEL_AC_OFF, DEFAULT_SIMPLE_NOTIFY_TEL_AC_OFF)):
            await self._async_simple_notify(msg)

    async def _async_simple_notify_manual_on(self, temp: float, target: float, use_internal: bool | None = None) -> None:
        """Notifica per un'accensione MANUALE rilevata (telecomando, app del
        produttore, o qualsiasi comando esterno alla nostra card) —
        selezionabile separatamente dalle altre notifiche di accensione."""
        if not bool(get_conf(self.entry, CONF_SIMPLE_NOTIFY_TTS_MANUAL_ON, DEFAULT_SIMPLE_NOTIFY_TTS_MANUAL_ON)) and \
           not bool(get_conf(self.entry, CONF_SIMPLE_NOTIFY_TEL_MANUAL_ON, DEFAULT_SIMPLE_NOTIFY_TEL_MANUAL_ON)):
            return
        if use_internal is None:
            use_internal = self._should_use_internal_probe()
        probe_label = "interna" if use_internal else "esterna"
        msg = await self._async_render(DEFAULT_SIMPLE_MSG_MANUAL_ON, {"name": self._get_display_name(), "temp": round(temp, 1), "target": round(target, 1), "sonda": probe_label})
        if bool(get_conf(self.entry, CONF_SIMPLE_NOTIFY_TTS_MANUAL_ON, DEFAULT_SIMPLE_NOTIFY_TTS_MANUAL_ON)):
            await self._async_simple_speak(msg)
        if bool(get_conf(self.entry, CONF_SIMPLE_NOTIFY_TEL_MANUAL_ON, DEFAULT_SIMPLE_NOTIFY_TEL_MANUAL_ON)):
            await self._async_simple_notify(msg)

    async def _async_simple_notify_manual_off(self) -> None:
        """Notifica per uno spegnimento MANUALE rilevato dall'esterno (non
        dalla nostra card) — ora selezionabile, prima era sempre attiva
        incondizionatamente."""
        if not bool(get_conf(self.entry, CONF_SIMPLE_NOTIFY_TTS_MANUAL_OFF, DEFAULT_SIMPLE_NOTIFY_TTS_MANUAL_OFF)) and \
           not bool(get_conf(self.entry, CONF_SIMPLE_NOTIFY_TEL_MANUAL_OFF, DEFAULT_SIMPLE_NOTIFY_TEL_MANUAL_OFF)):
            return
        msg = await self._async_render(DEFAULT_SIMPLE_MSG_MANUAL_OFF, {"name": self._get_display_name()})
        if bool(get_conf(self.entry, CONF_SIMPLE_NOTIFY_TTS_MANUAL_OFF, DEFAULT_SIMPLE_NOTIFY_TTS_MANUAL_OFF)):
            await self._async_simple_speak(msg)
        if bool(get_conf(self.entry, CONF_SIMPLE_NOTIFY_TEL_MANUAL_OFF, DEFAULT_SIMPLE_NOTIFY_TEL_MANUAL_OFF)):
            await self._async_simple_notify(msg)

    async def _async_simple_notify_temp_change(self, temp: float, target: float, fan: str | None = None, eco: bool = False) -> None:
        fan_labels = {"low": "bassa", "medium": "media", "high": "alta", "auto": "automatica"}
        fan_label = fan_labels.get(fan, fan) if fan else None
        msg = await self._async_render(
            DEFAULT_SIMPLE_MSG_TEMP_CHANGE,
            {"name": self._get_display_name(), "temp": round(temp, 1), "target": round(target, 1), "fan": fan_label, "eco": eco},
        )
        if bool(get_conf(self.entry, CONF_SIMPLE_NOTIFY_TTS_TEMP_CHANGE, DEFAULT_SIMPLE_NOTIFY_TTS_TEMP_CHANGE)):
            await self._async_simple_speak(msg)
        if bool(get_conf(self.entry, CONF_SIMPLE_NOTIFY_TEL_TEMP_CHANGE, DEFAULT_SIMPLE_NOTIFY_TEL_TEMP_CHANGE)):
            await self._async_simple_notify(msg)

    async def _async_simple_notify_night_start(self, target: float) -> None:
        msg = await self._async_render(DEFAULT_SIMPLE_MSG_NIGHT_START, {"name": self._get_display_name(), "target": round(target, 1)})
        if bool(get_conf(self.entry, CONF_SIMPLE_NOTIFY_TTS_NIGHT_START, DEFAULT_SIMPLE_NOTIFY_TTS_NIGHT_START)):
            await self._async_simple_speak(msg)
        if bool(get_conf(self.entry, CONF_SIMPLE_NOTIFY_TEL_NIGHT_START, DEFAULT_SIMPLE_NOTIFY_TEL_NIGHT_START)):
            await self._async_simple_notify(msg, bypass_quiet=True)

    async def _async_simple_notify_night_end(self) -> None:
        msg = await self._async_render(DEFAULT_SIMPLE_MSG_NIGHT_END, {"name": self._get_display_name()})
        if bool(get_conf(self.entry, CONF_SIMPLE_NOTIFY_TTS_NIGHT_END, DEFAULT_SIMPLE_NOTIFY_TTS_NIGHT_END)):
            await self._async_simple_speak(msg)
        if bool(get_conf(self.entry, CONF_SIMPLE_NOTIFY_TEL_NIGHT_END, DEFAULT_SIMPLE_NOTIFY_TEL_NIGHT_END)):
            await self._async_simple_notify(msg, bypass_quiet=True)

    def _get_display_name(self) -> str:
        """Nome da usare nei messaggi: nome area se assegnata, altrimenti nome entità.

        L'area può essere assegnata direttamente all'entità oppure ereditata
        dal device a cui appartiene — controlliamo entrambi i casi.
        """
        try:
            ent_reg = er.async_get(self.hass)
            entity_entry = ent_reg.async_get(self.entity_id)
            area_id = None
            if entity_entry:
                area_id = entity_entry.area_id
                if area_id is None and entity_entry.device_id:
                    from homeassistant.helpers import device_registry as dr
                    device = dr.async_get(self.hass).async_get(entity_entry.device_id)
                    if device:
                        area_id = device.area_id
            if area_id:
                area = ar.async_get(self.hass).async_get_area(area_id)
                if area and area.name:
                    return area.name
        except Exception as exc:
            _LOGGER.debug("%s: errore lettura area, uso nome entità: %s", self._attr_name, exc)
        return self._attr_name

    async def _async_simple_notify_door(self, is_open: bool) -> None:
        name = self._get_display_name()
        msg = f"{name} porta aperta" if is_open else f"{name} porta chiusa"
        if is_open:
            if bool(get_conf(self.entry, CONF_SIMPLE_NOTIFY_TTS_DOOR_OPEN, DEFAULT_SIMPLE_NOTIFY_TTS_DOOR_OPEN)):
                await self._async_simple_speak(msg)
            if bool(get_conf(self.entry, CONF_SIMPLE_NOTIFY_TEL_DOOR_OPEN, DEFAULT_SIMPLE_NOTIFY_TEL_DOOR_OPEN)):
                await self._async_simple_notify(msg)
        else:
            if bool(get_conf(self.entry, CONF_SIMPLE_NOTIFY_TTS_DOOR_CLOSE, DEFAULT_SIMPLE_NOTIFY_TTS_DOOR_CLOSE)):
                await self._async_simple_speak(msg)
            if bool(get_conf(self.entry, CONF_SIMPLE_NOTIFY_TEL_DOOR_CLOSE, DEFAULT_SIMPLE_NOTIFY_TEL_DOOR_CLOSE)):
                await self._async_simple_notify(msg)

    async def _async_simple_notify_window(self, is_open: bool, delay_min: int = 0, ac_was_on: bool = True) -> None:
        """Notifica apertura/chiusura finestra.

        Se il climatizzatore era acceso: messaggio completo originale (con
        minuti di attesa) usando il nome area. Se era già spento: messaggio
        ridotto a "{area} finestra aperta/chiusa" senza altro testo.
        """
        name = self._get_display_name()
        if ac_was_on:
            tpl = DEFAULT_SIMPLE_MSG_WINDOW_OPEN if is_open else DEFAULT_SIMPLE_MSG_WINDOW_CLOSE
            msg = await self._async_render(tpl, {"name": name, "delay": delay_min})
        else:
            msg = f"{name} finestra aperta" if is_open else f"{name} finestra chiusa"
        if is_open:
            if bool(get_conf(self.entry, CONF_SIMPLE_NOTIFY_TTS_WINDOW_OPEN, DEFAULT_SIMPLE_NOTIFY_TTS_WINDOW_OPEN)):
                await self._async_simple_speak(msg)
            if bool(get_conf(self.entry, CONF_SIMPLE_NOTIFY_TEL_WINDOW_OPEN, DEFAULT_SIMPLE_NOTIFY_TEL_WINDOW_OPEN)):
                await self._async_simple_notify(msg)
        else:
            if bool(get_conf(self.entry, CONF_SIMPLE_NOTIFY_TTS_WINDOW_CLOSE, DEFAULT_SIMPLE_NOTIFY_TTS_WINDOW_CLOSE)):
                await self._async_simple_speak(msg)
            if bool(get_conf(self.entry, CONF_SIMPLE_NOTIFY_TEL_WINDOW_CLOSE, DEFAULT_SIMPLE_NOTIFY_TEL_WINDOW_CLOSE)):
                await self._async_simple_notify(msg)

    async def _async_simple_notify_window_shutoff(self) -> None:
        """Notifica lo spegnimento causato dalla finestra rimasta aperta
        troppo a lungo — messaggio dedicato, diverso dall'avviso iniziale.
        Rientra nello stesso controllo 'finestra aperta' (nessun interruttore
        separato), dato che è la conseguenza diretta di quell'evento."""
        name = self._get_display_name()
        msg = await self._async_render(DEFAULT_SIMPLE_MSG_WINDOW_SHUTOFF, {"name": name, "minuti": SIMPLE_WINDOW_DELAY_MIN})
        if bool(get_conf(self.entry, CONF_SIMPLE_NOTIFY_TTS_WINDOW_OPEN, DEFAULT_SIMPLE_NOTIFY_TTS_WINDOW_OPEN)):
            await self._async_simple_speak(msg)
        if bool(get_conf(self.entry, CONF_SIMPLE_NOTIFY_TEL_WINDOW_OPEN, DEFAULT_SIMPLE_NOTIFY_TEL_WINDOW_OPEN)):
            await self._async_simple_notify(msg)

    # ------------------------------------------------------------------
    # Emergenza caldo
    # ------------------------------------------------------------------

    async def _async_handle_emergency_heat(
        self, temp: float, target: float, use_internal: bool, dry_enabled: bool
    ) -> None:
        """Gestisce l'emergenza (raffrescamento in Estate, riscaldamento in
        Inverno) nel modo semplificato FV e completo — stesso switch,
        comportamento specchiato in base alla stagione corrente.

        Estate — "Emergenza accendi raffrescamento":
        - Accende se temp ≥ target + soglia_emergenza (ignorando FV)
        - Si disattiva se temp scende sotto target + soglia_fine_emergenza

        Inverno — "Emergenza accendi riscaldamento":
        - Accende se temp ≤ target − soglia_emergenza_inverno (ignorando FV)
        - Si disattiva se temp risale sopra target − soglia_fine_emergenza_inverno

        In entrambi i casi: si disattiva automaticamente 5 min prima della notte.
        """
        config_mode = get_conf(self.entry, CONF_CONFIG_MODE, CONFIG_MODE_FULL)
        if config_mode not in (CONFIG_MODE_SIMPLE_FV, CONFIG_MODE_FULL):
            return

        is_winter = self._get_season_mode() == SEASON_WINTER
        emergency_on = self._switch_state(SWITCH_KEY_EMERGENCY, False)

        # --- Disattivazione automatica pre-notte ---
        if emergency_on:
            night_start_str = get_conf(self.entry, CONF_SIMPLE_NIGHT_START, DEFAULT_SIMPLE_NIGHT_START)
            try:
                night_start_t = dt_time.fromisoformat(str(night_start_str))
            except ValueError:
                night_start_t = None

            if night_start_t:
                now_local = dt_util.now()
                night_start_dt = now_local.replace(
                    hour=night_start_t.hour, minute=night_start_t.minute, second=0, microsecond=0
                )
                pre_night_dt = night_start_dt - timedelta(minutes=EMERGENCY_PRE_NIGHT_MIN)
                if now_local >= pre_night_dt and not self._simple_is_night():
                    _LOGGER.info("%s: [emergenza] disattivazione pre-notte", self._attr_name)
                    await self._async_turn_off_climate()
                    await self._async_emergency_set_switch(False)
                    await self._async_emergency_notify(False, temp, target)
                    self._emergency_notified = False
                    return

        # --- Disattivazione per temperatura rientrata ---
        if emergency_on:
            if is_winter:
                end_threshold = float(get_conf(self.entry, CONF_EMERGENCY_WINTER_HEAT_END_THRESHOLD, DEFAULT_EMERGENCY_WINTER_HEAT_END_THRESHOLD))
                rientrata = temp >= target - end_threshold
            else:
                end_threshold = float(get_conf(self.entry, CONF_EMERGENCY_HEAT_END_THRESHOLD, DEFAULT_EMERGENCY_HEAT_END_THRESHOLD))
                rientrata = temp <= target + end_threshold
            if rientrata:
                _LOGGER.info("%s: [emergenza] temperatura rientrata (temp=%.1f)", self._attr_name, temp)
                await self._async_emergency_set_switch(False)
                await self._async_emergency_notify(False, temp, target)
                self._emergency_notified = False
                return

        # --- Logica emergenza attiva ---
        if not emergency_on:
            return

        # Notifica accensione emergenza (una sola volta)
        if not self._emergency_notified:
            await self._async_emergency_notify(True, temp, target)
            self._emergency_notified = True

        if is_winter:
            threshold = float(get_conf(self.entry, CONF_EMERGENCY_WINTER_HEAT_THRESHOLD, DEFAULT_EMERGENCY_WINTER_HEAT_THRESHOLD))
            real_state = self.hass.states.get(self._climate_entity)
            is_on = real_state is not None and real_state.state == "heat"
            if not is_on and temp <= target - threshold:
                self._fv_auto_on = True
                _LOGGER.info("%s: [emergenza inverno] accensione HEAT (temp=%.1f)", self._attr_name, temp)
                await self._async_safe_climate_call("set_hvac_mode", {"entity_id": self._climate_entity, "hvac_mode": "heat"})
                await self._async_simple_notify_ac_on(temp, target, ac_type="emergenza")
            if is_on:
                await self._async_handle_thermal_winter_simple(temp, target, use_internal)
            return

        threshold = float(get_conf(self.entry, CONF_EMERGENCY_HEAT_THRESHOLD, DEFAULT_EMERGENCY_HEAT_THRESHOLD))
        real_state = self.hass.states.get(self._climate_entity)
        current_mode = real_state.state if real_state else "off"
        is_on = (self.hvac_mode == HVACMode.COOL or current_mode == "dry") and not self._is_unmanaged_real_mode()

        # Accende se non è già acceso e supera la soglia
        if not is_on and temp >= target + threshold:
            internal_temp = self._read_float(self._climate_entity, attr="current_temperature")
            self._fv_auto_on = True
            if dry_enabled:
                _LOGGER.info("%s: [emergenza] accensione DRY (temp=%.1f)", self._attr_name, temp)
                await self._async_safe_climate_call("set_hvac_mode", {"entity_id": self._climate_entity, "hvac_mode": "dry"})
                self._schedule_dry_timer("accensione_emergenza_dry")
            else:
                _LOGGER.info("%s: [emergenza] accensione COOL (temp=%.1f)", self._attr_name, temp)
                await self._async_safe_climate_call("turn_on", {"entity_id": self._climate_entity})
                self._cancel_dry_timer("accensione_emergenza_cool_no_dry")
            await self._async_simple_notify_ac_on(temp, target, ac_type="emergenza")

        # Regolazione termica normale (come semplificato puro)
        if is_on:
            internal_temp = self._read_float(self._climate_entity, attr="current_temperature")
            if use_internal:
                await self._async_thermal_simple_internal(temp, target, internal_temp, real_state, dry_enabled)
            else:
                await self._async_thermal_simple_external(temp, target, internal_temp, real_state, dry_enabled)

    async def _async_emergency_set_switch(self, state: bool) -> None:
        """Attiva/disattiva lo switch emergenza caldo."""
        entry_data = self.hass.data.get(DOMAIN, {}).get(self.entry.entry_id, {})
        switch = entry_data.get(SWITCH_KEY_EMERGENCY)
        if switch is not None:
            if state:
                await switch.async_turn_on()
            else:
                await switch.async_turn_off()

    async def _async_emergency_notify(self, is_on: bool, temp: float, target: float) -> None:
        """Notifica attivazione/disattivazione emergenza — messaggio
        diverso per raffrescamento (estate) o riscaldamento (inverno),
        stesso switch, stesso toggle di notifica."""
        notify_tts = bool(get_conf(self.entry, CONF_EMERGENCY_NOTIFY_TTS, DEFAULT_EMERGENCY_NOTIFY_TTS))
        notify_tel = bool(get_conf(self.entry, CONF_EMERGENCY_NOTIFY_TELEGRAM, DEFAULT_EMERGENCY_NOTIFY_TELEGRAM))
        if not notify_tts and not notify_tel:
            return

        config_mode = get_conf(self.entry, CONF_CONFIG_MODE, CONFIG_MODE_FULL)
        is_winter = self._get_season_mode() == SEASON_WINTER
        if is_winter:
            tpl = DEFAULT_EMERGENCY_WINTER_MSG_ON if is_on else DEFAULT_EMERGENCY_WINTER_MSG_OFF
        elif is_on:
            tpl = get_conf(self.entry, CONF_EMERGENCY_MSG_ON, DEFAULT_EMERGENCY_MSG_ON) if config_mode == CONFIG_MODE_FULL else DEFAULT_EMERGENCY_MSG_ON
        else:
            tpl = get_conf(self.entry, CONF_EMERGENCY_MSG_OFF, DEFAULT_EMERGENCY_MSG_OFF) if config_mode == CONFIG_MODE_FULL else DEFAULT_EMERGENCY_MSG_OFF

        msg = await self._async_render(tpl, {"name": self._get_display_name(), "temp": round(temp, 1), "target": round(target, 1)})

        if notify_tts:
            await self._async_simple_speak(msg)
        if notify_tel:
            await self._async_simple_notify(msg)

    # ------------------------------------------------------------------
    # Protezione potenza (evita distacco contatore)
    # ------------------------------------------------------------------

    async def _async_handle_power_limit(self) -> None:
        """Spegne il clima se il consumo supera la soglia per 30 secondi.

        Riaccende quando il consumo scende sotto soglia-isteresi per X minuti.
        Modalità unico: gestisce solo se stesso.
        Modalità multi: usa priorità FV con stagger 2 min tra riaccensioni.
        """
        if not bool(get_conf(self.entry, CONF_POWER_LIMIT_ENABLED, DEFAULT_POWER_LIMIT_ENABLED)):
            return

        sensor = get_conf(self.entry, CONF_POWER_LIMIT_SENSOR)
        if not sensor:
            return

        consumo = self._read_float(sensor)
        if consumo is None:
            return

        max_w = float(get_conf(self.entry, CONF_POWER_LIMIT_MAX_W, DEFAULT_POWER_LIMIT_MAX_W))
        hysteresis_w = float(get_conf(self.entry, CONF_POWER_LIMIT_HYSTERESIS_W, DEFAULT_POWER_LIMIT_HYSTERESIS_W))
        restore_min = int(get_conf(self.entry, CONF_POWER_LIMIT_RESTORE_MIN, DEFAULT_POWER_LIMIT_RESTORE_MIN))
        mode = get_conf(self.entry, CONF_POWER_LIMIT_MODE, DEFAULT_POWER_LIMIT_MODE)
        now = dt_util.utcnow()

        current_state = self.hass.states.get(self._climate_entity)
        is_on = current_state and current_state.state not in ("off", "unknown", "unavailable")

        # --- Spegnimento per eccesso consumo ---
        if is_on and not self._power_limit_off:
            if consumo > max_w:
                if self._power_limit_high_since is None:
                    self._power_limit_high_since = now
                elif (now - self._power_limit_high_since).total_seconds() >= POWER_LIMIT_SPIKE_SEC:
                    _LOGGER.warning(
                        "%s: [power limit] spegnimento (consumo=%.0fW > max=%.0fW)",
                        self._attr_name, consumo, max_w,
                    )
                    await self._async_turn_off_climate()
                    self._power_limit_off = True
                    self._power_limit_off_at = now
                    self._power_limit_high_since = None
                    self._power_limit_low_since = None
                    # Pausa del timer manuale (se attivo): il tempo trascorso
                    # spento per limite potenza non deve contare contro la
                    # durata configurata — memorizziamo i secondi rimanenti
                    # e cancelliamo il countdown, per riprenderlo dallo
                    # stesso punto quando (e se) il consumo rientra.
                    if self._shutoff_timer_cancel is not None and self._shutoff_timer_until is not None:
                        remaining = (self._shutoff_timer_until - now).total_seconds()
                        if remaining > 0:
                            self._shutoff_timer_remaining_seconds_paused = remaining
                        self._shutoff_timer_cancel()
                        self._shutoff_timer_cancel = None
                    # Registra in coordinamento per cascata multi
                    coord = self.hass.data.setdefault(DOMAIN, {}).setdefault("_coordination", {})
                    pl_order = coord.setdefault("power_limit_off_order", [])
                    if self.entry.entry_id not in pl_order:
                        pl_order.append(self.entry.entry_id)
                    await self._async_power_limit_notify(is_on=False, consumo=consumo)
                    return
            else:
                self._power_limit_high_since = None

        # --- Riaccensione dopo calo consumo ---
        if self._power_limit_off:
            restore_threshold = max_w - hysteresis_w
            if consumo <= restore_threshold:
                if self._power_limit_low_since is None:
                    self._power_limit_low_since = now
                elif (now - self._power_limit_low_since) >= timedelta(minutes=restore_min):
                    # Modalità multi: rispetta cascata e stagger
                    if mode == POWER_LIMIT_MODE_MULTI:
                        coord = self.hass.data.setdefault(DOMAIN, {}).setdefault("_coordination", {})
                        pl_order = coord.get("power_limit_off_order", [])
                        last_restore = coord.get("last_power_limit_restore")
                        # Riaccende solo se siamo il primo della lista e lo stagger è passato
                        if pl_order and pl_order[-1] == self.entry.entry_id:
                            if last_restore is None or (now - last_restore) >= timedelta(minutes=POWER_LIMIT_RESTORE_STAGGER_MIN):
                                # Verifica che il consumo sia ancora sotto soglia
                                if consumo <= restore_threshold:
                                    pl_order.pop()
                                    coord["last_power_limit_restore"] = now
                                    await self._async_power_limit_restore()
                        return
                    else:
                        # Modalità unico: riaccende direttamente
                        await self._async_power_limit_restore()
            else:
                self._power_limit_low_since = None

    async def _async_power_limit_restore(self) -> None:
        """Sblocca il clima dopo calo consumo.

        Controlla PRIMA se il dispositivo reale è già acceso (es. l'utente
        lo ha riacceso manualmente nel frattempo) — in quel caso non manda
        un comando ridondante né la notifica fuorviante "ho riacceso",
        ma sblocca comunque lo stato interno: la condizione di potenza è
        comunque rientrata, e lasciare il flag attivo bloccherebbe anche
        il ciclo FV a tempo indeterminato senza motivo.
        """
        real_state = self.hass.states.get(self._climate_entity)
        already_on = real_state is not None and real_state.state not in ("off", "unknown", "unavailable")

        self._power_limit_off = False
        self._power_limit_off_at = None
        self._power_limit_low_since = None
        self._power_limit_high_since = None

        if already_on:
            _LOGGER.info(
                "%s: [power limit] consumo rientrato — già acceso (probabilmente dall'utente), nessun comando inviato",
                self._attr_name,
            )
            return

        if self._is_manual_off_block_active():
            # Il timer manuale era scaduto proprio mentre eravamo spenti
            # per limite potenza (vedi _async_shutoff_timer_expired) e il
            # blocco riaccensione è abilitato — rispettiamo la sessione
            # manuale conclusa, non riaccendiamo qui. Il flag potenza
            # resta comunque sbloccato sopra, quindi il ciclo FV normale
            # può ancora operare in autonomia se le sue condizioni lo
            # giustificano.
            _LOGGER.info(
                "%s: [power limit] consumo rientrato ma blocco riaccensione attivo (timer manuale scaduto) — non riaccendo",
                self._attr_name,
            )
            return

        _LOGGER.info("%s: [power limit] riaccensione dopo calo consumo", self._attr_name)
        self._fv_auto_on = True
        await self._async_safe_climate_call("turn_on", {"entity_id": self._climate_entity})
        await self._async_power_limit_notify(is_on=True)

        # Ripresa del timer manuale dallo stesso punto in cui era in pausa
        # (vedi punto di spegnimento sopra) — la durata effettiva del
        # conteggio corrisponde così ai minuti configurati di funzionamento
        # reale, non al tempo di parete che include l'interruzione.
        if self._shutoff_timer_remaining_seconds_paused is not None:
            remaining = self._shutoff_timer_remaining_seconds_paused
            self._shutoff_timer_remaining_seconds_paused = None
            self._shutoff_timer_until = dt_util.utcnow() + timedelta(seconds=remaining)
            self._shutoff_timer_cancel = async_call_later(
                self.hass, remaining, self._async_shutoff_timer_expired
            )
            _LOGGER.info("%s: [power limit] timer manuale ripreso (%.0f minuti rimanenti)", self._attr_name, remaining / 60)

    async def _async_power_limit_notify(self, is_on: bool, consumo: float = 0) -> None:
        """Notifica spegnimento/riaccensione per protezione potenza."""
        notify_tts = bool(get_conf(self.entry, CONF_POWER_LIMIT_NOTIFY_TTS, DEFAULT_POWER_LIMIT_NOTIFY_TTS))
        notify_tel = bool(get_conf(self.entry, CONF_POWER_LIMIT_NOTIFY_TELEGRAM, DEFAULT_POWER_LIMIT_NOTIFY_TELEGRAM))
        if not notify_tts and not notify_tel:
            return

        config_mode = get_conf(self.entry, CONF_CONFIG_MODE, CONFIG_MODE_FULL)
        if is_on:
            if config_mode == CONFIG_MODE_FULL:
                tpl = get_conf(self.entry, CONF_POWER_LIMIT_MSG_ON, DEFAULT_POWER_LIMIT_MSG_ON)
            else:
                tpl = DEFAULT_POWER_LIMIT_MSG_ON
        else:
            if config_mode == CONFIG_MODE_FULL:
                tpl = get_conf(self.entry, CONF_POWER_LIMIT_MSG_OFF, DEFAULT_POWER_LIMIT_MSG_OFF)
            else:
                tpl = DEFAULT_POWER_LIMIT_MSG_OFF

        message = await self._async_render(tpl, {"name": self._get_display_name(), "consumo": round(consumo)})

        if notify_tts:
            await self._async_speak(message, bypass_quiet=True)
        if notify_tel:
            await self._async_send_notification(message, bypass_quiet=True)

    # ------------------------------------------------------------------
    # Helpers orari / stato
    # ------------------------------------------------------------------

    def _effective_target(self) -> float:
        target = self._target_temperature
        if self._is_night_mode_active():
            target += float(get_conf(self.entry, CONF_NIGHT_OFFSET, DEFAULT_NIGHT_OFFSET))
        return target

    def _is_night_mode_active(self) -> bool:
        return self._in_time_window(
            get_conf(self.entry, CONF_NIGHT_START_TIME, DEFAULT_NIGHT_START_TIME),
            get_conf(self.entry, CONF_NIGHT_END_TIME, DEFAULT_NIGHT_END_TIME),
        )

    def _within_fv_window(self) -> bool:
        return self._in_time_window(
            get_conf(self.entry, CONF_FV_START_TIME, DEFAULT_FV_START_TIME),
            get_conf(self.entry, CONF_FV_END_TIME, DEFAULT_FV_END_TIME),
        )

    def _within_fv_shutoff_window(self) -> bool:
        start_str = get_conf(self.entry, CONF_FV_START_TIME, DEFAULT_FV_START_TIME)
        end_str = get_conf(self.entry, CONF_FV_END_TIME, DEFAULT_FV_END_TIME)
        extra_h = float(get_conf(self.entry, CONF_FV_SHUTOFF_EXTRA_HOURS, DEFAULT_FV_SHUTOFF_EXTRA_HOURS))
        try:
            start = dt_time.fromisoformat(str(start_str))
            end_base = dt_time.fromisoformat(str(end_str))
        except ValueError:
            return True
        dummy_date = datetime(2000, 1, 1)
        end_dt = datetime.combine(dummy_date, end_base) + timedelta(hours=extra_h)
        end_extended = dt_time(23, 59, 59) if end_dt.date() > dummy_date.date() else end_dt.time()
        now_t = dt_util.now().time()
        if start <= end_extended:
            return start <= now_t <= end_extended
        return now_t >= start or now_t <= end_extended

    def _is_quiet_time(self) -> bool:
        if not bool(get_conf(self.entry, CONF_QUIET_ENABLED, DEFAULT_QUIET_ENABLED)):
            return False
        return self._in_time_window(
            get_conf(self.entry, CONF_QUIET_START_TIME, DEFAULT_QUIET_START_TIME),
            get_conf(self.entry, CONF_QUIET_END_TIME, DEFAULT_QUIET_END_TIME),
        )

    @staticmethod
    def _in_time_window(start_str: str, end_str: str) -> bool:
        try:
            start = dt_time.fromisoformat(str(start_str))
            end = dt_time.fromisoformat(str(end_str))
        except ValueError:
            return False
        if start == end:
            return False
        now_t = dt_util.now().time()
        if start <= end:
            return start <= now_t <= end
        return now_t >= start or now_t <= end

    def _is_window_open(self) -> bool:
        if not self._window_sensor:
            return False
        state = self.hass.states.get(self._window_sensor)
        if state is None or state.state in _INVALID_STATES:
            return False
        return state.state == "on"

    def _is_door_open(self) -> bool:
        if not self._door_sensor:
            return False
        state = self.hass.states.get(self._door_sensor)
        if state is None or state.state in _INVALID_STATES:
            return False
        return state.state == "on"

    def _switch_state(self, key: str, default: bool) -> bool:
        data = self.hass.data.get(DOMAIN, {}).get(self.entry.entry_id, {})
        switch = data.get(key)
        if switch is None:
            return default
        return bool(getattr(switch, "is_on", default))

    def _switch_entity_id(self, key: str) -> str | None:
        """Restituisce l'entity_id reale di uno switch ausiliario (es. il
        master switch), per poterlo esporre alla card e permetterle di
        controllarlo direttamente."""
        data = self.hass.data.get(DOMAIN, {}).get(self.entry.entry_id, {})
        switch = data.get(key)
        return getattr(switch, "entity_id", None) if switch is not None else None

    def _manual_shutoff_timer_minutes(self) -> float:
        """Minuti effettivi del timer manuale — il valore 'pending' (breve
        finestra di debounce dopo una regolazione dalla card) se presente,
        altrimenti quello configurato — un'unica fonte di verità."""
        if self._pending_timer_minutes_display is not None:
            return self._pending_timer_minutes_display
        return float(get_conf(self.entry, CONF_MANUAL_SHUTOFF_TIMER_MIN, DEFAULT_MANUAL_SHUTOFF_TIMER_MIN))

    def _manual_shutoff_timer_enabled(self) -> bool:
        """True se il timer di spegnimento automatico dopo accensione
        manuale è attivo — il valore 'pending' se presente, altrimenti
        quello configurato (0 minuti disattiva comunque tutto)."""
        if self._pending_timer_enabled_display is not None:
            return self._pending_timer_enabled_display
        if self._manual_shutoff_timer_minutes() <= 0:
            return False
        return bool(get_conf(self.entry, CONF_MANUAL_SHUTOFF_TIMER_ENABLED, DEFAULT_MANUAL_SHUTOFF_TIMER_ENABLED))

    def _read_float(self, entity_id: str | None) -> float | None:
        if not entity_id:
            return None
        state = self.hass.states.get(entity_id)
        if state is None:
            return None
        try:
            return float(state.state)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _round_setpoint(value: float) -> int:
        floor_val = math.floor(value)
        return int(floor_val) if value - floor_val <= 0.5 else int(floor_val) + 1

    @staticmethod
    def _is_real_transition(old_state: State | None, new_state: State | None, from_val: str, to_val: str) -> bool:
        """Verifica transizione esatta from_val→to_val, ignorando unavailable/unknown."""
        if new_state is None or old_state is None:
            return False
        if old_state.state in _INVALID_STATES or new_state.state in _INVALID_STATES:
            return False
        return old_state.state == from_val and new_state.state == to_val

    # ------------------------------------------------------------------
    # Accensione da FV
    # ------------------------------------------------------------------

    async def _async_handle_fv_turn_on(self, temp: float, target: float) -> None:
        if not self._fv_basic_eligible(temp, target):
            return
        coord = self.hass.data.setdefault(DOMAIN, {}).setdefault("_coordination", {})
        stagger_min = float(get_conf(self.entry, CONF_FV_STAGGER_MIN, DEFAULT_FV_STAGGER_MIN))
        last_on = coord.get("last_fv_turn_on")
        if last_on is not None and (dt_util.utcnow() - last_on) < timedelta(minutes=stagger_min):
            return
        my_priority = self._effective_priority()
        for entry_data in self.hass.data.get(DOMAIN, {}).values():
            if not isinstance(entry_data, dict):
                continue
            sibling = entry_data.get("climate")
            if sibling is None or sibling is self:
                continue
            if not sibling._fv_basic_eligible(sibling.current_temperature, sibling._effective_target()):
                continue
            sib_priority = sibling._effective_priority()
            if sib_priority < my_priority:
                return
        fv = self._read_float(self._fv_sensor) or 0
        self._fv_auto_on = True
        await self._async_safe_climate_call("turn_on", {"entity_id": self._climate_entity})
        coord["last_fv_turn_on"] = dt_util.utcnow()
        await self._async_notify_power_event(
            reason=REASON_FV, is_on=True,
            extra={"fv": round(fv), "temp": round(temp, 1), "target": round(target, 1)},
        )

    def _fv_basic_eligible(self, temp: float | None, target: float) -> bool:
        if not (self._fv_sensor and self._consumption_sensor and self._battery_sensor):
            return False
        if self.hvac_mode != HVACMode.OFF or temp is None:
            return False
        fv = self._read_float(self._fv_sensor)
        consumo = self._read_float(self._consumption_sensor)
        soc = self._read_float(self._battery_sensor)
        if fv is None or consumo is None or soc is None:
            return False
        margin = float(get_conf(self.entry, CONF_FV_MARGIN_W, DEFAULT_FV_MARGIN_W))
        soc_min = float(get_conf(self.entry, CONF_SOC_MIN, DEFAULT_SOC_MIN))
        turn_on_offset = float(get_conf(self.entry, CONF_TURN_ON_OFFSET, DEFAULT_TURN_ON_OFFSET))
        return fv > consumo + margin and soc > soc_min and temp > target + turn_on_offset

    # ------------------------------------------------------------------
    # Accensione notturna
    # ------------------------------------------------------------------

    async def _async_handle_night_turn_on(self, temp: float, target: float) -> None:
        if self.hvac_mode != HVACMode.OFF or temp is None:
            return
        night_turn_on_offset = float(get_conf(self.entry, CONF_NIGHT_TURN_ON_OFFSET, DEFAULT_NIGHT_TURN_ON_OFFSET))
        if temp <= target + night_turn_on_offset:
            return
        _LOGGER.debug("%s: accensione notturna (temp=%.1f)", self._attr_name, temp)
        # Impostiamo i flag PRIMA di chiamare il servizio — e ENTRAMBE le
        # varianti (questa funzione è condivisa tra modo Completo e
        # Semplice/Semplice+FV, ma il listener di rilevamento accensione
        # manuale del modo Semplice controlla `_simple_night_auto_on`, una
        # variabile DIVERSA da `_night_auto_on`). Senza questo, ogni
        # accensione notturna automatica veniva scambiata per manuale,
        # facendo scattare erroneamente il timer di spegnimento a tempo.
        self._night_auto_on = True
        self._simple_night_auto_on = True
        await self._async_safe_climate_call("turn_on", {"entity_id": self._climate_entity})
        await self._async_notify_power_event(
            reason=REASON_NIGHT, is_on=True,
            extra={"temp": round(temp, 1), "target": round(target, 1)},
        )

    # ------------------------------------------------------------------
    # Spegnimento diurno FV — sliding window
    # ------------------------------------------------------------------

    async def _async_handle_fv_shutoff(self, temp: float, target: float) -> None:
        if not self._within_fv_shutoff_window():
            self._fv_surplus_buffer = []
            return
        if not (self._fv_sensor and self._consumption_sensor):
            return
        if self.hvac_mode == HVACMode.OFF:
            self._fv_surplus_buffer = []
            return
        fv = self._read_float(self._fv_sensor)
        consumo = self._read_float(self._consumption_sensor)
        if fv is None or consumo is None:
            return
        surplus = fv - consumo
        threshold = float(get_conf(self.entry, CONF_FV_SHUTOFF_THRESHOLD, DEFAULT_FV_SHUTOFF_THRESHOLD))
        delay_min = int(get_conf(self.entry, CONF_FV_SHUTOFF_DELAY_MIN, DEFAULT_FV_SHUTOFF_DELAY_MIN))
        self._fv_surplus_buffer.append(surplus)
        if len(self._fv_surplus_buffer) > delay_min:
            self._fv_surplus_buffer.pop(0)
        _LOGGER.debug(
            "%s: FV shutoff buffer %s (soglia=%.0f, necessari=%d)",
            self._attr_name, [round(s) for s in self._fv_surplus_buffer], threshold, delay_min,
        )
        if len(self._fv_surplus_buffer) < delay_min:
            return
        if not all(s < threshold for s in self._fv_surplus_buffer):
            return
        now = dt_util.utcnow()
        coord = self.hass.data.setdefault(DOMAIN, {}).setdefault("_coordination", {})
        stagger_min = float(get_conf(self.entry, CONF_FV_STAGGER_MIN, DEFAULT_FV_STAGGER_MIN))
        last_off = coord.get("last_fv_shutoff")
        if last_off is not None and (now - last_off) < timedelta(minutes=stagger_min):
            return
        my_priority = self._effective_priority()
        for entry_data in self.hass.data.get(DOMAIN, {}).values():
            if not isinstance(entry_data, dict):
                continue
            sibling = entry_data.get("climate")
            if sibling is None or sibling is self or sibling.hvac_mode == HVACMode.OFF:
                continue
            sib_priority = sibling._effective_priority()
            if sib_priority > my_priority:
                return
        _LOGGER.info(
            "%s: spegnimento FV (buffer=%s, soglia=%.0fW)",
            self._attr_name, [round(s) for s in self._fv_surplus_buffer], threshold,
        )
        await self._async_turn_off_climate()
        coord["last_fv_shutoff"] = now
        self._fv_surplus_buffer = []
        self._fv_auto_on = False
        await self._async_notify_power_event(
            reason=REASON_FV_SHUTOFF, is_on=False,
            extra={"fv": round(fv), "consumo": round(consumo)},
        )

    # ------------------------------------------------------------------
    # Spegnimento notturno per target raggiunto
    # ------------------------------------------------------------------

    async def _async_handle_night_shutoff(self, temp: float, target: float) -> None:
        if self.hvac_mode == HVACMode.OFF:
            self._night_below_since = None
            return
        shutoff_delta = float(get_conf(self.entry, CONF_NIGHT_SHUTOFF_DELTA, DEFAULT_NIGHT_SHUTOFF_DELTA))
        shutoff_min = int(get_conf(self.entry, CONF_NIGHT_SHUTOFF_MIN, DEFAULT_NIGHT_SHUTOFF_MIN))
        threshold = target + shutoff_delta
        if temp > threshold:
            self._night_below_since = None
            return
        now = dt_util.utcnow()
        if self._night_below_since is None:
            self._night_below_since = now
            return
        if (now - self._night_below_since) < timedelta(minutes=shutoff_min):
            return
        _LOGGER.info("%s: spegnimento notturno target (temp=%.1f ≤ %.1f)", self._attr_name, temp, threshold)
        await self._async_turn_off_climate()
        self._night_below_since = None
        self._night_auto_on = False
        await self._async_notify_power_event(
            reason=REASON_NIGHT_SHUTOFF, is_on=False,
            extra={"temp": round(temp, 1), "target": round(target, 1)},
        )

    # ------------------------------------------------------------------
    # Spegnimento a fine modalità notturna
    # ------------------------------------------------------------------

    async def _async_handle_night_end_shutoff(self) -> None:
        """Chiamato una volta al ciclo in cui la modalità notturna termina.

        Logica:
        - Se night_end_shutoff_enabled=True → spegne sempre (se clima è acceso)
        - Se night_end_shutoff_auto_only=True → spegne solo se _night_auto_on è True
        - I due flag sono indipendenti: entrambi possono essere attivi,
          nel qual caso il "sempre" ha precedenza.
        """
        shutoff_always = bool(get_conf(self.entry, CONF_NIGHT_END_SHUTOFF_ENABLED, DEFAULT_NIGHT_END_SHUTOFF_ENABLED))
        shutoff_auto_only = bool(get_conf(self.entry, CONF_NIGHT_END_SHUTOFF_AUTO_ONLY, DEFAULT_NIGHT_END_SHUTOFF_AUTO_ONLY))

        if not shutoff_always and not shutoff_auto_only:
            return  # nessuno dei due abilitato

        if self.hvac_mode == HVACMode.OFF:
            self._night_auto_on = False
            return  # clima già spento, niente da fare

        should_shutoff = shutoff_always or (shutoff_auto_only and self._night_auto_on)

        if not should_shutoff:
            # auto_only attivo ma il clima non era stato acceso automaticamente
            _LOGGER.debug(
                "%s: fine notte — spegnimento auto_only attivo ma clima non era acceso automaticamente, skip",
                self._attr_name,
            )
            return

        _LOGGER.info("%s: spegnimento fine modalità notturna (auto_on=%s)", self._attr_name, self._night_auto_on)
        await self._async_turn_off_climate()
        self._night_auto_on = False
        self._night_below_since = None

        # Nel modo semplificato la notifica fine notte è gestita da
        # _async_simple_notify_night_end — non inviare duplicati
        mode = self._get_config_mode()
        if mode not in (CONFIG_MODE_SIMPLE, CONFIG_MODE_SIMPLE_FV):
            await self._async_notify_night_end_shutoff()

    # ------------------------------------------------------------------
    # Regolazione termica
    # ------------------------------------------------------------------

    async def _async_handle_thermal(self, temp: float, target: float) -> None:
        if self.hvac_mode == HVACMode.OFF:
            return
        extreme_offset = float(get_conf(self.entry, CONF_EXTREME_OFFSET, DEFAULT_EXTREME_OFFSET))
        hot_offset = float(get_conf(self.entry, CONF_HOT_OFFSET, DEFAULT_HOT_OFFSET))
        range_offset = float(get_conf(self.entry, CONF_RANGE_OFFSET, DEFAULT_RANGE_OFFSET))
        below_offset = float(get_conf(self.entry, CONF_BELOW_OFFSET, DEFAULT_BELOW_OFFSET))
        delta = float(get_conf(self.entry, CONF_TEMP_DELTA, DEFAULT_TEMP_DELTA))
        extreme_delta = float(get_conf(self.entry, CONF_EXTREME_DELTA, DEFAULT_EXTREME_DELTA))
        if temp > target + extreme_offset:
            new_temp, fan_mode = target - extreme_delta, "high"
        elif temp > target + hot_offset:
            new_temp, fan_mode = target - delta, "medium"
        elif temp > target + range_offset:
            new_temp, fan_mode = target - delta, "low"
        elif temp > target - below_offset:
            new_temp, fan_mode = target, "low"
        else:
            new_temp, fan_mode = target + delta, "low"
        if self._switch_state(SWITCH_KEY_QUICK, False) and temp > target + range_offset:
            new_temp -= 1.0
            fan_mode = "high"
        real_state = self.hass.states.get(self._climate_entity)
        current_temp = real_state.attributes.get("temperature") if real_state else None
        current_fan = real_state.attributes.get("fan_mode") if real_state else None
        internal_temp_raw = real_state.attributes.get("current_temperature") if real_state else None
        internal_temp_value: float | None = None
        if internal_temp_raw is not None:
            try:
                internal_temp_value = float(internal_temp_raw)
            except (TypeError, ValueError):
                pass
        if internal_temp_value is not None:
            calib_raw = temp - internal_temp_value
            if calib_raw > 0:
                gap = max(0.0, temp - target)
                fraction = min(gap / extreme_offset, 1.0) if extreme_offset > 0 else (1.0 if gap > 0 else 0.0)
                calib_scaled = min(calib_raw * fraction, float(get_conf(self.entry, CONF_CALIBRATION_MAX_OFFSET, DEFAULT_CALIBRATION_MAX_OFFSET)))
                new_temp -= calib_scaled
        new_temp_rounded = self._round_setpoint(new_temp)
        if internal_temp_value is not None and temp > target + range_offset:
            min_gap = float(get_conf(self.entry, CONF_MIN_BELOW_INTERNAL, DEFAULT_MIN_BELOW_INTERNAL))
            max_allowed = math.floor(internal_temp_value - min_gap)
            if new_temp_rounded > max_allowed:
                new_temp_rounded = int(max_allowed)
        current_temp_rounded: int | None = None
        if current_temp is not None:
            try:
                current_temp_rounded = self._round_setpoint(float(current_temp))
            except (TypeError, ValueError):
                pass
        if current_temp_rounded is None or current_temp_rounded != new_temp_rounded:
            await self._async_safe_climate_call("set_temperature", {"entity_id": self._climate_entity, "temperature": new_temp_rounded})
            mode = self._get_config_mode()
            if mode in (CONFIG_MODE_SIMPLE, CONFIG_MODE_SIMPLE_FV):
                await self._async_simple_notify_temp_change(temp, target)
            else:
                await self._async_notify_temp_change(current_temp_rounded, new_temp_rounded, fan_mode, temp, target)
        if current_fan != fan_mode:
            await self._async_safe_climate_call("set_fan_mode", {"entity_id": self._climate_entity, "fan_mode": fan_mode})

    # ------------------------------------------------------------------
    # Boost presenza
    # ------------------------------------------------------------------

    async def _async_handle_presence_boost(self, temp: float, target: float) -> None:
        if self.hvac_mode != HVACMode.COOL or not self._presence_sensor or self._presence_since is None:
            return
        if not bool(get_conf(self.entry, CONF_PRESENCE_BOOST_ENABLED, DEFAULT_PRESENCE_BOOST_ENABLED)):
            return
        boost_minutes = int(get_conf(self.entry, CONF_PRESENCE_BOOST_MIN, DEFAULT_PRESENCE_BOOST_MIN))
        boost_offset = float(get_conf(self.entry, CONF_PRESENCE_BOOST_OFFSET, DEFAULT_PRESENCE_BOOST_OFFSET))
        elapsed = dt_util.utcnow() - self._presence_since
        if elapsed >= timedelta(minutes=boost_minutes) and temp > target + boost_offset and self.fan_mode != "medium":
            await self._async_safe_climate_call("set_fan_mode", {"entity_id": self._climate_entity, "fan_mode": "medium"})

    # ------------------------------------------------------------------
    # Gestione finestra
    # ------------------------------------------------------------------

    async def _async_handle_window(self, new_state: State | None, old_state: State | None) -> None:
        if new_state is None:
            return
        if not self._switch_state(SWITCH_KEY_MASTER, True):
            return
        if not bool(get_conf(self.entry, CONF_WINDOW_DETECTION_ENABLED, DEFAULT_WINDOW_DETECTION_ENABLED)):
            return  # rilevamento finestra disattivato per questa istanza — non deve mai influire sul climatizzatore
        mode = self._get_config_mode()
        is_simple = mode in (CONFIG_MODE_SIMPLE, CONFIG_MODE_SIMPLE_FV)
        real_state = self.hass.states.get(self._climate_entity)
        ac_was_on = bool(real_state and real_state.state not in ("off", "unknown", "unavailable"))

        if self._is_real_transition(old_state, new_state, "off", "on"):
            if self._window_cancel_timer is not None:
                self._window_cancel_timer()
                self._window_cancel_timer = None
            if is_simple:
                await self._async_simple_notify_window(True, SIMPLE_WINDOW_DELAY_MIN, ac_was_on)
                await self._async_window_opened_simple()
            else:
                await self._async_window_opened()
        elif self._is_real_transition(old_state, new_state, "on", "off"):
            if self._window_cancel_timer is not None:
                self._window_cancel_timer()
                self._window_cancel_timer = None
            if is_simple:
                await self._async_simple_notify_window(False, 0, ac_was_on)
                await self._async_window_closed_simple()
            else:
                await self._async_window_closed()



    def _is_manual_off_block_active(self) -> bool:
        """True se la riaccensione automatica è bloccata perché il clima è
        stato spento manualmente da meno del tempo configurato.

        Vale sia di giorno che di notte — nessuna distinzione tra le due
        fasce, il blocco è sullo spegnimento manuale in sé.
        """
        if self._manual_off_since is None:
            return False
        if not bool(get_conf(self.entry, CONF_SIMPLE_NO_REON_MANUAL_OFF, DEFAULT_SIMPLE_NO_REON_MANUAL_OFF)):
            return False
        hours = float(get_conf(self.entry, CONF_SIMPLE_NO_REON_MANUAL_OFF_HOURS, DEFAULT_SIMPLE_NO_REON_MANUAL_OFF_HOURS))
        elapsed = dt_util.utcnow() - self._manual_off_since
        if elapsed >= timedelta(hours=hours):
            # Blocco scaduto — lo rimuoviamo così i log/attributi restano puliti
            self._manual_off_since = None
            return False
        return True

    async def _async_safe_climate_call(self, service: str, data: dict) -> bool:
        """Chiama un servizio sul climatizzatore reale con gestione errori.

        Se il dispositivo è irraggiungibile (offline, integrazione del
        produttore in errore, ecc.), l'eccezione viene catturata e loggata
        invece di propagarsi — evitando che quel singolo ciclo si interrompa
        a metà lasciando lo stato interno incoerente. Il prossimo ciclo
        periodico riproverà normalmente. Restituisce True se il comando è
        andato a buon fine, False altrimenti (il chiamante può ignorare il
        valore se non gli serve distinguere i due casi).
        """
        try:
            await self.hass.services.async_call("climate", service, data, blocking=True)
            return True
        except Exception as exc:  # noqa: BLE001 — qualsiasi errore del dispositivo/integrazione reale
            _LOGGER.warning(
                "%s: comando '%s' non riuscito (climatizzatore irraggiungibile?) — riprovo al prossimo ciclo: %s",
                self._attr_name, service, exc,
            )
            return False

    async def _async_turn_off_climate(self) -> None:
        """Spegne il climatizzatore marcandolo come spegnimento PROGRAMMATO
        (dall'integrazione stessa), non manuale. Usare questo metodo invece
        di chiamare direttamente climate.turn_off, così _async_on_state_change
        può distinguere uno spegnimento nostro da uno fatto dall'utente/telecomando.

        Usiamo un timestamp con finestra di tolleranza (non un semplice
        booleano) perché Home Assistant elabora l'evento state_changed in
        modo asincrono sul bus eventi: anche con blocking=True il servizio
        può ritornare prima che il nostro listener abbia effettivamente
        ricevuto ed elaborato il cambio di stato — un booleano resettato
        subito dopo la chiamata rischierebbe di essere già tornato False
        quando l'evento arriva, facendo scattare erroneamente il rilevamento
        di spegnimento "manuale".
        """
        self._programmatic_off_until = dt_util.utcnow() + timedelta(seconds=STATE_CHANGE_DEBOUNCE_SECONDS + 30)
        if self._eco_mode_active:
            # Se il clima è in Eco (preset_mode=eco) e stiamo per spegnerlo
            # per QUALSIASI motivo (timer, fine notte/giorno, target, FV,
            # limite potenza...), puliamo prima il preset — altrimenti una
            # riaccensione manuale successiva (es. comando vocale) partirebbe
            # ancora in modalità eco, dato che il dispositivo mantiene il
            # preset anche da spento fino a un comando esplicito che lo cambi.
            await self.hass.services.async_call(
                "climate", "set_preset_mode", {"entity_id": self._climate_entity, "preset_mode": "none"}, blocking=True
            )
            self._eco_mode_active = False
        await self.hass.services.async_call(
            "climate", "turn_off", {"entity_id": self._climate_entity}, blocking=True
        )

    def _cancel_dry_timer(self, reason: str = "n/d") -> None:
        """Cancella il timer DRY→COOL e resetta le variabili di stato."""
        was_active = self._simple_dry_end is not None
        if self._dry_cancel_timer is not None:
            self._dry_cancel_timer()
            self._dry_cancel_timer = None
        self._simple_dry_end = None
        self._simple_dry_since = None
        if was_active:
            _LOGGER.warning("%s: [DRY-TRACE] timer CANCELLATO — motivo: %s", self._attr_name, reason)

    def _schedule_dry_timer(self, reason: str = "n/d") -> None:
        """Avvia il timer DRY→COOL usando async_track_point_in_time.

        Calcola il timestamp assoluto di scadenza (now + dry_max_min) e
        schedula la callback a quell'ora esatta. Al riavvio di HA, il
        timestamp viene recuperato da RestoreEntity (attributo dry_end) e
        il timer viene rischedulato — se il timestamp è già nel passato,
        HA lo fa scattare immediatamente al prossimo tick dell'event loop.
        """
        # Cancella eventuale timer precedente
        if self._dry_cancel_timer is not None:
            self._dry_cancel_timer()
            self._dry_cancel_timer = None

        now = dt_util.utcnow()
        dry_max_min = int(get_conf(self.entry, CONF_SIMPLE_DRY_MAX_MIN, DEFAULT_SIMPLE_DRY_MAX_MIN))
        dry_end = now + timedelta(minutes=dry_max_min)

        self._simple_dry_since = now
        self._simple_dry_end = dry_end

        self._dry_cancel_timer = async_track_point_in_time(
            self.hass, self._async_dry_to_cool, dry_end
        )
        _LOGGER.warning(
            "%s: [DRY-TRACE] timer AVVIATO — motivo: %s — scadrà alle %s (%s min)",
            self._attr_name, reason, dry_end.isoformat(), dry_max_min,
        )

    async def _async_dry_to_cool(self, *_) -> None:
        """Callback di async_track_point_in_time: passa da DRY a COOL.

        Se il Gree è unavailable al momento dello scatto, non fa niente —
        il fallback nel loop periodico (ogni 5 min) rileverà che dry_end
        è nel passato e completerà la transizione al ciclo successivo.
        """
        self._dry_cancel_timer = None  # già scattato, non serve più cancellare
        if not self._switch_state(SWITCH_KEY_MASTER, True):
            _LOGGER.info("%s: [DRY→COOL] timer scattato ma termostato disabilitato — nessuna azione", self._attr_name)
            self._simple_dry_end = None
            self._simple_dry_since = None
            return
        real_state = self.hass.states.get(self._climate_entity)
        if real_state and real_state.state == "dry":
            _LOGGER.warning("%s: [DRY-TRACE] timer scattato — passo a raffreddamento (set_hvac_mode cool)", self._attr_name)
            await self.hass.services.async_call(
                "climate", "set_hvac_mode",
                {"entity_id": self._climate_entity, "hvac_mode": "cool"},
                blocking=True,
            )
            self._simple_dry_end = None
            self._simple_dry_since = None
        elif real_state and real_state.state in ("unknown", "unavailable"):
            # Gree non raggiungibile in questo momento — il fallback del loop
            # periodico ci pensa al prossimo ciclo (dry_end rimane settato)
            _LOGGER.warning(
                "%s: [DRY→COOL] timer scattato ma Gree è %s — il fallback periodico completerà la transizione",
                self._attr_name, real_state.state,
            )
        else:
            # Clima già spento o in COOL — nessuna azione, pulisci
            _LOGGER.debug(
                "%s: [DRY→COOL] timer scattato ma stato=%s — nessuna azione",
                self._attr_name, real_state.state if real_state else "None",
            )
            self._simple_dry_end = None
            self._simple_dry_since = None

    async def _async_window_opened_simple(self) -> None:
        """Apertura finestra in modo semplificato — delay fisso 5 minuti."""
        if self.hvac_mode != HVACMode.COOL:
            return
        real_state = self.hass.states.get(self._climate_entity)
        if real_state is None:
            return
        self._snapshot = {
            "hvac_mode": real_state.state,
            "temperature": real_state.attributes.get("temperature"),
            "fan_mode": real_state.attributes.get("fan_mode"),
        }
        self._window_cancel_timer = async_call_later(
            self.hass, timedelta(minutes=SIMPLE_WINDOW_DELAY_MIN), self._async_window_timeout
        )

    async def _async_window_closed_simple(self) -> None:
        """Chiusura finestra in modo semplificato — ripristina clima senza notifiche duplicate."""
        if self._snapshot is None:
            return
        snap, self._snapshot = self._snapshot, None
        if snap["hvac_mode"] == "off":
            return
        self._fv_auto_on = True  # ripristino da snapshot, non è una nuova accensione manuale
        await self._async_safe_climate_call("turn_on", {"entity_id": self._climate_entity})
        if snap.get("temperature") is not None:
            await self._async_safe_climate_call("set_temperature", {"entity_id": self._climate_entity, "temperature": snap["temperature"]})
        if snap.get("fan_mode") is not None:
            await self._async_safe_climate_call("set_fan_mode", {"entity_id": self._climate_entity, "fan_mode": snap["fan_mode"]})

    async def _async_window_opened(self) -> None:
        if self.hvac_mode != HVACMode.COOL:
            return
        real_state = self.hass.states.get(self._climate_entity)
        if real_state is None:
            return
        self._snapshot = {
            "hvac_mode": real_state.state,
            "temperature": real_state.attributes.get("temperature"),
            "fan_mode": real_state.attributes.get("fan_mode"),
        }
        delay_min = int(get_conf(self.entry, CONF_WINDOW_DELAY_MIN, DEFAULT_WINDOW_DELAY_MIN))
        await self._async_notify_window_open_tts(delay_min)
        self._window_cancel_timer = async_call_later(self.hass, timedelta(minutes=delay_min), self._async_window_timeout)

    async def _async_window_timeout(self, now: datetime | None = None) -> None:
        self._window_cancel_timer = None
        if not self._switch_state(SWITCH_KEY_MASTER, True):
            return
        if not self._is_window_open():
            return
        await self._async_turn_off_climate()
        await self._async_simple_notify_window_shutoff()
        self.async_write_ha_state()

    async def _async_shutoff_timer_expired(self, now: datetime | None = None) -> None:
        """Spegne il clima quando scade il timer impostato manualmente
        dalla card. A differenza delle altre automazioni, questo funziona
        SEMPRE, anche se il master switch è disattivato — è un comando
        esplicito dell'utente (es. per uno scaldotto usato manualmente
        d'inverno), non una decisione automatica del termostato."""
        self._shutoff_timer_cancel = None
        self._shutoff_timer_until = None
        real_state = self.hass.states.get(self._climate_entity)
        already_off = real_state is not None and real_state.state in ("off", "unknown", "unavailable")
        if already_off:
            # Già spento da un altro meccanismo prima che il timer
            # scadesse — evitiamo una notifica fuorviante che attribuirebbe
            # lo spegnimento al timer, e un comando turn_off ridondante.
            # Caso specifico: se era spento per LIMITE POTENZA, il timer
            # scaduto significa che la sessione manuale doveva comunque
            # finire qui — attiviamo il blocco riaccensione (se abilitato)
            # per impedire che il ripristino automatico del limite potenza
            # riaccenda la stanza subito dopo, vanificando lo scopo del
            # timer. Non tocca il caso di accensione dal FV, che resta
            # libero di operare normalmente.
            if self._power_limit_off and bool(get_conf(self.entry, CONF_SIMPLE_NO_REON_MANUAL_OFF, DEFAULT_SIMPLE_NO_REON_MANUAL_OFF)):
                self._manual_off_since = dt_util.utcnow()
            self.async_write_ha_state()
            return
        await self._async_simple_notify_ac_off_timer(self.current_temperature or 0, self._manual_shutoff_timer_minutes())
        await self._async_turn_off_climate()
        self.async_write_ha_state()

    async def _async_window_closed(self) -> None:
        await self._async_notify_window_closed()
        if self._snapshot is None:
            return
        snap, self._snapshot = self._snapshot, None
        if snap["hvac_mode"] == "off":
            return
        self._fv_auto_on = True  # ripristino da snapshot, non è una nuova accensione manuale
        await self._async_safe_climate_call("turn_on", {"entity_id": self._climate_entity})
        if snap.get("temperature") is not None:
            await self._async_safe_climate_call("set_temperature", {"entity_id": self._climate_entity, "temperature": snap["temperature"]})
        if snap.get("fan_mode") is not None:
            await self._async_safe_climate_call("set_fan_mode", {"entity_id": self._climate_entity, "fan_mode": snap["fan_mode"]})

    # ------------------------------------------------------------------
    # Gestione porta
    # ------------------------------------------------------------------

    async def _async_handle_door(self, new_state: State | None, old_state: State | None) -> None:
        if new_state is None:
            return
        # Debounce 1 secondo — ignora rimbalzi sensore reed
        if hasattr(self, '_door_debounce_cancel') and self._door_debounce_cancel:
            self._door_debounce_cancel()
            self._door_debounce_cancel = None
        _new_state = new_state
        _old_state = old_state
        async def _process_door(_now=None):
            self._door_debounce_cancel = None
            current = self.hass.states.get(self._door_sensor)
            if current is None or current.state != _new_state.state:
                return
            await self._async_handle_door_debounced(_new_state, _old_state)
        self._door_debounce_cancel = async_call_later(
            self.hass, timedelta(seconds=1),
            _process_door
        )

    async def _async_handle_door_debounced(self, new_state: State | None, old_state: State | None) -> None:
        """Gestisce l'evento porta dopo il debounce di 1 secondo."""
        if not self._switch_state(SWITCH_KEY_MASTER, True):
            return
        mode = self._get_config_mode()
        is_simple = mode in (CONFIG_MODE_SIMPLE, CONFIG_MODE_SIMPLE_FV)

        if self._is_real_transition(old_state, new_state, "off", "on"):
            if is_simple:
                await self._async_simple_notify_door(True)
            else:
                if not bool(get_conf(self.entry, CONF_DOOR_ALERT_ENABLED, DEFAULT_DOOR_ALERT_ENABLED)):
                    return
                message = await self._async_render(DEFAULT_DOOR_ALERT_OPEN_MESSAGE, {"name": self._get_display_name()})
                if bool(get_conf(self.entry, CONF_DOOR_ALERT_TTS, DEFAULT_DOOR_ALERT_TTS)):
                    await self._async_speak(message, bypass_quiet=False)
                if bool(get_conf(self.entry, CONF_DOOR_ALERT_NOTIFY, DEFAULT_DOOR_ALERT_NOTIFY)):
                    await self._async_send_notification(message, bypass_quiet=False)

        elif self._is_real_transition(old_state, new_state, "on", "off"):
            if is_simple:
                await self._async_simple_notify_door(False)
            else:
                if not bool(get_conf(self.entry, CONF_DOOR_ALERT_ENABLED, DEFAULT_DOOR_ALERT_ENABLED)):
                    return
                message = await self._async_render(DEFAULT_DOOR_ALERT_CLOSED_MESSAGE, {"name": self._get_display_name()})
                if bool(get_conf(self.entry, CONF_DOOR_ALERT_TTS, DEFAULT_DOOR_ALERT_TTS)):
                    await self._async_speak(message, bypass_quiet=False)
                if bool(get_conf(self.entry, CONF_DOOR_ALERT_NOTIFY, DEFAULT_DOOR_ALERT_NOTIFY)):
                    await self._async_send_notification(message, bypass_quiet=False)

    # ------------------------------------------------------------------
    # Avvisi accensione / spegnimento automatico
    # ------------------------------------------------------------------

    async def _async_notify_power_event(
        self,
        reason: str,
        is_on: bool,
        extra: dict[str, Any] | None = None,
    ) -> None:
        power_tts = bool(get_conf(self.entry, CONF_NOTIFY_POWER_TTS, DEFAULT_NOTIFY_POWER_TTS))
        power_notify = bool(get_conf(self.entry, CONF_NOTIFY_POWER_NOTIFY, DEFAULT_NOTIFY_POWER_NOTIFY))
        if not power_tts and not power_notify:
            return
        if is_on and reason == REASON_FV:
            tpl = DEFAULT_POWER_ON_FV_MESSAGE
        elif is_on and reason == REASON_NIGHT:
            tpl = DEFAULT_POWER_ON_NIGHT_MESSAGE
        elif not is_on and reason == REASON_FV_SHUTOFF:
            tpl = DEFAULT_POWER_OFF_FV_MESSAGE
        elif not is_on and reason == REASON_NIGHT_SHUTOFF:
            tpl = DEFAULT_POWER_OFF_NIGHT_MESSAGE
        else:
            stato = "acceso" if is_on else "spento"
            tpl = f"{{{{ name }}}}: climatizzatore {stato} automaticamente"
        variables = {"name": self._get_display_name(), **(extra or {})}
        message = await self._async_render(tpl, variables)
        if power_tts:
            await self._async_speak(message, bypass_quiet=False)
        if power_notify:
            await self._async_send_notification(message, bypass_quiet=False)

    async def _async_notify_night_end_shutoff(self) -> None:
        """Notifica dedicata per lo spegnimento a fine modalità notturna.

        Usa canali separati (notify_night_end_tts e notify_night_end_notify)
        indipendenti dagli altri avvisi di accensione/spegnimento.
        """
        tts_enabled = bool(get_conf(self.entry, CONF_NOTIFY_NIGHT_END_TTS, DEFAULT_NOTIFY_NIGHT_END_TTS))
        notify_enabled = bool(get_conf(self.entry, CONF_NOTIFY_NIGHT_END_NOTIFY, DEFAULT_NOTIFY_NIGHT_END_NOTIFY))
        if not tts_enabled and not notify_enabled:
            return
        message = await self._async_render(DEFAULT_POWER_OFF_NIGHT_END_MESSAGE, {"name": self._get_display_name()})
        if tts_enabled:
            await self._async_speak(message, bypass_quiet=True)  # fine notte = di giorno, non serve bypass_quiet
        if notify_enabled:
            await self._async_send_notification(message, bypass_quiet=True)

    # ------------------------------------------------------------------
    # Notifiche (helper base)
    # ------------------------------------------------------------------

    async def _async_render(self, template_str: str, variables: dict[str, Any]) -> str:
        try:
            tpl = Template(template_str, self.hass)
            return tpl.async_render(variables=variables, parse_result=False)
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning("%s: errore rendering ('%s'): %s", self._attr_name, template_str, err)
            return template_str

    async def _async_speak(self, message: str, bypass_quiet: bool = False) -> None:
        players = get_conf(self.entry, CONF_TTS_PLAYERS, [])
        if not players:
            return
        if not bypass_quiet and self._is_quiet_time() and bool(get_conf(self.entry, CONF_QUIET_TTS, DEFAULT_QUIET_TTS)):
            _LOGGER.debug("%s: TTS soppresso (fascia silenzio)", self._attr_name)
            return
        engine = get_conf(self.entry, CONF_TTS_ENGINE)
        if not engine:
            tts_states = self.hass.states.async_all("tts")
            if not tts_states:
                _LOGGER.warning("%s: nessun motore TTS disponibile", self._attr_name)
                return
            engine = tts_states[0].entity_id
        await self.hass.services.async_call(
            "tts", "speak",
            {"entity_id": engine, "media_player_entity_id": players, "message": message, "cache": True},
            blocking=True,
        )

    async def _async_send_notification(self, message: str, bypass_quiet: bool = False) -> None:
        targets = get_conf(self.entry, CONF_NOTIFY_TARGETS, [])
        chat_ids = get_conf(self.entry, CONF_NOTIFY_CHAT_IDS)
        if not targets and not chat_ids:
            return
        if not bypass_quiet and self._is_quiet_time() and bool(get_conf(self.entry, CONF_QUIET_NOTIFY, DEFAULT_QUIET_NOTIFY)):
            _LOGGER.debug("%s: notifica soppressa (fascia silenzio)", self._attr_name)
            return
        if targets:
            await self.hass.services.async_call("notify", "send_message", {"entity_id": targets, "message": message}, blocking=True)
        elif chat_ids:
            ids = [c.strip() for c in str(chat_ids).split(",") if c.strip()]
            await self.hass.services.async_call("telegram_bot", "send_message", {"target": ids, "message": message}, blocking=True)

    async def _async_notify_window_open_tts(self, delay_min: int) -> None:
        variables = {"delay": delay_min, "name": self._get_display_name(), "target": self._target_temperature}
        tts_tpl = get_conf(self.entry, CONF_TTS_MESSAGE_OPEN, DEFAULT_TTS_MESSAGE_OPEN)
        tts_msg = await self._async_render(tts_tpl, variables)
        await self._async_speak(tts_msg, bypass_quiet=False)
        notify_msg = await self._async_render(DEFAULT_NOTIFY_MESSAGE_OPEN, variables)
        await self._async_send_notification(notify_msg, bypass_quiet=False)

    async def _async_notify_window_closed(self) -> None:
        variables = {"name": self._get_display_name()}
        tts_msg = await self._async_render(DEFAULT_TTS_MESSAGE_CLOSED, variables)
        await self._async_speak(tts_msg, bypass_quiet=False)
        notify_msg = await self._async_render(DEFAULT_NOTIFY_MESSAGE_CLOSED, variables)
        await self._async_send_notification(notify_msg, bypass_quiet=False)

    async def _async_notify_window_closed_off(self) -> None:
        variables = {"name": self._get_display_name(), "target": self._target_temperature}
        tts_msg = await self._async_render(
            "Attenzione: il climatizzatore della {{ name }} è stato spento "
            "perché la finestra è rimasta aperta troppo a lungo.",
            variables,
        )
        await self._async_speak(tts_msg, bypass_quiet=False)
        notify_msg = await self._async_render(
            "⚠️ {{ name }}: finestra rimasta aperta, climatizzatore spento.",
            variables,
        )
        await self._async_send_notification(notify_msg, bypass_quiet=False)

    async def _async_notify_temp_change(self, old_temp, new_temp, fan_mode, room_temp, target) -> None:
        if not bool(get_conf(self.entry, CONF_NOTIFY_TEMP_CHANGE_ENABLED, DEFAULT_NOTIFY_TEMP_CHANGE_ENABLED)):
            return
        # Limite frequenza notifiche cambio temperatura
        if bool(get_conf(self.entry, CONF_NOTIFY_TEMP_CHANGE_LIMIT_ENABLED, DEFAULT_NOTIFY_TEMP_CHANGE_LIMIT_ENABLED)):
            limit_min = int(get_conf(self.entry, CONF_NOTIFY_TEMP_CHANGE_LIMIT_MIN, DEFAULT_NOTIFY_TEMP_CHANGE_LIMIT_MIN))
            now = dt_util.utcnow()
            if self._last_temp_notify is not None and (now - self._last_temp_notify) < timedelta(minutes=limit_min):
                _LOGGER.debug(
                    "%s: notifica cambio temp soppressa (limite %d min, ultima %s)",
                    self._attr_name, limit_min, self._last_temp_notify.isoformat(),
                )
                return
            self._last_temp_notify = now
        message_tpl = get_conf(self.entry, CONF_NOTIFY_TEMP_CHANGE_MESSAGE, DEFAULT_NOTIFY_TEMP_CHANGE_MESSAGE)
        message = await self._async_render(message_tpl, {
            "name": self._get_display_name(),
            "old_temp": old_temp,
            "new_temp": new_temp,
            "fan_mode": fan_mode,
            "room_temp": round(room_temp, 1),
            "target": round(target, 1),
        })
        await self._async_send_notification(message, bypass_quiet=False)
