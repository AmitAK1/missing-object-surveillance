import json
import time
import os
from datetime import datetime
import paho.mqtt.client as mqtt
import config

# Optional environment overrides (useful for AWS IoT cert-based deployments)
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
MQTT_TLS_CA_CERT = os.getenv("MQTT_TLS_CA_CERT", "")
MQTT_TLS_CERTFILE = os.getenv("MQTT_TLS_CERTFILE", "")
MQTT_TLS_KEYFILE = os.getenv("MQTT_TLS_KEYFILE", "")

class IoTBridge:
    """
    Bridges the Computer Vision pipeline to the IIoT Ecosystem.
    Publishes JSON telemetry data over MQTT whenever an object is missing.
    """
    
    def __init__(self, broker=None, port=None, topic=None):
        self.enabled = bool(getattr(config, "IOT_MQTT_ENABLED", True))
        self.broker = broker or config.IOT_MQTT_BROKER
        self.port = int(port or config.IOT_MQTT_PORT)
        self.topic = topic or config.IOT_MQTT_TOPIC_ALERTS
        self.device_id = getattr(config, "IOT_DEVICE_ID", "camera_node_01")
        self.client = mqtt.Client(client_id="CV_Surveillance_Node")
        
        # Setup Callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        
        self.connected = False
        
    def connect_to_cloud(self):
        """Connects to the MQTT Broker (ThingSpeak / AWS)."""
        if not self.enabled:
            print("ℹ️ IIoT MQTT disabled by config. Skipping broker connection.")
            return

        print(f"📡 Connecting to IIoT Cloud Broker at {self.broker}:{self.port}...")
        try:
            if MQTT_USERNAME:
                self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

            if MQTT_TLS_CA_CERT:
                self.client.tls_set(
                    ca_certs=MQTT_TLS_CA_CERT,
                    certfile=MQTT_TLS_CERTFILE or None,
                    keyfile=MQTT_TLS_KEYFILE or None,
                )

            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()  # Run network loop in background thread
        except Exception as e:
            print(f"❌ IIoT Connection Failed: {e}")
            
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            print("✅ Connected to IIoT Cloud successfully!")
        else:
            print(f"⚠️ IIoT Connection refused with code: {rc}")
            
    def _on_disconnect(self, client, userdata, rc):
        self.connected = False
        print("⚠️ Disconnected from IIoT Cloud.")
        
    def publish_alert(self, object_name: str, object_id: int, roi_index: int, confidence: float = 0.0):
        """
        Formats CV alert data into an IIoT JSON Telemetry payload and publishes it.
        """
        if not self.connected:
            print("⚠️ Cannot publish IIoT data: Not connected to broker.")
            return False
            
        # 1. Structure the Telemetry Payload
        payload = {
            "device_id": self.device_id,
            "timestamp": datetime.now().isoformat(),
            "event_type": "MISSING_OBJECT",
            "data": {
                "object_class": object_name,
                "tracking_id": object_id,
                "zone_id": roi_index,
                "last_confidence": round(confidence, 2)
            },
            "sensor_status": "active"
        }
        
        # 2. Serialize to JSON string
        json_payload = json.dumps(payload)
        
        # 3. Transmit via MQTT
        print(f"📤 Publishing IIoT Payload to {self.topic} -> {json_payload}")
        result = self.client.publish(self.topic, json_payload, qos=1)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print("✅ IIoT Telemetry Sent.")
            return True
        else:
            print("❌ Failed to send IIoT Telemetry.")
            return False

if __name__ == "__main__":
    # Quick Test of the Bridge
    print("--- Testing IIoT MQTT Bridge ---")
    bridge = IoTBridge()
    bridge.connect_to_cloud()
    
    # Wait for connection
    time.sleep(2)
    
    # Send a dummy test alert
    bridge.publish_alert(
        object_name="laptop",
        object_id=42,
        roi_index=1,
        confidence=0.88
    )
    
    time.sleep(1)
    bridge.client.loop_stop()
    bridge.client.disconnect()
