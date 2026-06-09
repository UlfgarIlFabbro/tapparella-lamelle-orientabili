import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN


def _get_shelly_devices(hass):
    """Restituisce dict {nome_dispositivo: ip} per tutti i dispositivi Shelly integrati."""
    dev_reg = dr.async_get(hass)
    shelly_devices = {}

    for device in dev_reg.devices.values():
        # I dispositivi Shelly hanno almeno un entry con integration "shelly"
        is_shelly = any(
            entry_id
            for entry_id in device.config_entries
            if hass.config_entries.async_get_entry(entry_id) is not None
            and hass.config_entries.async_get_entry(entry_id).domain == "shelly"
        )
        if not is_shelly:
            continue

        # L'IP è nella connessione del dispositivo (connection type = local_ip)
        for conn_type, conn_val in device.connections:
            if conn_type == "local_ip":
                name = device.name_by_user or device.name or conn_val
                shelly_devices[name] = conn_val
                break

    return shelly_devices


class TapparellaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        shelly_devices = _get_shelly_devices(self.hass)

        if shelly_devices:
            # Step con lista dispositivi Shelly rilevati
            if user_input is not None:
                selected_name = user_input["shelly_device"]
                ip = shelly_devices[selected_name]
                return self.async_create_entry(
                    title=user_input["name"],
                    data={
                        "name": user_input["name"],
                        "ip": ip,
                    },
                )

            schema = vol.Schema({
                vol.Required("name"): str,
                vol.Required("shelly_device"): vol.In(list(shelly_devices.keys())),
            })

            return self.async_show_form(
                step_id="user",
                data_schema=schema,
                errors=errors,
                description_placeholders={
                    "count": str(len(shelly_devices))
                },
            )

        else:
            # Nessun dispositivo Shelly trovato: chiedi IP manuale
            if user_input is not None:
                return self.async_create_entry(
                    title=user_input["name"],
                    data=user_input,
                )

            schema = vol.Schema({
                vol.Required("name"): str,
                vol.Required("ip"): str,
            })

            return self.async_show_form(
                step_id="user",
                data_schema=schema,
                errors=errors,
            )
