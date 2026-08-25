"""Piattaforma cover per Tapparella Lamelle Orientabili."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .cover import async_setup_entry as _setup

async def async_setup_entry(hass, entry, async_add_entities):
    await _setup(hass, entry, async_add_entities)
