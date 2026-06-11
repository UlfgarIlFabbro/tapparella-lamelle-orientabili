"""Lock per le lamelle della Tapparella Lamelle Orientabili."""
import logging
from homeassistant.components.lock import LockEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ENTITY_STORE, STATE_OPEN, STATE_CLOSED, STATE_TILT, ip_slug

_LOGGER = logging.getLogger(__name__)


class TapparellaLamelleLock(LockEntity):
    _attr_icon = "mdi:blinds"

    def __init__(self, entry: ConfigEntry, cover_entity):
        self._entry = entry
        self._cover = cover_entity
        self._attr_name = f"{entry.data['name']} Lamelle"
        self._attr_unique_id = f"tlo_{ip_slug(entry.data['ip'])}_lock"

    @property
    def is_locked(self) -> bool | None:
        if self._cover._state == STATE_OPEN:
            return None
        return self._cover._state == STATE_CLOSED

    @property
    def available(self) -> bool:
        return self._cover._state != STATE_OPEN

    async def async_lock(self, **kwargs):
        await self._cover.async_close_cover()
        self.async_write_ha_state()

    async def async_unlock(self, **kwargs):
        await self._cover.async_open_cover_tilt()
        self.async_write_ha_state()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    ip_s = ip_slug(entry.data["ip"])
    cover_entity = ENTITY_STORE.get(ip_s)
    if cover_entity is not None:
        async_add_entities([TapparellaLamelleLock(entry, cover_entity)], update_before_add=False)
    else:
        _LOGGER.warning("TLO lock: cover entity non trovata per %s", ip_s)
