"""Interruttori ausiliari per il Termostato Intelligente FV."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN, SWITCH_KEY_EMERGENCY, SWITCH_KEY_FV, SWITCH_KEY_MASTER, SWITCH_KEY_QUICK


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Crea i 3 interruttori ausiliari legati a questa istanza del termostato."""
    base_name = entry.data.get("name") or "Termostato Intelligente"

    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=base_name,
        manufacturer="Termostato Intelligente FV",
        model="Termostato Intelligente",
    )

    entities = [
        TermostatoAuxSwitch(
            hass,
            entry,
            key=SWITCH_KEY_EMERGENCY,
            name=f"{base_name} - Emergenza caldo",
            icon="mdi:fire-alert",
            default_on=False,
            device_info=device_info,
        ),
        TermostatoAuxSwitch(
            hass,
            entry,
            key=SWITCH_KEY_MASTER,
            name=f"{base_name} - Abilita Termostato Intelligente",
            icon="mdi:brain",
            default_on=True,
            device_info=device_info,
        ),
        TermostatoAuxSwitch(
            hass,
            entry,
            key=SWITCH_KEY_FV,
            name=f"{base_name} - Accensione automatica da FV",
            icon="mdi:white-balance-sunny",
            default_on=True,
            device_info=device_info,
        ),
        TermostatoAuxSwitch(
            hass,
            entry,
            key=SWITCH_KEY_QUICK,
            name=f"{base_name} - Raffreddamento rapido",
            icon="mdi:snowflake-variant",
            default_on=False,
            device_info=device_info,
        ),
    ]
    async_add_entities(entities)


class TermostatoAuxSwitch(SwitchEntity, RestoreEntity):
    """Interruttore ausiliario persistente, registrato in hass.data per essere letto da climate.py."""

    _attr_should_poll = False

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        key: str,
        name: str,
        icon: str,
        default_on: bool,
        device_info: DeviceInfo,
    ) -> None:
        self.hass = hass
        self.entry = entry
        self._key = key
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_is_on = default_on
        self._attr_device_info = device_info

        # Si registra subito in hass.data così climate.py può leggerne lo stato
        # anche prima che async_added_to_hass sia stato chiamato.
        hass.data.setdefault(DOMAIN, {}).setdefault(entry.entry_id, {})[key] = self

    @property
    def is_on(self) -> bool:
        return self._attr_is_on

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state is not None:
            self._attr_is_on = last_state.state == "on"

    async def async_turn_on(self, **kwargs) -> None:
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_will_remove_from_hass(self) -> None:
        data = self.hass.data.get(DOMAIN, {}).get(self.entry.entry_id, {})
        if data.get(self._key) is self:
            data.pop(self._key, None)
