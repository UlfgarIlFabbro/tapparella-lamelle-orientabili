DOMAIN = "tapparella_lamelle_orientabili"

STATE_OPEN = "open"
STATE_CLOSED = "closed"
STATE_TILT = "tilt"

HA_URL = "https://ea0u0eglo2dfbrtt.myfritz.net:9000"

# Store globale: slug IP -> entita CherubiniCover
ENTITY_STORE = {}


def ip_slug(ip: str) -> str:
    return ip.replace(".", "_")
