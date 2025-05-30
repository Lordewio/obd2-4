#ifndef OBD2_PARSER_H
#define OBD2_PARSER_H

#include <Arduino.h>

#ifndef OBD2_PARSER_H
#define OBD2_PARSER_H

#include <Arduino.h>
#include <map>
#include <vector>

// Thresholds for critical parameters
struct ParameterThresholds {
    float min_rpm = 0;
    float max_rpm = 8000;
    float min_engine_temp = -40;
    float max_engine_temp = 150;
    float min_oil_temp = -40;
    float max_oil_temp = 150;
    float min_fuel_pressure = 0;
    float max_fuel_pressure = 500; // kPa
    float min_battery_voltage = 11.5;
    float max_battery_voltage = 14.5;
};

// Parameter validation results
class ParameterValidation {
public:
    bool isValid;
    String error;
    float value;
    
    ParameterValidation() : isValid(false), error(""), value(0) {}
    ParameterValidation(float val) : isValid(true), error(""), value(val) {}
};

// Unit conversion functions
class UnitConverter {
public:
    static float kPaToPSI(float kpa) { return kpa * 0.145038; }
    static float PSIToKPa(float psi) { return psi / 0.145038; }
    static float LhToGph(float lph) { return lph * 0.264172; }
    static float GphToLh(float gph) { return gph / 0.264172; }
    static float CelsiusToFahrenheit(float c) { return (c * 9.0/5.0) + 32; }
    static float FahrenheitToCelsius(float f) { return (f - 32) * 5.0/9.0; }
};

class OBD2Parser {
private:
    ParameterThresholds thresholds;
    
    // Helper function to validate parameter values
    ParameterValidation validateParameter(float value, float min, float max, const char* paramName) {
        if (value < min || value > max) {
            return ParameterValidation();
        }
        return ParameterValidation(value);
    }
    
    // Helper function to check if response is valid
    bool isValidResponse(String response) {
        if (response.length() < 8) return false;
        if (response.startsWith("NO DATA") || response.startsWith("UNABLE TO CONNECT")) return false;
        return true;
    }
    
public:
    OBD2Parser() {
        // Initialize default thresholds
        thresholds.min_rpm = 0;
        thresholds.max_rpm = 8000;
        thresholds.min_engine_temp = -40;
        thresholds.max_engine_temp = 150;
        thresholds.min_oil_temp = -40;
        thresholds.max_oil_temp = 150;
        thresholds.min_fuel_pressure = 0;
        thresholds.max_fuel_pressure = 500;
        thresholds.min_battery_voltage = 11.5;
        thresholds.max_battery_voltage = 14.5;
    }
    
    // Set custom thresholds
    void setThresholds(const ParameterThresholds& newThresholds) {
        thresholds = newThresholds;
    }
    
    // Engine Parameters
    ParameterValidation parseRPM(String response) {
        if (!isValidResponse(response) || !response.startsWith("41 0C")) {
            return ParameterValidation();
        }
        
        String hex = response.substring(6, 10);
        int value = hexToDec(hex);
        float rpm = value / 4.0;
        
        return validateParameter(rpm, thresholds.min_rpm, thresholds.max_rpm, "RPM");
    }
    
    ParameterValidation parseEngineLoad(String response) {
        if (!isValidResponse(response) || !response.startsWith("41 04")) {
            return ParameterValidation();
        }
        
        String hex = response.substring(6, 8);
        int value = hexToDec(hex);
        float load = value * 100.0 / 255.0;
        
        return validateParameter(load, 0, 100, "Engine Load");
    }
    
    ParameterValidation parseEngineCoolantTemp(String response) {
        if (!isValidResponse(response) || !response.startsWith("41 05")) {
            return ParameterValidation();
        }
        
        String hex = response.substring(6, 8);
        int value = hexToDec(hex);
        float temp = value - 40;
        
        return validateParameter(temp, thresholds.min_engine_temp, thresholds.max_engine_temp, "Engine Temp");
    }
    
    ParameterValidation parseEngineOilTemp(String response) {
        if (!isValidResponse(response) || !response.startsWith("41 5C")) {
            return ParameterValidation();
        }
        
        String hex = response.substring(6, 8);
        int value = hexToDec(hex);
        float temp = value - 40;
        
        return validateParameter(temp, thresholds.min_oil_temp, thresholds.max_oil_temp, "Oil Temp");
    }
    
