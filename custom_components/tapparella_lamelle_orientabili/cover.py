"""Tapparella Cherubini con lamelle orientabili - controllo diretto Shelly Gen2."""
import logging
import aiohttp

from homeassistant.components.cover import CoverEntity, CoverEntityFeature
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, ENTITY_STORE, STATE_OPEN, STATE_CLOSED, STATE_TILT, ip_slug

_LOGGER = logging.getLogger(__name__)


class CherubiniCover(CoverEntity):
    """Tapparella Cherubini con lamelle orientabili via Shelly Plus 2PM."""

    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.OPEN_TILT
    )

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.hass = hass
        self._entry = entry
        self._name = entry.data["name"]
        self._ip = entry.data["ip"]
        self._state = entry.data.get("state", STATE_OPEN)
        self._attr_unique_id = f"tlo_{ip_slug(self._ip)}"

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_closed(self) -> bool | None:
        if self._state == STATE_TILT:
            return None
        return self._state == STATE_CLOSED

    @property
    def current_cover_tilt_position(self) -> int:
        return 100 if self._state == STATE_TILT else 0

    def _save_state(self):
        new_data = {**self._entry.data, "state": self._state}
        self.hass.config_entries.async_update_entry(self._entry, data=new_data)

    async def _shelly_call(self, path: str) -> bool:
        url = f"http://{self._ip}/{path}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        return True
                    _LOGGER.warning("Shelly risponde %s per %s", resp.status, url)
        except Exception as err:
            _LOGGER.error("Errore chiamata Shelly %s: %s", url, err)
        return False

    async def async_open_cover(self, **kwargs):
        """Su."""
        if await self._shelly_call("roller/0?go=open"):
            self._state = STATE_OPEN
            self._save_state()
            self.async_write_ha_state()

    async def async_close_cover(self, **kwargs):
        """Giù — pressione breve (duration=1s)."""
        if await self._shelly_call("roller/0?go=close&duration=1"):
            self._state = STATE_CLOSED
            self._save_state()
            self.async_write_ha_state()

    async def async_open_cover_tilt(self, **kwargs):
        """Lamelle — va al finecorsa 2.5s."""
        if await self._shelly_call("roller/0?go=close"):
            self._state = STATE_TILT
            self._save_state()
            self.async_write_ha_state()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    entity = CherubiniCover(hass=hass, entry=entry)
    ENTITY_STORE[ip_slug(entry.data["ip"])] = entity
    async_add_entities([entity], update_before_add=False)
