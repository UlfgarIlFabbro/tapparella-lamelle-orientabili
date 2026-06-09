"""Tapparella Cherubini con lamelle orientabili - controllo diretto Shelly Gen2."""
import logging
import aiohttp
from aiohttp import web

from homeassistant.components.cover import CoverEntity, CoverEntityFeature
from homeassistant.components.http import HomeAssistantView
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

STATE_OPEN = "open"
STATE_CLOSED = "closed"
STATE_TILT = "tilt"

HA_URL = "http://192.168.1.2:8123"


def _ip_slug(ip: str) -> str:
    return ip.replace(".", "_")


class TapparellaView(HomeAssistantView):
    """View HTTP per ricevere aggiornamenti stato dalla pressione pulsanti Shelly."""

    requires_auth = False

    def __init__(self, cover_entity):
        self._cover = cover_entity
        ip_slug = _ip_slug(cover_entity._ip)
        self.url = f"/api/tapparella/{ip_slug}/{{action}}"
        self.name = f"tapparella_{ip_slug}"

    async def get(self, request, action):
        cover = self._cover
        if action == "su":
            cover._state = STATE_OPEN
        elif action == "giu":
            cover._state = STATE_CLOSED
        elif action == "lamelle":
            cover._state = STATE_TILT
        else:
            return web.Response(status=404, text="Unknown action")

        cover._save_state()
        cover.async_write_ha_state()
        _LOGGER.debug("Stato tapparella aggiornato via HTTP: %s", action)
        return web.Response(status=200, text="OK")


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
        self._attr_unique_id = f"tlo_{_ip_slug(self._ip)}"

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_closed(self) -> bool:
        return self._state in (STATE_CLOSED, STATE_TILT)

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
    hass.http.register_view(TapparellaView(entity))
    async_add_entities([entity], update_before_add=False)
