"""Integrazione Tapparella Lamelle Orientabili."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.http import HomeAssistantView
from aiohttp.web import Request, Response

from .const import DOMAIN, ENTITY_STORE, ip_slug

_LOGGER = logging.getLogger(__name__)

VIEW_REGISTERED = False


class TapparellaView(HomeAssistantView):
    """View HTTP per ricevere aggiornamenti stato dalla pressione pulsanti Shelly."""

    url = "/api/tapparella/{slug}/{action}"
    name = "api:tapparella"
    requires_auth = False

    def __init__(self, hass: HomeAssistant):
        self.hass = hass

    async def get(self, request: Request, slug: str, action: str) -> Response:
        entity = ENTITY_STORE.get(slug)
        if entity is None:
            _LOGGER.warning("TLO: nessuna entità per slug=%s", slug)
            return Response(text="not found", status=404)
        entity.handle_webhook(action)
        return Response(text="ok")


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    global VIEW_REGISTERED
    if not VIEW_REGISTERED:
        hass.http.register_view(TapparellaView(hass))
        VIEW_REGISTERED = True

    await hass.config_entries.async_forward_entry_setups(entry, ["cover", "sensor", "lock"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ip_s = ip_slug(entry.data["ip"])
    ENTITY_STORE.pop(ip_s, None)
    return await hass.config_entries.async_unload_platforms(entry, ["cover", "sensor", "lock"])
