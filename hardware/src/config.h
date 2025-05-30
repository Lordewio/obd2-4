#ifndef CONFIG_H
#define CONFIG_H

// Network Configuration
#define WIFI_SSID "your_wifi_ssid"  // Fallback WiFi SSID
#define WIFI_PASSWORD "your_wifi_password"  // Fallback WiFi Password

// GSM Configuration
#define GSM_APN "internet"  // Your GSM APN
#define GSM_USER ""  // GSM Username (if required)
#define GSM_PASS ""  // GSM Password (if required)

// Cloud API Configuration
#define API_URL "https://api.yourdomain.com/api/diagnostics"
#define API_KEY "your_api_key_here"

// Vehicle Configuration
#define VEHICLE_ID ""  // Will be set during setup

// GPS Configuration
#define GPS_BAUD 9600

// SD Card Configuration
#define SD_CS 5  // Chip Select pin for SD card
#define SD_MOSI 23  // MOSI pin for SD card
#define SD_MISO 19  // MISO pin for SD card
#define SD_SCK 18  // SCK pin for SD card

// Bluetooth Configuration
#define BLUETOOTH_NAME "OBD2_Device"
#define BLUETOOTH_PIN "1234"  // Default pin for ELM327 pairing

// OBD2 Configuration
#define OBD2_BAUD 38400  // Default baud rate for ELM327

// Data Collection Interval
#define DATA_INTERVAL 1000  // 1 second between readings

// Offline Storage Configuration
#define MAX_OFFLINE_RECORDS 100  // Maximum number of records to store offline
#define OFFLINE_FILE "offline_data.txt"  // File name for offline storage

// Error Handling
#define ERROR_BUFFER_SIZE 100  // Size of error message buffer

#endif // CONFIG_H
