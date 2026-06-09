"""Tapparella Cherubini con lamelle orientabili - controllo diretto Shelly Gen2."""
import logging
import aiohttp

from homeassistant.components.cover import CoverEntity, CoverEntityFeature
from homeassistant.components.webhook import async_register, async_unregister
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, Request

_LOGGER = logging.getLogger(__name__)

STATE_OPEN = "open"
STATE_CLOSED = "closed"
STATE_TILT = "tilt"

HA_URL = "http://192.168.1.2:8123"


def webhook_id_su(ip: str) -> str:
    return f"tapparella_{ip.replace('.', '_')}_su"

def webhook_id_giu(ip: str) -> str:
    return f"tapparella_{ip.replace('.', '_')}_giu"

def webhook_id_lamelle(ip: str) -> str:
    return f"tapparella_{ip.replace('.', '_')}_lamelle"


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
        return 100 if self._state == STATE_TILT else 0

    async def async_added_to_hass(self):
        """Registra i webhook quando l'entità viene aggiunta a HA."""
        ip = self._ip

        async def handle_su(hass, webhook_id, request: Request):
            self._state = STATE_OPEN
            self.async_write_ha_state()

        async def handle_giu(hass, webhook_id, request: Request):
            self._state = STATE_CLOSED
            self.async_write_ha_state()

        async def handle_lamelle(hass, webhook_id, request: Request):
            self._state = STATE_TILT
            self.async_write_ha_state()

        async_register(
            self.hass, "tapparella_lamelle_orientabili",
            webhook_id_su(ip), handle_su
        )
        async_register(
            self.hass, "tapparella_lamelle_orientabili",
            webhook_id_giu(ip), handle_giu
        )
        async_register(
            self.hass, "tapparella_lamelle_orientabili",
            webhook_id_lamelle(ip), handle_lamelle
        )

    async def async_will_remove_from_hass(self):
        """Deregistra i webhook alla rimozione."""
        async_unregister(self.hass, webhook_id_su(self._ip))
        async_unregister(self.hass, webhook_id_giu(self._ip))
        async_unregister(self.hass, webhook_id_lamelle(self._ip))

    async def _shelly_call(self, path: str) -> bool:
        """Chiama l'API REST dello Shelly."""
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
            self.async_write_ha_state()

    async def async_close_cover(self, **kwargs):
        """Giù — pressione breve (duration=1s)."""
        if await self._shelly_call("roller/0?go=close&duration=1"):
            self._state = STATE_CLOSED
            self.async_write_ha_state()

    async def async_open_cover_tilt(self, **kwargs):
        """Lamelle — va al finecorsa 2.5s."""
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
