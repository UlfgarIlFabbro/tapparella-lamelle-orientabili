"""Integrazione Termostato Intelligente FV + Batteria + Finestra + Presenza."""

from __future__ import annotations

import logging
from datetime import timedelta
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_call_later
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    CONF_SEASON_MODE,
    CONF_SIMPLE_TARGET_DAY,
    CONF_SIMPLE_TARGET_NIGHT,
    CONF_FV_PRIORITY,
    CONFIG_WRITE_DEBOUNCE_SECONDS,
    CONF_MANUAL_SHUTOFF_TIMER_ENABLED,
    CONF_MANUAL_SHUTOFF_TIMER_MIN,
    SEASON_SUMMER,
    SEASON_WINTER,
    SEASON_AUTO,
    SEASON_MANUAL,
    SEASON_OFF,
    DEFAULT_EMERGENCY_HEAT_END_THRESHOLD,
    DEFAULT_EMERGENCY_HEAT_THRESHOLD,
    DEFAULT_EMERGENCY_NOTIFY_TELEGRAM,
    DEFAULT_EMERGENCY_NOTIFY_TTS,
    DEFAULT_FV_MARGIN_W,
    DEFAULT_FV_PRIORITY,
    DEFAULT_FV_SHUTOFF_DELAY_MIN,
    DEFAULT_FV_SHUTOFF_ENABLED,
    DEFAULT_FV_SHUTOFF_MANUAL,
    DEFAULT_FV_SHUTOFF_THRESHOLD,
    DEFAULT_FV_STAGGER_MIN,
    DEFAULT_NIGHT_END_SHUTOFF_AUTO_ONLY,
    DEFAULT_NIGHT_END_SHUTOFF_ENABLED,
    DEFAULT_POWER_LIMIT_ENABLED,
    DEFAULT_POWER_LIMIT_HYSTERESIS_W,
    DEFAULT_POWER_LIMIT_MAX_W,
    DEFAULT_POWER_LIMIT_MODE,
    DEFAULT_POWER_LIMIT_NOTIFY_TELEGRAM,
    DEFAULT_POWER_LIMIT_NOTIFY_TTS,
    DEFAULT_POWER_LIMIT_RESTORE_MIN,
    DEFAULT_SIMPLE_DRY_ENABLED,
    DEFAULT_SIMPLE_DRY_MAX_MIN,
    DEFAULT_SIMPLE_NIGHT_END,
    DEFAULT_SIMPLE_NIGHT_START,
    DEFAULT_SIMPLE_NO_AUTO_ON_NIGHT,
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
    DEFAULT_SIMPLE_SUNSET_ANTICIPATE_H,
    DEFAULT_SIMPLE_TARGET_DAY,
    DEFAULT_SIMPLE_TARGET_NIGHT,
    DEFAULT_SIMPLE_TURN_ON_OFFSET_EXT,
    DEFAULT_SOC_MIN,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.CLIMATE, Platform.SWITCH]
SCHEMA_VERSION = 2
VALID_MODES = ("simple", "simple_fv", "full")

