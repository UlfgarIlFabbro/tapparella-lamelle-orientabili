from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from aiohttp import web

from homeassistant.components.http import HomeAssistantView
from .const import DOMAIN, ENTITY_STORE
from .cover import STATE_OPEN, STATE_CLOSED, STATE_TILT, _ip_slug


class TapparellaView(HomeAssistantView):
    """View HTTP per ricevere aggiornamenti stato dalla pressione pulsanti Shelly."""

    url = "/api/tapparella/{slug}/{action}"
    name = "api:tapparella"
    requires_auth = False

    async def get(self, request, slug, action):
        entity = ENTITY_STORE.get(slug)
        if entity is None:
            return web.Response(status=404, text="Tapparella non trovata")

        if action == "su":
            entity._state = STATE_OPEN
        elif action == "giu":
            entity._state = STATE_CLOSED
        elif action == "lamelle":
            entity._state = STATE_TILT
        else:
            return web.Response(status=400, text="Azione non valida")

        entity._save_state()
        entity.async_write_ha_state()
        return web.Response(status=200, text="OK")


async def async_setup(hass: HomeAssistant, config: dict):
    hass.http.register_view(TapparellaView())
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data.setdefault(DOMAIN, {})
    await hass.config_entries.async_forward_entry_setups(entry, ["cover"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    ip = entry.data.get("ip", "")
    ENTITY_STORE.pop(_ip_slug(ip), None)
    await hass.config_entries.async_unload_platforms(entry, ["cover"])
    return True
