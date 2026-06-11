from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from aiohttp.web import Request, Response

from homeassistant.components.http import HomeAssistantView
from .const import DOMAIN, ENTITY_STORE, STATE_OPEN, STATE_CLOSED, STATE_TILT, ip_slug

_VIEW_REGISTERED = False


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
            entity._state = STATE_TILT
        else:
            return Response(status=400, text="Azione non valida")

        entity._save_state()
        entity.async_write_ha_state()
        return Response(status=200, text="OK")


async def async_setup(hass: HomeAssistant, config: dict):
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    global _VIEW_REGISTERED
    hass.data.setdefault(DOMAIN, {})

    if not _VIEW_REGISTERED:
        hass.http.register_view(TapparellaView())
        _VIEW_REGISTERED = True

    await hass.config_entries.async_forward_entry_setups(entry, ["cover", "sensor", "lock"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    ENTITY_STORE.pop(ip_slug(entry.data.get("ip", "")), None)
    await hass.config_entries.async_unload_platforms(entry, ["cover", "sensor", "lock"])
    return True
