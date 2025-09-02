# Fonctionnement et Programmes

the workintg code is com.py in the /com folder

Le programme **`main.py`** ([lien vers le projet sur Wokwi](https://wokwi.com/projects/417291363808846849)) utilise MicroPython sur l'ESP32 pour gérer les capteurs HX711 (poids) et MPU6500 (accéléromètre et gyroscope). Il utilise ensuite le module **`com.py`** pour envoyer les données de puissance au Garmin via Bluetooth Low Energy (BLE).

Le programme **`FakeBikePowerMeter.ino`** ([lien vers le projet github](https://github.com/JohanWieslander/ESP32-Bike-Powermeter/blob/master/FakeBikePowerMeter.ino)) implémente la même fonctionnalité en C++ pour Arduino.

---

## Problème rencontré :(

Le Garmin réussit à détecter l'ESP32 avec **`com.py`**, mais il rencontre des difficultés pour établir une connexion stable et encore plus pour recevoir les données. Au départ, j'avais écrit un programme **`Cadence and Speed.py`** dans lequel le Garmin parvenait à se connecter, mais ne recevait pas de données.

---

## Objectif

Faire fonctionner le programme afin d'envoyer les données de puissance (et éventuellement de cadence) de **`main.py`** vers le compteur Garmin.

---

## Recherche

### UUIDs utilisés pour la communication BLE (selon le protocole BLE / **Assigned_Numbers.pdf**)

Voici les UUIDs associés aux services et caractéristiques utilisés pour la communication avec le Garmin :

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
  Ce drapeau indique qu'il s'agit d'une mesure de puissance instantanée : `'00000010'`

---

## Bibliothèques Python utilisées

- **`asyncio`** :  
  Permet de gérer plusieurs tâches simultanément sans bloquer le programme principal, essentiel pour la gestion des capteurs comme HX711.

- **`aioble`** :  
  Gère les communications Bluetooth Low Energy (BLE) et permet de créer des connexions BLE ainsi que d'envoyer et recevoir des données.

- **`bluetooth`** :  
  Fournit des outils pour travailler avec Bluetooth Classic et Bluetooth Low Energy (BLE), notamment pour la gestion des UUIDs.

- **`struct`** :  
  Permet de travailler avec des données binaires, ce qui est essentiel pour envoyer et recevoir des informations dans un format binaire via BLE.

---

## Envoi des données (selon le protocole BLE / **CPS_v1.1.pdf**)

### Envoi de la puissance

Pour envoyer uniquement la puissance, il faut utiliser la fonction **`pack`** de la bibliothèque **`struct`** afin d'empaqueter les données en binaire, dans l'ordre **little-endian** (**`<`**), comme suit :
```python

power_data = struct.pack("<HH", flags, power)  # empaquetage de la puissance
```
Pour envoyer la puissance et cadence :
```python
data = struct.pack('<HHIH', flags, instant_power, crank_revs, last_event_time)