_FIELD_DEFAULTS = {
    "simple_notify_tel_ac_on": DEFAULT_SIMPLE_NOTIFY_TEL_AC_ON,
    "simple_notify_tel_ac_off": DEFAULT_SIMPLE_NOTIFY_TEL_AC_OFF,
    "simple_notify_tel_temp_change": DEFAULT_SIMPLE_NOTIFY_TEL_TEMP_CHANGE,
    "simple_notify_tel_window_open": DEFAULT_SIMPLE_NOTIFY_TEL_WINDOW_OPEN,
    "simple_notify_tel_window_close": DEFAULT_SIMPLE_NOTIFY_TEL_WINDOW_CLOSE,
    "simple_notify_tel_door_open": DEFAULT_SIMPLE_NOTIFY_TEL_DOOR_OPEN,
    "simple_notify_tel_door_close": DEFAULT_SIMPLE_NOTIFY_TEL_DOOR_CLOSE,
    "simple_notify_tel_night_start": DEFAULT_SIMPLE_NOTIFY_TEL_NIGHT_START,
    "simple_notify_tel_night_end": DEFAULT_SIMPLE_NOTIFY_TEL_NIGHT_END,
    "simple_notify_tts_ac_on": DEFAULT_SIMPLE_NOTIFY_TTS_AC_ON,
    "simple_notify_tts_ac_off": DEFAULT_SIMPLE_NOTIFY_TTS_AC_OFF,
    "simple_notify_tts_temp_change": DEFAULT_SIMPLE_NOTIFY_TTS_TEMP_CHANGE,
    "simple_notify_tts_window_open": DEFAULT_SIMPLE_NOTIFY_TTS_WINDOW_OPEN,
    "simple_notify_tts_window_close": DEFAULT_SIMPLE_NOTIFY_TTS_WINDOW_CLOSE,
    "simple_notify_tts_door_open": DEFAULT_SIMPLE_NOTIFY_TTS_DOOR_OPEN,
    "simple_notify_tts_door_close": DEFAULT_SIMPLE_NOTIFY_TTS_DOOR_CLOSE,
    "simple_notify_tts_night_start": DEFAULT_SIMPLE_NOTIFY_TTS_NIGHT_START,
    "simple_notify_tts_night_end": DEFAULT_SIMPLE_NOTIFY_TTS_NIGHT_END,
    "simple_quiet_night_tts": DEFAULT_SIMPLE_QUIET_NIGHT_TTS,
    "simple_quiet_night_notify": DEFAULT_SIMPLE_QUIET_NIGHT_NOTIFY,
    "simple_no_auto_on_night": DEFAULT_SIMPLE_NO_AUTO_ON_NIGHT,
    "simple_turn_on_offset": DEFAULT_SIMPLE_TURN_ON_OFFSET_EXT,
    "simple_dry_enabled": DEFAULT_SIMPLE_DRY_ENABLED,
    "simple_dry_max_min": DEFAULT_SIMPLE_DRY_MAX_MIN,
    "simple_target_day": DEFAULT_SIMPLE_TARGET_DAY,
    "simple_target_night": DEFAULT_SIMPLE_TARGET_NIGHT,
    "simple_night_start": DEFAULT_SIMPLE_NIGHT_START,
    "simple_night_end": DEFAULT_SIMPLE_NIGHT_END,
    "simple_sunset_anticipate_h": DEFAULT_SIMPLE_SUNSET_ANTICIPATE_H,
    "night_end_shutoff_enabled": DEFAULT_NIGHT_END_SHUTOFF_ENABLED,
    "night_end_shutoff_auto_only": DEFAULT_NIGHT_END_SHUTOFF_AUTO_ONLY,
    "update_interval_minutes": 1,
    "fv_margin_w": DEFAULT_FV_MARGIN_W,
    "fv_priority": DEFAULT_FV_PRIORITY,
    "fv_shutoff_delay_min": DEFAULT_FV_SHUTOFF_DELAY_MIN,
    "fv_shutoff_enabled": DEFAULT_FV_SHUTOFF_ENABLED,
        "fv_shutoff_manual": DEFAULT_FV_SHUTOFF_MANUAL,
    "fv_shutoff_threshold": DEFAULT_FV_SHUTOFF_THRESHOLD,
    "fv_stagger_minutes": DEFAULT_FV_STAGGER_MIN,
    "soc_min": DEFAULT_SOC_MIN,
    "power_limit_enabled": DEFAULT_POWER_LIMIT_ENABLED,
    "power_limit_mode": DEFAULT_POWER_LIMIT_MODE,
    "power_limit_max_w": DEFAULT_POWER_LIMIT_MAX_W,
    "power_limit_hysteresis_w": DEFAULT_POWER_LIMIT_HYSTERESIS_W,
    "power_limit_restore_min": DEFAULT_POWER_LIMIT_RESTORE_MIN,
    "power_limit_notify_tts": DEFAULT_POWER_LIMIT_NOTIFY_TTS,
    "power_limit_notify_telegram": DEFAULT_POWER_LIMIT_NOTIFY_TELEGRAM,
    "emergency_heat_threshold": DEFAULT_EMERGENCY_HEAT_THRESHOLD,
    "emergency_heat_end_threshold": DEFAULT_EMERGENCY_HEAT_END_THRESHOLD,
    "emergency_notify_tts": DEFAULT_EMERGENCY_NOTIFY_TTS,
    "emergency_notify_telegram": DEFAULT_EMERGENCY_NOTIFY_TELEGRAM,
}