    ParameterValidation parseEngineRuntime(String response) {
        if (!isValidResponse(response) || !response.startsWith("41 1F")) {
            return ParameterValidation();
        }
        
        String hex = response.substring(6, 10);
        int value = hexToDec(hex);
        float runtime = value / 60.0;
        
        return validateParameter(runtime, 0, 1000000, "Engine Runtime");
    }
    
    // Fuel System
    ParameterValidation parseFuelLevel(String response) {
        if (!isValidResponse(response) || !response.startsWith("41 2F")) {
            return ParameterValidation();
        }
        
        String hex = response.substring(6, 8);
        int value = hexToDec(hex);
        float level = value * 100.0 / 255.0;
        
        return validateParameter(level, 0, 100, "Fuel Level");
    }
    
    ParameterValidation parseFuelPressure(String response) {
        if (!isValidResponse(response) || !response.startsWith("41 0A")) {
            return ParameterValidation();
        }
        
        String hex = response.substring(6, 8);
        int value = hexToDec(hex);
        float pressure = value * 3; // kPa
        
        return validateParameter(pressure, thresholds.min_fuel_pressure, thresholds.max_fuel_pressure, "Fuel Pressure");
    }
    
    ParameterValidation parseFuelRate(String response) {
        if (!isValidResponse(response) || !response.startsWith("41 5E")) {
            return ParameterValidation();
        }
        
        String hex = response.substring(6, 10);
        int value = hexToDec(hex);
        float rate = value / 20; // L/h
        
        return validateParameter(rate, 0, 1000, "Fuel Rate");
    }
    
    // Vehicle Speed
    ParameterValidation parseVehicleSpeed(String response) {
        if (!isValidResponse(response) || !response.startsWith("41 0D")) {
            return ParameterValidation();
        }
        
        String hex = response.substring(6, 8);
        int value = hexToDec(hex);
        
        return validateParameter(value, 0, 255, "Vehicle Speed");
    }
    
    // Intake System
    ParameterValidation parseIntakeTemp(String response) {
        if (!isValidResponse(response) || !response.startsWith("41 0F")) {
            return ParameterValidation();
        }
        
        String hex = response.substring(6, 8);
        int value = hexToDec(hex);
        float temp = value - 40;
        
        return validateParameter(temp, -40, 215, "Intake Temp");
    }
    
    ParameterValidation parseIntakePressure(String response) {
        if (!isValidResponse(response) || !response.startsWith("41 0B")) {
            return ParameterValidation();
        }
        
        String hex = response.substring(6, 8);
        int value = hexToDec(hex);
        float pressure = value * 0.145038; // Convert to PSI
        
        return validateParameter(pressure, 0, 30, "Intake Pressure");
    }
    
    // Exhaust System
    ParameterValidation parseExhaustTemp(String response) {
        if (!isValidResponse(response) || !response.startsWith("41 5E")) {
            return ParameterValidation();
        }
        
        String hex = response.substring(6, 8);
        int value = hexToDec(hex);
        float temp = value - 40;
        
        return validateParameter(temp, -40, 1000, "Exhaust Temp");
    }
    
    // Emissions
    ParameterValidation parseOxygenSensor1(String response) {
        if (!isValidResponse(response) || !response.startsWith("41 14")) {
            return ParameterValidation();
        }
        
        String hex = response.substring(6, 8);
        int value = hexToDec(hex);
        float voltage = value * 100.0 / 255.0;
        
        return validateParameter(voltage, 0, 100, "Oxygen Sensor 1");
    }
    
    ParameterValidation parseOxygenSensor2(String response) {
        if (!isValidResponse(response) || !response.startsWith("41 15")) {
            return ParameterValidation();
        }
        
        String hex = response.substring(6, 8);
        int value = hexToDec(hex);
        float voltage = value * 100.0 / 255.0;
        
        return validateParameter(voltage, 0, 100, "Oxygen Sensor 2");
    }
    
    // Transmission
    ParameterValidation parseTransmissionGear(String response) {
        if (!isValidResponse(response) || !response.startsWith("41 5A")) {
            return ParameterValidation();
        }
        
        String hex = response.substring(6, 8);
        int value = hexToDec(hex);
        
        return validateParameter(value, 0, 10, "Transmission Gear");
    }
    
