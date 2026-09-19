# Station Météo TinyML - ESP32 + TensorFlow Lite Micro

Projet de station météo connectée basée sur une carte ESP32, des capteurs environnementaux, un affichage OLED et un modèle TinyML pour prédire une augmentation de température à court terme.

Le système lit des données de température, d’humidité et de luminosité, affiche les informations localement sur un écran OLED, active une alerte visuelle/sonore si les seuils sont dépassés, et envoie les mesures vers ThingSpeak.

## 1. Vue d’ensemble

Ce projet combine :

- un ESP32 pour la collecte et le traitement local,
- un capteur DHT11 pour température et humidité,
- une photo-résistance (LDR) pour mesurer la luminosité,
- un écran OLED SSD1306 pour afficher les données,
- un modèle de machine learning TinyML pour prévoir la température future,
- une connexion Wi‑Fi pour envoyer les données vers ThingSpeak.

L’objectif principal est de surveiller l’environnement et d’alerter lorsque la température mesurée ou prédite dépasse un seuil défini.

---

## 2. Fonctionnalités

- Mesure de température via DHT11
- Mesure d’humidité via DHT11
- Mesure de luminosité via LDR
- Affichage sur OLED : température, humidité, luminosité, prédiction
- Alerte locale avec LED et buzzer
- Envoi des données vers ThingSpeak
- Prédiction de température future à partir d’une fenêtre de valeurs glissantes
- Modèle TensorFlow Lite Micro embarqué dans l’ESP32

---

## 3. Matériel requis

### Composants

- ESP32 DevKit (ou carte compatible ESP32)
- DHT11 ou DHT22
- LDR / résistance selon montage
- Écran OLED SSD1306 128x64 I2C
- LED 2 ou 3 broches
- Buzzer actif/passif
- Fils de connexion
- Résistances et breadboard si nécessaire

### Broches utilisées dans le code

- DHT11 -> GPIO 15
- LDR -> GPIO 34 (analogique)
- LED -> GPIO 2
- Buzzer -> GPIO 13
- OLED -> I2C (adresse 0x3C)

> Le montage exact dépend de votre câblage. Vérifiez les broches sur votre carte avant de flasher.

---

## 4. Structure du projet

```text
station_m-t-o/
├─ .gitignore
├─ README.md
├─ platformio.ini
├─ model.cc
├─ include/
│  └─ README
├─ lib/
│  └─ README
├─ src/
│  ├─ main.cpp
│  ├─ train_model.py
│  ├─ convert_tflite.py
│  ├─ coverttocc.py
│  ├─ fetch_thingspeak.py
│  ├─ model_keras.h5
│  ├─ model.tflite
│  ├─ scaler_params.npz
│  ├─ thingspeak_data.csv
│  └─ c_cpp_properties.json
├─ test/
│  └─ README
└─ .vscode/
```

### Description des fichiers importants

- `platformio.ini` : configuration du projet PlatformIO pour ESP32
- `src/main.cpp` : firmware principal (capteurs, OLED, Wi‑Fi, ThingSpeak, inference TinyML)
- `src/train_model.py` : entraînement du modèle à partir d’un historique de température
- `src/convert_tflite.py` : conversion du modèle Keras vers TensorFlow Lite
- `src/coverttocc.py` : génération du fichier `model.cc` contenant le binaire TFLite
- `src/fetch_thingspeak.py` : récupération des données depuis ThingSpeak
- `src/model.tflite` : modèle TinyML compilé
- `src/scaler_params.npz` : paramètres de normalisation utilisés pendant l’inférence
- `model.cc` : fichier chargé par le firmware pour embarquer le modèle

---

## 5. Dépendances logicielles

### Pour le firmware ESP32

- VS Code
- PlatformIO
- Extension PlatformIO pour VS Code

### Pour l’entraînement du modèle

Le script Python requiert généralement :

- Python 3.9+
- TensorFlow
- NumPy
- Pandas
- scikit-learn

Exemple d’installation :

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# ou .venv\Scripts\activate  # Windows

