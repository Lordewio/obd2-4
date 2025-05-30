#include <Arduino.h>
#include <BluetoothSerial.h>
#include <TinyGSM.h>
#include <SD.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include "obd2_parser.h"
#include "gps_handler.h"

// Error handling
#define ERROR_BUFFER_SIZE 100
#define MAX_RETRIES 3
#define RETRY_DELAY 1000

// State management
enum DeviceState {
    STATE_INIT,
    STATE_CONNECTING_BT,
    STATE_CONNECTING_GSM,
    STATE_READING_OBD,
    STATE_SENDING_DATA,
    STATE_ERROR
};

DeviceState currentState = STATE_INIT;
unsigned long lastErrorTime = 0;
unsigned long errorTimeout = 30000; // 30 seconds
OBD2Parser obd2Parser;
GPSHandler gpsHandler;

// Bluetooth Serial for ELM327
BluetoothSerial SerialBT;

// GSM Module Settings
#define PIN_SERIAL Serial1
#define TINY_GSM_MODEM_SIM7600
#define GSM_BAUD 115200

// SD Card Settings
#define SD_CS 5

// Cloud API Settings
const char* API_URL = "https://api.yourdomain.com/api/diagnostics";
const char* API_KEY = "your_api_key_here";

// Vehicle ID (configured during setup)
String vehicle_id = "";

// Buffer for storing offline data
const int MAX_OFFLINE_RECORDS = 100;
struct DiagnosticData {
    String timestamp;
    String rpm;
    String speed;
    String engine_load;
    String coolant_temp;
    String intake_temp;
    String throttle_pos;
    String fuel_level;
    String has_mil;
    String dtc_code;
    String dtc_description;
    String latitude;
    String longitude;
};

DiagnosticData offline_data[MAX_OFFLINE_RECORDS];
int offline_count = 0;

// GSM Client
TinyGSMClient client(PIN_SERIAL, GSM_BAUD);

void setup() {
    Serial.begin(115200);
    Serial.println("Starting OBD2 IoT Device...");
    currentState = STATE_INIT;
    
    // Initialize GPS
    if (!gpsHandler.begin()) {
        Serial.println("Failed to initialize GPS");
    }
    
    // Initialize all components
    initializeComponents();
}

void loop() {
    switch (currentState) {
        case STATE_INIT:
            currentState = STATE_CONNECTING_BT;
            break;
        
        case STATE_CONNECTING_BT:
            if (connectBluetooth()) {
                currentState = STATE_CONNECTING_GSM;
            }
            break;
        
        case STATE_CONNECTING_GSM:
            if (connectGSM()) {
                currentState = STATE_READING_OBD;
            }
            break;
        
        case STATE_READING_OBD:
            if (readAndProcessData()) {
                currentState = STATE_SENDING_DATA;
            }
            break;
        
        case STATE_SENDING_DATA:
            if (!sendData()) {
                currentState = STATE_ERROR;
            }
            break;
        
        case STATE_ERROR:
            handleErrors();
            break;
    }
    
    delay(100);
}

bool connectBluetooth() {
    Serial.println("Connecting to ELM327...");
    int retries = 0;
    
    while (retries < MAX_RETRIES) {
        SerialBT.println("ATZ");
        delay(1000);
        
        String response = SerialBT.readStringUntil('\n');
        if (response.indexOf("OK") != -1) {
            Serial.println("ELM327 Connected");
            return true;
        }
        
        retries++;
        delay(RETRY_DELAY);
    }
    
    Serial.println("Failed to connect to ELM327");
    return false;
}

bool connectGSM() {
    Serial.println("Connecting to GSM network...");
    int retries = 0;
    
    while (retries < MAX_RETRIES) {
        if (client.connect()) {
            Serial.println("GSM Connected");
            return true;
        }
        
        retries++;
        delay(RETRY_DELAY);
    }
    
    Serial.println("Failed to connect to GSM");
    return false;
}

bool readAndProcessData() {
    Serial.println("Reading diagnostic data...");
    String response = "";
    
    // Send initialization commands
    if (!sendOBDCommand("ATZ")) return false;
    if (!sendOBDCommand("ATSP0")) return false;
    
    // Read various OBD2 PIDs
    if (!sendOBDCommand("01 0C")) return false; // RPM
    if (!sendOBDCommand("01 0D")) return false; // Speed
    if (!sendOBDCommand("01 04")) return false; // Engine Load
    if (!sendOBDCommand("01 05")) return false; // Coolant Temp
    if (!sendOBDCommand("01 0F")) return false; // Intake Temp
    if (!sendOBDCommand("01 11")) return false; // Throttle Pos
    if (!sendOBDCommand("01 2F")) return false; // Fuel Level
    if (!sendOBDCommand("01 01")) return false; // MIL
    if (!sendOBDCommand("03")) return false; // DTC
    
    return true;
}

