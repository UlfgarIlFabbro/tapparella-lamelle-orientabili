from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .cover import CherubiniCover


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
):

    data = entry.data

    entity = CherubiniCover(
        hass,
        data["name"],
        data["cover_entity"],
        data.get("ip")
    )

    async_add_entities([entity])
