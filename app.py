import RPi.GPIO as GPIO
import dht11
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime

# Configuración del GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

# Inicialización del sensor DHT11 en GPIO4
sensor = dht11.DHT11(pin=4)

# Configuración del broker MQTT
BROKER_URL = "mqtt://<BROKER_IP>"  # Cambia <BROKER_IP> por la dirección IP del broker
BROKER_HOST = "<BROKER_IP>"        # Cambia <BROKER_IP> por la IP pública del broker EC2
BROKER_PORT = 1883                # Puerto estándar de MQTT
TOPIC = "sensores"                # Tema donde se publicarán los datos
CLIENT_ID = f"mqtt_producer_{int(time.time())}"

# Configuración del cliente MQTT
client = mqtt.Client(CLIENT_ID)
client.username_pw_set(username="ubuntu", password="pezcadofrito.1")  # Credenciales del broker

# Conexión al broker
client.connect(BROKER_HOST, BROKER_PORT, 60)

def read_and_publish():
    """
    Lee datos del sensor DHT11 y los publica en el broker MQTT en formato JSON.
    """
    result = sensor.read()
    if result.is_valid():
        # Crear el mensaje en el formato deseado
        message = {
            "timestamp": datetime.utcnow().isoformat(),  # Fecha y hora en formato ISO
            "sensorData": {
                "temperature": result.temperature,
                "humidity": result.humidity
            }
        }
        # Convertir el mensaje a JSON
        message_json = json.dumps(message)
        try:
            # Publicar el mensaje
            client.publish(TOPIC, message_json, qos=0)
            print(f"Mensaje enviado: {message_json}")
        except Exception as e:
            print(f"Error al publicar: {e}")
    else:
        print("Error al leer los datos del sensor")

# Publicar datos cada 5 segundos
try:
    while True:
        read_and_publish()
        time.sleep(5)
except KeyboardInterrupt:
    print("Interrumpido por el usuario")
finally:
    GPIO.cleanup()
    client.disconnect()