bool sendOBDCommand(String command) {
    SerialBT.println(command);
    delay(500);
    String response = SerialBT.readStringUntil('\n');
    
    if (response.indexOf("NO DATA") != -1 || response.indexOf("UNABLE") != -1) {
        return false;
    }
    
    return true;
}

bool updateGPSLocation() {
    GPSData* gpsData = gpsHandler.update();
    
    if (gpsData->isValid) {
        // Update geofence checks
        checkGeofences(gpsData->latitude, gpsData->longitude);
        return true;
    }
    return false;
}

bool sendData() {
    // Get all OBD2 data
    String rpm = sendOBDCommand("01 0C");
    String speed = sendOBDCommand("01 0D");
    String engine_load = sendOBDCommand("01 04");
    String coolant_temp = sendOBDCommand("01 05");
    String oil_temp = sendOBDCommand("41 5C");
    String runtime = sendOBDCommand("41 1F");
    String intake_temp = sendOBDCommand("01 0F");
    String throttle_pos = sendOBDCommand("01 11");
    String throttle_pos_b = sendOBDCommand("01 13");
    String intake_pressure = sendOBDCommand("01 0B");
    String fuel_level = sendOBDCommand("01 2F");
    String fuel_pressure = sendOBDCommand("01 0A");
    String fuel_rate = sendOBDCommand("41 5E");
    String exhaust_temp = sendOBDCommand("41 5E");
    String oxygen1 = sendOBDCommand("01 14");
    String oxygen2 = sendOBDCommand("01 15");
    String gear = sendOBDCommand("41 5A");
    String trans_temp = sendOBDCommand("41 5B");
    String battery = sendOBDCommand("41 23");
    String brake = sendOBDCommand("41 40");
    String vin = sendOBDCommand("09 02");
    String mil = sendOBDCommand("01 01");
    String dtc = sendOBDCommand("03");

    // Parse the data
    DiagnosticData data;
    data.timestamp = String(millis());
    data.rpm = String(obd2Parser.parseRPM(rpm));
    data.speed = String(obd2Parser.parseVehicleSpeed(speed));
    data.engine_load = String(obd2Parser.parseEngineLoad(engine_load));
    data.coolant_temp = String(obd2Parser.parseEngineCoolantTemp(coolant_temp));
    data.oil_temp = String(obd2Parser.parseEngineOilTemp(oil_temp));
    data.runtime = String(obd2Parser.parseEngineRuntime(runtime));
    data.intake_temp = String(obd2Parser.parseIntakeTemp(intake_temp));
    data.throttle_pos = String(obd2Parser.parseThrottlePos(throttle_pos));
    data.throttle_pos_b = String(obd2Parser.parseThrottlePosB(throttle_pos_b));
    data.intake_pressure = String(obd2Parser.parseIntakePressure(intake_pressure));
    data.fuel_level = String(obd2Parser.parseFuelLevel(fuel_level));
    data.fuel_pressure = String(obd2Parser.parseFuelPressure(fuel_pressure));
    data.fuel_rate = String(obd2Parser.parseFuelRate(fuel_rate));
    data.exhaust_temp = String(obd2Parser.parseExhaustTemp(exhaust_temp));
    data.oxygen_sensor_1 = String(obd2Parser.parseOxygenSensor1(oxygen1));
    data.oxygen_sensor_2 = String(obd2Parser.parseOxygenSensor2(oxygen2));
    data.gear = String(obd2Parser.parseTransmissionGear(gear));
    data.transmission_temp = String(obd2Parser.parseTransmissionTemp(trans_temp));
    data.battery_voltage = String(obd2Parser.parseBatteryVoltage(battery));
    data.brake_switch = String(obd2Parser.parseBrakeSwitch(brake));
    data.vin = obd2Parser.parseVIN(vin);
    data.has_mil = String(obd2Parser.parseMILStatus(mil));
    data.dtc_code = obd2Parser.parseDTC(dtc);
    data.dtc_description = getDTCDescription(data.dtc_code);
    
    // Get GPS location
    GPSData* gpsData = gpsHandler.update();
    if (gpsData->isValid) {
        data.latitude = String(gpsData->latitude, 6);
        data.longitude = String(gpsData->longitude, 6);
        data.altitude = String(gpsData->altitude, 1);
        data.gps_speed = String(gpsData->speed, 1);
        data.satellites = String(gpsData->satellites);
    } else {
        data.latitude = "0";
        data.longitude = "0";
        data.altitude = "0";
        data.gps_speed = "0";
        data.satellites = "0";
    }
    
    // Send to cloud
    if (sendToCloud(data)) {
        return true;
    }
    
    // Store offline if cloud failed
    storeOfflineData(data);
    return false;
}

