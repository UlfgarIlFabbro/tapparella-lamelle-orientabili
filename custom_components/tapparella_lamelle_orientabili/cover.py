"""Tapparella Cherubini con lamelle orientabili - controllo diretto Shelly Gen2."""
import logging
import aiohttp
from datetime import timedelta

from homeassistant.components.cover import CoverEntity, CoverEntityFeature
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, ENTITY_STORE, STATE_OPEN, STATE_CLOSED, STATE_TILT, ip_slug

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)


class CherubiniCover(CoverEntity):
    """Tapparella Cherubini con lamelle orientabili via Shelly Plus 2PM."""

    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.OPEN_TILT
    )

    should_poll = True

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.hass = hass
        self._entry = entry
        self._name = entry.data["name"]
        self._ip = entry.data["ip"]
        self._state = entry.data.get("state", STATE_CLOSED)
        self._attr_unique_id = f"tlo_{ip_slug(self._ip)}"
        self._attr_name = self._name
        self._attr_extra_state_attributes = {
            "tlo": True,
            "tlo_slug": ip_slug(self._ip),
        }
        self._available = True

    @property
    def available(self) -> bool:
        return self._available

    @property
    def is_closed(self) -> bool:
        return self._state == STATE_CLOSED

    @property
    def assumed_state(self) -> bool:
        return self._state == STATE_TILT

    @property
    def current_cover_position(self) -> int:
        if self._state == STATE_OPEN:
            return 100
        return 0

    @property
    def current_cover_tilt_position(self) -> int:
        return 100 if self._state == STATE_TILT else 0

    async def async_update(self) -> None:
        """Polling ogni 30 secondi per verificare se lo Shelly è raggiungibile."""
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(
                    f"http://{self._ip}/rpc/Shelly.GetStatus"
                ) as resp:
                    if resp.status == 200:
                        if not self._available:
                            _LOGGER.info("TLO: Shelly %s tornato online", self._ip)
                        self._available = True
                    else:
                        self._available = False
        except aiohttp.ClientConnectorError:
            if self._available:
                _LOGGER.warning("TLO: Shelly %s non raggiungibile", self._ip)
            self._available = False
        except Exception as err:
            if self._available:
                _LOGGER.warning("TLO: Shelly %s errore: %s", self._ip, err)
            self._available = False

    def _save_state(self):
        new_data = {**self._entry.data, "state": self._state}
        self.hass.config_entries.async_update_entry(self._entry, data=new_data)

    def handle_webhook(self, action: str) -> None:
        if action == "su":
            self._state = STATE_OPEN
        elif action == "giu":
            self._state = STATE_CLOSED
        elif action == "lamelle":
            self._toggle_lamelle_state()
        self._save_state()
        self.async_write_ha_state()

    async def async_open_cover(self, **kwargs):
        if await self._shelly_call("roller/0?go=open"):
            self._state = STATE_OPEN
            self._save_state()
            self.async_write_ha_state()
        else:
            self.async_write_ha_state()

    async def async_close_cover(self, **kwargs):
        if await self._shelly_call("roller/0?go=close&duration=1"):
            self._state = STATE_CLOSED
            self._save_state()
            self.async_write_ha_state()
        else:
            self.async_write_ha_state()

    def _toggle_lamelle_state(self):
        """Aggiorna lo stato dopo il comando fisico lamelle.

        Il motore Cherubini usa lo stesso comando per alternare la posizione
        delle lamelle: OPEN -> TILT e TILT -> CLOSED. Da CLOSED, il comando
        riporta invece alla posizione TILT (lamelle aperte).
        """
        if self._state == STATE_TILT:
            self._state = STATE_CLOSED
        else:
            self._state = STATE_TILT

    async def async_open_cover_tilt(self, **kwargs):
        """Porta la tapparella in modo assoluto a TILT.

        Questo comando NON è un toggle: se le lamelle sono già aperte
        (TILT) non invia alcun comando al motore. È quindi sicuro anche
        quando viene usato su un gruppo di più tapparelle.
        """
        if self._state == STATE_TILT:
            return

        if await self._shelly_call("roller/0?go=close"):
            self._state = STATE_TILT
            self._save_state()
            self.async_write_ha_state()
        else:
            self.async_write_ha_state()

    async def _shelly_call(self, path: str) -> bool:
        """Esegue un comando sullo Shelly e restituisce True solo se accettato."""
        url = f"http://{self._ip}/{path}"
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        self._available = False
                        _LOGGER.warning("Shelly risponde %s per %s", resp.status, url)
                        return False
                    self._available = True
                    return True
        except Exception as err:
            self._available = False
            _LOGGER.error("Errore chiamata Shelly %s: %s", url, err)
            return False


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    entity = CherubiniCover(hass=hass, entry=entry)
    ENTITY_STORE[ip_slug(entry.data["ip"])] = entity
    async_add_entities([entity], update_before_add=True)
