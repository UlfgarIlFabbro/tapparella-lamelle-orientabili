DOMAIN = "tapparella_lamelle_orientabili"

STATE_OPEN = "open"
STATE_CLOSED = "closed"
STATE_TILT = "tilt"

HA_URL = "https://192.168.1.2:8123"

# Store globale: slug IP -> entita CherubiniCover
ENTITY_STORE = {}


def ip_slug(ip: str) -> str:
    return ip.replace(".", "_")
