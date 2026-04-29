# Motor Thermal Monitoring — Setup Guide

## 1. Clone and Go to the Folder
```bash
git clone <repo-url>
cd e20-co326-Motor-Thermal-Monitoring-Digital-Twin/code-v2
```

## 2. Start Everything

```bash
docker compose up --build
```

This starts 4 services: MQTT broker, Node-RED, the simulated device, and the edge AI. The first run takes a minute — Node-RED will auto-install its dashboard plugin.

## 3. Open the Dashboard

Once you see logs scrolling, go to:

```
http://localhost:1880/dashboard
```

You'll see:

- A live temperature chart and gauge (updates every 2 seconds)
- An alert status indicator — `NORMAL` / `WARNING` / `CRITICAL`
- An alert log with the last 10 events
- A spinning fan widget showing fan state

## 4. Play With It

### Manual Fan Control

1. Toggle the **Control Mode** switch to `MANUAL`
2. Use the **Fan ON** / **Fan OFF** buttons to control the fan yourself
3. Watch the temperature drop when the fan is on

### Auto Mode

Toggle back to `AUTO` — the edge AI takes over and switches the fan on/off based on z-score anomaly detection.

### Node-RED Flows *(optional)*

Go to `http://localhost:1880` to see and edit the flow logic visually.

## 5. Stop

```bash
docker compose down
```

---

## Container Reference

| Container | Role |
|---|---|
| `mqtt` | Mosquitto broker — message bus for everything |
| `python-device` | Simulates motor temp sensor, publishes readings every 2s |
| `python-edge` | Edge AI — z-score anomaly detection, controls fan in AUTO mode |
| `node-red` | Dashboard + fan control UI |