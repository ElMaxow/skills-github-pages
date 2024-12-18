from time import sleep
from struct import pack
import ubluetooth

# Constantes et UUIDs basés sur la spécification CSC
CSC_SERVICE_UUID = 0x1816
CSC_MEASUREMENT_CHAR_UUID = 0x2A5B
CSC_FEATURE_CHAR_UUID = 0x2A5C

# Flags pour la caractéristique CSC Measurement
FLAGS_WHEEL_REVOLUTION = 0x01  # Indique que les données de révolution de roue sont présentes
FLAGS_CRANK_REVOLUTION = 0x02  # Indique que les données de révolution de pédale sont présentes

class BLEServer:
    def __init__(self):
        self.ble = ubluetooth.BLE()
        self.ble.active(True)
        self.connections = []
        self.ble.irq(self.ble_irq)

    def ble_irq(self, event, data):
        if event == ubluetooth.IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self.connections.append(conn_handle)
            print("Device connected, handle:", conn_handle)
        elif event == ubluetooth.IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self.connections.remove(conn_handle)
            print("Device disconnected, handle:", conn_handle)
            self.ble.gap_advertise(100_000)  # Restart advertising

    def advertise(self, name):
        payload = self.advertising_payload(name=name, services=[CSC_SERVICE_UUID])
        self.ble.gap_advertise(100_000, adv_data=payload)
        print(f"Advertising as {name}.")

    def advertising_payload(self, name=None, services=None):
        payload = bytearray()
        if name:
            payload += bytearray((len(name) + 1, 0x09)) + name.encode('utf-8')
        if services:
            for uuid in services:
                payload += bytearray((3, 0x03, uuid & 0xFF, (uuid >> 8) & 0xFF))
        return payload

class CyclingSpeedCadenceSimulator:
    def __init__(self):
        self.ble_server = BLEServer()
        self.cumulative_wheel_revs = 0
        self.last_wheel_event_time = 0  # En 1/1024 secondes
        self.cumulative_crank_revs = 0
        self.last_crank_event_time = 0  # En 1/1024 secondes

        self.csc_measurement_handle = None
        self.csc_feature_handle = None
        self.setup_service()

    def setup_service(self):
        # Définir le service et les caractéristiques
        csc_service = (
            ubluetooth.UUID(CSC_SERVICE_UUID),
            (
                (ubluetooth.UUID(CSC_MEASUREMENT_CHAR_UUID),
                 ubluetooth.FLAG_READ | ubluetooth.FLAG_NOTIFY),
                (ubluetooth.UUID(CSC_FEATURE_CHAR_UUID),
                 ubluetooth.FLAG_READ),
            ),
        )
        handles = self.ble_server.ble.gatts_register_services([csc_service])

        # Récupérer les handles pour les caractéristiques
        self.csc_measurement_handle = handles[0][0]
        self.csc_feature_handle = handles[0][1]

        # Initialiser la caractéristique CSC Feature
        feature_value = pack("<H", FLAGS_WHEEL_REVOLUTION | FLAGS_CRANK_REVOLUTION)
        self.ble_server.ble.gatts_write(self.csc_feature_handle, feature_value)

    def update_measurement(self):
        # Simuler les données
        self.cumulative_wheel_revs = min(self.cumulative_wheel_revs + 5, 0xFFFFFFFF)  # UINT32 max
        self.last_wheel_event_time = (self.last_wheel_event_time + 1024) % 0x10000  # UINT16 max

        self.cumulative_crank_revs = min(self.cumulative_crank_revs + 2, 0xFFFFFFFF)  # UINT32 max
        self.last_crank_event_time = (self.last_crank_event_time + 512) % 0x10000  # UINT16 max

        # Vérification des types de données avant l'emballage
        print(f"flags: {FLAGS_WHEEL_REVOLUTION | FLAGS_CRANK_REVOLUTION}, "
              f"wheel_revs: {self.cumulative_wheel_revs}, wheel_time: {self.last_wheel_event_time}, "
              f"crank_revs: {self.cumulative_crank_revs}, crank_time: {self.last_crank_event_time}")
        
        # Préparer les données au format binaire
        flags = FLAGS_WHEEL_REVOLUTION | FLAGS_CRANK_REVOLUTION
        try:
            data = pack(
                "<B I H I H",  # Format pour struct.pack
                flags,  # 1 byte pour les flags
                self.cumulative_wheel_revs,  # 4 bytes pour les révolutions de roue
                self.last_wheel_event_time,  # 2 bytes pour le temps de l'événement de la roue
                self.cumulative_crank_revs,  # 4 bytes pour les révolutions de pédale
                self.last_crank_event_time   # 2 bytes pour le temps de l'événement de la pédale
            )
        except Exception as e:
            print("Error packing data:", e)
            return

        # Notifier les périphériques connectés
        for conn_handle in self.ble_server.connections:
            self.ble_server.ble.gatts_notify(conn_handle, self.csc_measurement_handle, data)

    def start(self):
        self.ble_server.advertise("ESP32_CSC")
        print("BLE Peripheral started. Advertising CSC Service.")

        try:
            while True:
                self.update_measurement()
                sleep(1)  # Mise à jour toutes les secondes
        except KeyboardInterrupt:
            self.ble_server.ble.active(False)
            print("BLE Peripheral stopped.")

if __name__ == "__main__":
    simulator = CyclingSpeedCadenceSimulator()
    simulator.start()
