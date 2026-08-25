"""Costanti per Tapparella Lamelle Orientabili."""
DOMAIN = "tapparella_lamelle_orientabili"

STATE_OPEN = "open"
STATE_CLOSED = "closed"
STATE_TILT = "tilt"

ENTITY_STORE: dict = {}

HA_URL = "https://192.168.1.2:8123"


def ip_slug(ip: str) -> str:
    return ip.replace(".", "_")