pip install tensorflow pandas numpy scikit-learn
```

> Selon votre environnement, la version de TensorFlow peut varier en fonction de votre carte et de votre système d’exploitation.

---

## 6. Configuration avant utilisation

### 6.1 Paramètres Wi‑Fi et ThingSpeak

Ouvrez le fichier :

- `src/main.cpp`

Modifiez ces valeurs :

```cpp
const char* ssid = "VOTRE_WIFI";
const char* password = "VOTRE_MOT_DE_PASSE";
String apiKey = "VOTRE_API_KEY_THINGSPEAK";
```

Il faut aussi configurer le serveur ThingSpeak s’il est utilisé exactement comme prévu :

```cpp
const char* server = "http://api.thingspeak.com/update";
```

### 6.2 Seuil d’alerte

Vous pouvez modifier le seuil de température :

```cpp
#define TEMP_ALERT 25.0
```

### 6.3 Paramètres de normalisation du modèle

Dans le firmware, on trouve :

```cpp
const int N_STEPS = 6;
float mean_train = 23.0;
float std_train  = 2.0;
```

Ces valeurs doivent correspondre à celles utilisées lors de l’entraînement du modèle. Elles sont stockées dans `scaler_params.npz` et doivent être cohérentes avec le modèle exporté pour éviter des prédictions inutiles ou fausses.

---

## 7. Flux de travail complet

### Étape 1 : Collecter des données

Utilisez le script :

```bash
python src/fetch_thingspeak.py
```

Ce script télécharge les données depuis ThingSpeak et sauvegarde un fichier :

- `src/thingspeak_data.csv`

### Étape 2 : Entraîner le modèle

```bash
python src/train_model.py
```

Cette étape génère :

- `src/model_keras.h5`
- `src/scaler_params.npz`

### Étape 3 : Convertir en TensorFlow Lite

```bash
python src/convert_tflite.py
```

Le modèle Keras est converti vers :

- `src/model.tflite`

### Étape 4 : Générer le fichier C embarqué

```bash
python src/coverttocc.py
```

Ce script produit :

- `model.cc`

Ce fichier est ensuite utilisé par le firmware Arduino/ESP32.

> Dans le dépôt, un `model.cc` est déjà présent, mais il doit être régénéré si le modèle change.

---

## 8. Compilation et flash du firmware

### Ouvrir le projet

Dans VS Code :

1. Ouvrez le dossier du projet
2. Installez l’extension PlatformIO
3. Vérifiez que `platformio.ini` est bien détecté

### Compiler

```bash
pio run
```

### Flasher sur la carte

```bash
pio run --target upload
```

### Ouvrir le moniteur série

```bash
pio device monitor
```

---

## 9. Déploiement et utilisation

Après le démarrage de l’ESP32 :

1. La carte se connecte au Wi‑Fi
2. L’écran OLED affiche le statut de démarrage
3. Les capteurs sont lus périodiquement
4. La température, l’humidité et la luminosité sont affichées
5. Une fenêtre glissante de valeurs est alimentée
6. Le modèle TinyML tente une prédiction de température future
7. Si la température mesurée ou prédite dépasse le seuil, la LED et le buzzer s’activent
8. Les données sont envoyées vers ThingSpeak toutes les quelques secondes ou selon le réglage du code

---

## 10. Exemple de fonctionnement

Affichage OLED attendu :

```text
Station Meteo Int.
Temp: 24.8 C
Hum:  45.0 %
Lumi: 78 %
```

Et si la prédiction est disponible :

```text
Pred T+: 26.5 C
```

---

## 11. Points importants à vérifier

### 11.1 Compatibilité du modèle

Le code C++ attend :

- un modèle compatible avec TensorFlow Lite Micro,
- une taille de mémoire suffisante dans le tensor arena,
- un format de données cohérent avec les paramètres de normalisation.

Si l’inférence ne fonctionne pas, vérifiez :

- présence de `model.cc`
- taille de `tensor_arena`
- cohérence entre `N_STEPS`, `mean_train`, `std_train`
- version du modèle et des opérations supportées

### 11.2 Problèmes fréquents

#### Le modèle ne charge pas

Vérifiez :

- `model.cc` est bien généré
- le fichier n’est pas vide
- le modèle TFLite est compatible avec l’ESP32

#### Les prédictions sont incohérentes

Vérifiez :

- `N_STEPS` dans le modèle et dans le firmware
- `mean_train` / `std_train`
- le script d’entraînement et les données de température

#### L’ESP32 ne se connecte pas au Wi‑Fi

Vérifiez :

- SSID et mot de passe
- qualité du signal
- présence du mode 2.4 GHz si votre routeur est en double bande

---

## 12. Sécurité et bonnes pratiques

- Ne laissez pas vos identifiants Wi‑Fi ou votre clé API ThingSpeak dans le dépôt public.
- Préférez les variables d’environnement ou un fichier de configuration local non versionné.
- Ne publiez pas les fichiers contenant des secrets dans GitHub.

---

## 13. Possibles améliorations

- Ajouter une logique de calibration automatique des capteurs
- Utiliser un DHT22 plus précis
- Ajouter des seuils différents selon les heures de journée
- Envoyer des alertes SMS/Email quand le seuil est dépassé
- Ajouter un stockage local des données si le réseau est indisponible
- Ajouter un dashboard web ou visualisation graphique
- Passer à un modèle plus robuste avec plusieurs variables d’entrée

---

## 14. Licence

Ce projet est fourni à titre éducatif et de démonstration. Si vous le réutilisez, ajoutez la mention de l’auteur original et respectez les licences des bibliothèques tierces utilisées.

---

## 15. Conclusion

Ce projet illustre un cas réel d’intégration de capteurs embarqués, de cloud IoT et de TinyML sur microcontrôleur. Il est idéal pour apprendre :

- la programmation ESP32,
- la collecte de données environnementales,
- la communication Wi‑Fi,
- le stockage cloud avec ThingSpeak,
- le développement et l’intégration d’un modèle de prédiction embarqué.

---

## 16. Références utiles

- PlatformIO : https://platformio.org/
- ESP32 Arduino Core : https://github.com/espressif/arduino-esp32
- TensorFlow Lite Micro : https://www.tensorflow.org/lite/microcontrollers
- ThingSpeak : https://thingspeak.com/
- Adafruit SSD1306 : https://github.com/adafruit/Adafruit_SSD1306
- Adafruit DHT : https://github.com/adafruit/Adafruit_Python_DHT

Si vous voulez, je peux aussi vous préparer :

- une version du README en anglais,
- une version plus professionnelle pour GitHub,
- un README avec schéma de câblage et captures d’écran,
- ou une version plus courte et plus élégante pour un portfolio.