void checkGeofences(double latitude, double longitude) {
    // Read geofences from SD card
    File geofenceFile = SD.open("geofences.txt");
    if (!geofenceFile) {
        Serial.println("Failed to open geofences file");
        return;
    }
    
    while (geofenceFile.available()) {
        String line = geofenceFile.readStringUntil('\n');
        if (line.length() > 0) {
            // Parse geofence data
            String id = line.substring(0, line.indexOf(','));
            line.remove(0, id.length() + 1);
            
            String name = line.substring(0, line.indexOf(','));
            line.remove(0, name.length() + 1);
            
            double geofence_lat = line.substring(0, line.indexOf(',')).toDouble();
            line.remove(0, line.indexOf(',') + 1);
            
            double geofence_lon = line.substring(0, line.indexOf(',')).toDouble();
            line.remove(0, line.indexOf(',') + 1);
            
            double radius = line.substring(0, line.indexOf(',')).toDouble();
            line.remove(0, line.indexOf(',') + 1);
            
            // Calculate distance
            double distance = calculateDistance(latitude, longitude, geofence_lat, geofence_lon);
            
            // Check if vehicle is outside geofence
            if (distance > radius) {
                // Create alert
                File alertFile = SD.open("alerts.txt", FILE_APPEND);
                if (alertFile) {
                    alertFile.println(String(millis()) + "," +
                                    id + "," +
                                    name + "," +
                                    String(latitude) + "," +
                                    String(longitude) + "," +
                                    String(distance));
                    alertFile.close();
                }
            }
        }
    }
    geofenceFile.close();
}

// Haversine formula for distance calculation
double calculateDistance(double lat1, double lon1, double lat2, double lon2) {
    const double R = 6371000; // Earth radius in meters
    double dLat = (lat2 - lat1) * M_PI / 180.0;
    double dLon = (lon2 - lon1) * M_PI / 180.0;
    
    double a = sin(dLat/2) * sin(dLat/2) +
               cos(lat1 * M_PI / 180.0) * cos(lat2 * M_PI / 180.0) *
               sin(dLon/2) * sin(dLon/2);
    
    double c = 2 * atan2(sqrt(a), sqrt(1-a));
    return R * c;
}

void handleErrors() {
    unsigned long currentTime = millis();
    
    if (currentTime - lastErrorTime >= errorTimeout) {
        // Reset state machine
        currentState = STATE_INIT;
        lastErrorTime = currentTime;
        
        // Log error
        File errorFile = SD.open("errors.txt", FILE_APPEND);
        if (errorFile) {
            errorFile.println(String(currentTime) + ": System reset due to errors");
            errorFile.close();
        }
        
        // Reset GPS
        gpsHandler.reset();
        gpsHandler.begin();
    }
} {
    String response = "";
    
    // Send OBD2 commands to ELM327
    SerialBT.println("ATZ"); // Reset ELM327
    delay(1000);
    
    SerialBT.println("ATSP0"); // Set protocol to auto
    delay(500);
    
    // Read RPM
    SerialBT.println("01 0C");
    delay(500);
    response += SerialBT.readStringUntil('\n');
    
    // Read Vehicle Speed
    SerialBT.println("01 0D");
    delay(500);
    response += SerialBT.readStringUntil('\n');
    
    // Read Engine Load
    SerialBT.println("01 04");
    delay(500);
    response += SerialBT.readStringUntil('\n');
    
    // Read Coolant Temperature
    SerialBT.println("01 05");
    delay(500);
    response += SerialBT.readStringUntil('\n');
    
    // Read Intake Temperature
    SerialBT.println("01 0F");
    delay(500);
    response += SerialBT.readStringUntil('\n');
    
    // Read Throttle Position
    SerialBT.println("01 11");
    delay(500);
    response += SerialBT.readStringUntil('\n');
    
    // Read Fuel Level
    SerialBT.println("01 2F");
    delay(500);
    response += SerialBT.readStringUntil('\n');
    
    // Check for MIL
    SerialBT.println("01 01");
    delay(500);
    response += SerialBT.readStringUntil('\n');
    
    // Read DTC codes
    SerialBT.println("03");
    delay(500);
    response += SerialBT.readStringUntil('\n');
    
    return response;
}

