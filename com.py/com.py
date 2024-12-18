from micropython import const
import asyncio
import aioble
import bluetooth
import struct
from machine import Pin
from random import randint

# UUIDs pour la communication BLE
CSC_SERVICE_UUID = 0x1818  # UUID du Cycling Power Service
CSC_MEASUREMENT_CHAR_UUID = 0x2A63  # UUID de la mesure de puissance

# Drapeaux pour les données
FLAGS_INSTANTANEOUS_POWER = 0x02  # Indique une mesure de puissance instantanée

# Simule la lecture des données de puissance
def get_power_data():
    # Génère une puissance aléatoire entre 100W et 400W
    power = randint(100, 400)
    # Structure des données : [Flags (2 octets), Instantaneous Power (2 octets)]
    return struct.pack("<Hh", FLAGS_INSTANTANEOUS_POWER, power)

# Tâche pour mettre à jour périodiquement les données de puissance
async def power_data_task(power_characteristic):
    while True:
        try:
            power_data = get_power_data()
            # Écriture des données dans la caractéristique
            power_characteristic.write(power_data, send_update=True)
            power = struct.unpack("<Hh", power_data)[1]  # Extraire la puissance
            print(f"Puissance envoyée : {power} W")
            await asyncio.sleep(1)  # Envoi toutes les secondes
        except Exception as e:
            print("Erreur lors de l'envoi des données de puissance :", e)
            break

# Fonction principale pour configurer le périphérique BLE
async def main():
    print("Initialisation du périphérique BLE...")

    # Enregistrer le service et la caractéristique
    power_service = aioble.Service(bluetooth.UUID(CSC_SERVICE_UUID))
    power_characteristic = aioble.Characteristic(
        power_service, bluetooth.UUID(CSC_MEASUREMENT_CHAR_UUID), read=True, notify=True
    )
    aioble.register_services(power_service)

    print("Démarrage de la publicité BLE...")
    print("En attente de connexion...")
    connection = await aioble.advertise(250_000, name="ESP32-Power", services=[bluetooth.UUID(CSC_SERVICE_UUID)],)
    print("Connexion établie avec", connection.device)

    # Démarrer la publicité BLE
    while connection.is_connected():
        try:   
            # Démarrer la tâche d'envoi de puissance
            await power_data_task(power_characteristic)
            print("Déconnexion du périphérique.")
        except Exception as e:
            print("Erreur lors de la publicité ou de la connexion :", e)

# Exécution de la boucle principale
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Programme interrompu.")
