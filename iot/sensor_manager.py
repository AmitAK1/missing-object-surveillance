"""
IIoT Sensor Manager
Provides a hardware abstraction layer for physical sensors.

On a PC (development):  Simulates a PIR motion sensor via keyboard 'm'.
On Raspberry Pi (prod): Replace the _read_mock_sensor() method with actual
                       RPi.GPIO code.
"""

import time
import threading


class SensorManager:
    """
    Manages IIoT physical sensor inputs.
    
    Provides a unified interface so that switching from PC simulation to a
    real Raspberry Pi GPIO sensor requires changing ONE method only.

    SBC Deployment (RPi): Replace _is_sensor_triggered() with:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIR_PIN, GPIO.IN)
        
        def _is_sensor_triggered(self):
            return GPIO.input(PIR_PIN) == GPIO.HIGH
    """

    def __init__(self, on_trigger_callback: callable = None):
        """
        Args:
            on_trigger_callback: Function to call when sensor is activated.
                                 Will be: lambda: <start_monitoring>
        """
        self.on_trigger = on_trigger_callback
        self._running = False
        self._triggered_state = False   # Simulated PIR sensor state
        self._poll_thread = None

    def simulate_trigger(self):
        """
        Manually trigger the simulated PIR sensor.
        Call this from the GUI or press 'm' in terminal to simulate motion.
        """
        self._triggered_state = True
        print("🔴 [Sensor] Motion Detected! (Simulated PIR Trigger)")
        if self.on_trigger:
            self.on_trigger()

    def _is_sensor_triggered(self) -> bool:
        """
        Returns True if the sensor has been triggered.
        SWAP THIS METHOD for RPi.GPIO.input() when deploying to hardware.
        """
        if self._triggered_state:
            self._triggered_state = False   # Auto-reset (simulate one-shot trigger)
            return True
        return False

    def _poll_loop(self):
        """Background thread: Polls the sensor and fires the callback."""
        print("📡 [Sensor] Polling loop started. Press 'm' or call simulate_trigger() to fire.")
        while self._running:
            if self._is_sensor_triggered():
                if self.on_trigger:
                    self.on_trigger()
            time.sleep(0.1)     # 10Hz polling rate — fine for a PIR sensor

    def start_polling(self):
        """Start the sensor polling in a daemon thread."""
        self._running = True
        self._poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._poll_thread.start()
        print("📡 [SensorManager] Started sensor polling in background.")

    def stop_polling(self):
        """Stop the sensor polling thread."""
        self._running = False
        print("📡 [SensorManager] Sensor polling stopped.")


if __name__ == "__main__":
    # Quick Demo
    def on_motion():
        print("🚨 SENSOR TRIGGERED → Start CV Monitoring now!")

    sensor = SensorManager(on_trigger_callback=on_motion)
    sensor.start_polling()

    # Simulate 3 sensor triggers
    for i in range(3):
        time.sleep(1.5)
        sensor.simulate_trigger()
        time.sleep(0.5)

    sensor.stop_polling()
