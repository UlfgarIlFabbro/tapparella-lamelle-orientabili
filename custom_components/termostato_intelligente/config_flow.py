"""Config flow per Termostato Intelligente FV."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from datetime import timedelta

from homeassistant import config_entries
from homeassistant.util import dt as dt_util
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_CONFIG_MODE,
    CONF_SIMPLE_DRY_ENABLED,
    CONF_SIMPLE_DRY_MAX_MIN,
    CONF_SIMPLE_NO_AUTO_ON_NIGHT,
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
    DEFAULT_MANUAL_SHUTOFF_TIMER_MIN,
    DEFAULT_SIMPLE_SHUTOFF_MARGIN,
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
    CONF_SIMPLE_NOTIFY_TTS_MANUAL_ON,
    CONF_SIMPLE_NOTIFY_TEL_MANUAL_ON,
    CONF_SIMPLE_NOTIFY_TTS_MANUAL_OFF,
    CONF_SIMPLE_NOTIFY_TEL_MANUAL_OFF,
    DEFAULT_SIMPLE_NOTIFY_TTS_MANUAL_ON,
    DEFAULT_SIMPLE_NOTIFY_TEL_MANUAL_ON,
    DEFAULT_SIMPLE_NOTIFY_TTS_MANUAL_OFF,
    DEFAULT_SIMPLE_NOTIFY_TEL_MANUAL_OFF,
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
    CONFIG_MODE_FULL,
    CONFIG_MODE_SIMPLE,
    CONFIG_MODE_SIMPLE_FV,
    DEFAULT_CONFIG_MODE,
    DEFAULT_SIMPLE_DRY_ENABLED,
    DEFAULT_SIMPLE_DRY_MAX_MIN,
    DEFAULT_SIMPLE_NO_AUTO_ON_NIGHT,
    DEFAULT_SIMPLE_TURN_ON_OFFSET_EXT,
    DEFAULT_SIMPLE_TURN_ON_OFFSET_INT,
    DEFAULT_SIMPLE_NIGHT_END,
    DEFAULT_SIMPLE_NIGHT_START,
    DEFAULT_SIMPLE_SUNSET_ANTICIPATE_H,
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
    CONF_EMERGENCY_HEAT_END_THRESHOLD,
    SWITCH_KEY_EMERGENCY,
    CONF_EMERGENCY_HEAT_THRESHOLD,
    CONF_EMERGENCY_MSG_OFF,
    CONF_EMERGENCY_MSG_ON,
    CONF_EMERGENCY_NOTIFY_TELEGRAM,
    CONF_EMERGENCY_NOTIFY_TTS,
    DEFAULT_EMERGENCY_HEAT_END_THRESHOLD,
    DEFAULT_EMERGENCY_HEAT_THRESHOLD,
    DEFAULT_EMERGENCY_MSG_OFF,
    DEFAULT_EMERGENCY_MSG_ON,
    DEFAULT_EMERGENCY_NOTIFY_TELEGRAM,
    DEFAULT_EMERGENCY_NOTIFY_TTS,
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
    DEFAULT_POWER_LIMIT_ENABLED,
    DEFAULT_POWER_LIMIT_HYSTERESIS_W,
    DEFAULT_POWER_LIMIT_MAX_W,
    DEFAULT_POWER_LIMIT_MODE,
    DEFAULT_POWER_LIMIT_MSG_OFF,
    DEFAULT_POWER_LIMIT_MSG_ON,
    DEFAULT_POWER_LIMIT_NOTIFY_TELEGRAM,
    DEFAULT_POWER_LIMIT_NOTIFY_TTS,
    DEFAULT_POWER_LIMIT_RESTORE_MIN,
    POWER_LIMIT_MODE_MULTI,
    POWER_LIMIT_MODE_SINGLE,
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
    CONF_FV_SHUTOFF_TOTAL_MINUTES,
    CONF_FV_TURN_ON_TOTAL_MINUTES,
    CONF_FV_SENSOR_OFFLINE_SHUTOFF_ENABLED,
    DEFAULT_FV_SENSOR_OFFLINE_SHUTOFF_ENABLED,
    CONF_FV_SENSOR_OFFLINE_SHUTOFF_MIN,
    DEFAULT_FV_SENSOR_OFFLINE_SHUTOFF_MIN,
    CONF_FV_SENSOR_OFFLINE_NOTIFY_TTS,
    DEFAULT_FV_SENSOR_OFFLINE_NOTIFY_TTS,
    CONF_FV_SENSOR_OFFLINE_NOTIFY_TELEGRAM,
    DEFAULT_FV_SENSOR_OFFLINE_NOTIFY_TELEGRAM,
    DEFAULT_FV_SHUTOFF_TOTAL_MINUTES,
    DEFAULT_FV_TURN_ON_TOTAL_MINUTES,
    CONF_FV_SHUTOFF_ENABLED,
    CONF_FV_SHUTOFF_MANUAL,
    CONF_FV_SHUTOFF_MANUAL_DELAY_MIN,
    DEFAULT_FV_SHUTOFF_MANUAL_DELAY_MIN,
    CONF_SIMPLE_NO_REON_MANUAL_OFF,
    CONF_SIMPLE_NO_REON_MANUAL_OFF_HOURS,
    DEFAULT_SIMPLE_NO_REON_MANUAL_OFF,
    DEFAULT_SIMPLE_NO_REON_MANUAL_OFF_HOURS,
    CONF_FV_SHUTOFF_EXTRA_HOURS,
    CONF_FV_SHUTOFF_THRESHOLD,
    CONF_FV_STAGGER_MIN,
    CONF_FV_START_TIME,
    CONF_HOT_OFFSET,
    CONF_MIN_BELOW_INTERNAL,
    CONF_NAME,
    CONF_NIGHT_AC_ENABLED,
    CONF_NIGHT_END_SHUTOFF_AUTO_ONLY,
    CONF_NIGHT_END_SHUTOFF_ENABLED,
    CONF_NIGHT_END_TIME,
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
    CONF_PROFILE,
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
    CONF_SIMPLE_EXTERNAL_SENSOR_STALE_MIN,
    DEFAULT_SIMPLE_EXTERNAL_SENSOR_STALE_MIN,
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
    DEFAULT_FV_SHUTOFF_EXTRA_HOURS,
    DEFAULT_FV_SHUTOFF_THRESHOLD,
    DEFAULT_FV_STAGGER_MIN,
    DEFAULT_FV_START_TIME,
    DEFAULT_HOT_OFFSET,
    DEFAULT_MIN_BELOW_INTERNAL,
    DEFAULT_NAME,
    DEFAULT_NIGHT_AC_ENABLED,
    DEFAULT_NIGHT_END_SHUTOFF_AUTO_ONLY,
    DEFAULT_NIGHT_END_SHUTOFF_ENABLED,
    DEFAULT_NIGHT_END_TIME,
    DEFAULT_NIGHT_OFFSET,
    DEFAULT_NIGHT_SHUTOFF_DELTA,
    DEFAULT_NIGHT_SHUTOFF_ENABLED,
    DEFAULT_NIGHT_SHUTOFF_MIN,
    DEFAULT_NIGHT_START_TIME,
    DEFAULT_NIGHT_TURN_ON_OFFSET,
    DEFAULT_NOTIFY_NIGHT_END_NOTIFY,
    DEFAULT_NOTIFY_NIGHT_END_TTS,
    DEFAULT_NOTIFY_POWER_NOTIFY,
    DEFAULT_NOTIFY_POWER_TTS,
    DEFAULT_NOTIFY_TEMP_CHANGE_ENABLED,
    DEFAULT_NOTIFY_TEMP_CHANGE_LIMIT_ENABLED,
    DEFAULT_NOTIFY_TEMP_CHANGE_LIMIT_MIN,
    DEFAULT_NOTIFY_TEMP_CHANGE_MESSAGE,
    DEFAULT_PRESENCE_BOOST_ENABLED,
    DEFAULT_PRESENCE_BOOST_MIN,
    DEFAULT_PRESENCE_BOOST_OFFSET,
    DEFAULT_PROFILE,
    DEFAULT_QUIET_ENABLED,
    DEFAULT_QUIET_END_TIME,
    DEFAULT_QUIET_NOTIFY,
    DEFAULT_QUIET_START_TIME,
    DEFAULT_QUIET_TTS,
    DEFAULT_RANGE_OFFSET,
    DEFAULT_SOC_MIN,
    DEFAULT_TARGET_TEMP,
    DEFAULT_TEMP_DELTA,
    DEFAULT_TTS_MESSAGE_OPEN,
    DEFAULT_TURN_ON_OFFSET,
    DEFAULT_UPDATE_INTERVAL_MIN,
    DEFAULT_WINDOW_DELAY_MIN,
    DOMAIN,
    PRESET_AGGRESSIVO,
    PRESET_BILANCIATO,
    PRESET_DELICATO,
    PRESET_PERSONALIZZATO,
    PRESET_VALUES,
)


def _f(schema_cls, key: str, defaults: dict, fallback: Any = None):
    if key in defaults and defaults[key] not in (None, "", []):
        return schema_cls(key, default=defaults[key])
    if fallback is not None:
        return schema_cls(key, default=fallback)
    return schema_cls(key)


def _schema_modalita(defaults: dict) -> vol.Schema:
    return vol.Schema({
        _f(vol.Required, CONF_CONFIG_MODE, defaults, DEFAULT_CONFIG_MODE): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[CONFIG_MODE_SIMPLE, CONFIG_MODE_SIMPLE_FV, CONFIG_MODE_FULL],
                mode=selector.SelectSelectorMode.LIST,
                translation_key="config_mode",
            )
        ),
    })


def _schema_simple_entita(defaults: dict) -> vol.Schema:
    return vol.Schema({
        _f(vol.Required, CONF_NAME, defaults, DEFAULT_NAME): selector.TextSelector(),
        _f(vol.Required, CONF_CLIMATE_ENTITY, defaults): selector.EntitySelector(selector.EntitySelectorConfig(domain="climate")),
        _f(vol.Optional, CONF_TEMP_SENSOR, defaults): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
        _f(vol.Optional, CONF_SIMPLE_EXTERNAL_SENSOR_STALE_MIN, defaults, DEFAULT_SIMPLE_EXTERNAL_SENSOR_STALE_MIN): selector.NumberSelector(selector.NumberSelectorConfig(min=15, max=180, step=5, unit_of_measurement="min", mode="box")),
        _f(vol.Optional, CONF_WINDOW_SENSOR, defaults): selector.EntitySelector(selector.EntitySelectorConfig(domain="binary_sensor")),
        _f(vol.Optional, CONF_WINDOW_DETECTION_ENABLED, defaults, DEFAULT_WINDOW_DETECTION_ENABLED): selector.BooleanSelector(),
        _f(vol.Optional, CONF_DOOR_SENSOR, defaults): selector.EntitySelector(selector.EntitySelectorConfig(domain="binary_sensor")),
    })


def _schema_simple_temperature(defaults: dict) -> vol.Schema:
    return vol.Schema({
        _f(vol.Optional, CONF_SEASON_MODE, defaults, DEFAULT_SEASON_MODE): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[SEASON_SUMMER, SEASON_WINTER, SEASON_AUTO, SEASON_MANUAL, SEASON_OFF],
                translation_key="season_mode",
            )
        ),
        _f(vol.Required, CONF_SIMPLE_TARGET_DAY, defaults, DEFAULT_SIMPLE_TARGET_DAY): selector.NumberSelector(selector.NumberSelectorConfig(min=16, max=30, step=0.5, unit_of_measurement="°C", mode="box")),
        _f(vol.Optional, CONF_SIMPLE_TURN_ON_OFFSET, defaults, DEFAULT_SIMPLE_TURN_ON_OFFSET_EXT): selector.NumberSelector(selector.NumberSelectorConfig(min=0.3, max=3.0, step=0.1, unit_of_measurement="°C", mode="box")),
        _f(vol.Optional, CONF_SIMPLE_SHUTOFF_MARGIN, defaults, DEFAULT_SIMPLE_SHUTOFF_MARGIN): selector.NumberSelector(selector.NumberSelectorConfig(min=0, max=2.0, step=0.1, unit_of_measurement="°C", mode="box")),
        _f(vol.Optional, CONF_SIMPLE_ECO_DAY_ENABLED, defaults, DEFAULT_SIMPLE_ECO_DAY_ENABLED): selector.BooleanSelector(),
        _f(vol.Optional, CONF_SIMPLE_ECO_NIGHT_ENABLED, defaults, DEFAULT_SIMPLE_ECO_NIGHT_ENABLED): selector.BooleanSelector(),
        _f(vol.Optional, CONF_MANUAL_SHUTOFF_TIMER_ENABLED, defaults, DEFAULT_MANUAL_SHUTOFF_TIMER_ENABLED): selector.BooleanSelector(),
        _f(vol.Optional, CONF_MANUAL_SHUTOFF_TIMER_MIN, defaults, DEFAULT_MANUAL_SHUTOFF_TIMER_MIN): selector.NumberSelector(selector.NumberSelectorConfig(min=0, max=480, step=5, unit_of_measurement="min", mode="box")),
        _f(vol.Optional, CONF_SIMPLE_DRY_ENABLED, defaults, DEFAULT_SIMPLE_DRY_ENABLED): selector.BooleanSelector(),
        _f(vol.Optional, CONF_SIMPLE_DRY_MAX_MIN, defaults, DEFAULT_SIMPLE_DRY_MAX_MIN): selector.NumberSelector(selector.NumberSelectorConfig(min=10, max=60, step=5, unit_of_measurement="min", mode="box")),
        _f(vol.Required, CONF_SIMPLE_TARGET_NIGHT, defaults, DEFAULT_SIMPLE_TARGET_NIGHT): selector.NumberSelector(selector.NumberSelectorConfig(min=16, max=30, step=0.5, unit_of_measurement="°C", mode="box")),
        _f(vol.Required, CONF_SIMPLE_NIGHT_START, defaults, DEFAULT_SIMPLE_NIGHT_START): selector.TimeSelector(),
        _f(vol.Required, CONF_SIMPLE_NIGHT_END, defaults, DEFAULT_SIMPLE_NIGHT_END): selector.TimeSelector(),
        _f(vol.Optional, CONF_NIGHT_END_SHUTOFF_ENABLED, defaults, DEFAULT_NIGHT_END_SHUTOFF_ENABLED): selector.BooleanSelector(),
        _f(vol.Optional, CONF_NIGHT_END_SHUTOFF_AUTO_ONLY, defaults, DEFAULT_NIGHT_END_SHUTOFF_AUTO_ONLY): selector.BooleanSelector(),
        _f(vol.Optional, CONF_SIMPLE_NO_AUTO_ON_NIGHT, defaults, DEFAULT_SIMPLE_NO_AUTO_ON_NIGHT): selector.BooleanSelector(),
    })


def _schema_inverno(defaults: dict) -> vol.Schema:
    """❄️ Schermata dedicata al funzionamento invernale — separata e ben
    evidenziata, visibile solo quando la modalità stagionale lo richiede."""
    return vol.Schema({
        _f(vol.Required, CONF_WINTER_TARGET_DAY, defaults, DEFAULT_WINTER_TARGET_DAY): selector.NumberSelector(selector.NumberSelectorConfig(min=14, max=26, step=0.5, unit_of_measurement="°C", mode="box")),
        _f(vol.Required, CONF_WINTER_TARGET_NIGHT, defaults, DEFAULT_WINTER_TARGET_NIGHT): selector.NumberSelector(selector.NumberSelectorConfig(min=14, max=26, step=0.5, unit_of_measurement="°C", mode="box")),
        _f(vol.Optional, CONF_WINTER_TURN_ON_OFFSET, defaults, DEFAULT_WINTER_TURN_ON_OFFSET): selector.NumberSelector(selector.NumberSelectorConfig(min=0.2, max=2.0, step=0.1, unit_of_measurement="°C", mode="box")),
        _f(vol.Optional, CONF_WINTER_SHUTOFF_MARGIN, defaults, DEFAULT_WINTER_SHUTOFF_MARGIN): selector.NumberSelector(selector.NumberSelectorConfig(min=0, max=2.0, step=0.1, unit_of_measurement="°C", mode="box")),
        _f(vol.Optional, CONF_WINTER_SOC_MIN, defaults, DEFAULT_WINTER_SOC_MIN): selector.NumberSelector(selector.NumberSelectorConfig(min=0, max=100, step=1, unit_of_measurement="%", mode="box")),
        _f(vol.Optional, CONF_WINTER_FLOOR_SENSOR, defaults): selector.EntitySelector(selector.EntitySelectorConfig(domain="binary_sensor")),
        _f(vol.Optional, CONF_EMERGENCY_WINTER_HEAT_THRESHOLD, defaults, DEFAULT_EMERGENCY_WINTER_HEAT_THRESHOLD): selector.NumberSelector(selector.NumberSelectorConfig(min=0.5, max=5.0, step=0.1, unit_of_measurement="°C", mode="box")),
        _f(vol.Optional, CONF_EMERGENCY_WINTER_HEAT_END_THRESHOLD, defaults, DEFAULT_EMERGENCY_WINTER_HEAT_END_THRESHOLD): selector.NumberSelector(selector.NumberSelectorConfig(min=0.1, max=3.0, step=0.1, unit_of_measurement="°C", mode="box")),
    })


def _schema_energia_simple(defaults: dict, sunset_str: str = "", cutoff_str: str = "") -> vol.Schema:
    """Schema step FV con campi readonly per orario tramonto e orario limite controllo manuale.

    Fascia oraria accensione FV non configurabile — parte dalla fine della notte
    e termina automaticamente al tramonto - X ore (sun.sun).
    """
    return vol.Schema({
        _f(vol.Optional, "sunset_info", defaults, sunset_str): selector.TextSelector(),
        _f(vol.Optional, "cutoff_info", defaults, cutoff_str): selector.TextSelector(),
        _f(vol.Optional, CONF_SIMPLE_SUNSET_ANTICIPATE_H, defaults, DEFAULT_SIMPLE_SUNSET_ANTICIPATE_H): selector.NumberSelector(selector.NumberSelectorConfig(min=2, max=4, step=0.5, unit_of_measurement="ore", mode="box")),
        _f(vol.Optional, CONF_FV_SENSOR, defaults): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
        _f(vol.Optional, CONF_CONSUMPTION_SENSOR, defaults): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
        _f(vol.Optional, CONF_BATTERY_SENSOR, defaults): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
        _f(vol.Optional, CONF_FV_MARGIN_W, defaults, DEFAULT_FV_MARGIN_W): selector.NumberSelector(selector.NumberSelectorConfig(min=0, max=5000, step=50, unit_of_measurement="W", mode="box")),
        _f(vol.Optional, CONF_SOC_MIN, defaults, DEFAULT_SOC_MIN): selector.NumberSelector(selector.NumberSelectorConfig(min=0, max=100, step=1, unit_of_measurement="%", mode="box")),
        _f(vol.Optional, CONF_FV_PRIORITY, defaults, DEFAULT_FV_PRIORITY): selector.NumberSelector(selector.NumberSelectorConfig(min=1, max=99, step=1, mode="box")),
        _f(vol.Optional, CONF_FV_STAGGER_MIN, defaults, DEFAULT_FV_STAGGER_MIN): selector.NumberSelector(selector.NumberSelectorConfig(min=0, max=60, step=1, unit_of_measurement="min", mode="box")),
        _f(vol.Optional, CONF_FV_SHUTOFF_ENABLED, defaults, DEFAULT_FV_SHUTOFF_ENABLED): selector.BooleanSelector(),
        _f(vol.Optional, CONF_FV_SHUTOFF_MANUAL, defaults, DEFAULT_FV_SHUTOFF_MANUAL): selector.BooleanSelector(),
        _f(vol.Optional, CONF_FV_SHUTOFF_MANUAL_DELAY_MIN, defaults, DEFAULT_FV_SHUTOFF_MANUAL_DELAY_MIN): selector.NumberSelector(selector.NumberSelectorConfig(min=10, max=120, step=5, unit_of_measurement="min", mode="box")),
        _f(vol.Optional, CONF_SIMPLE_NO_REON_MANUAL_OFF, defaults, DEFAULT_SIMPLE_NO_REON_MANUAL_OFF): selector.BooleanSelector(),
        _f(vol.Optional, CONF_SIMPLE_NO_REON_MANUAL_OFF_HOURS, defaults, DEFAULT_SIMPLE_NO_REON_MANUAL_OFF_HOURS): selector.NumberSelector(selector.NumberSelectorConfig(min=0.5, max=24, step=0.5, unit_of_measurement="ore", mode="box")),
        _f(vol.Optional, CONF_FV_SHUTOFF_TOTAL_MINUTES, defaults, DEFAULT_FV_SHUTOFF_TOTAL_MINUTES): selector.NumberSelector(selector.NumberSelectorConfig(min=5, max=60, step=1, unit_of_measurement="min", mode="box")),
        _f(vol.Optional, CONF_FV_TURN_ON_TOTAL_MINUTES, defaults, DEFAULT_FV_TURN_ON_TOTAL_MINUTES): selector.NumberSelector(selector.NumberSelectorConfig(min=5, max=60, step=1, unit_of_measurement="min", mode="box")),
        _f(vol.Optional, CONF_FV_SENSOR_OFFLINE_SHUTOFF_ENABLED, defaults, DEFAULT_FV_SENSOR_OFFLINE_SHUTOFF_ENABLED): selector.BooleanSelector(),
        _f(vol.Optional, CONF_FV_SENSOR_OFFLINE_SHUTOFF_MIN, defaults, DEFAULT_FV_SENSOR_OFFLINE_SHUTOFF_MIN): selector.NumberSelector(selector.NumberSelectorConfig(min=15, max=180, step=5, unit_of_measurement="min", mode="box")),
        _f(vol.Optional, CONF_FV_SHUTOFF_THRESHOLD, defaults, DEFAULT_FV_SHUTOFF_THRESHOLD): selector.NumberSelector(selector.NumberSelectorConfig(min=-5000, max=5000, step=50, unit_of_measurement="W", mode="box")),
    })


def _schema_simple_notifiche(defaults: dict, has_fv: bool = True) -> vol.Schema:
    fields = {
        # --- Google Home ---
        _f(vol.Optional, CONF_TTS_PLAYERS, defaults): selector.EntitySelector(selector.EntitySelectorConfig(domain="media_player", multiple=True)),
        _f(vol.Optional, CONF_TTS_ENGINE, defaults): selector.EntitySelector(selector.EntitySelectorConfig(domain="tts")),
        _f(vol.Optional, CONF_SIMPLE_NOTIFY_TTS_AC_ON, defaults, DEFAULT_SIMPLE_NOTIFY_TTS_AC_ON): selector.BooleanSelector(),
        _f(vol.Optional, CONF_SIMPLE_NOTIFY_TTS_MANUAL_ON, defaults, DEFAULT_SIMPLE_NOTIFY_TTS_MANUAL_ON): selector.BooleanSelector(),
        _f(vol.Optional, CONF_SIMPLE_NOTIFY_TTS_MANUAL_OFF, defaults, DEFAULT_SIMPLE_NOTIFY_TTS_MANUAL_OFF): selector.BooleanSelector(),
        _f(vol.Optional, CONF_SIMPLE_NOTIFY_TTS_AC_OFF, defaults, DEFAULT_SIMPLE_NOTIFY_TTS_AC_OFF): selector.BooleanSelector(),
        _f(vol.Optional, CONF_SIMPLE_NOTIFY_TTS_TEMP_CHANGE, defaults, DEFAULT_SIMPLE_NOTIFY_TTS_TEMP_CHANGE): selector.BooleanSelector(),
        _f(vol.Optional, CONF_SIMPLE_NOTIFY_TTS_WINDOW_OPEN, defaults, DEFAULT_SIMPLE_NOTIFY_TTS_WINDOW_OPEN): selector.BooleanSelector(),
        _f(vol.Optional, CONF_SIMPLE_NOTIFY_TTS_WINDOW_CLOSE, defaults, DEFAULT_SIMPLE_NOTIFY_TTS_WINDOW_CLOSE): selector.BooleanSelector(),
        _f(vol.Optional, CONF_SIMPLE_NOTIFY_TTS_DOOR_OPEN, defaults, DEFAULT_SIMPLE_NOTIFY_TTS_DOOR_OPEN): selector.BooleanSelector(),
        _f(vol.Optional, CONF_SIMPLE_NOTIFY_TTS_DOOR_CLOSE, defaults, DEFAULT_SIMPLE_NOTIFY_TTS_DOOR_CLOSE): selector.BooleanSelector(),
        _f(vol.Optional, CONF_SIMPLE_NOTIFY_TTS_NIGHT_START, defaults, DEFAULT_SIMPLE_NOTIFY_TTS_NIGHT_START): selector.BooleanSelector(),
        _f(vol.Optional, CONF_SIMPLE_NOTIFY_TTS_NIGHT_END, defaults, DEFAULT_SIMPLE_NOTIFY_TTS_NIGHT_END): selector.BooleanSelector(),
        _f(vol.Optional, CONF_SIMPLE_QUIET_NIGHT_TTS, defaults, DEFAULT_SIMPLE_QUIET_NIGHT_TTS): selector.BooleanSelector(),
    }
    if has_fv:
        fields[_f(vol.Optional, CONF_FV_SENSOR_OFFLINE_NOTIFY_TTS, defaults, DEFAULT_FV_SENSOR_OFFLINE_NOTIFY_TTS)] = selector.BooleanSelector()
    fields.update({
        # --- Telegram ---
        _f(vol.Optional, CONF_NOTIFY_TARGETS, defaults): selector.EntitySelector(selector.EntitySelectorConfig(domain="notify", multiple=True)),
        _f(vol.Optional, CONF_NOTIFY_CHAT_IDS, defaults): selector.TextSelector(),
        _f(vol.Optional, CONF_SIMPLE_NOTIFY_TEL_AC_ON, defaults, DEFAULT_SIMPLE_NOTIFY_TEL_AC_ON): selector.BooleanSelector(),
        _f(vol.Optional, CONF_SIMPLE_NOTIFY_TEL_MANUAL_ON, defaults, DEFAULT_SIMPLE_NOTIFY_TEL_MANUAL_ON): selector.BooleanSelector(),
        _f(vol.Optional, CONF_SIMPLE_NOTIFY_TEL_MANUAL_OFF, defaults, DEFAULT_SIMPLE_NOTIFY_TEL_MANUAL_OFF): selector.BooleanSelector(),
        _f(vol.Optional, CONF_SIMPLE_NOTIFY_TEL_AC_OFF, defaults, DEFAULT_SIMPLE_NOTIFY_TEL_AC_OFF): selector.BooleanSelector(),
        _f(vol.Optional, CONF_SIMPLE_NOTIFY_TEL_TEMP_CHANGE, defaults, DEFAULT_SIMPLE_NOTIFY_TEL_TEMP_CHANGE): selector.BooleanSelector(),
        _f(vol.Optional, CONF_SIMPLE_NOTIFY_TEL_WINDOW_OPEN, defaults, DEFAULT_SIMPLE_NOTIFY_TEL_WINDOW_OPEN): selector.BooleanSelector(),
        _f(vol.Optional, CONF_SIMPLE_NOTIFY_TEL_WINDOW_CLOSE, defaults, DEFAULT_SIMPLE_NOTIFY_TEL_WINDOW_CLOSE): selector.BooleanSelector(),
        _f(vol.Optional, CONF_SIMPLE_NOTIFY_TEL_DOOR_OPEN, defaults, DEFAULT_SIMPLE_NOTIFY_TEL_DOOR_OPEN): selector.BooleanSelector(),
        _f(vol.Optional, CONF_SIMPLE_NOTIFY_TEL_DOOR_CLOSE, defaults, DEFAULT_SIMPLE_NOTIFY_TEL_DOOR_CLOSE): selector.BooleanSelector(),
        _f(vol.Optional, CONF_SIMPLE_NOTIFY_TEL_NIGHT_START, defaults, DEFAULT_SIMPLE_NOTIFY_TEL_NIGHT_START): selector.BooleanSelector(),
        _f(vol.Optional, CONF_SIMPLE_NOTIFY_TEL_NIGHT_END, defaults, DEFAULT_SIMPLE_NOTIFY_TEL_NIGHT_END): selector.BooleanSelector(),
        _f(vol.Optional, CONF_SIMPLE_QUIET_NIGHT_NOTIFY, defaults, DEFAULT_SIMPLE_QUIET_NIGHT_NOTIFY): selector.BooleanSelector(),
    })
    if has_fv:
        fields[_f(vol.Optional, CONF_FV_SENSOR_OFFLINE_NOTIFY_TELEGRAM, defaults, DEFAULT_FV_SENSOR_OFFLINE_NOTIFY_TELEGRAM)] = selector.BooleanSelector()
    return vol.Schema(fields)




def _schema_emergenza_simple(defaults: dict) -> vol.Schema:
    """Schema emergenza caldo per modo semplificato FV."""
    return vol.Schema({
        _f(vol.Optional, "emergency_heat_active", defaults, False): selector.BooleanSelector(),
        _f(vol.Optional, CONF_EMERGENCY_HEAT_THRESHOLD, defaults, DEFAULT_EMERGENCY_HEAT_THRESHOLD): selector.NumberSelector(selector.NumberSelectorConfig(min=0.5, max=5.0, step=0.1, unit_of_measurement="°C", mode="box")),
        _f(vol.Optional, CONF_EMERGENCY_HEAT_END_THRESHOLD, defaults, DEFAULT_EMERGENCY_HEAT_END_THRESHOLD): selector.NumberSelector(selector.NumberSelectorConfig(min=0.1, max=3.0, step=0.1, unit_of_measurement="°C", mode="box")),
        _f(vol.Optional, CONF_EMERGENCY_NOTIFY_TTS, defaults, DEFAULT_EMERGENCY_NOTIFY_TTS): selector.BooleanSelector(),
        _f(vol.Optional, CONF_EMERGENCY_NOTIFY_TELEGRAM, defaults, DEFAULT_EMERGENCY_NOTIFY_TELEGRAM): selector.BooleanSelector(),
    })


def _schema_emergenza_completo(defaults: dict) -> vol.Schema:
    """Schema emergenza caldo per modo completo — aggiunge messaggi personalizzabili."""
    return vol.Schema({
        _f(vol.Optional, "emergency_heat_active", defaults, False): selector.BooleanSelector(),
        _f(vol.Optional, CONF_EMERGENCY_HEAT_THRESHOLD, defaults, DEFAULT_EMERGENCY_HEAT_THRESHOLD): selector.NumberSelector(selector.NumberSelectorConfig(min=0.5, max=5.0, step=0.1, unit_of_measurement="°C", mode="box")),
        _f(vol.Optional, CONF_EMERGENCY_HEAT_END_THRESHOLD, defaults, DEFAULT_EMERGENCY_HEAT_END_THRESHOLD): selector.NumberSelector(selector.NumberSelectorConfig(min=0.1, max=3.0, step=0.1, unit_of_measurement="°C", mode="box")),
        _f(vol.Optional, CONF_EMERGENCY_NOTIFY_TTS, defaults, DEFAULT_EMERGENCY_NOTIFY_TTS): selector.BooleanSelector(),
        _f(vol.Optional, CONF_EMERGENCY_NOTIFY_TELEGRAM, defaults, DEFAULT_EMERGENCY_NOTIFY_TELEGRAM): selector.BooleanSelector(),
        _f(vol.Optional, CONF_EMERGENCY_MSG_ON, defaults, DEFAULT_EMERGENCY_MSG_ON): selector.TextSelector(selector.TextSelectorConfig(multiline=True)),
        _f(vol.Optional, CONF_EMERGENCY_MSG_OFF, defaults, DEFAULT_EMERGENCY_MSG_OFF): selector.TextSelector(selector.TextSelectorConfig(multiline=True)),
    })

def _schema_protezione_potenza(defaults: dict) -> vol.Schema:
    """Schema protezione potenza — comune a tutti i modi."""
    return vol.Schema({
        _f(vol.Optional, CONF_POWER_LIMIT_ENABLED, defaults, DEFAULT_POWER_LIMIT_ENABLED): selector.BooleanSelector(),
        _f(vol.Optional, CONF_POWER_LIMIT_SENSOR, defaults): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
        _f(vol.Optional, CONF_POWER_LIMIT_MODE, defaults, DEFAULT_POWER_LIMIT_MODE): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[POWER_LIMIT_MODE_SINGLE, POWER_LIMIT_MODE_MULTI],
                mode=selector.SelectSelectorMode.LIST,
                translation_key="power_limit_mode",
            )
        ),
        _f(vol.Optional, CONF_POWER_LIMIT_MAX_W, defaults, DEFAULT_POWER_LIMIT_MAX_W): selector.NumberSelector(selector.NumberSelectorConfig(min=500, max=15000, step=100, unit_of_measurement="W", mode="box")),
        _f(vol.Optional, CONF_POWER_LIMIT_HYSTERESIS_W, defaults, DEFAULT_POWER_LIMIT_HYSTERESIS_W): selector.NumberSelector(selector.NumberSelectorConfig(min=100, max=3000, step=50, unit_of_measurement="W", mode="box")),
        _f(vol.Optional, CONF_POWER_LIMIT_RESTORE_MIN, defaults, DEFAULT_POWER_LIMIT_RESTORE_MIN): selector.NumberSelector(selector.NumberSelectorConfig(min=1, max=30, step=1, unit_of_measurement="min", mode="box")),
        _f(vol.Optional, CONF_POWER_LIMIT_NOTIFY_TTS, defaults, DEFAULT_POWER_LIMIT_NOTIFY_TTS): selector.BooleanSelector(),
        _f(vol.Optional, CONF_POWER_LIMIT_NOTIFY_TELEGRAM, defaults, DEFAULT_POWER_LIMIT_NOTIFY_TELEGRAM): selector.BooleanSelector(),
    })


def _schema_protezione_potenza_completo(defaults: dict) -> vol.Schema:
    """Schema protezione potenza per modo completo — aggiunge messaggi personalizzabili."""
    return vol.Schema({
        _f(vol.Optional, CONF_POWER_LIMIT_ENABLED, defaults, DEFAULT_POWER_LIMIT_ENABLED): selector.BooleanSelector(),
        _f(vol.Optional, CONF_POWER_LIMIT_SENSOR, defaults): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
        _f(vol.Optional, CONF_POWER_LIMIT_MODE, defaults, DEFAULT_POWER_LIMIT_MODE): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[POWER_LIMIT_MODE_SINGLE, POWER_LIMIT_MODE_MULTI],
                mode=selector.SelectSelectorMode.LIST,
                translation_key="power_limit_mode",
            )
        ),
        _f(vol.Optional, CONF_POWER_LIMIT_MAX_W, defaults, DEFAULT_POWER_LIMIT_MAX_W): selector.NumberSelector(selector.NumberSelectorConfig(min=500, max=15000, step=100, unit_of_measurement="W", mode="box")),
        _f(vol.Optional, CONF_POWER_LIMIT_HYSTERESIS_W, defaults, DEFAULT_POWER_LIMIT_HYSTERESIS_W): selector.NumberSelector(selector.NumberSelectorConfig(min=100, max=3000, step=50, unit_of_measurement="W", mode="box")),
        _f(vol.Optional, CONF_POWER_LIMIT_RESTORE_MIN, defaults, DEFAULT_POWER_LIMIT_RESTORE_MIN): selector.NumberSelector(selector.NumberSelectorConfig(min=1, max=30, step=1, unit_of_measurement="min", mode="box")),
        _f(vol.Optional, CONF_POWER_LIMIT_NOTIFY_TTS, defaults, DEFAULT_POWER_LIMIT_NOTIFY_TTS): selector.BooleanSelector(),
        _f(vol.Optional, CONF_POWER_LIMIT_NOTIFY_TELEGRAM, defaults, DEFAULT_POWER_LIMIT_NOTIFY_TELEGRAM): selector.BooleanSelector(),
        _f(vol.Optional, CONF_POWER_LIMIT_MSG_OFF, defaults, DEFAULT_POWER_LIMIT_MSG_OFF): selector.TextSelector(selector.TextSelectorConfig(multiline=True)),
        _f(vol.Optional, CONF_POWER_LIMIT_MSG_ON, defaults, DEFAULT_POWER_LIMIT_MSG_ON): selector.TextSelector(selector.TextSelectorConfig(multiline=True)),
    })

def _schema_user(defaults: dict) -> vol.Schema:
    return vol.Schema({
        _f(vol.Required, CONF_NAME, defaults, DEFAULT_NAME): selector.TextSelector(),
        _f(vol.Required, CONF_CLIMATE_ENTITY, defaults): selector.EntitySelector(selector.EntitySelectorConfig(domain="climate")),
        _f(vol.Required, CONF_TEMP_SENSOR, defaults): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
        _f(vol.Required, CONF_WINDOW_SENSOR, defaults): selector.EntitySelector(selector.EntitySelectorConfig(domain="binary_sensor")),
        _f(vol.Optional, CONF_WINDOW_DETECTION_ENABLED, defaults, DEFAULT_WINDOW_DETECTION_ENABLED): selector.BooleanSelector(),
        _f(vol.Optional, CONF_PRESENCE_SENSOR, defaults): selector.EntitySelector(selector.EntitySelectorConfig(domain="binary_sensor")),
        _f(vol.Optional, CONF_DOOR_SENSOR, defaults): selector.EntitySelector(selector.EntitySelectorConfig(domain="binary_sensor")),
    })


def _schema_sensori(defaults: dict) -> vol.Schema:
    return vol.Schema({
        _f(vol.Optional, CONF_NAME, defaults, DEFAULT_NAME): selector.TextSelector(),
        _f(vol.Required, CONF_TEMP_SENSOR, defaults): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
        _f(vol.Required, CONF_WINDOW_SENSOR, defaults): selector.EntitySelector(selector.EntitySelectorConfig(domain="binary_sensor")),
        _f(vol.Optional, CONF_WINDOW_DETECTION_ENABLED, defaults, DEFAULT_WINDOW_DETECTION_ENABLED): selector.BooleanSelector(),
        _f(vol.Optional, CONF_PRESENCE_SENSOR, defaults): selector.EntitySelector(selector.EntitySelectorConfig(domain="binary_sensor")),
        _f(vol.Optional, CONF_DOOR_SENSOR, defaults): selector.EntitySelector(selector.EntitySelectorConfig(domain="binary_sensor")),
    })


def _schema_energia(defaults: dict) -> vol.Schema:
    return vol.Schema({
        _f(vol.Optional, CONF_FV_SENSOR, defaults): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
        _f(vol.Optional, CONF_CONSUMPTION_SENSOR, defaults): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
        _f(vol.Optional, CONF_BATTERY_SENSOR, defaults): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
        _f(vol.Optional, CONF_FV_MARGIN_W, defaults, DEFAULT_FV_MARGIN_W): selector.NumberSelector(selector.NumberSelectorConfig(min=0, max=5000, step=50, unit_of_measurement="W", mode="box")),
        _f(vol.Optional, CONF_SOC_MIN, defaults, DEFAULT_SOC_MIN): selector.NumberSelector(selector.NumberSelectorConfig(min=0, max=100, step=1, unit_of_measurement="%", mode="box")),
        _f(vol.Optional, CONF_FV_START_TIME, defaults, DEFAULT_FV_START_TIME): selector.TimeSelector(),
        _f(vol.Optional, CONF_FV_END_TIME, defaults, DEFAULT_FV_END_TIME): selector.TimeSelector(),
        _f(vol.Optional, CONF_FV_PRIORITY, defaults, DEFAULT_FV_PRIORITY): selector.NumberSelector(selector.NumberSelectorConfig(min=1, max=99, step=1, mode="box")),
        _f(vol.Optional, CONF_FV_STAGGER_MIN, defaults, DEFAULT_FV_STAGGER_MIN): selector.NumberSelector(selector.NumberSelectorConfig(min=0, max=60, step=1, unit_of_measurement="min", mode="box")),
        _f(vol.Optional, CONF_FV_SHUTOFF_ENABLED, defaults, DEFAULT_FV_SHUTOFF_ENABLED): selector.BooleanSelector(),
        _f(vol.Optional, CONF_FV_SHUTOFF_MANUAL, defaults, DEFAULT_FV_SHUTOFF_MANUAL): selector.BooleanSelector(),
        _f(vol.Optional, CONF_SIMPLE_NO_REON_MANUAL_OFF, defaults, DEFAULT_SIMPLE_NO_REON_MANUAL_OFF): selector.BooleanSelector(),
        _f(vol.Optional, CONF_SIMPLE_NO_REON_MANUAL_OFF_HOURS, defaults, DEFAULT_SIMPLE_NO_REON_MANUAL_OFF_HOURS): selector.NumberSelector(selector.NumberSelectorConfig(min=0.5, max=24, step=0.5, unit_of_measurement="ore", mode="box")),
        _f(vol.Optional, CONF_FV_SHUTOFF_DELAY_MIN, defaults, DEFAULT_FV_SHUTOFF_DELAY_MIN): selector.NumberSelector(selector.NumberSelectorConfig(min=1, max=60, step=1, unit_of_measurement="campioni", mode="box")),
        _f(vol.Optional, CONF_FV_SHUTOFF_THRESHOLD, defaults, DEFAULT_FV_SHUTOFF_THRESHOLD): selector.NumberSelector(selector.NumberSelectorConfig(min=-5000, max=5000, step=50, unit_of_measurement="W", mode="box")),
        _f(vol.Optional, CONF_FV_SHUTOFF_EXTRA_HOURS, defaults, DEFAULT_FV_SHUTOFF_EXTRA_HOURS): selector.NumberSelector(selector.NumberSelectorConfig(min=0, max=4, step=0.5, unit_of_measurement="h", mode="box")),
        _f(vol.Optional, CONF_FV_SENSOR_OFFLINE_SHUTOFF_ENABLED, defaults, DEFAULT_FV_SENSOR_OFFLINE_SHUTOFF_ENABLED): selector.BooleanSelector(),
        _f(vol.Optional, CONF_FV_SENSOR_OFFLINE_SHUTOFF_MIN, defaults, DEFAULT_FV_SENSOR_OFFLINE_SHUTOFF_MIN): selector.NumberSelector(selector.NumberSelectorConfig(min=15, max=180, step=5, unit_of_measurement="min", mode="box")),
        _f(vol.Optional, CONF_FV_SENSOR_OFFLINE_NOTIFY_TTS, defaults, DEFAULT_FV_SENSOR_OFFLINE_NOTIFY_TTS): selector.BooleanSelector(),
        _f(vol.Optional, CONF_FV_SENSOR_OFFLINE_NOTIFY_TELEGRAM, defaults, DEFAULT_FV_SENSOR_OFFLINE_NOTIFY_TELEGRAM): selector.BooleanSelector(),
    })


def _schema_profilo(defaults: dict) -> vol.Schema:
    return vol.Schema({
        _f(vol.Required, CONF_PROFILE, defaults, DEFAULT_PROFILE): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[PRESET_BILANCIATO, PRESET_AGGRESSIVO, PRESET_DELICATO, PRESET_PERSONALIZZATO],
                mode=selector.SelectSelectorMode.LIST,
                translation_key="profile",
            )
        ),
    })


def _schema_soglie_termiche(defaults: dict) -> vol.Schema:
    return vol.Schema({
        _f(vol.Optional, CONF_TARGET_TEMP_DEFAULT, defaults, DEFAULT_TARGET_TEMP): selector.NumberSelector(selector.NumberSelectorConfig(min=16, max=30, step=0.5, unit_of_measurement="°C", mode="box")),
        _f(vol.Optional, CONF_EXTREME_OFFSET, defaults, DEFAULT_EXTREME_OFFSET): selector.NumberSelector(selector.NumberSelectorConfig(min=0, max=8, step=0.1, unit_of_measurement="°C", mode="box")),
        _f(vol.Optional, CONF_HOT_OFFSET, defaults, DEFAULT_HOT_OFFSET): selector.NumberSelector(selector.NumberSelectorConfig(min=0, max=5, step=0.1, unit_of_measurement="°C", mode="box")),
        _f(vol.Optional, CONF_RANGE_OFFSET, defaults, DEFAULT_RANGE_OFFSET): selector.NumberSelector(selector.NumberSelectorConfig(min=0, max=5, step=0.1, unit_of_measurement="°C", mode="box")),
        _f(vol.Optional, CONF_BELOW_OFFSET, defaults, DEFAULT_BELOW_OFFSET): selector.NumberSelector(selector.NumberSelectorConfig(min=0, max=3, step=0.05, unit_of_measurement="°C", mode="box")),
        _f(vol.Optional, CONF_TURN_ON_OFFSET, defaults, DEFAULT_TURN_ON_OFFSET): selector.NumberSelector(selector.NumberSelectorConfig(min=0, max=5, step=0.1, unit_of_measurement="°C", mode="box")),
        _f(vol.Optional, CONF_TEMP_DELTA, defaults, DEFAULT_TEMP_DELTA): selector.NumberSelector(selector.NumberSelectorConfig(min=0.5, max=5, step=0.5, unit_of_measurement="°C", mode="box")),
        _f(vol.Optional, CONF_EXTREME_DELTA, defaults, DEFAULT_EXTREME_DELTA): selector.NumberSelector(selector.NumberSelectorConfig(min=0.5, max=8, step=0.5, unit_of_measurement="°C", mode="box")),
        _f(vol.Optional, CONF_MANUAL_SHUTOFF_TIMER_ENABLED, defaults, DEFAULT_MANUAL_SHUTOFF_TIMER_ENABLED): selector.BooleanSelector(),
        _f(vol.Optional, CONF_MANUAL_SHUTOFF_TIMER_MIN, defaults, DEFAULT_MANUAL_SHUTOFF_TIMER_MIN): selector.NumberSelector(selector.NumberSelectorConfig(min=0, max=480, step=5, unit_of_measurement="min", mode="box")),
    })


def _schema_modalita_notturna(defaults: dict) -> vol.Schema:
    return vol.Schema({
        _f(vol.Optional, CONF_CALIBRATION_MAX_OFFSET, defaults, DEFAULT_CALIBRATION_MAX_OFFSET): selector.NumberSelector(selector.NumberSelectorConfig(min=0, max=8, step=0.5, unit_of_measurement="°C", mode="box")),
        _f(vol.Optional, CONF_MIN_BELOW_INTERNAL, defaults, DEFAULT_MIN_BELOW_INTERNAL): selector.NumberSelector(selector.NumberSelectorConfig(min=0, max=5, step=0.5, unit_of_measurement="°C", mode="box")),
        _f(vol.Optional, CONF_NIGHT_START_TIME, defaults, DEFAULT_NIGHT_START_TIME): selector.TimeSelector(),
        _f(vol.Optional, CONF_NIGHT_END_TIME, defaults, DEFAULT_NIGHT_END_TIME): selector.TimeSelector(),
        _f(vol.Optional, CONF_NIGHT_OFFSET, defaults, DEFAULT_NIGHT_OFFSET): selector.NumberSelector(selector.NumberSelectorConfig(min=0, max=5, step=0.5, unit_of_measurement="°C", mode="box")),
        _f(vol.Optional, CONF_NIGHT_AC_ENABLED, defaults, DEFAULT_NIGHT_AC_ENABLED): selector.BooleanSelector(),
        _f(vol.Optional, CONF_NIGHT_TURN_ON_OFFSET, defaults, DEFAULT_NIGHT_TURN_ON_OFFSET): selector.NumberSelector(selector.NumberSelectorConfig(min=0, max=6, step=0.5, unit_of_measurement="°C", mode="box")),
        _f(vol.Optional, CONF_NIGHT_SHUTOFF_ENABLED, defaults, DEFAULT_NIGHT_SHUTOFF_ENABLED): selector.BooleanSelector(),
        _f(vol.Optional, CONF_NIGHT_SHUTOFF_DELTA, defaults, DEFAULT_NIGHT_SHUTOFF_DELTA): selector.NumberSelector(selector.NumberSelectorConfig(min=0, max=3, step=0.1, unit_of_measurement="°C", mode="box")),
        _f(vol.Optional, CONF_NIGHT_SHUTOFF_MIN, defaults, DEFAULT_NIGHT_SHUTOFF_MIN): selector.NumberSelector(selector.NumberSelectorConfig(min=5, max=120, step=5, unit_of_measurement="min", mode="box")),
        _f(vol.Optional, CONF_NIGHT_END_SHUTOFF_ENABLED, defaults, DEFAULT_NIGHT_END_SHUTOFF_ENABLED): selector.BooleanSelector(),
        _f(vol.Optional, CONF_NIGHT_END_SHUTOFF_AUTO_ONLY, defaults, DEFAULT_NIGHT_END_SHUTOFF_AUTO_ONLY): selector.BooleanSelector(),
        _f(vol.Optional, CONF_PRESENCE_BOOST_ENABLED, defaults, DEFAULT_PRESENCE_BOOST_ENABLED): selector.BooleanSelector(),
        _f(vol.Optional, CONF_PRESENCE_BOOST_MIN, defaults, DEFAULT_PRESENCE_BOOST_MIN): selector.NumberSelector(selector.NumberSelectorConfig(min=1, max=60, step=1, unit_of_measurement="min", mode="box")),
        _f(vol.Optional, CONF_PRESENCE_BOOST_OFFSET, defaults, DEFAULT_PRESENCE_BOOST_OFFSET): selector.NumberSelector(selector.NumberSelectorConfig(min=0, max=5, step=0.1, unit_of_measurement="°C", mode="box")),
        _f(vol.Optional, CONF_WINDOW_DELAY_MIN, defaults, DEFAULT_WINDOW_DELAY_MIN): selector.NumberSelector(selector.NumberSelectorConfig(min=1, max=60, step=1, unit_of_measurement="min", mode="box")),
        _f(vol.Optional, CONF_UPDATE_INTERVAL_MIN, defaults, DEFAULT_UPDATE_INTERVAL_MIN): selector.NumberSelector(selector.NumberSelectorConfig(min=1, max=30, step=1, unit_of_measurement="min", mode="box")),
    })


def _schema_notifiche(defaults: dict) -> vol.Schema:
    return vol.Schema({
        _f(vol.Optional, CONF_TTS_PLAYERS, defaults): selector.EntitySelector(selector.EntitySelectorConfig(domain="media_player", multiple=True)),
        _f(vol.Optional, CONF_TTS_ENGINE, defaults): selector.EntitySelector(selector.EntitySelectorConfig(domain="tts")),
        _f(vol.Optional, CONF_TTS_MESSAGE_OPEN, defaults, DEFAULT_TTS_MESSAGE_OPEN): selector.TextSelector(selector.TextSelectorConfig(multiline=True)),
        _f(vol.Optional, CONF_NOTIFY_TARGETS, defaults): selector.EntitySelector(selector.EntitySelectorConfig(domain="notify", multiple=True)),
        _f(vol.Optional, CONF_NOTIFY_CHAT_IDS, defaults): selector.TextSelector(),
        _f(vol.Optional, CONF_NOTIFY_TEMP_CHANGE_ENABLED, defaults, DEFAULT_NOTIFY_TEMP_CHANGE_ENABLED): selector.BooleanSelector(),
        _f(vol.Optional, CONF_NOTIFY_TEMP_CHANGE_LIMIT_ENABLED, defaults, DEFAULT_NOTIFY_TEMP_CHANGE_LIMIT_ENABLED): selector.BooleanSelector(),
        _f(vol.Optional, CONF_NOTIFY_TEMP_CHANGE_LIMIT_MIN, defaults, DEFAULT_NOTIFY_TEMP_CHANGE_LIMIT_MIN): selector.NumberSelector(selector.NumberSelectorConfig(min=1, max=120, step=1, unit_of_measurement="min", mode="box")),
        _f(vol.Optional, CONF_NOTIFY_TEMP_CHANGE_MESSAGE, defaults, DEFAULT_NOTIFY_TEMP_CHANGE_MESSAGE): selector.TextSelector(selector.TextSelectorConfig(multiline=True)),
        _f(vol.Optional, CONF_NOTIFY_POWER_TTS, defaults, DEFAULT_NOTIFY_POWER_TTS): selector.BooleanSelector(),
        _f(vol.Optional, CONF_NOTIFY_POWER_NOTIFY, defaults, DEFAULT_NOTIFY_POWER_NOTIFY): selector.BooleanSelector(),
        _f(vol.Optional, CONF_NOTIFY_NIGHT_END_TTS, defaults, DEFAULT_NOTIFY_NIGHT_END_TTS): selector.BooleanSelector(),
        _f(vol.Optional, CONF_NOTIFY_NIGHT_END_NOTIFY, defaults, DEFAULT_NOTIFY_NIGHT_END_NOTIFY): selector.BooleanSelector(),
        _f(vol.Optional, CONF_DOOR_ALERT_ENABLED, defaults, DEFAULT_DOOR_ALERT_ENABLED): selector.BooleanSelector(),
        _f(vol.Optional, CONF_DOOR_ALERT_TTS, defaults, DEFAULT_DOOR_ALERT_TTS): selector.BooleanSelector(),
        _f(vol.Optional, CONF_DOOR_ALERT_NOTIFY, defaults, DEFAULT_DOOR_ALERT_NOTIFY): selector.BooleanSelector(),
        _f(vol.Optional, CONF_DOOR_ALERT_MESSAGE, defaults, DEFAULT_DOOR_ALERT_MESSAGE): selector.TextSelector(selector.TextSelectorConfig(multiline=True)),
        _f(vol.Optional, CONF_QUIET_ENABLED, defaults, DEFAULT_QUIET_ENABLED): selector.BooleanSelector(),
        _f(vol.Optional, CONF_QUIET_START_TIME, defaults, DEFAULT_QUIET_START_TIME): selector.TimeSelector(),
        _f(vol.Optional, CONF_QUIET_END_TIME, defaults, DEFAULT_QUIET_END_TIME): selector.TimeSelector(),
        _f(vol.Optional, CONF_QUIET_TTS, defaults, DEFAULT_QUIET_TTS): selector.BooleanSelector(),
        _f(vol.Optional, CONF_QUIET_NOTIFY, defaults, DEFAULT_QUIET_NOTIFY): selector.BooleanSelector(),
    })




def _calc_sunset_info(hass, anticipate_h: float = 2.0) -> tuple[str, str]:
    """Calcola orario tramonto e orario limite controllo manuale."""
    sun_state = hass.states.get("sun.sun") if hass else None
    if sun_state is None:
        return "non disponibile", "non disponibile"
    next_setting = sun_state.attributes.get("next_setting")
    if not next_setting:
        return "non disponibile", "non disponibile"
    try:
        from homeassistant.util import dt as dt_util
        sunset_dt = dt_util.as_local(dt_util.parse_datetime(str(next_setting)))
        sunset_str = sunset_dt.strftime("%H:%M")
        cutoff_dt = sunset_dt - timedelta(hours=anticipate_h)
        cutoff_str = cutoff_dt.strftime("%H:%M")
        return sunset_str, cutoff_str
    except Exception:
        return "non disponibile", "non disponibile"

class TermostatoIntelligenteConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    async def async_step_user(self, user_input=None):
        """Primo step: scelta della modalità di configurazione."""
        errors: dict[str, str] = {}
        if user_input is not None:
            self._data.update(user_input)
            mode = user_input[CONF_CONFIG_MODE]
            if mode == CONFIG_MODE_FULL:
                return await self.async_step_entita_completo()
            return await self.async_step_simple_entita()
        return self.async_show_form(step_id="user", data_schema=_schema_modalita(self._data), errors=errors)

    # --- Step modo completo ---

    async def async_step_entita_completo(self, user_input=None):
        errors: dict[str, str] = {}
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_CLIMATE_ENTITY])
            self._abort_if_unique_id_configured()
            self._data.update(user_input)
            return await self.async_step_energia()
        return self.async_show_form(step_id="entita_completo", data_schema=_schema_user(self._data), errors=errors)

    async def async_step_energia(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_profilo()
        return self.async_show_form(step_id="energia", data_schema=_schema_energia(self._data))

    async def async_step_profilo(self, user_input=None):
        if user_input is not None:
            profile = user_input[CONF_PROFILE]
            self._data[CONF_PROFILE] = profile
            if profile in PRESET_VALUES:
                self._data.update(PRESET_VALUES[profile])
                return await self.async_step_notifiche()
            return await self.async_step_soglie_termiche()
        return self.async_show_form(step_id="profilo", data_schema=_schema_profilo(self._data))

    async def async_step_soglie_termiche(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_modalita_notturna()
        return self.async_show_form(step_id="soglie_termiche", data_schema=_schema_soglie_termiche(self._data))

    async def async_step_modalita_notturna(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_notifiche()
        return self.async_show_form(step_id="modalita_notturna", data_schema=_schema_modalita_notturna(self._data))

    async def async_step_notifiche(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_protezione_potenza_completo()
        return self.async_show_form(step_id="notifiche", data_schema=_schema_notifiche(self._data))

    async def async_step_protezione_potenza_completo(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_emergenza_completo()
        return self.async_show_form(step_id="protezione_potenza_completo", data_schema=_schema_protezione_potenza_completo(self._data))

    async def async_step_emergenza_completo(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(title=self._data.get(CONF_NAME, DEFAULT_NAME), data=self._data)
        return self.async_show_form(step_id="emergenza_completo", data_schema=_schema_emergenza_completo(self._data))

    # --- Step modo semplificato e semplificato FV ---

    async def async_step_simple_entita(self, user_input=None):
        errors: dict[str, str] = {}
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_CLIMATE_ENTITY])
            self._abort_if_unique_id_configured()
            self._data.update(user_input)
            return await self.async_step_simple_temperature()
        return self.async_show_form(step_id="simple_entita", data_schema=_schema_simple_entita(self._data), errors=errors)

    async def async_step_simple_temperature(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            if self._data.get(CONF_SEASON_MODE) in (SEASON_WINTER, SEASON_AUTO):
                return await self.async_step_inverno()
            return await self._async_after_temperature_step()
        return self.async_show_form(step_id="simple_temperature", data_schema=_schema_simple_temperature(self._data))

    async def async_step_inverno(self, user_input=None):
        """❄️ Schermata dedicata all'inverno — mostrata solo se la stagione
        selezionata è Inverno o Auto."""
        if user_input is not None:
            self._data.update(user_input)
            return await self._async_after_temperature_step()
        return self.async_show_form(step_id="inverno", data_schema=_schema_inverno(self._data))

    async def _async_after_temperature_step(self):
        mode = self._data.get(CONF_CONFIG_MODE, CONFIG_MODE_SIMPLE)
        if mode == CONFIG_MODE_SIMPLE_FV:
            return await self.async_step_energia_simple()
        return await self.async_step_simple_notifiche()

    async def async_step_energia_simple(self, user_input=None):
        """Step FV per il modo semplificato con fotovoltaico."""
        if user_input is not None:
            # Ignora i campi readonly sunset_info e cutoff_info
            user_input.pop("sunset_info", None)
            user_input.pop("cutoff_info", None)
            self._data.update(user_input)
            return await self.async_step_simple_notifiche()
        anticipate_h = float(self._data.get(CONF_SIMPLE_SUNSET_ANTICIPATE_H, DEFAULT_SIMPLE_SUNSET_ANTICIPATE_H))
        sunset_str, cutoff_str = _calc_sunset_info(self.hass, anticipate_h)
        return self.async_show_form(
            step_id="energia_simple",
            data_schema=_schema_energia_simple(self._data, sunset_str, cutoff_str),
        )

    async def async_step_simple_notifiche(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_protezione_potenza()
        return self.async_show_form(step_id="simple_notifiche", data_schema=_schema_simple_notifiche(self._data, has_fv=(self._data.get(CONF_CONFIG_MODE) == CONFIG_MODE_SIMPLE_FV)))

    async def async_step_protezione_potenza(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_emergenza_simple()
        return self.async_show_form(step_id="protezione_potenza", data_schema=_schema_protezione_potenza(self._data))

    async def async_step_emergenza_simple(self, user_input=None):
        if user_input is not None:
            # Gestisci attivazione/disattivazione switch emergenza
            emergency_active = user_input.pop("emergency_heat_active", False)
            self._data.update(user_input)
            # Attiva/disattiva lo switch tramite HA
            entry_id = getattr(self, "config_entry", None) and self.config_entry.entry_id
            if entry_id:
                entry_data = self.hass.data.get(DOMAIN, {}).get(entry_id, {})
                switch = entry_data.get(SWITCH_KEY_EMERGENCY)
                if switch is not None:
                    if emergency_active:
                        await switch.async_turn_on()
                    else:
                        await switch.async_turn_off()
            return self.async_create_entry(title=self._data.get(CONF_NAME, DEFAULT_NAME), data=self._data)
        mode = self._data.get(CONF_CONFIG_MODE, CONFIG_MODE_FULL)
        if mode != CONFIG_MODE_SIMPLE_FV:
            return self.async_create_entry(title=self._data.get(CONF_NAME, DEFAULT_NAME), data=self._data)
        # Leggi stato attuale dello switch per pre-popolare il campo
        defaults = dict(self._data)
        return self.async_show_form(step_id="emergenza_simple", data_schema=_schema_emergenza_simple(defaults))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return TermostatoIntelligenteOptionsFlow(config_entry)


class TermostatoIntelligenteOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry) -> None:
        merged = dict(config_entry.data)
        merged.update(config_entry.options)
        if CONF_PROFILE not in merged:
            merged[CONF_PROFILE] = PRESET_PERSONALIZZATO
        self._data: dict[str, Any] = merged

    async def async_step_init(self, user_input=None):
        """Primo step options: permette di cambiare la modalità di configurazione."""
        return await self.async_step_cambia_modalita()

    async def async_step_cambia_modalita(self, user_input=None):
        """Step per scegliere/cambiare la modalità — mostrato sempre come primo step delle opzioni."""
        if user_input is not None:
            new_mode = user_input[CONF_CONFIG_MODE]
            self._data[CONF_CONFIG_MODE] = new_mode
            if new_mode == CONFIG_MODE_FULL:
                return await self.async_step_sensori()
            return await self.async_step_simple_entita()
        return self.async_show_form(
            step_id="cambia_modalita",
            data_schema=_schema_modalita(self._data),
        )

    # --- Options modo completo ---

    async def async_step_sensori(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_energia()
        return self.async_show_form(step_id="sensori", data_schema=_schema_sensori(self._data))

    async def async_step_energia(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_profilo()
        return self.async_show_form(step_id="energia", data_schema=_schema_energia(self._data))

    async def async_step_profilo(self, user_input=None):
        if user_input is not None:
            profile = user_input[CONF_PROFILE]
            self._data[CONF_PROFILE] = profile
            if profile in PRESET_VALUES:
                self._data.update(PRESET_VALUES[profile])
                return await self.async_step_notifiche()
            return await self.async_step_soglie_termiche()
        return self.async_show_form(step_id="profilo", data_schema=_schema_profilo(self._data))

    async def async_step_soglie_termiche(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_modalita_notturna()
        return self.async_show_form(step_id="soglie_termiche", data_schema=_schema_soglie_termiche(self._data))

    async def async_step_modalita_notturna(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_notifiche()
        return self.async_show_form(step_id="modalita_notturna", data_schema=_schema_modalita_notturna(self._data))

    async def async_step_notifiche(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_protezione_potenza_completo()
        return self.async_show_form(step_id="notifiche", data_schema=_schema_notifiche(self._data))

    async def async_step_protezione_potenza_completo(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_emergenza_completo()
        return self.async_show_form(step_id="protezione_potenza_completo", data_schema=_schema_protezione_potenza_completo(self._data))

    async def async_step_emergenza_completo(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(data=self._data)
        return self.async_show_form(step_id="emergenza_completo", data_schema=_schema_emergenza_completo(self._data))

    # --- Options modo semplificato ---

    async def async_step_simple_entita(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_simple_temperature()
        return self.async_show_form(step_id="simple_entita", data_schema=_schema_simple_entita(self._data))

    async def async_step_simple_temperature(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            if self._data.get(CONF_SEASON_MODE) in (SEASON_WINTER, SEASON_AUTO):
                return await self.async_step_inverno()
            return await self._async_after_temperature_step()
        return self.async_show_form(step_id="simple_temperature", data_schema=_schema_simple_temperature(self._data))

    async def async_step_inverno(self, user_input=None):
        """❄️ Schermata dedicata all'inverno — mostrata solo se la stagione
        selezionata è Inverno o Auto."""
        if user_input is not None:
            self._data.update(user_input)
            return await self._async_after_temperature_step()
        return self.async_show_form(step_id="inverno", data_schema=_schema_inverno(self._data))

    async def _async_after_temperature_step(self):
        mode = self._data.get(CONF_CONFIG_MODE, CONFIG_MODE_SIMPLE)
        if mode == CONFIG_MODE_SIMPLE_FV:
            return await self.async_step_energia_simple()
        return await self.async_step_simple_notifiche()

    async def async_step_energia_simple(self, user_input=None):
        if user_input is not None:
            user_input.pop("sunset_info", None)
            user_input.pop("cutoff_info", None)
            self._data.update(user_input)
            return await self.async_step_simple_notifiche()
        anticipate_h = float(self._data.get(CONF_SIMPLE_SUNSET_ANTICIPATE_H, DEFAULT_SIMPLE_SUNSET_ANTICIPATE_H))
        sunset_str, cutoff_str = _calc_sunset_info(self.hass, anticipate_h)
        return self.async_show_form(
            step_id="energia_simple",
            data_schema=_schema_energia_simple(self._data, sunset_str, cutoff_str),
        )

    async def async_step_simple_notifiche(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_protezione_potenza()
        return self.async_show_form(step_id="simple_notifiche", data_schema=_schema_simple_notifiche(self._data, has_fv=(self._data.get(CONF_CONFIG_MODE) == CONFIG_MODE_SIMPLE_FV)))

    async def async_step_protezione_potenza(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_emergenza_simple()
        return self.async_show_form(step_id="protezione_potenza", data_schema=_schema_protezione_potenza(self._data))

    async def async_step_emergenza_simple(self, user_input=None):
        if user_input is not None:
            emergency_active = user_input.pop("emergency_heat_active", False)
            self._data.update(user_input)
            entry_data = self.hass.data.get(DOMAIN, {}).get(self.config_entry.entry_id, {})
            switch = entry_data.get(SWITCH_KEY_EMERGENCY)
            if switch is not None:
                if emergency_active:
                    await switch.async_turn_on()
                else:
                    await switch.async_turn_off()
            return self.async_create_entry(data=self._data)
        mode = self._data.get(CONF_CONFIG_MODE, CONFIG_MODE_FULL)
        if mode != CONFIG_MODE_SIMPLE_FV:
            return self.async_create_entry(data=self._data)
        # Leggi stato attuale switch per pre-popolare
        entry_data = self.hass.data.get(DOMAIN, {}).get(self.config_entry.entry_id, {})
        switch = entry_data.get(SWITCH_KEY_EMERGENCY)
        defaults = dict(self._data)
        if switch is not None:
            defaults["emergency_heat_active"] = switch.is_on
        return self.async_show_form(step_id="emergenza_simple", data_schema=_schema_emergenza_simple(defaults))
