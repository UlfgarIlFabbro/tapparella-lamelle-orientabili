import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN
from .cover import HA_URL, _ip_slug


def _get_shelly_covers(hass):
    """Restituisce dict {nome_entita (ip): ip} filtrando solo le cover Shelly."""
    ent_reg = er.async_get(hass)
    result = {}

    for entry in hass.config_entries.async_entries("shelly"):
        ip = entry.data.get("host")
        if not ip:
            continue

        covers = [
            e for e in ent_reg.entities.values()
            if e.config_entry_id == entry.entry_id
            and e.domain == "cover"
        ]

        for cover_entity in covers:
            name = cover_entity.name or cover_entity.original_name or cover_entity.entity_id
            result[f"{name} ({ip})"] = ip

    return result


class TapparellaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    def __init__(self):
        self._ip = None
        self._name = None

    async def async_step_user(self, user_input=None):
        errors = {}
        shelly_covers = _get_shelly_covers(self.hass)

        if user_input is not None:
            self._name = user_input["name"]
            if shelly_covers:
                self._ip = shelly_covers[user_input["shelly_device"]]
            else:
                self._ip = user_input["ip"]
            return await self.async_step_webhook()

        if shelly_covers:
            schema = vol.Schema({
                vol.Required("name"): str,
                vol.Required("shelly_device"): vol.In(list(shelly_covers.keys())),
            })
        else:
            schema = vol.Schema({
                vol.Required("name"): str,
                vol.Required("ip"): str,
            })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_webhook(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title=self._name,
                data={"name": self._name, "ip": self._ip},
            )

        slug = _ip_slug(self._ip)
        url_su = f"{HA_URL}/api/tapparella/{slug}/su"
        url_giu = f"{HA_URL}/api/tapparella/{slug}/giu"
        url_lamelle = f"{HA_URL}/api/tapparella/{slug}/lamelle"

        return self.async_show_form(
            step_id="webhook",
            data_schema=vol.Schema({}),
            description_placeholders={
                "url_su": url_su,
                "url_giu": url_giu,
                "url_lamelle": url_lamelle,
            },
        )
