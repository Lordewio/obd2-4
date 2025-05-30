#ifndef GPS_HANDLER_H
#define GPS_HANDLER_H

#include <Arduino.h>
#include <TinyGPS++.h>
#include <SoftwareSerial.h>

// GPS Configuration
#define GPS_RX_PIN 16
#define GPS_TX_PIN 17
#define GPS_BAUD 9600

// GPS Timeouts
#define GPS_TIMEOUT 1000
#define GPS_FIX_TIMEOUT 30000

// GPS Accuracy
#define MIN_SAT_COUNT 4
#define MIN_HDOP 10

// GPS Data Structure
class GPSData {
    public:
        bool isValid;
        double latitude;
        double longitude;
        float altitude;
        float speed;
        int satellites;
        unsigned long age;
        
        void clear() {
            isValid = false;
            latitude = 0;
            longitude = 0;
            altitude = 0;
            speed = 0;
            satellites = 0;
            age = 0;
        }
};

class GPSHandler {
    private:
        TinyGPSPlus gps;
        SoftwareSerial *gpsSerial;
        GPSData currentData;
        
        bool validateGPSData() {
            if (gps.location.isValid() && 
                gps.altitude.isValid() && 
                gps.speed.isValid() && 
                gps.satellites.isValid() &&
                gps.hdop.isValid()) {
                
                if (gps.satellites.value() >= MIN_SAT_COUNT &&
                    gps.hdop.value() <= MIN_HDOP) {
                    return true;
                }
            }
            return false;
        }
        
    public:
        GPSHandler() {
            currentData.clear();
        }
        
        bool begin() {
            gpsSerial = new SoftwareSerial(GPS_RX_PIN, GPS_TX_PIN);
            gpsSerial->begin(GPS_BAUD);
            return true;
        }
        
        GPSData* update() {
            unsigned long start = millis();
            
            while (millis() - start < GPS_TIMEOUT) {
                while (gpsSerial->available()) {
                    gps.encode(gpsSerial->read());
                }
                
                if (validateGPSData()) {
                    currentData.isValid = true;
                    currentData.latitude = gps.location.lat();
                    currentData.longitude = gps.location.lng();
                    currentData.altitude = gps.altitude.meters();
                    currentData.speed = gps.speed.kmph();
                    currentData.satellites = gps.satellites.value();
                    currentData.age = gps.location.age();
                    
                    return &currentData;
                }
            }
            
            currentData.clear();
            return &currentData;
        }
        
        void reset() {
            currentData.clear();
        }
        
        void end() {
            if (gpsSerial) {
                delete gpsSerial;
                gpsSerial = nullptr;
            }
        }
};

#endif // GPS_HANDLER_H
