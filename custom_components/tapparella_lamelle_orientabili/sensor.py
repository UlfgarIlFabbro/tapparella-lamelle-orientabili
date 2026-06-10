"""Sensori per Tapparella Lamelle Orientabili."""
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ENTITY_STORE, STATE_OPEN, STATE_CLOSED, STATE_TILT, ip_slug

_LOGGER = logging.getLogger(__name__)

STATE_LABELS = {
    STATE_OPEN: "Aperta",
    STATE_CLOSED: "Chiusa",
    STATE_TILT: "Lamelle aperte",
}

BUTTON_LABELS = {
    STATE_OPEN: "Su",
    STATE_CLOSED: "Giù",
    STATE_TILT: "Lamelle",
}


class TapparellaStatoSensor(SensorEntity):
    """Sensore che mostra lo stato della tapparella in italiano."""

    _attr_icon = "mdi:blinds"

    def __init__(self, entry: ConfigEntry, cover_entity):
        self._entry = entry
        self._cover = cover_entity
        self._attr_name = f"{entry.data['name']} Stato"
        self._attr_unique_id = f"tlo_{ip_slug(entry.data['ip'])}_stato"

    @property
    def native_value(self):
        return STATE_LABELS.get(self._cover._state, "Sconosciuto")

    @property
    def extra_state_attributes(self):
        return {"stato_raw": self._cover._state}


class TapparellaUltimoPulsanteSensor(SensorEntity):
    """Sensore che mostra l'ultimo pulsante premuto."""

    _attr_icon = "mdi:gesture-tap-button"

    def __init__(self, entry: ConfigEntry, cover_entity):
        self._entry = entry
        self._cover = cover_entity
        self._attr_name = f"{entry.data['name']} Ultimo Pulsante"
        self._attr_unique_id = f"tlo_{ip_slug(entry.data['ip'])}_ultimo_pulsante"

    @property
    def native_value(self):
        return BUTTON_LABELS.get(self._cover._state, "Nessuno")


class TapparellaIPSensor(SensorEntity):
    """Sensore che mostra l'indirizzo IP dello Shelly."""

    _attr_icon = "mdi:ip-network"

    def __init__(self, entry: ConfigEntry):
        self._entry = entry
        self._attr_name = f"{entry.data['name']} IP"
        self._attr_unique_id = f"tlo_{ip_slug(entry.data['ip'])}_ip"

    @property
    def native_value(self):
        return self._entry.data.get("ip")


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Attendi che la cover entity sia disponibile nell'ENTITY_STORE."""
    ip_s = ip_slug(entry.data["ip"])
    cover_entity = ENTITY_STORE.get(ip_s)

    entities = [TapparellaIPSensor(entry)]

    if cover_entity is not None:
        entities.append(TapparellaStatoSensor(entry, cover_entity))
        entities.append(TapparellaUltimoPulsanteSensor(entry, cover_entity))
    else:
        _LOGGER.warning("TLO sensor: cover entity non trovata per %s", ip_s)

    async_add_entities(entities, update_before_add=False)
