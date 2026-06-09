"""Tapparella Cherubini con lamelle orientabili - controllo diretto Shelly Gen2."""
import logging
import aiohttp

from homeassistant.components.cover import CoverEntity, CoverEntityFeature
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

# Stati possibili
STATE_OPEN = "open"          # tapparella su
STATE_CLOSED = "closed"      # tapparella giù (chiusa)
STATE_TILT = "tilt"          # tapparella giù con lamelle aperte


class CherubiniCover(CoverEntity):
    """Tapparella Cherubini con lamelle orientabili via Shelly Plus 2PM."""

    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.OPEN_TILT
    )

    def __init__(self, hass: HomeAssistant, name: str, ip: str):
        self.hass = hass
        self._name = name
        self._ip = ip
        self._state = STATE_OPEN
        self._attr_unique_id = f"cherubini_{ip.replace('.', '_')}"

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_closed(self) -> bool:
        return self._state in (STATE_CLOSED, STATE_TILT)

    @property
    def current_cover_tilt_position(self) -> int:
        """100 = lamelle aperte, 0 = lamelle chiuse."""
        return 100 if self._state == STATE_TILT else 0

    async def _shelly_call(self, path: str) -> bool:
        """Chiama l'API REST dello Shelly Gen1-style (roller endpoint)."""
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
        """Su — pressione breve salita (finecorsa 0.25s)."""
        if await self._shelly_call("roller/0?go=open"):
            self._state = STATE_OPEN
            self.async_write_ha_state()

    async def async_close_cover(self, **kwargs):
        """Giù — pressione breve discesa (duration=1s, finecorsa 2.5s)."""
        if await self._shelly_call("roller/0?go=close&duration=1"):
            self._state = STATE_CLOSED
            self.async_write_ha_state()

    async def async_open_cover_tilt(self, **kwargs):
        """Lamelle — pressione lunga discesa (va al finecorsa 2.5s)."""
        if await self._shelly_call("roller/0?go=close"):
            self._state = STATE_TILT
            self.async_write_ha_state()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    entity = CherubiniCover(
        hass=hass,
        name=entry.data["name"],
        ip=entry.data["ip"],
    )
    async_add_entities([entity], update_before_add=False)
