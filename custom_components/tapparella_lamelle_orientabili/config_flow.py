import logging
import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import entity_registry as er, area_registry as ar

from .const import DOMAIN, HA_URL, ip_slug

_LOGGER = logging.getLogger(__name__)


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


def _get_areas(hass):
    """Restituisce dict {nome_area: area_id}."""
    area_reg = ar.async_get(hass)
    return {area.name: area.id for area in area_reg.async_list_areas()}


async def _configure_shelly_actions(shelly_ip, input_salita, ha_url, ip_s):
    """Aggiunge le URL actions sullo Shelly via RPC senza toccare quelle esistenti."""
    input_discesa = 1 if input_salita == 0 else 0

    actions = [
        {
            "input_id": input_salita,
            "event": "btn_up",
            "url": f"{ha_url}/api/tapparella/{ip_s}/su",
        },
        {
            "input_id": input_discesa,
            "event": "btn_up",
            "url": f"{ha_url}/api/tapparella/{ip_s}/giu",
        },
        {
            "input_id": input_discesa,
            "event": "btn_down",
            "url": f"{ha_url}/api/tapparella/{ip_s}/lamelle",
        },
    ]

    try:
        async with aiohttp.ClientSession() as session:
            for action in actions:
                payload = {
                    "id": 1,
                    "method": "Webhook.Create",
                    "params": {
                        "cid": action["input_id"],
                        "enable": True,
                        "event": f"input.{action['event']}",
                        "urls": [action["url"]],
                        "ssl_ca": "*",
                    }
                }
                async with session.post(
                    f"http://{shelly_ip}/rpc",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    result = await resp.json()
                    _LOGGER.debug("Webhook.Create response: %s", result)
    except Exception as err:
        _LOGGER.warning("Errore configurazione azioni Shelly: %s", err)


class TapparellaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    def __init__(self):
        self._ip = None
        self._name = None
        self._input_salita = None
        self._area_id = None
        self._ha_url = None

    async def async_step_user(self, user_input=None):
        """Step 1: scegli dispositivo Shelly e nome."""
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

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_configure(self, user_input=None):
        """Step 2: configura input, area e URL HA."""
        errors = {}
        areas = _get_areas(self.hass)
        area_options = {v: k for k, v in areas.items()}

        if user_input is not None:
            self._input_salita = user_input["input_salita"]
            self._area_id = areas.get(user_input["area"]) if user_input.get("area") else None
            self._ha_url = user_input["ha_url"].rstrip("/")
            return await self.async_step_finish()

        area_names = list(areas.keys())
        schema = vol.Schema({
            vol.Required("input_salita", default=0): vol.In([0, 1]),
            vol.Optional("area"): vol.In(area_names) if area_names else str,
            vol.Required("ha_url", default=HA_URL): str,
        })

        return self.async_show_form(
            step_id="configure",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_finish(self, user_input=None):
        """Step 3: configura automaticamente le azioni sullo Shelly e crea entry."""
        ip_s = ip_slug(self._ip)
        await _configure_shelly_actions(self._ip, self._input_salita, self._ha_url, ip_s)

        entry = self.async_create_entry(
            title=self._name,
            data={
                "name": self._name,
                "ip": self._ip,
                "input_salita": self._input_salita,
                "ha_url": self._ha_url,
            },
        )

        # Associa all'area se selezionata
        if self._area_id:
            entity_registry = er.async_get(self.hass)
            # L'associazione area viene fatta dopo la creazione entry
            # tramite hass.data o post-setup

        return entry