    ParameterValidation parseTransmissionTemp(String response) {
        if (!isValidResponse(response) || !response.startsWith("41 5B")) {
            return ParameterValidation();
        }
        
        String hex = response.substring(6, 8);
        int value = hexToDec(hex);
        float temp = value - 40;
        
        return validateParameter(temp, -40, 150, "Transmission Temp");
    }
    
    // Battery
    ParameterValidation parseBatteryVoltage(String response) {
        if (!isValidResponse(response) || !response.startsWith("41 23")) {
            return ParameterValidation();
        }
        
        String hex = response.substring(6, 8);
        int value = hexToDec(hex);
        float voltage = value * 0.1;
        
        return validateParameter(voltage, thresholds.min_battery_voltage, thresholds.max_battery_voltage, "Battery Voltage");
    }
    
    // Throttle System
    ParameterValidation parseThrottlePos(String response) {
        if (!isValidResponse(response) || !response.startsWith("41 11")) {
            return ParameterValidation();
        }
        
        String hex = response.substring(6, 8);
        int value = hexToDec(hex);
        float pos = value * 100.0 / 255.0;
        
        return validateParameter(pos, 0, 100, "Throttle Position");
    }
    
    ParameterValidation parseThrottlePosB(String response) {
        if (!isValidResponse(response) || !response.startsWith("41 13")) {
            return ParameterValidation();
        }
        
        String hex = response.substring(6, 8);
        int value = hexToDec(hex);
        float pos = value * 100.0 / 255.0;
        
        return validateParameter(pos, 0, 100, "Throttle Position B");
    }
    
    // Accelerator Pedal
    ParameterValidation parseAcceleratorPos(String response) {
        if (!isValidResponse(response) || !response.startsWith("41 49")) {
            return ParameterValidation();
        }
        
        String hex = response.substring(6, 8);
        int value = hexToDec(hex);
        float pos = value * 100.0 / 255.0;
        
        return validateParameter(pos, 0, 100, "Accelerator Position");
    }
    
    // Brake System
    ParameterValidation parseBrakeSwitch(String response) {
        if (!isValidResponse(response) || !response.startsWith("41 40")) {
            return ParameterValidation();
        }
        
        String hex = response.substring(6, 8);
        int value = hexToDec(hex);
        return ParameterValidation(value > 0 ? 1.0 : 0.0);
    }
    
    // Vehicle Identification
    String parseVIN(String response) {
        if (!isValidResponse(response) || !response.startsWith("09 02")) {
            return "";
        }
        
        String vin = "";
        for (int i = 6; i < response.length(); i += 2) {
            String byte = response.substring(i, i + 2);
            vin += (char)hexToDec(byte);
        }
        return vin;
    }
    
    // Diagnostic Trouble Codes
    String parseDTC(String response) {
        if (!isValidResponse(response) || !response.startsWith("43")) {
            return "";
        }
        
        String dtc = "";
        for (int i = 2; i < response.length(); i += 2) {
            String code = response.substring(i, i + 2);
            if (code == "00") break;
            dtc += code + ", ";
        }
        return dtc;
    }
    
    // MIL (Check Engine Light)
    ParameterValidation parseMILStatus(String response) {
        if (!isValidResponse(response) || !response.startsWith("41 01")) {
            return ParameterValidation();
        }
        
        String hex = response.substring(6, 8);
        int value = hexToDec(hex);
        return ParameterValidation((value & 0x01) > 0 ? 1.0 : 0.0);
    }
    
    // Convert hex string to decimal
    int hexToDec(String hex) {
        int value = 0;
        for (int i = 0; i < hex.length(); i++) {
            char c = hex.charAt(i);
            value = value * 16 + hexCharToInt(c);
        }
        return value;
    }
    
    // Convert hex character to integer
    int hexCharToInt(char c) {
        if (c >= '0' && c <= '9') return c - '0';
        if (c >= 'A' && c <= 'F') return c - 'A' + 10;
        if (c >= 'a' && c <= 'f') return c - 'a' + 10;
        return 0;
    }
};

#endif // OBD2_PARSER_H

#endif // OBD2_PARSER_H