_FRONTEND_URL_PATH = f"/{DOMAIN}_static/termostato-diag-card.js"
_FRONTEND_VERSION_TAG = "v090b56"  # cambiare ad ogni release che tocca il file JS, per invalidare la cache browser


async def _async_register_frontend_card(hass: HomeAssistant) -> None:
    """Rende disponibile il file JS della card diagnostica via HTTP, servendolo
    direttamente dalla cartella www/ dell'integrazione, e la registra come
    risorsa Lovelace senza richiedere alcuna azione manuale all'utente.

    NOTA storica: la prima versione usava add_extra_js_url per iniettare lo
    script nel frontend, ma con molte altre custom card installate il picker
    "Aggiungi card" a volte apriva prima che lo script avesse finito di
    caricare, restando bloccato in caricamento perenne. Ora registriamo
    direttamente una risorsa Lovelace nel resource storage collection —
    lo stesso identico meccanismo usato quando l'utente aggiunge una
    risorsa a mano — che ha il corretto sistema di attesa e funziona in
    modo affidabile.

    Non deve mai bloccare il setup dell'integrazione: qualsiasi errore qui
    viene solo loggato come warning.
    """
    try:
        www_path = Path(__file__).parent / "www" / "termostato-diag-card.js"
        if not www_path.exists():
            _LOGGER.warning("Card frontend non trovata in %s — salto la registrazione", www_path)
            return

        try:
            # HA moderno (2024.7+)
            from homeassistant.components.http import StaticPathConfig
            await hass.http.async_register_static_paths(
                [StaticPathConfig(_FRONTEND_URL_PATH, str(www_path), cache_headers=False)]
            )
        except ImportError:
            # HA più vecchio — API sincrona deprecata ma ancora funzionante
            hass.http.register_static_path(_FRONTEND_URL_PATH, str(www_path), cache_headers=False)

        # Registra la risorsa Lovelace programmaticamente, usando lo stesso
        # storage collection che usa l'interfaccia quando l'utente aggiunge
        # una risorsa a mano da Impostazioni → Dashboard → Risorse — a
        # differenza di add_extra_js_url, questo meccanismo ha il corretto
        # sistema di attesa lato picker "Aggiungi card" e non causa il
        # caricamento perenne osservato con l'iniezione diretta.
        await _async_ensure_lovelace_resource(hass)
    except Exception as exc:
        _LOGGER.warning("Impossibile rendere disponibile la card frontend: %s", exc)


