"""
IIoT Actuator Manager
Provides optional Raspberry Pi GPIO actuation with safe fallback mode.
"""

import threading
import time
import importlib
import config


class ActuatorManager:
    """Handles a single alert actuator (buzzer/relay) with optional GPIO backend."""

    def __init__(self):
        self.enabled = bool(getattr(config, "ACTUATION_ENABLED", False))
        self.hardware_enabled = bool(getattr(config, "IOT_HARDWARE_ENABLED", False))
        self.pin = int(getattr(config, "ACTUATOR_GPIO_PIN", 23))
        self.active_high = bool(getattr(config, "ACTUATOR_ACTIVE_HIGH", True))
        self.pulse_seconds = float(getattr(config, "ACTUATION_PULSE_SECONDS", 2.0))

        self._gpio_available = False
        self._gpio = None

        if self.enabled and self.hardware_enabled:
            self._setup_gpio()

    def _setup_gpio(self):
        try:
            GPIO = importlib.import_module("RPi.GPIO")

            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.OUT)
            GPIO.output(self.pin, GPIO.LOW if self.active_high else GPIO.HIGH)

            self._gpio = GPIO
            self._gpio_available = True
            print(f"🔧 [Actuator] GPIO ready on BCM pin {self.pin}")
        except Exception as exc:
            self._gpio_available = False
            print(f"⚠️ [Actuator] GPIO unavailable, simulation mode active: {exc}")

    def _write(self, active: bool):
        if not self.enabled:
            return

        value = self._gpio.HIGH if (active == self.active_high) else self._gpio.LOW

        if self._gpio_available:
            self._gpio.output(self.pin, value)
        else:
            state = "ON" if active else "OFF"
            print(f"🟠 [Actuator-Sim] {state} on pin {self.pin}")

    def pulse(self, duration_seconds: float = None):
        """Activate actuator for a short duration in background thread."""
        if not self.enabled:
            return

        duration = float(duration_seconds if duration_seconds is not None else self.pulse_seconds)

        def _pulse_worker():
            self._write(True)
            time.sleep(max(0.1, duration))
            self._write(False)

        threading.Thread(target=_pulse_worker, daemon=True).start()

    def cleanup(self):
        """Cleanup GPIO resources if used."""
        if self._gpio_available and self._gpio:
            try:
                self._write(False)
                self._gpio.cleanup(self.pin)
            except Exception:
                pass
