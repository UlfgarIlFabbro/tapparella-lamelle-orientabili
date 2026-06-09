from homeassistant.components.cover import CoverEntity, CoverEntityFeature
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


class CherubiniCover(CoverEntity):

    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.SET_TILT_POSITION
    )

    def __init__(self, hass: HomeAssistant, name: str, entity_id: str, ip: str = None):
        self.hass = hass
        self._name = name
        self._entity_id = entity_id
        self._ip = ip
        self._tilt_position = 0
        self._is_closed = False
        self._attr_unique_id = f"cherubini_{entity_id}"

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_closed(self) -> bool:
        return self._is_closed

    @property
    def current_cover_tilt_position(self) -> int:
        return self._tilt_position

    def open_cover(self, **kwargs):
        self.hass.services.call(
            "cover", "open_cover", {"entity_id": self._entity_id}, False
        )
        self._is_closed = False
        self._tilt_position = 0
        self.schedule_update_ha_state()

    def close_cover(self, **kwargs):
        self.hass.services.call(
            "cover", "close_cover", {"entity_id": self._entity_id}, False
        )
        self._is_closed = True
        self._tilt_position = 0
        self.schedule_update_ha_state()

    def set_cover_tilt_position(self, tilt_position: int, **kwargs):
        # Tilt: chiusura breve via Shelly per orientare le lamelle
        self.hass.services.call(
            "cover", "close_cover", {"entity_id": self._entity_id}, False
        )
        self._tilt_position = tilt_position
        self.schedule_update_ha_state()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    entity = CherubiniCover(
        hass=hass,
        name=entry.data["name"],
        entity_id=entry.data["cover_entity"],
        ip=entry.data.get("ip"),
    )
    async_add_entities([entity], update_before_add=True)
