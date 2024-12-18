# Programmes

Le programme **`main.py`** (MicroPython) sur l'ESP32 rassemble toutes les fonctions des capteurs (HX711 et MPU6500) et utilise ensuite le module **`com.py`** pour envoyer les données au Garmin via BLE.

Le programme **`FakeBikePowerMeter.ino`** fait la même chose, mais en C++ pour Arduino.

---

# Recherche

## UUIDs utilisés pour la communication BLE (protocol BLE / Assigned_Numbers.pdf)

- **Cycling Power Service UUID** :  
  `CYCLING_POWER_SERVICE_UUID = bluetooth.UUID(0x1818)`  
  UUID du service de puissance cycliste : `'00001818-0000-1000-8000-00805f9b34fb'`

- **Power Measurement Characteristic UUID** :  
  `POWER_MEASUREMENT_CHAR_UUID = bluetooth.UUID(0x2A63)`  
  UUID de la mesure de puissance : `'00002a63-0000-1000-8000-00805f9b34fb'`

- **Cycling Power Feature Characteristic UUID** :  
  `CYCLING_POWER_FEATURE_CHAR_UUID = bluetooth.UUID(0x2A65)`

- **Sensor Location Characteristic UUID** :  
  `SENSOR_LOCATION_CHAR_UUID = bluetooth.UUID(0x2A5D)`

### Drapeaux pour les données de mesure

- **Instantaneous Power Flag** :  
  `FLAGS_INSTANTANEOUS_POWER = 0x02`  
  Indique une mesure de puissance instantanée : `'00000010'`

---

# Bibliothèques utilisées

- **`asyncio`** :  
  Permet de gérer plusieurs tâches simultanément sans bloquer le programme principal, essentiel pour le capteur HX711.

- **`aioble`** :  
  Permet la gestion des communications Bluetooth Low Energy (BLE), pour établir des connexions BLE et échanger des données.

- **`bluetooth`** :  
  Fournit des outils pour travailler avec Bluetooth Classic et Bluetooth Low Energy (BLE), notamment pour la gestion des UUIDs.

- **`struct`** :  
  Permet de travailler avec des données binaires, essentiel pour envoyer et recevoir des informations via BLE dans un format binaire.

---

# Envoi des données

### Envoi de la puissance

Pour envoyer uniquement la puissance, on doit utiliser la fonction **`pack`** de la bibliothèque **`struct`** pour empaqueter les données en binaire dans l'ordre **little-endian** (**`<`**), comme suit :
```python
power_data = struct.pack("<Hh", flags, power)  # empaquetage de la puissance

