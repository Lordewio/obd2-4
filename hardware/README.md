# OBD2 IoT Device Firmware

This directory contains the firmware for the ESP32 + SIM7600 OBD2 device.

## Hardware Components

- ESP32 Development Board
- SIM7600 Cellular Module
- OBD2 Connector
- Power Supply Circuit
- External Antenna

## Setup Requirements

1. Install ESP-IDF (Espressif IoT Development Framework)
2. Arduino IDE with ESP32 support
3. PlatformIO (recommended)
4. USB to Serial Converter

## Project Structure

```
hardware/
├── src/              # Source code
├── include/          # Header files
├── lib/              # External libraries
├── components/       # ESP-IDF components
└── docs/            # Documentation
```

## Getting Started

1. Clone the repository
2. Set up your development environment:
   ```bash
   # Install ESP-IDF
   git clone --recursive https://github.com/espressif/esp-idf.git
   cd esp-idf
   ./install.sh
   . ./export.sh
   ```
3. Build and flash the firmware:
   ```bash
   cd hardware
   idf.py build
   idf.py -p <PORT> flash
   ```

## Hardware Connections

- ESP32 TX -> SIM7600 RX
- ESP32 RX -> SIM7600 TX
- ESP32 GPIO -> OBD2 Pins
- External Power Supply -> VIN

## Features

- Cellular connectivity via SIM7600
- OBD2 protocol parsing
- Real-time data transmission
- Power management
- Error handling and recovery
