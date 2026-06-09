import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN
from .cover import HA_URL, webhook_id_su, webhook_id_giu, webhook_id_lamelle


def _get_shelly_devices(hass):
    """Restituisce dict {nome_dispositivo: ip} leggendo l'IP dalle config entry Shelly."""
    result = {}

    for entry in hass.config_entries.async_entries("shelly"):
        ip = entry.data.get("host")
        if not ip:
            continue
        name = entry.title or ip
        result[name] = ip

    return result


class TapparellaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    def __init__(self):
        self._ip = None
        self._name = None

    async def async_step_user(self, user_input=None):
        errors = {}
        shelly_devices = _get_shelly_devices(self.hass)

        if user_input is not None:
            self._name = user_input["name"]
            if shelly_devices:
                self._ip = shelly_devices[user_input["shelly_device"]]
            else:
                self._ip = user_input["ip"]
            return await self.async_step_webhook()

        if shelly_devices:
            schema = vol.Schema({
                vol.Required("name"): str,
                vol.Required("shelly_device"): vol.In(list(shelly_devices.keys())),
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

        url_su = f"{HA_URL}/api/webhook/{webhook_id_su(self._ip)}"
        url_giu = f"{HA_URL}/api/webhook/{webhook_id_giu(self._ip)}"
        url_lamelle = f"{HA_URL}/api/webhook/{webhook_id_lamelle(self._ip)}"

        return self.async_show_form(
            step_id="webhook",
            data_schema=vol.Schema({}),
            description_placeholders={
                "url_su": url_su,
                "url_giu": url_giu,
                "url_lamelle": url_lamelle,
            },
        )
