"""Utility condivise per il Termostato Intelligente FV."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry


def get_conf(entry: ConfigEntry, key: str, default=None):
    """Legge un valore dalla configurazione dell'entry.
    
    Le options hanno precedenza sui data — così le modifiche
    fatte dall'utente nelle opzioni sovrascrivono i valori originali.
    """
    # Prima controlla options (valori aggiornati dall'utente)
    if key in entry.options:
        return entry.options[key]
    # Poi controlla data (valori originali della configurazione)
    if key in entry.data:
        return entry.data[key]
    # Infine usa il default
    return default
