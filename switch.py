import socket
import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator
from datetime import timedelta

_LOGGER = logging.getLogger(__name__)

SPA25_IP = "xxx.xxx.xxx.xxx" """ enter the IP of your primare device here"""
SPA25_PORT = 50006
END_CHARACTER = "\r\n"

def send_command(command):
    """Sendet einen Befehl an den SPA25 und gibt die Antwort zurück."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SPA25_IP, SPA25_PORT))
            s.sendall((command + END_CHARACTER).encode("ascii"))
            response = s.recv(1024).decode("ascii").strip()
            return response
    except Exception as e:
        _LOGGER.error(f"Fehler beim Senden des Befehls: {e}")
        return None

def get_power_state():
    """Fragt den aktuellen Power-Status ab."""
    response = send_command("!1pow.?")
    return response == "!1pow.1"

def get_mute_state():
    """Fragt den aktuellen Mute-Status ab."""
    response = send_command("!1mut.?")
    return response == "!1mut.1"

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Setzt die Switch-Entitäten in Home Assistant auf."""
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="spa25_switch_status",
        update_method=async_update_data,
        update_interval=timedelta(seconds=5),
    )
    add_entities([SPA25PowerSwitch(coordinator), SPA25MuteSwitch(coordinator)])
    coordinator.async_config_entry_first_refresh()

async def async_update_data():
    """Abrufen der aktuellen Daten."""
    return {
        "power": get_power_state(),
        "mute": get_mute_state()
    }

class SPA25PowerSwitch(CoordinatorEntity, SwitchEntity):
    """Switch-Entität für den Power-Status des SPA25."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = "sp25_power_switch"
    
    @property
    def name(self):
        return "SPA25 Power"

    @property
    def is_on(self):
        return self.coordinator.data.get("power")

    def turn_on(self, **kwargs):
        send_command("!1pow.1")
        self.coordinator.async_request_refresh()

    def turn_off(self, **kwargs):
        send_command("!1pow.0")
        self.coordinator.async_request_refresh()

class SPA25MuteSwitch(CoordinatorEntity, SwitchEntity):
    """Switch-Entität für den Mute-Status des SPA25."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = "sp25_mute_switch"
    
    @property
    def name(self):
        return "SPA25 Mute"

    @property
    def is_on(self):
        return self.coordinator.data.get("mute")

    def turn_on(self, **kwargs):
        send_command("!1mut.1")
        self.coordinator.async_request_refresh()

    def turn_off(self, **kwargs):
        send_command("!1mut.0")
        self.coordinator.async_request_refresh()
