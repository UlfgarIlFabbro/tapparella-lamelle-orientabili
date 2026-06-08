import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.entity_registry import async_get
from homeassistant.helpers import area_registry as ar

from .const import DOMAIN


class Flow(config_entries.ConfigFlow, domain=DOMAIN):

    async def async_step_user(self, user_input=None):

        er = async_get(self.hass)
        areas = ar.async_get(self.hass)

        covers = [
            e.entity_id
            for e in er.entities.values()
            if e.entity_id.startswith("cover.")
        ]

        if user_input:
            return self.async_create_entry(
                title=user_input["name"],
                data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("name"): str,
                vol.Required("cover_entity"): vol.In(covers),
                vol.Required("area"): vol.In([a.name for a in areas.areas.values()]),
                vol.Optional("ip"): str
            })
        )