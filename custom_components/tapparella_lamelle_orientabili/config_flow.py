import logging
import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import entity_registry as er, area_registry as ar

from .const import DOMAIN, ip_slug

_LOGGER = logging.getLogger(__name__)


def _get_shelly_covers(hass):
    ent_reg = er.async_get(hass)
    result = {}
    for entry in hass.config_entries.async_entries("shelly"):
        ip = entry.data.get("host")
        if not ip:
            continue
        covers = [
            e for e in ent_reg.entities.values()
            if e.config_entry_id == entry.entry_id and e.domain == "cover"
        ]
        for cover_entity in covers:
            name = cover_entity.name or cover_entity.original_name or cover_entity.entity_id
            result[f"{name} ({ip})"] = ip
    return result


def _get_areas(hass):
    area_reg = ar.async_get(hass)
    return {area.name: area.id for area in area_reg.async_list_areas()}


def _guess_ha_url(shelly_ip):
    """Ricava un URL HA plausibile dallo stesso subnet dello Shelly."""
    parts = shelly_ip.split(".")
    if len(parts) == 4:
        return f"https://{parts[0]}.{parts[1]}.{parts[2]}.2:8123"
    return "https://192.168.1.2:8123"


async def _configure_shelly_actions(shelly_ip, input_salita, ha_url, ip_s):
    """Aggiunge gli URL HA agli webhook esistenti sullo Shelly via Webhook.Update."""
    input_discesa = 1 if input_salita == 0 else 0

    _LOGGER.error("TLO SHELLY CONFIG START: ip=%s input_salita=%s ha_url=%s ip_s=%s",
                  shelly_ip, input_salita, ha_url, ip_s)

    event_map = {
        "input.button_push": {
            input_salita: f"{ha_url}/api/tapparella/{ip_s}/su",
            input_discesa: f"{ha_url}/api/tapparella/{ip_s}/giu",
        },
        "input.button_longpush": {
            input_discesa: f"{ha_url}/api/tapparella/{ip_s}/lamelle",
        },
    }

    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:

            # Leggi gli hook esistenti
            _LOGGER.error("TLO: chiamata Webhook.List a %s", shelly_ip)
            async with session.post(
                f"http://{shelly_ip}/rpc",
                json={"id": 1, "method": "Webhook.List"},
            ) as resp:
                data = await resp.json()

            hooks = data.get("hooks", [])
            _LOGGER.error("TLO: trovati %d hook", len(hooks))

            for hook in hooks:
                hook_cid = hook.get("cid")
                hook_event = hook.get("event")
                hook_id = hook.get("id")
                existing_urls = list(hook.get("urls", []))

                url_to_add = event_map.get(hook_event, {}).get(hook_cid)
                _LOGGER.error("TLO: hook id=%s event=%s cid=%s url_to_add=%s",
                              hook_id, hook_event, hook_cid, url_to_add)

                if url_to_add and url_to_add not in existing_urls:
                    new_urls = existing_urls + [url_to_add]
                    payload = {
                        "id": 1,
                        "method": "Webhook.Update",
                        "params": {
                            "id": hook_id,
                            "urls": new_urls,
                            "ssl_ca": "*",
                        }
                    }
                    async with session.post(
                        f"http://{shelly_ip}/rpc",
                        json=payload,
                    ) as resp:
                        result = await resp.json()
                        _LOGGER.error("TLO: Webhook.Update id=%s result=%s", hook_id, result)

        _LOGGER.error("TLO SHELLY CONFIG END: completato")

    except Exception as err:
        _LOGGER.error("TLO ERRORE: %s", err, exc_info=True)


class TapparellaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    def __init__(self):
        self._ip = None
        self._name = None
        self._input_salita = None
        self._area_id = None
        self._ha_url = None

    async def async_step_user(self, user_input=None):
        errors = {}
        shelly_covers = _get_shelly_covers(self.hass)

        if user_input is not None:
            self._name = user_input["name"]
            if shelly_covers:
                self._ip = shelly_covers[user_input["shelly_device"]]
            else:
                self._ip = user_input["ip"]
            return await self.async_step_configure()

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

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_configure(self, user_input=None):
        errors = {}
        areas = _get_areas(self.hass)
        default_url = _guess_ha_url(self._ip)

        if user_input is not None:
            self._input_salita = int(user_input["input_salita"])
            self._area_id = areas.get(user_input.get("area"))
            self._ha_url = user_input["ha_url"].rstrip("/")
            return await self.async_step_finish()

        schema_dict = {
            vol.Required("input_salita", default=0): vol.In([0, 1]),
        }
        area_names = list(areas.keys())
        if area_names:
            schema_dict[vol.Optional("area")] = vol.In(area_names)
        schema_dict[vol.Required("ha_url", default=default_url)] = str

        return self.async_show_form(
            step_id="configure",
            data_schema=vol.Schema(schema_dict),
            errors=errors,
        )

    async def async_step_finish(self, user_input=None):
        ip_s = ip_slug(self._ip)
        _LOGGER.error("TLO async_step_finish: ip=%s ip_s=%s ha_url=%s", self._ip, ip_s, self._ha_url)
        await _configure_shelly_actions(self._ip, self._input_salita, self._ha_url, ip_s)
        return self.async_create_entry(
            title=self._name,
            data={
                "name": self._name,
                "ip": self._ip,
                "input_salita": self._input_salita,
                "ha_url": self._ha_url,
                "area_id": self._area_id,
            },
        )
