# Smart Weather Station with TinyML on ESP32

This project is a connected weather station built around an ESP32 microcontroller. It reads environmental data from sensors, displays live information on an OLED screen, triggers local alerts, and sends telemetry to ThingSpeak.

It also includes a TinyML model for short-term temperature prediction, allowing the device to forecast temperature based on recent readings before the threshold is reached.

## Overview

The system combines:

- ESP32 for local processing and Wi‑Fi communication
- DHT11 sensor for temperature and humidity
- LDR sensor for light level measurement
- SSD1306 OLED display for local visualization
- TinyML inference for temperature forecasting
- ThingSpeak cloud upload for remote monitoring
- LED + buzzer for local warning alerts

## Features

- Temperature sensing with DHT11
- Humidity sensing with DHT11
- Light intensity measurement with LDR
- Real-time OLED display of sensor values
- Short-term temperature prediction using a sliding window model
- Local alert system with LED and buzzer
- ThingSpeak data upload
- Embedded TensorFlow Lite Micro inference on ESP32

## Hardware Requirements

### Components

- ESP32 development board
- DHT11 or DHT22 sensor
- LDR and resistor network
- SSD1306 OLED display (128x64, I2C)
- LED
- Buzzer
- Jumper wires
- Breadboard (optional but recommended)

### Pin mapping used in the firmware

- DHT11 -> GPIO 15
- LDR -> GPIO 34
- LED -> GPIO 2
- Buzzer -> GPIO 13
- OLED -> I2C (default address 0x3C)

## Project Structure

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

## Key Files

- `platformio.ini` – PlatformIO project configuration for ESP32
- `src/main.cpp` – main firmware for sensors, display, Wi‑Fi, alerts, and inference
- `src/train_model.py` – trains the temperature prediction model
- `src/convert_tflite.py` – converts the Keras model into TensorFlow Lite
- `src/coverttocc.py` – generates the C header file used by the firmware
- `src/fetch_thingspeak.py` – downloads historical data from ThingSpeak
- `src/model.tflite` – compiled model for embedded inference
- `src/scaler_params.npz` – normalization statistics used by the model
- `model.cc` – embedded compiled model data for Arduino/ESP32

## Software Dependencies

### Embedded firmware

- VS Code
- PlatformIO
- PlatformIO VS Code extension

### Python environment for training and conversion

- Python 3.9+
- TensorFlow
- NumPy
- Pandas
- scikit-learn

Install dependencies with:

```bash
python -m venv .venv
source .venv/bin/activate     # Linux/macOS
# or .venv\Scripts\activate  # Windows

pip install tensorflow pandas numpy scikit-learn
```

## Configuration

### Wi‑Fi and ThingSpeak credentials

Open `src/main.cpp` and update the connection values:

```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
String apiKey = "YOUR_THINGSPEAK_API_KEY";
```

You may also need to confirm the ThingSpeak endpoint:

```cpp
const char* server = "http://api.thingspeak.com/update";
```

### Alert threshold

You can change the warning threshold here:

```cpp
#define TEMP_ALERT 25.0
```

### Model normalization parameters

These values must match the model that was trained:

```cpp
const int N_STEPS = 6;
float mean_train = 23.0;
float std_train  = 2.0;
```

These values should remain consistent with the data used during training and the exported model.

## Workflow

### 1. Collect historical data

```bash
python src/fetch_thingspeak.py
```

This generates:

- `src/thingspeak_data.csv`

### 2. Train the model

```bash
python src/train_model.py
```

This generates:

- `src/model_keras.h5`
- `src/scaler_params.npz`

### 3. Convert to TensorFlow Lite

```bash
python src/convert_tflite.py
```

This creates:

- `src/model.tflite`

### 4. Generate the embedded C model file

```bash
python src/coverttocc.py
```

This creates:

- `model.cc`

This file is then included and used by the ESP32 firmware.

## Build and Upload

### Compile the project

```bash
pio run
```

### Upload to the ESP32

```bash
pio run --target upload
```

### Open serial monitor

```bash
pio device monitor
```

## Usage

After powering on the ESP32:

1. It connects to Wi‑Fi
2. It initializes the OLED display
3. It reads temperature, humidity, and light intensity
4. It pushes the latest values into a sliding prediction window
5. It runs TinyML inference to estimate near-future temperature
6. It triggers the LED and buzzer if the measured or predicted temperature exceeds the defined threshold
7. It sends the collected data to ThingSpeak

## Example OLED output

```text
Station Weather Int.
Temp: 24.8 C
Hum:  45.0 %
Lumi: 78 %
```

If a prediction is available:

```text
Pred T+: 26.5 C
```

## Notes

- The project is designed as a prototype and learning tool.
- The Wi‑Fi SSID/password and ThingSpeak API key should not be committed to a public repository.
- Model compatibility and normalization parameters must stay aligned between training and inference.

## Possible Improvements

- Improve sensor calibration
- Replace DHT11 with DHT22 for better precision
- Add multiple weather features to the model
- Add local storage when the network is unavailable
- Add an online dashboard for visualization
- Trigger email or SMS notifications when alert conditions are met

## License

This project is provided for educational and experimental use. Please respect the licenses of the third-party libraries used in this project.

## References

- PlatformIO: https://platformio.org/
- ESP32 Arduino Core: https://github.com/espressif/arduino-esp32
- TensorFlow Lite Micro: https://www.tensorflow.org/lite/microcontrollers
- ThingSpeak: https://thingspeak.com/
- Adafruit SSD1306: https://github.com/adafruit/Adafruit_SSD1306
- Adafruit DHT: https://github.com/adafruit/Adafruit_Python_DHT
