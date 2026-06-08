from homeassistant.components.cover import CoverEntity


class CherubiniCover(CoverEntity):

    def __init__(self, hass, name, real_cover, ip):
        self.hass = hass
        self._name = name
        self._real = real_cover
        self._ip = ip
        self._tilt = False

    @property
    def name(self):
        return self._name

    def open_cover(self, **kwargs):
        self.hass.services.call(
            "cover",
            "open_cover",
            {"entity_id": self._real},
            False
        )
        self._tilt = False

    def close_cover(self, **kwargs):
        self.hass.services.call(
            "rest_command",
            "tlo_close_short",
            {},
            False
        )
        self._tilt = False

    def set_cover_tilt_position(self, **kwargs):
        self.hass.services.call(
            "cover",
            "close_cover",
            {"entity_id": self._real},
            False
        )
        self._tilt = True

    @property
    def current_cover_tilt_position(self):
        return 100 if self._tilt else 0