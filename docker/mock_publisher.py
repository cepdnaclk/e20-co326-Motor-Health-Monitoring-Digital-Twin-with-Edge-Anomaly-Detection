import paho.mqtt.client as mqtt
import json, time, random, math

BROKER = "localhost"
PORT = 1883
USER = "motoradmin"
PASS = "motor2026secure"
TOPIC_BASE = "factoryA/area1/motor01"
MOTOR_ID = "motor01"

def generate_normal():
    rms = round(random.gauss(0.42, 0.03), 4)
    peak = round(rms * random.uniform(1.5, 1.8), 4)
    variance = round(random.uniform(0.02, 0.05), 4)
    score = round(random.uniform(0.05, 0.2), 4)
    return rms, peak, variance, score, 0

def generate_abnormal():
    rms = round(random.gauss(0.85, 0.08), 4)
    peak = round(rms * random.uniform(2.2, 3.0), 4)
    variance = round(random.uniform(0.15, 0.35), 4)
    score = round(random.uniform(0.7, 0.98), 4)
    return rms, peak, variance, score, 1

client = mqtt.Client()
client.username_pw_set(USER, PASS)
client.connect(BROKER, PORT)
client.loop_start()

print("Mock publisher running... Ctrl+C to stop")
cycle = 0
while True:
    cycle += 1
    # simulate degradation: abnormal every 30 cycles
    if cycle % 30 == 0:
        rms, peak, variance, score, flag = generate_abnormal()
        mode = "live"
        print(f"[ABNORMAL] cycle={cycle}")
    else:
        rms, peak, variance, score, flag = generate_normal()
        mode = "live"

    payload = {
        "ts": int(time.time()),
        "motor_id": MOTOR_ID,
        "rms": rms,
        "peak": peak,
        "variance": variance,
        "anomaly_score": score,
        "anomaly_flag": flag,
        "relay_state": 1,
        "mode": mode,
        "wifi_rssi": -55
    }

    client.publish(f"{TOPIC_BASE}/telemetry/features", json.dumps(payload))
    print(f"Published: {payload}")
    time.sleep(1)