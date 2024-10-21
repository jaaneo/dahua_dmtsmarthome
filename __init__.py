import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .sensor import DahuaIVSSensor

_LOGGER = logging.getLogger(__name__)

DOMAIN = "dahua_dmtsmartome"

async def async_setup(hass: HomeAssistant, config: dict):
    """Configure el componente desde configuration.yaml."""
    if DOMAIN not in config:
        return True

    cameras = config[DOMAIN]["cameras"]
    for camera_config in cameras:
        camera = DahuaIVSSensor(hass, camera_config)
        camera.start_listening()  # Llama al método que escuche los eventos IVS

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Configurar la integración desde la UI."""
    return await async_setup(hass, entry.data)
