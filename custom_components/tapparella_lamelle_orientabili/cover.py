"""Tapparella Cherubini con lamelle orientabili - controllo diretto Shelly Gen2."""
import logging
import aiohttp
from datetime import timedelta
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.cover import CoverEntity, CoverEntityFeature

from .const import DOMAIN, ENTITY_STORE, STATE_OPEN, STATE_CLOSED, STATE_TILT, ip_slug

_LOGGER = logging.getLogger(__name__)

# HA chiama async_update ogni 30 secondi per verificare disponibilità Shelly
SCAN_INTERVAL = timedelta(seconds=30)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    ip = entry.data["ip"]
    ip_s = ip_slug(ip)
    name = entry.data["name"]
    state = entry.options.get("state", entry.data.get("state", STATE_CLOSED))
    entity = CherubiniCover(entry, ip, ip_s, name, state)
    ENTITY_STORE[ip_s] = entity
    # update_before_add=True fa un async_update subito al caricamento
    async_add_entities([entity], update_before_add=True)


class CherubiniCover(CoverEntity):
    """Cover per tapparella Cherubini con lamelle orientabili."""

    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.OPEN_TILT
    )

    # HA usa should_poll=True (default) insieme a SCAN_INTERVAL per il polling
    should_poll = True

    def __init__(self, entry, ip, ip_s, name, initial_state):
        self._entry = entry
        self._ip = ip
        self._ip_s = ip_s
        self._attr_name = name
        self._attr_unique_id = f"tlo_{ip_s}"
        self._state = initial_state
        self._available = True

    @property
    def available(self) -> bool:
        return self._available

    @property
    def is_closed(self) -> bool:
        return self._state == STATE_CLOSED

    @property
    def assumed_state(self) -> bool:
        # Quando le lamelle sono aperte, salita e discesa restano abilitati
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
        """Polling ogni 30 secondi: verifica se lo Shelly è raggiungibile in locale."""
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
                        _LOGGER.warning("TLO: Shelly %s risposta inattesa: %s", self._ip, resp.status)
                        self._available = False
        except aiohttp.ClientConnectorError:
            if self._available:
                _LOGGER.warning("TLO: Shelly %s non raggiungibile (connessione rifiutata)", self._ip)
            self._available = False
        except aiohttp.ServerTimeoutError:
            if self._available:
                _LOGGER.warning("TLO: Shelly %s timeout", self._ip)
            self._available = False
        except Exception as err:
            if self._available:
                _LOGGER.warning("TLO: Shelly %s errore: %s", self._ip, err)
            self._available = False

    def _set_state(self, new_state: str) -> None:
        self._state = new_state
        self._entry.options = {**self._entry.options, "state": new_state}
        self.async_write_ha_state()

    async def async_open_cover(self, **kwargs) -> None:
        await self._send_command("roller/0?go=open")
        self._set_state(STATE_OPEN)

    async def async_close_cover(self, **kwargs) -> None:
        await self._send_command("roller/0?go=close&duration=1")
        self._set_state(STATE_CLOSED)

    async def async_open_cover_tilt(self, **kwargs) -> None:
        await self._send_command("roller/0?go=close")
        self._set_state(STATE_TILT)

    async def _send_command(self, cmd: str) -> None:
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"http://{self._ip}/{cmd}") as resp:
                    _LOGGER.debug("Shelly response: %s", resp.status)
        except Exception as err:
            _LOGGER.warning("Errore comando Shelly: %s", err)

    def handle_webhook(self, action: str) -> None:
        if action == "su":
            self._set_state(STATE_OPEN)
        elif action == "giu":
            self._set_state(STATE_CLOSED)
        elif action == "lamelle":
            self._set_state(STATE_TILT)
