# e20-CO326 Motor Health Monitoring — Digital Twin with Edge Anomaly Detection

## Project Overview

This project implements an **Industrial IoT Digital Twin** for motor health monitoring using a 4-layer edge-to-cloud architecture. It follows the CO326 Course Project specification for Industrial Digital Twin & Cyber-Physical Security.

**Industrial Problem:** Detect early-stage motor bearing failure, imbalance, or abnormal behavior using edge-level anomaly detection and cloud-based RUL estimation.

**Stack:**
| Layer | Technology |
|---|---|
| Edge Device | ESP32-S3 (firmware — pending) |
| Message Broker | Eclipse Mosquitto (MQTT + Sparkplug B) |
| Flow Logic | Node-RED |
| Historian | InfluxDB 2.7 |
| Visualization / Digital Twin | Grafana |
| Infrastructure | Docker + Docker Compose |

---

## What Has Been Done (by @janith — Day 1)

- ✅ Repository structure initialized with all folders and `.gitkeep` placeholders
- ✅ Docker Compose stack configured with all 4 services (Mosquitto, Node-RED, InfluxDB, Grafana)
- ✅ Mosquitto broker running with password authentication (no anonymous access)
- ✅ Unified Namespace (UNS) topic hierarchy defined
- ✅ Node-RED ingestion flow built and deployed:
  - MQTT In → JSON Parse → Alarm Logic (Function) → InfluxDB Write + Debug
- ✅ InfluxDB `motor_health` bucket initialized and receiving data
- ✅ Grafana connected to InfluxDB as data source (Flux query)
- ✅ First Grafana dashboard panel created — live RMS time-series graph
- ✅ End-to-end pipeline tested with mock MQTT data
- ✅ `.env.example` created — secrets shared separately via WhatsApp

---

## Repository Structure

```
e20-co326-Motor-Health-Monitoring-Digital-Twin-with-Edge-Anomaly-Detection/
├── docker/
│   ├── docker-compose.yml        ← All 4 services definition
│   ├── mosquitto.conf            ← Legacy (replaced by config/)
│   ├── config/
│   │   ├── mosquitto.conf        ← Active Mosquitto config
│   │   └── passwd                ← Broker auth (auto-generated, not in git)
│   ├── .env.example              ← Template — copy to .env and fill in secrets
│   └── mock_publisher.py         ← Python script to simulate ESP32 telemetry
├── nodered/
│   └── flows.json                ← Node-RED flow export (import this)
├── firmware/
│   ├── src/                      ← ESP32 Arduino/PlatformIO source (pending)
│   └── include/                  ← Header files (pending)
├── grafana/
│   ├── dashboards/               ← Dashboard JSON exports (pending)
│   └── provisioning/             ← Auto-provisioning configs (pending)
├── docs/
│   ├── diagrams/                 ← Architecture diagrams (Mermaid)
│   └── evidence/                 ← Screenshots and test logs
└── README.md
```

---

## Prerequisites

- Docker Engine 24+ and Docker Compose Plugin
- Python 3.8+ with `paho-mqtt` (for mock publisher only)
- `mosquitto-clients` (for CLI testing)
- A browser (for Node-RED, InfluxDB, Grafana)

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-org/e20-co326-Motor-Health-Monitoring-Digital-Twin-with-Edge-Anomaly-Detection.git
cd e20-co326-Motor-Health-Monitoring-Digital-Twin-with-Edge-Anomaly-Detection
```

### 2. Create your `.env` file

```bash
cp docker/.env.example docker/.env
```

Then open `docker/.env` and fill in the credentials shared on WhatsApp. **Never commit the `.env` file.**

### 3. Regenerate the Mosquitto password file

The `passwd` file is not committed to git. Each team member must generate it locally using the shared password:

```bash
cd docker

# Start mosquitto temporarily in anonymous mode
# Edit config/mosquitto.conf — change allow_anonymous to true and comment out password_file
nano config/mosquitto.conf

docker compose up mosquitto -d
sleep 3

# Generate the password file
docker run --rm -v "$(pwd)/config:/mosquitto/config" eclipse-mosquitto:2   mosquitto_passwd -c -b /mosquitto/config/passwd motoradmin YOUR_MQTT_PASSWORD

# Restore config/mosquitto.conf — set allow_anonymous false and uncomment password_file
nano config/mosquitto.conf

