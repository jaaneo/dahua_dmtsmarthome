import requests
from requests.auth import HTTPDigestAuth
from homeassistant.helpers.entity import Entity
import logging
from datetime import datetime

_LOGGER = logging.getLogger(__name__)

class DahuaIVSSensor(Entity):
    def __init__(self, hass, config):
        """Inicializa la cámara y sus eventos IVS."""
        self.hass = hass
        self.name = config["name"]
        self.host = config["host"]
        self.port = config["port"]
        self.user = config["user"]
        self.password = config["pass"]
        self.events = config["events"]
        self._state = None

    def start_listening(self):
        """Inicia la escucha de eventos IVS en la cámara Dahua."""
        events = ",".join(self.events)
        url = f'http://{self.host}:{self.port}/cgi-bin/eventManager.cgi?action=attach&codes=[{events}]'
        _LOGGER.info(f"Conectando a {self.name} en {url}")

        try:
            with requests.get(url, auth=HTTPDigestAuth(self.user, self.password), stream=True, timeout=3600) as response:
                if response.status_code == 200:
                    _LOGGER.info(f"Conectado. Escuchando eventos IVS en {self.host}:{self.port}")

                    # Itera sobre las líneas de la respuesta en tiempo real
                    for line in response.iter_lines():
                        if line:
                            decoded_line = line.decode('utf-8')
                            if "Code=CrossLineDetection" in decoded_line:
                                self.handle_event("CrossLineDetection")
                            elif "Code=CrossRegionDetection" in decoded_line:
                                self.handle_event("CrossRegionDetection")
                else:
                    _LOGGER.error(f"Error en el canal {self.host}:{self.port}: Codigo de estado HTTP {response.status_code}")
                    _LOGGER.error(f"Respuesta: {response.text}")

        except requests.exceptions.RequestException as e:
            _LOGGER.error(f"Error de conexion en el canal {self.host}:{self.port}: {e}")

    def handle_event(self, event_type):
        """Maneja los eventos recibidos de IVS."""
        current_time = datetime.now().strftime("%H:%M:%S")
        _LOGGER.info(f"Evento IVS detectado - {event_type} en {self.name} - Hora: {current_time}")

        sensor_id = f"binary_sensor.sensor_{self.name.lower()}_{event_type.lower()}_termal"
        self.hass.states.set(sensor_id, "on")
        # Programar apagar el sensor después de 5 segundos
        self.hass.helpers.event.async_call_later(5, self.turn_off_sensor(sensor_id))

    def turn_off_sensor(self, sensor_id):
        """Apaga el sensor despues de un retraso."""
        self.hass.states.set(sensor_id, "off")
        _LOGGER.info(f"Sensor {sensor_id} apagado automaticamente despues de 5 segundos.")

    @property
    def state(self):
        return self._state
