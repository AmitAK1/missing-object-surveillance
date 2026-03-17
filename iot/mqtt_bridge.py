import json
import time
from datetime import datetime
import paho.mqtt.client as mqtt

# --- IIoT Cloud Configuration ---
# Example for a local Mosquito broker or cloud like AWS IoT / ThingSpeak
MQTT_BROKER = "test.mosquitto.org"  # Free public testing broker
MQTT_PORT = 1883
MQTT_TOPIC = "college/iot/surveillance/alerts"

class IoTBridge:
    """
    Bridges the Computer Vision pipeline to the IIoT Ecosystem.
    Publishes JSON telemetry data over MQTT whenever an object is missing.
    """
    
    def __init__(self, broker=MQTT_BROKER, port=MQTT_PORT):
        self.broker = broker
        self.port = port
        self.client = mqtt.Client(client_id="CV_Surveillance_Node")
        
        # Setup Callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        
        self.connected = False
        
    def connect_to_cloud(self):
        """Connects to the MQTT Broker (ThingSpeak / AWS)."""
        print(f"📡 Connecting to IIoT Cloud Broker at {self.broker}:{self.port}...")
        try:
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
            "device_id": "camera_node_01",
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
        print(f"📤 Publishing IIoT Payload to {MQTT_TOPIC} -> {json_payload}")
        result = self.client.publish(MQTT_TOPIC, json_payload, qos=1)
        
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
