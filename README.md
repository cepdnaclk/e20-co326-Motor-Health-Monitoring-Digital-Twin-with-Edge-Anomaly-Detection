# Motor Health Monitoring Digital Twin (Thermal)

This repository contains an Industrial IoT digital twin focused on temperature-based motor condition monitoring using a mock sensor publisher, MQTT, Node-RED, InfluxDB, and Grafana.

## Industrial Problem

Detect motor overheating, thermal runaway, and cooling failure using edge-level temperature monitoring and cloud-based thermal trend analysis.

## Stack (Unchanged)

- Docker stack: same 4 containers (Mosquitto, Node-RED, InfluxDB, Grafana)
- MQTT topic hierarchy: unchanged structure
- Ingestion path: MQTT -> Node-RED -> InfluxDB -> Grafana

## MQTT Topics

- Features topic (unchanged): `factoryA/area1/motor01/telemetry/features`
- Raw topic description (optional rename in docs): `factoryA/area1/motor01/telemetry/raw` (raw temperature reading)

## Thermal Payload Schema

Messages published to `telemetry/features` use:

```json
{
	"ts": 1712566800,
	"motor_id": "motor01",
	"temperature": 42.5,
	"temp_rate": 0.3,
	"temp_baseline": 35.0,
	"temp_delta": 7.5,
	"anomaly_score": 0.25,
	"anomaly_flag": 0,
	"relay_state": 1,
	"mode": "live",
	"wifi_rssi": -55
}
```

| Field | Description |
|---|---|
| `ts` | Unix timestamp (seconds) |
| `motor_id` | Device identifier |
| `temperature` | Current motor surface temperature (C) |
| `temp_rate` | Rate of change (C per second) |
| `temp_baseline` | Rolling average baseline temperature |
| `temp_delta` | Difference from baseline |
| `anomaly_score` | 0.0 to 1.0 derived from temp_delta and temp_rate |
| `anomaly_flag` | 1 if threshold exceeded, else 0 |
| `relay_state` | Relay state (0/1) |
| `mode` | Source mode, e.g. `live` |
| `wifi_rssi` | WiFi RSSI in dBm |

## Node-RED + InfluxDB Updates

- Alarm logic uses temperature thresholds:
	- warning at `temperature >= 65`
	- alarm at `temperature >= 80`
	- warning on fast rise `temp_rate >= 0.5`
- Influx measurement renamed:
	- old: `motor_features`
	- new: `motor_thermal`

## Grafana Panels (Thermal)

- Live Temperature (Gauge, 0-100 C)
- Temperature Trend (Time series)
- Rate of Change (Time series)
- Temp Delta from Baseline (Stat)
- Anomaly Score (Gauge, 0-1)
- Alarm State (State timeline)
- Relay State (Stat)

Example Flux query:

```flux
from(bucket: "motor_health")
	|> range(start: -1h)
	|> filter(fn: (r) => r._measurement == "motor_thermal")
	|> filter(fn: (r) => r._field == "temperature")
```

Recommended gauge thresholds for temperature:

- Green: 0-64 C
- Orange: 65-79 C
- Red: 80 C+

## Sensor and Actuator Notes

- Current phase: mock telemetry generator is used instead of ESP32 firmware.
- Sensor: NTC thermistor (cheap, simple) or DS18B20 digital sensor (more accurate)
- Actuator: Relay (cuts motor power when thermal alarm triggers)
