import bluetooth
import struct
import time
from micropython import const

# Définition des UUID et des drapeaux
CSC_SERVICE_UUID = 0x1818  # UUID du Cycling Power Service
CSC_MEASUREMENT_CHAR_UUID = 0x2A63  # UUID de la mesure de puissance
FLAGS_INSTANTANEOUS_POWER = 0x02  # Drapeaux pour la mesure
DEVICE_NAME = "CyclingPowerSen"  # Nom du capteur BLE

class BLEServer:
    def __init__(self):
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.connections = []
        self.ble.irq(self.ble_irq)

    def ble_irq(self, event, data):
        if event == 1:  # Connexion BLE
            conn_handle, _, _ = data
            self.connections.append(conn_handle)
            print(f"Appareil connecté : handle={conn_handle}")
        elif event == 2:  # Déconnexion BLE
            conn_handle, _, _ = data
            self.connections.remove(conn_handle)
            print(f"Appareil déconnecté : handle={conn_handle}")
            self.start_advertising()  # Redémarrer la publicité BLE

    def start_advertising(self):
        payload = self.advertising_payload(name=DEVICE_NAME, services=[CSC_SERVICE_UUID])
        self.ble.gap_advertise(100_000, adv_data=payload)
        print(f"Publicité BLE démarrée en tant que {DEVICE_NAME}.")

    def advertising_payload(self, name=None, services=None):
        payload = bytearray()
        if name:
            payload += bytearray((len(name) + 1, 0x09)) + name.encode('utf-8')
        if services:
            for uuid in services:
                payload += bytearray((3, 0x03, uuid & 0xFF, (uuid >> 8) & 0xFF))
        return payload

class CyclingPowerService:
    def __init__(self):
        self.ble_server = BLEServer()
        self.measurement_handle = None
        self.setup_service()

    def setup_service(self):
        # Déclare un service avec une caractéristique pour la mesure
        csc_service = (
            bluetooth.UUID(CSC_SERVICE_UUID),
            ((bluetooth.UUID(CSC_MEASUREMENT_CHAR_UUID), bluetooth.FLAG_NOTIFY,),),
        )
        handles = self.ble_server.ble.gatts_register_services((csc_service,))
        self.measurement_handle = handles[0][0]
        print("Cycling Power Service enregistré avec succès.")

    def send_measurement(self, power):
        # Crée les données de notification : drapeaux et puissance
        flags = FLAGS_INSTANTANEOUS_POWER
        data = struct.pack("<Hh", flags, power)
        print(f"Envoi des données : {data}")
        for conn_handle in self.ble_server.connections:
            self.ble_server.ble.gatts_notify(conn_handle, self.measurement_handle, data)
            print(f"Notification envoyée à handle={conn_handle} : puissance={power} W")

    def start_advertising(self):
        self.ble_server.start_advertising()

# Exemple d'utilisation
if __name__ == "__main__":
    csc = CyclingPowerService()
    csc.start_advertising()
    try:
        while True:
            if csc.ble_server.connections:
                csc.send_measurement(power=250)  # Envoi d'une puissance fixe de 250W
            time.sleep(1)
    except KeyboardInterrupt:
        print("Arrêt du serveur.")
