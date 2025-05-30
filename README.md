# OBD2 IoT Vehicle Intelligence & Mechanic Hailing Platform

A comprehensive vehicle intelligence platform powered by an OBD2 IoT device with cellular connectivity, integrated with cloud services, mobile applications, and an on-demand mechanic hailing system.

## Project Structure

```
obd2-4/
├── hardware/           # ESP32 + SIM7600 firmware
├── mobile/            # React Native mobile app
├── web/              # Web dashboard
├── backend/          # Supabase backend
└── docs/             # Documentation
```

## Key Features

- Real-time vehicle diagnostics
- Trip management and tracking
- Maintenance management
- Driving behavior analysis
- Vehicle health analytics
- Emergency mechanic hailing
- Geofencing & anti-theft
- Vehicle location tracking
- Mechanic portal
- Driver and fleet portals
- Vehicle document vault
- Smart notifications
- Crowdsourced fault solutions

## Technology Stack

- **Hardware**: ESP32 + SIM7600
- **Backend**: Supabase
- **Mobile**: React Native with Expo
- **Web**: React.js
- **Database**: PostgreSQL (via Supabase)
- **Hosting**: Firebase/AWS/GCP

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- Expo CLI
- ESP-IDF (for hardware development)
- Supabase account

### Installation

1. Clone the repository
2. Install dependencies for each component:
   ```bash
   # Mobile app
   cd mobile
   npm install

   # Web dashboard
   cd web
   npm install

   # Hardware
   cd hardware
   # Follow ESP-IDF setup instructions
   ```

## Development Status

🚧 Project is currently under development 🚧

## License

[License details to be added] 