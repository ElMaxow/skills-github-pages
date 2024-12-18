# Fonctionnement  & Programmes

Le programme **`main.py`** **`https://wokwi.com/projects/417291363808846849`** (MicroPython) sur l'ESP32 rassemble toutes les fonctions des capteurs (HX711 et MPU6500) et utilise ensuite le module **`com.py`** pour envoyer les données au Garmin via BLE.

Le programme **`FakeBikePowerMeter.ino`** fait la même chose, mais en C++ pour Arduino.

---
# Problème :(
Le garmin réuissi à détecter le ESP32 avec **`com.py`**, mais ensuite il n'arrive pas vraiment à se connecter :( et enncore moins recevoir des données. Au début, j'ai écrit un programme **`Cadence and speed.py`** dans lequel le Garmin réussi à se connecter, mais pas recevoir de données.
# But
Faire marcher le programme pour envoyer les données de puissance (& si possible cadence) de **`main.py`**  vers le compteur Grmin
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

# Bibliothèques python utilisées

- **`asyncio`** :  
  Permet de gérer plusieurs tâches simultanément sans bloquer le programme principal, essentiel pour le capteur HX711.

- **`aioble`** :  
  Permet la gestion des communications Bluetooth Low Energy (BLE), pour établir des connexions BLE et échanger des données.

- **`bluetooth`** :  
  Fournit des outils pour travailler avec Bluetooth Classic et Bluetooth Low Energy (BLE), notamment pour la gestion des UUIDs.

- **`struct`** :  
  Permet de travailler avec des données binaires, essentiel pour envoyer et recevoir des informations via BLE dans un format binaire.

---

# Envoi des données (protocol BLE / CPS_v1.1.pdf)

### Envoi de la puissance

Pour envoyer uniquement la puissance, on doit utiliser la fonction **`pack`** de la bibliothèque **`struct`** pour empaqueter les données en binaire dans l'ordre **little-endian** (**`<`**), comme suit :
```python
power_data = struct.pack("<Hh", flags, power)  # empaquetage de la puissance
```
Pour envoyer la puissance et cadence :
```python
data = struct.pack('<HHHH', flags, instant_power, crank_revs, last_event_time)