docker compose restart mosquitto
```

> **Shortcut:** If Mosquitto is already running correctly on one machine, the passwd file can be shared directly via WhatsApp alongside the .env secrets.

### 4. Start the full stack

```bash
cd docker
docker compose up -d
docker compose ps
```

Expected output — all 4 containers `Up`:
```
NAME        STATUS          PORTS
grafana     Up              0.0.0.0:3000->3000/tcp
influxdb    Up              0.0.0.0:8086->8086/tcp
mosquitto   Up              0.0.0.0:1883->1883/tcp, 0.0.0.0:9001->9001/tcp
nodered     Up (healthy)    0.0.0.0:1880->1880/tcp
```

### 5. Fix Docker DNS (Kali Linux only)

If `docker run hello-world` fails with a DNS error:

```bash
sudo nano /etc/docker/daemon.json
```

Add:
```json
{
  "dns": ["8.8.8.8", "1.1.1.1"]
}
```

```bash
sudo systemctl restart docker
```

### 6. Import the Node-RED flow

1. Open `http://localhost:1880`
2. Click hamburger menu (top right) → **Import**
3. Select **Upload file** → choose `nodered/flows.json`
4. Click **Import** → **Deploy**

> **Important:** After import, double-click the MQTT In node → edit the server → confirm Host is `mosquitto` (not localhost). Same for InfluxDB Out node — URL must be `http://influxdb:8086`.

### 7. Verify InfluxDB

1. Open `http://localhost:8086`
2. Log in with credentials from `.env`
3. Confirm `motor_health` bucket exists under **Load Data → Buckets**
4. Go to **Data Explorer** → select `motor_health` → `motor_features` → field `rms` → Submit

### 8. Verify Grafana

1. Open `http://localhost:3000`
2. Log in with credentials from `.env`
3. Go to **Connections → Data Sources** → confirm InfluxDB is connected (green tick)
4. Go to **Dashboards** → open **Motor Health Dashboard**

---

## Service URLs

| Service | URL | Notes |
|---|---|---|
| Node-RED | http://localhost:1880 | No login required by default |
| InfluxDB | http://localhost:8086 | Credentials in `.env` |
| Grafana | http://localhost:3000 | Credentials in `.env` |
| MQTT Broker | localhost:1883 | Auth required |
| MQTT WebSocket | localhost:9001 | For browser clients |

---

## Unified Namespace (MQTT Topic Hierarchy)

```
factoryA/
└── area1/
    └── motor01/
        ├── telemetry/
        │   ├── raw             ← Raw sensor values (ESP32)
        │   ├── features        ← Extracted features + anomaly score
        │   └── anomaly         ← Anomaly flag and score only
        ├── state/
        │   ├── device          ← Heartbeat, WiFi, uptime
        │   └── relay           ← Current relay state
        ├── cmd/
        │   └── relay           ← Control commands from dashboard
        └── sim/
            └── mode            ← Simulation mode toggle
```

**Sparkplug B namespace (for formal compliance):**
```
spBv1.0/factoryA/DDATA/area1/motor01
```

---

## MQTT Payload Schema

All telemetry messages on `telemetry/features` use this JSON structure:

```json
{
  "ts": 1712566800,
  "motor_id": "motor01",
  "rms": 0.42,
  "peak": 0.71,
  "variance": 0.03,
  "anomaly_score": 0.12,
  "anomaly_flag": 0,
  "relay_state": 1,
  "mode": "live",
  "wifi_rssi": -55
}
```

| Field | Type | Description |
|---|---|---|
| `ts` | int | Unix timestamp (seconds) |
| `motor_id` | string | Device identifier |
| `rms` | float | Root mean square of sensor signal |
| `peak` | float | Peak signal value in window |
| `variance` | float | Signal variance in window |
| `anomaly_score` | float | 0.0 (normal) to 1.0 (critical) |
| `anomaly_flag` | int | 0 = normal, 1 = anomaly detected |
| `relay_state` | int | 0 = open, 1 = closed |
| `mode` | string | `live` or `simulation` |
| `wifi_rssi` | int | WiFi signal strength (dBm) |

---

## Testing with Mock Publisher

Run the mock publisher to simulate ESP32 telemetry without hardware:

```bash
pip install paho-mqtt
python3 docker/mock_publisher.py
```

The script publishes one message per second, simulating normal motor behavior with an abnormal spike every 30 cycles.

Alternatively, send a single test message:

```bash
mosquitto_pub -h localhost -p 1883   -u motoradmin -P motor2026secure   -t "factoryA/area1/motor01/telemetry/features"   -m '{"motor_id":"motor01","rms":0.42,"anomaly_score":0.1,"anomaly_flag":0,"relay_state":1}'
```

---

## Node-RED Flow Description

The current flow (`nodered/flows.json`) implements:

1. **MQTT In** — subscribes to `factoryA/area1/motor01/telemetry/features`
2. **JSON Parse** — converts raw MQTT string payload to JavaScript object
3. **Alarm Logic** (Function node) — adds `alarm_state` field:
   - `anomaly_flag === 1` → `"ALARM"`
   - `anomaly_score > 0.5` → `"WARNING"`
   - Otherwise → `"NORMAL"`
4. **InfluxDB Out** — writes to `motor_features` measurement in `motor_health` bucket
5. **Debug** — prints all messages to the Node-RED debug panel

---

## What Needs to Be Done Next

### Member 1 — ESP32-S3 Firmware
- [ ] Set up PlatformIO project in `firmware/`
- [ ] Implement Wi-Fi connect and reconnect logic
- [ ] Implement MQTT connect, reconnect, and Last Will & Testament
- [ ] Read sensor (vibration or current)
- [ ] Compute features: RMS, peak, variance
- [ ] Implement edge anomaly detection (threshold or z-score)
- [ ] Publish telemetry to `factoryA/area1/motor01/telemetry/features`
- [ ] Subscribe to `factoryA/area1/motor01/cmd/relay` for control commands
- [ ] Drive relay output based on command

### Member 2 — Node-RED + MQTT
- [ ] Add heartbeat/LWT topic subscription and processing
- [ ] Add relay command validation and routing flow
- [ ] Implement simple RUL estimation (rolling trend of anomaly score)
- [ ] Add simulation mode toggle flow
- [ ] Export updated `flows.json` and commit

### Member 3 — Grafana Dashboard
- [ ] Build full Motor Health Dashboard:
  - Live RMS panel ✅
  - Anomaly score gauge
  - Alarm state indicator
  - Relay state panel
  - Device heartbeat panel
  - Historical trend panel
  - RUL estimate panel
- [ ] Add relay control button (Grafana → Node-RED → ESP32)
- [ ] Export dashboard JSON to `grafana/dashboards/`

### Member 4 — Documentation & Hardware
- [ ] Draw electrical wiring diagram (ESP32 + sensor + relay)
- [ ] Draw simplified P&ID
- [ ] Write cybersecurity design summary
- [ ] Write reliability features summary
- [ ] Capture test evidence (screenshots, logs, photos)
- [ ] Start final report structure

---

## Architecture

```mermaid
flowchart LR
    subgraph L1["Layer 1 - Physical"]
        Motor["Induction Motor"]
        Sensor["Vibration/Current Sensor"]
        Relay["Relay Actuator"]
    end

    subgraph L2["Layer 2 - Edge"]
        ESP["ESP32-S3
        Acquire + Features
        Anomaly Detection
        MQTT Client + LWT"]
    end

    subgraph L3["Layer 3 - Integration"]
        MQ["Mosquitto
        MQTT Broker"]
        NR["Node-RED
        Rules + RUL + Simulation"]
    end

    subgraph L4["Layer 4 - Application"]
        IF["InfluxDB
        Historian"]
        GF["Grafana
        Digital Twin Dashboard"]
    end

    Sensor --> ESP
    ESP -->|telemetry + anomaly| MQ
    MQ --> NR
    NR --> IF
    IF --> GF
    NR --> GF
    GF -->|operator command| NR
    NR -->|control cmd| MQ
    MQ --> ESP
    ESP --> Relay
    Relay --> Motor
    Motor --> Sensor
```

---

## Security Notes

- Mosquitto requires username/password authentication — anonymous access is disabled
- Credentials are stored in `.env` — never commit this file
- `.env` is in `.gitignore`
- Use `.env.example` as the template
- Credentials shared via WhatsApp only
- All Docker services use non-default passwords

---

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| Mosquitto restarting | passwd file missing | Regenerate passwd file (Step 3) |
| Node-RED `connecting` | Wrong MQTT host | Change host to `mosquitto` not `localhost` |
| InfluxDB `ECONNREFUSED` | Wrong InfluxDB URL | Change URL to `http://influxdb:8086` |
| Docker DNS failure | IPv6 DNS issue on Kali | Add `8.8.8.8` to `/etc/docker/daemon.json` |
| `sed` permission error | Project on NTFS `/mnt/` | Edit config files manually, not with sed |
| Empty Data Explorer | No data written yet | Run mock publisher or publish test message |

---

## Team

| Member | Role |
|---|---|
| Member 1 | Infrastructure, Docker, MQTT, Node-RED, InfluxDB, Grafana |
| Member 2 | Node-RED flows, MQTT topic design, RUL logic |
| Member 3 | Grafana dashboard, Digital Twin UI |
| Member 4 | ESP32 firmware, sensor, relay, wiring |

---

*CO326 — Computer Systems Engineering & Industrial Networks | University of Peradeniya | 2026*