async def _async_ensure_lovelace_resource(hass: HomeAssistant) -> None:
    """Aggiunge (o aggiorna alla versione corrente) la risorsa Lovelace per la
    card diagnostica, senza richiedere alcuna azione manuale all'utente.

    Funziona solo se la dashboard è in modalità "storage" (quella di default
    per la maggior parte degli utenti). Se è in modalità YAML, il resource
    storage collection non esiste — in quel caso ci limitiamo a loggare
    un'indicazione per l'aggiunta manuale, senza generare errori.
    """
    try:
        lovelace_data = hass.data.get("lovelace")
        resources = getattr(lovelace_data, "resources", None) if lovelace_data else None
        if resources is None:
            _LOGGER.info(
                "Dashboard non in modalità storage — aggiungi manualmente la risorsa %s da "
                "Impostazioni → Dashboard → Risorse (tipo: Modulo JavaScript) se la card non compare",
                _FRONTEND_URL_PATH,
            )
            return

        target_url = f"{_FRONTEND_URL_PATH}?v={_FRONTEND_VERSION_TAG}"
        existing_items = resources.async_items()
        matches = [item for item in existing_items if _FRONTEND_URL_PATH in item.get("url", "")]

        if not matches:
            await resources.async_create_item({"res_type": "module", "url": target_url})
            _LOGGER.info("Risorsa frontend per la card diagnostica registrata automaticamente: %s", target_url)
            return

        # Teniamo la PRIMA voce trovata (aggiornata se serve) ed eliminiamo
        # eventuali duplicati — può capitare che una versione precedente di
        # questa funzione, letta prima che lo storage risorse fosse
        # completamente caricato all'avvio, non trovasse la voce esistente e
        # ne creasse una seconda invece di aggiornarla. Questa pulizia si
        # auto-risana anche per chi ha già accumulato duplicati.
        keep = matches[0]
        if keep.get("url") != target_url:
            await resources.async_update_item(keep["id"], {"res_type": "module", "url": target_url})
            _LOGGER.info("Risorsa frontend per la card diagnostica aggiornata alla nuova versione: %s", target_url)
        for duplicate in matches[1:]:
            await resources.async_delete_item(duplicate["id"])
            _LOGGER.info("Rimossa risorsa frontend duplicata: %s", duplicate.get("url"))
    except Exception as exc:
        _LOGGER.warning(
            "Impossibile registrare/aggiornare automaticamente la risorsa frontend — "
            "aggiungila manualmente da Impostazioni → Dashboard → Risorse (URL: %s, "
            "tipo: Modulo JavaScript) se la card non compare: %s",
            _FRONTEND_URL_PATH, exc,
        )


