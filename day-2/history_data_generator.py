import csv
import random

LOG_FILE = "history.csv"

SENSOR_FIELDS = ["temperature", "pressure", "vibration", "rpm", "current"]
LOG_FIELDS = SENSOR_FIELDS + ["state"]


def generate_sensor_reading():
    return {
        "temperature": round(random.uniform(20, 95), 1),
        "pressure": round(random.uniform(900, 1200), 1),
        "vibration": round(random.uniform(0, 2), 1),
        "rpm": round(random.uniform(1100, 1600), 1),
        "current": round(random.uniform(0, 30), 1),
    }


RULES = [

    {"name": "HIGH_TEMP", "priority": 1,"condition": lambda r: r["temperature"] > 80, "action": "STOP_MACHINE"},
    {"name": "LOW_TEMP", "priority": 1,"condition": lambda r: r["temperature"] < 30, "action": "STOP_MACHINE"},
    {"name": "HIGH_CURRENT", "priority": 1,"condition": lambda r: r["current"] > 25, "action": "STOP_MACHINE"},
    {"name": "LOW_CURRENT", "priority": 1,"condition": lambda r: r["current"] < 5, "action": "STOP_MACHINE"},
    {"name": "LOW_PRESSURE", "priority": 2,"condition": lambda r: r["pressure"] < 950, "action": "STOP_MACHINE"},
    {"name": "HIGH_PRESSURE", "priority": 2,"condition": lambda r: r["pressure"] > 1050, "action": "STOP_MACHINE"},
    {"name": "LOW_VIBRATION", "priority": 3,"condition": lambda r: r["vibration"] < 0.2, "action": "STOP_MACHINE"},
    {"name": "HIGH_VIBRATION", "priority": 3,"condition": lambda r: r["vibration"] > 1.8, "action": "STOP_MACHINE"},
    {"name": "LOW_RPM", "priority": 3,"condition": lambda r: r["rpm"] < 1150, "action": "STOP_MACHINE"},
    {"name": "HIGH_RPM", "priority": 3,"condition": lambda r: r["rpm"] > 1550, "action": "STOP_MACHINE"},


    {"name": "HIGH_TEMP", "priority": 4,"condition": lambda r: r["temperature"] > 70, "action": "WARNING"},
    {"name": "LOW_TEMP", "priority": 4,"condition": lambda r: r["temperature"] < 40, "action": "WARNING"},
    {"name": "HIGH_CURRENT", "priority": 4,"condition": lambda r: r["current"] > 22, "action": "WARNING"},
    {"name": "LOW_CURRENT", "priority": 4,"condition": lambda r: r["current"] < 8, "action": "WARNING"},
    {"name": "LOW_PRESSURE", "priority": 5,"condition": lambda r: r["pressure"] < 980, "action": "WARNING"},
    {"name": "HIGH_PRESSURE", "priority": 5,"condition": lambda r: r["pressure"] > 1030, "action": "WARNING"},
    {"name": "LOW_VIBRATION", "priority": 6,"condition": lambda r: r["vibration"] < 0.4, "action": "WARNING"},
    {"name": "HIGH_VIBRATION", "priority": 6,"condition": lambda r: r["vibration"] > 1.6, "action": "WARNING"},
    {"name": "LOW_RPM", "priority": 6,"condition": lambda r: r["rpm"] < 1200, "action": "WARNING"},
    {"name": "HIGH_RPM", "priority": 6,"condition": lambda r: r["rpm"] > 1500, "action": "WARNING"},
]


def evaluate_rules(reading, rules):
    missing = [
        sensor for sensor in SENSOR_FIELDS
        if sensor not in reading or reading[sensor] is None
    ]
    if missing:
        return "MISSING_SENSOR_DATA", "IGNORE"

    for rule in sorted(rules, key=lambda item: item["priority"]):
        if rule["condition"](reading):
            return rule["name"], rule["action"]

    return "NO_RULE_FIRED", "CONTINUE_NORMAL"


MESSAGE_MAP = {
    "STOP_MACHINE": "Warning",
    "WARNING": "Warning",
    "CONTINUE_NORMAL": "Normal",
    "IGNORE": "Normal",
}


def take_action(action):
    return MESSAGE_MAP.get(action, f"No handler for action: {action}")


def log_decision(reading, rule_name, action):
    try:
        with open(LOG_FILE, "r", newline="") as csvfile:
            has_header = next(csv.reader(csvfile), None) == LOG_FIELDS
    except FileNotFoundError:
        has_header = False

    with open(LOG_FILE, "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=LOG_FIELDS)

        if not has_header:
            writer.writeheader()

        row = {sensor: reading.get(sensor) for sensor in SENSOR_FIELDS}
        row.update({"state": MESSAGE_MAP[action]})
        writer.writerow(row)


def main():
    reading = generate_sensor_reading()
    rule_name, action = evaluate_rules(reading, RULES)
    log_decision(reading, rule_name, action)



if __name__ == "__main__":
    main()