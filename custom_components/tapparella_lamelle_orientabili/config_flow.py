import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN
from .cover import HA_URL, webhook_id_su, webhook_id_giu, webhook_id_lamelle


def _get_shelly_devices(hass):
    """Restituisce dict {nome_dispositivo: ip} per tutti i dispositivi Shelly integrati."""
    dev_reg = dr.async_get(hass)
    shelly_devices = {}

    for device in dev_reg.devices.values():
        is_shelly = any(
            hass.config_entries.async_get_entry(entry_id) is not None
            and hass.config_entries.async_get_entry(entry_id).domain == "shelly"
            for entry_id in device.config_entries
        )
        if not is_shelly:
            continue

        for conn_type, conn_val in device.connections:
            if conn_type == "local_ip":
                name = device.name_by_user or device.name or conn_val
                shelly_devices[name] = conn_val
                break

    return shelly_devices


class TapparellaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    def __init__(self):
        self._ip = None
        self._name = None

    async def async_step_user(self, user_input=None):
        """Step 1: scegli dispositivo Shelly o inserisci IP manuale."""
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
        """Step 2: mostra gli URL webhook da configurare nello Shelly."""
        if user_input is not None:
            return self.async_create_entry(
                title=self._name,
                data={
                    "name": self._name,
                    "ip": self._ip,
                },
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