async def _async_register_services(hass: HomeAssistant) -> None:
    """Registra i servizi custom usati dalla card diagnostica per regolare
    target e priorità direttamente, senza ricaricare l'integrazione (che
    interromperebbe timer DRY attivi, immunità in corso, ecc. — a
    differenza di una normale modifica delle opzioni via wizard).
    """

    def _find_climate_entities(call):
        entity_ids = call.data.get("entity_id", [])
        if isinstance(entity_ids, str):
            entity_ids = [entity_ids]
        found = []
        for entry_data in hass.data.get(DOMAIN, {}).values():
            if not isinstance(entry_data, dict):
                continue
            climate_entity = entry_data.get("climate")
            if climate_entity is not None and climate_entity.entity_id in entity_ids:
                found.append(climate_entity)
        return found

    def _schedule_config_write(climate_entity, field_key: str, conf_key: str, new_value: float) -> None:
        """Schedula la scrittura del nuovo valore in configurazione dopo un
        breve debounce — click ripetuti ravvicinati cancellano e
        rischedulano, producendo un solo ricaricamento finale invece di uno
        per ogni click."""
        cancel = climate_entity._config_write_debounce_cancel.get(field_key)
        if cancel is not None:
            cancel()

        async def _write_to_config(_now):
            climate_entity._config_write_debounce_cancel.pop(field_key, None)
            entry = climate_entity.entry
            new_options = dict(entry.options)
            new_options[conf_key] = new_value
            hass.config_entries.async_update_entry(entry, options=new_options)
            # async_update_entry attiva _async_update_listener, che ricarica
            # l'entry — la nuova istanza leggerà il valore direttamente
            # dalla configurazione, nessun pending/override da ripristinare.

        climate_entity._config_write_debounce_cancel[field_key] = async_call_later(
            hass, CONFIG_WRITE_DEBOUNCE_SECONDS, _write_to_config
        )

    async def _handle_adjust_target(call) -> None:
        delta = float(call.data.get("delta", 0))
        for climate_entity in _find_climate_entities(call):
            current = climate_entity._simple_current_target()
            new_value = round(current + delta, 1)
            if climate_entity._simple_is_night():
                climate_entity._pending_target_night_display = new_value
                _schedule_config_write(climate_entity, "target_night", CONF_SIMPLE_TARGET_NIGHT, new_value)
            else:
                climate_entity._pending_target_day_display = new_value
                _schedule_config_write(climate_entity, "target_day", CONF_SIMPLE_TARGET_DAY, new_value)
            climate_entity.async_write_ha_state()

    async def _handle_adjust_priority(call) -> None:
        delta = float(call.data.get("delta", 0))
        for climate_entity in _find_climate_entities(call):
            current = climate_entity._effective_priority()
            new_value = max(1, round(current + delta))
            climate_entity._pending_priority_display = new_value
            _schedule_config_write(climate_entity, "priority", CONF_FV_PRIORITY, new_value)
            climate_entity.async_write_ha_state()

    async def _handle_set_shutoff_timer(call) -> None:
        minutes = float(call.data.get("minutes", 0))
        for climate_entity in _find_climate_entities(call):
            # Annulliamo sempre un eventuale timer già attivo prima di
            # procedere, sia per sostituirlo con uno nuovo sia per
            # annullarlo del tutto (minutes=0 dalla card).
            if climate_entity._shutoff_timer_cancel is not None:
                climate_entity._shutoff_timer_cancel()
                climate_entity._shutoff_timer_cancel = None
                climate_entity._shutoff_timer_until = None
            if minutes > 0:
                climate_entity._shutoff_timer_until = dt_util.utcnow() + timedelta(minutes=minutes)
                climate_entity._shutoff_timer_cancel = async_call_later(
                    hass, timedelta(minutes=minutes), climate_entity._async_shutoff_timer_expired
                )
            climate_entity.async_write_ha_state()

    async def _handle_toggle_manual_shutoff_timer(call) -> None:
        enabled = bool(call.data.get("enabled", True))
        for climate_entity in _find_climate_entities(call):
            climate_entity._pending_timer_enabled_display = enabled
            _schedule_config_write(climate_entity, "timer_enabled", CONF_MANUAL_SHUTOFF_TIMER_ENABLED, enabled)
            climate_entity.async_write_ha_state()

    async def _handle_adjust_manual_shutoff_timer_minutes(call) -> None:
        delta = float(call.data.get("delta", 0))
        for climate_entity in _find_climate_entities(call):
            current = climate_entity._manual_shutoff_timer_minutes()
            new_value = max(5, round(current + delta))
            climate_entity._pending_timer_minutes_display = new_value
            _schedule_config_write(climate_entity, "timer_minutes", CONF_MANUAL_SHUTOFF_TIMER_MIN, new_value)
            # Se il timer è GIÀ in conto alla rovescia (accensione manuale
            # avvenuta prima di questa regolazione), il nuovo valore deve
            # valere subito anche per quel conteggio in corso — altrimenti
            # regolare i minuti dalla card non avrebbe alcun effetto finché
            # non scatta un'accensione manuale successiva. Riprogrammiamo
            # da adesso con il nuovo totale di minuti.
            if climate_entity._shutoff_timer_cancel is not None:
                climate_entity._shutoff_timer_cancel()
                climate_entity._shutoff_timer_until = dt_util.utcnow() + timedelta(minutes=new_value)
                climate_entity._shutoff_timer_cancel = async_call_later(
                    hass, timedelta(minutes=new_value), climate_entity._async_shutoff_timer_expired
                )
            climate_entity.async_write_ha_state()

    async def _handle_set_season_mode(call) -> None:
        season = call.data.get("season")
        if season not in (SEASON_SUMMER, SEASON_WINTER, SEASON_AUTO, SEASON_MANUAL, SEASON_OFF):
            return
        for climate_entity in _find_climate_entities(call):
            entry = climate_entity.entry
            new_options = dict(entry.options)
            new_options[CONF_SEASON_MODE] = season
            hass.config_entries.async_update_entry(entry, options=new_options)
            # async_update_entry attiva automaticamente _async_update_listener,
            # che ricarica l'entry — la nuova stagione si applica subito, con
            # un ricaricamento pulito invece di un override runtime in
            # memoria (evitiamo lo stesso tipo di bug di persistenza già
            # trovato per timer ed altri override in questa integrazione).

    hass.services.async_register(DOMAIN, "adjust_target", _handle_adjust_target)
    hass.services.async_register(DOMAIN, "adjust_priority", _handle_adjust_priority)
    hass.services.async_register(DOMAIN, "set_shutoff_timer", _handle_set_shutoff_timer)
    hass.services.async_register(DOMAIN, "toggle_manual_shutoff_timer", _handle_toggle_manual_shutoff_timer)
    hass.services.async_register(DOMAIN, "adjust_manual_shutoff_timer_minutes", _handle_adjust_manual_shutoff_timer_minutes)
    hass.services.async_register(DOMAIN, "set_season_mode", _handle_set_season_mode)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configura una entry. NON chiama async_update_entry per evitare loop."""
    hass.data.setdefault(DOMAIN, {}).setdefault(entry.entry_id, {})
    # Registra la card e i servizi una sola volta, indipendentemente da
    # quante istanze (termostati) sono configurate — evita registrazioni
    # duplicate.
    if not hass.data[DOMAIN].get("_frontend_card_registered"):
        hass.data[DOMAIN]["_frontend_card_registered"] = True
        await _async_register_frontend_card(hass)
    if not hass.data[DOMAIN].get("_services_registered"):
        hass.data[DOMAIN]["_services_registered"] = True
        await _async_register_services(hass)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Rimuove una entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return unload_ok


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migra le entry — scatta solo quando version < SCHEMA_VERSION.
    
    TABELLA CONVERSIONE config_mode:
    - None / "semplificato" / "semplificato_fv" / qualsiasi valore non valido:
      → "simple_fv" se fv_sensor presente, altrimenti "simple"
    - "simple" / "simple_fv" / "full": mantieni invariato
    
    NON chiama async_update_entry dentro async_setup_entry per evitare loop.
    """
    _LOGGER.info(
        "Migrazione %s v%s → v%s",
        config_entry.title,
        config_entry.version,
        SCHEMA_VERSION,
    )

    new_data = dict(config_entry.data)

    # TABELLA CONVERSIONE config_mode
    # Vecchi valori: None, "semplificato", "semplificato_fv" → nuovi
    CONVERSION = {
        "semplificato_fv": "simple_fv",
        "semplificato": "simple",
    }
    current_mode = new_data.get("config_mode")
    if current_mode in CONVERSION:
        new_data["config_mode"] = CONVERSION[current_mode]
    elif current_mode not in VALID_MODES:
        new_data["config_mode"] = "simple_fv" if new_data.get("fv_sensor") else "simple"
        _LOGGER.info(
            "%s: config_mode '%s' → '%s'",
            config_entry.title,
            current_mode,
            new_data["config_mode"],
        )

    # Aggiunge solo i campi MANCANTI — non sovrascrive mai
    for key, default in _FIELD_DEFAULTS.items():
        if key not in new_data:
            new_data[key] = default

    hass.config_entries.async_update_entry(
        config_entry,
        data=new_data,
        version=SCHEMA_VERSION,
    )
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Ricarica l'integrazione quando le opzioni vengono modificate dall'utente."""
    await hass.config_entries.async_reload(entry.entry_id)
