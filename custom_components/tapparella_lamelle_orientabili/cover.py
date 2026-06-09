from homeassistant.components.cover import CoverEntity, CoverEntityFeature
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


class CherubiniCover(CoverEntity):
    """Tapparella Cherubini con lamelle orientabili via Shelly."""

    # Solo apertura, chiusura, stop e tilt — niente position slider
    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.STOP
        | CoverEntityFeature.OPEN_TILT
        | CoverEntityFeature.CLOSE_TILT
        | CoverEntityFeature.STOP_TILT
    )

    def __init__(self, hass: HomeAssistant, name: str, entity_id: str, ip: str = None):
        self.hass = hass
        self._name = name
        self._entity_id = entity_id
        self._ip = ip
        self._is_closed = False
        self._tilt_open = False
        self._attr_unique_id = f"cherubini_{entity_id}"

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_closed(self) -> bool:
        return self._is_closed

    @property
    def current_cover_tilt_position(self) -> int:
        return 100 if self._tilt_open else 0

    # --- Tapparella su/giù/stop ---

    def open_cover(self, **kwargs):
        """Su."""
        self.hass.services.call(
            "cover", "open_cover", {"entity_id": self._entity_id}, False
        )
        self._is_closed = False
        self.schedule_update_ha_state()

    def close_cover(self, **kwargs):
        """Giù."""
        self.hass.services.call(
            "cover", "close_cover", {"entity_id": self._entity_id}, False
        )
        self._is_closed = True
        self.schedule_update_ha_state()

    def stop_cover(self, **kwargs):
        """Stop tapparella."""
        self.hass.services.call(
            "cover", "stop_cover", {"entity_id": self._entity_id}, False
        )
        self.schedule_update_ha_state()

    # --- Lamelle apri/chiudi/stop ---

    def open_cover_tilt(self, **kwargs):
        """Apri lamelle (impulso breve Shelly)."""
        self.hass.services.call(
            "cover", "close_cover", {"entity_id": self._entity_id}, False
        )
        self._tilt_open = True
        self.schedule_update_ha_state()

    def close_cover_tilt(self, **kwargs):
        """Chiudi lamelle."""
        self.hass.services.call(
            "cover", "close_cover", {"entity_id": self._entity_id}, False
        )
        self._tilt_open = False
        self.schedule_update_ha_state()

    def stop_cover_tilt(self, **kwargs):
        """Stop lamelle."""
        self.hass.services.call(
            "cover", "stop_cover", {"entity_id": self._entity_id}, False
        )
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
