from homeassistant.components.cover import CoverEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

class CherubiniCover(CoverEntity):

    def __init__(self, hass, name, entity_id, ip=None):
        self.hass = hass
        self._name = name
        self._entity_id = entity_id
        self._ip = ip
        self._tilt = False

    @property
    def name(self):
        return self._name

    @property
    def is_closed(self):
        return self.hass.states.is_state(self._entity_id, "closed")

    def open_cover(self, **kwargs):
        self.hass.services.call(
            "cover",
            "open_cover",
            {"entity_id": self._entity_id},
            False
        )
        self._tilt = False

    def close_cover(self, **kwargs):
        # impulso breve shelly (rest_command opzionale)
        self.hass.services.call(
            "cover",
            "close_cover",
            {"entity_id": self._entity_id},
            False
        )
        self._tilt = False

    def set_cover_tilt_position(self, **kwargs):
        # lamelle (logica motore)
        self.hass.services.call(
            "cover",
            "close_cover",
            {"entity_id": self._entity_id},
            False
        )
        self._tilt = True

    @property
    def current_cover_tilt_position(self):
        return 100 if self._tilt else 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    entity = CherubiniCover(
        hass,
        entry.data["name"],
        entry.data["cover_entity"],
        entry.data.get("ip"),
    )
    async_add_entities([entity])
