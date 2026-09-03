"""Integrazione Tapparella Lamelle Orientabili."""
import logging
import asyncio
from aiohttp.web import Request, Response
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.components.http import HomeAssistantView
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, ENTITY_STORE, STATE_OPEN, STATE_CLOSED, STATE_TILT

_LOGGER = logging.getLogger(__name__)
_VIEW_REGISTERED = False
_SERVICES_REGISTERED = False


class TapparellaView(HomeAssistantView):
    """View HTTP per ricevere aggiornamenti stato dalla pressione pulsanti Shelly."""

    url = "/api/tapparella/{slug}/{action}"
    name = "api:tapparella"
    requires_auth = False
    cors_allowed = True

    async def get(self, request: Request, slug: str, action: str) -> Response:
        entity = ENTITY_STORE.get(slug)
        if entity is None:
            return Response(status=404, text="Tapparella non trovata")

        if action == "su":
            entity._state = STATE_OPEN
        elif action == "giu":
            entity._state = STATE_CLOSED
        elif action == "lamelle":
            # Comando fisico Cherubini: è un toggle.
            if entity._state == STATE_TILT:
                entity._state = STATE_CLOSED
            else:
                entity._state = STATE_TILT
        else:
            return Response(status=400, text="Azione non valida")

        entity._save_state()
        entity.async_write_ha_state()
        return Response(status=200, text="OK")


async def _service_open_all(call: ServiceCall) -> None:
    """Porta tutte le tapparelle orientabili allo stato OPEN + LOCKED."""
    tasks = [entity.async_open_cover() for entity in list(ENTITY_STORE.values()) if entity._state != STATE_OPEN]
    if tasks:
        await asyncio.gather(*tasks)


async def _service_close_all(call: ServiceCall) -> None:
    """Porta tutte le tapparelle orientabili allo stato CLOSED + LOCKED."""
    tasks = [entity.async_close_cover() for entity in list(ENTITY_STORE.values()) if entity._state != STATE_CLOSED]
    if tasks:
        await asyncio.gather(*tasks)


async def _service_open_all_tilt(call: ServiceCall) -> None:
    """Porta tutte le tapparelle orientabili allo stato TILT (OPEN + UNLOCKED)."""
    tasks = [entity.async_open_cover_tilt() for entity in list(ENTITY_STORE.values()) if entity._state != STATE_TILT]
    if tasks:
        await asyncio.gather(*tasks)


async def _register_services(hass: HomeAssistant) -> None:
    global _SERVICES_REGISTERED
    if _SERVICES_REGISTERED:
        return

    hass.services.async_register(
        DOMAIN,
        "open_all",
        _service_open_all,
        schema=cv.empty_config_schema,
    )
    hass.services.async_register(
        DOMAIN,
        "close_all",
        _service_close_all,
        schema=cv.empty_config_schema,
    )
    hass.services.async_register(
        DOMAIN,
        "open_all_tilt",
        _service_open_all_tilt,
        schema=cv.empty_config_schema,
    )
    _SERVICES_REGISTERED = True


async def async_setup(hass: HomeAssistant, config: dict):
    global _VIEW_REGISTERED

    if not _VIEW_REGISTERED:
        hass.http.register_view(TapparellaView())
        _VIEW_REGISTERED = True

    await _register_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data.setdefault(DOMAIN, {})
    await hass.config_entries.async_forward_entry_setups(entry, ["cover", "sensor", "lock"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    ip = entry.data.get("ip", "")
    from .const import ip_slug
    ENTITY_STORE.pop(ip_slug(ip), None)
    return await hass.config_entries.async_unload_platforms(entry, ["cover", "sensor", "lock"])