DiagnosticData parseDiagnosticData(String data) {
    DiagnosticData parsedData;
    parsedData.timestamp = String(millis());
    
    // TODO: Implement parsing logic for each OBD2 PID
    // This is a placeholder - actual parsing will depend on your ELM327 response format
    
    return parsedData;
}

bool sendToCloud(DiagnosticData data) {
    // Check GSM connection
    if (!client.connect()) {
        return false;
    }

    // Prepare JSON payload
    String json = "{";
    json += "\"vehicle_id\":\"" + vehicle_id + "\",";
    json += "\"timestamp\":\"" + data.timestamp + "\",";
    json += "\"rpm\":\"" + data.rpm + "\",";
    json += "\"speed\":\"" + data.speed + "\",";
    json += "\"engine_load\":\"" + data.engine_load + "\",";
    json += "\"coolant_temp\":\"" + data.coolant_temp + "\",";
    json += "\"intake_temp\":\"" + data.intake_temp + "\",";
    json += "\"throttle_pos\":\"" + data.throttle_pos + "\",";
    json += "\"fuel_level\":\"" + data.fuel_level + "\",";
    json += "\"has_mil\":\"" + data.has_mil + "\",";
    json += "\"dtc_code\":\"" + data.dtc_code + "\",";
    json += "\"dtc_description\":\"" + data.dtc_description + "\",";
    json += "\"latitude\":\"" + data.latitude + "\",";
    json += "\"longitude\":\"" + data.longitude + "\"";
    json += "}";

    // Send HTTP POST request
    HTTPClient http;
    http.begin(client, API_URL);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("Authorization", "Bearer " + String(API_KEY));
    
    int httpResponseCode = http.POST(json);
    
    if (httpResponseCode == HTTP_CODE_OK) {
        return true;
    }
    
    return false;
}

void storeOfflineData(DiagnosticData data) {
    if (offline_count >= MAX_OFFLINE_RECORDS) {
        // Remove oldest record
        for (int i = 0; i < MAX_OFFLINE_RECORDS - 1; i++) {
            offline_data[i] = offline_data[i + 1];
        }
        offline_count--;
    }
    
    // Add new record
    offline_data[offline_count] = data;
    offline_count++;
    
    // Save to SD card
    File file = SD.open("offline_data.txt", FILE_APPEND);
    if (file) {
        file.println(String(data.timestamp) + "," +
                    data.rpm + "," +
                    data.speed + "," +
                    data.engine_load + "," +
                    data.coolant_temp + "," +
                    data.intake_temp + "," +
                    data.throttle_pos + "," +
                    data.fuel_level + "," +
                    data.has_mil + "," +
                    data.dtc_code + "," +
                    data.dtc_description + "," +
                    data.latitude + "," +
                    data.longitude);
        file.close();
    }
}

void sendOfflineData() {
    if (offline_count == 0) {
        return;
    }

    // Try to send oldest record
    if (sendToCloud(offline_data[0])) {
        // Remove sent record
        for (int i = 0; i < offline_count - 1; i++) {
            offline_data[i] = offline_data[i + 1];
        }
        offline_count--;
        
        // Update SD card
        File file = SD.open("offline_data.txt", FILE_WRITE);
        if (file) {
            file.truncate(0);
            for (int i = 0; i < offline_count; i++) {
                file.println(String(offline_data[i].timestamp) + "," +
                            offline_data[i].rpm + "," +
                            offline_data[i].speed + "," +
                            offline_data[i].engine_load + "," +
                            offline_data[i].coolant_temp + "," +
                            offline_data[i].intake_temp + "," +
                            offline_data[i].throttle_pos + "," +
                            offline_data[i].fuel_level + "," +
                            offline_data[i].has_mil + "," +
                            offline_data[i].dtc_code + "," +
                            offline_data[i].dtc_description + "," +
                            offline_data[i].latitude + "," +
                            offline_data[i].longitude);
            }
            file.close();
        }
    }
}
