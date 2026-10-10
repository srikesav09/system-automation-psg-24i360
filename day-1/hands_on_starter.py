"""
DAY 1 · HANDS-ON — Build Your Rule Engine
23IF02 System Automation

Work through the TODOs in order. Each one matches a step on the
"Hands-on · Build Your Rule Engine" slide. Run this file after each
step to see your progress:

    python hands_on_starter.py

Need the answer? See hands_on_solution.py — but try it yourself first.
"""

import random
import time

LOG_FILE = "day1_log.txt"


# ---------------------------------------------------------------------------
# STEP 1 — Generate simulated sensor data
# ---------------------------------------------------------------------------
def generate_sensor_data():
    """Return a dict with at least 'temperature', 'pressure', 'vibration'."""
    # TODO: fill in realistic random values, e.g. temperature 50-95 (deg C)
    return {
        "temperature": round(random.uniform(20,95)),   # TODO
        "pressure": round(random.uniform(900, 1100)),    # TODO
        "vibration": round(random.uniform(0, 2), 2),    # TODO
        "current" : round(random.uniform(0, 30), 2)
    }
    # STRETCH GOAL (after the 8 steps below all work): real sensors aren't
    # perfectly clean. Try making one field randomly return None (a
    # dropout) or spike far outside its normal range every so often, then
    # update evaluate_rules() so a dropout doesn't crash your engine.


# ---------------------------------------------------------------------------
# STEP 2 — Write your first automation rules
# STEP 7 — Add a rule of your own (add another dict to this list)
# STEP 8 — Add one priority rule (lower "priority" number checked first)
# ---------------------------------------------------------------------------
RULES = [
    # TODO: add rule dicts like:
    {"name": "HIGH_TEMP", "priority": 1, "condition": lambda r: r["temperature"] > 80, "action": "STOP_MACHINE"},
    {"name": "LOW_TEMP", "priority": 1, "condition": lambda r: r["temperature"] < 30, "action": "STOP_MACHINE"},
    {"name": "LOW_PRESSURE", "priority": 2, "condition": lambda r: r["pressure"] > 1050, "action": "STOP_MACHINE"},
    {"name": "HIGH_PRESSURE", "priority": 2, "condition": lambda r: r["pressure"] < 950, "action": "STOP_MACHINE"},
    {"name": "LOW_VIBRATION", "priority": 3, "condition": lambda r: r["vibration"] < 0.2, "action": "STOP_MACHINE"},
    {"name": "HIGH_VIBRATION", "priority": 3, "condition": lambda r: r["vibration"] > 1.8, "action": "STOP_MACHINE"},
    {"name": "HIGH_CURRENT", "priority": 1, "condition": lambda r: r["current"] > 25, "action": "STOP_MACHINE"},
    {"name": "LOW_CURRENT", "priority": 1, "condition": lambda r: r["current"] < 5, "action": "STOP_MACHINE"},


    {"name": "HIGH_TEMP", "priority": 1, "condition": lambda r: r["temperature"] > 70, "action": "WARNING"},
    {"name": "LOW_TEMP", "priority": 1, "condition": lambda r: r["temperature"] < 40, "action": "WARNING"},
    {"name": "LOW_PRESSURE", "priority": 2, "condition": lambda r: r["pressure"] > 1030, "action": "WARNING"},
    {"name": "HIGH_PRESSURE", "priority": 2, "condition": lambda r: r["pressure"] < 980, "action": "WARNING"},
    {"name": "LOW_VIBRATION", "priority": 3, "condition": lambda r: r["vibration"] < 0.4, "action": "WARNING"},
    {"name": "HIGH_VIBRATION", "priority": 3, "condition": lambda r: r["vibration"] > 1.6, "action": "WARNING"},
    {"name": "HIGH_CURRENT", "priority": 1, "condition": lambda r: r["current"] > 22, "action": "WARNING"},
    {"name": "LOW_CURRENT", "priority": 1, "condition": lambda r: r["current"] < 8, "action": "WARNING"},
]


# ---------------------------------------------------------------------------
# STEP 3 — Detect machine state from the rules
# ---------------------------------------------------------------------------
def evaluate_rules(reading, rules):
    """Return (rule_name, action) for the first matching rule, checked in
    priority order (lowest number first). If nothing matches, return
    ("NO_RULE_FIRED", "CONTINUE_NORMAL")."""
    # TODO: sort `rules` by priority, then check each rule's condition(reading)

    required_sensors= ["temperature","vibration","pressure","current"]
    missing= [sensor for sensor in required_sensors if sensor not in reading or sensor is None]
    if missing:
        return "MISSING_SENSOR_DATA", "IGNORE"
    for rule in sorted(rules, key=lambda r: r["priority"]):
        if rule["condition"](reading):
            return rule["name"], rule["action"]
    return "NO_RULE_FIRED", "CONTINUE_NORMAL"


# ---------------------------------------------------------------------------
# STEP 4 — Trigger an action when a rule fires
# ---------------------------------------------------------------------------
message_map = {
    "STOP_MACHINE": "[STOP_MACHINE] The machine has been stopped due to a safety violation.",
    "CONTINUE_NORMAL": "[CONTINUE_NORMAL] The machine is operating normally.",
    "WARNING": "[WARNING] The machine is operating with warnings."
}
def take_action(action):
    """Return a human-readable string describing what happens for this action."""
    # TODO: map action names (e.g. "STOP_MACHINE") to a message
    for action_name, message in message_map.items():
        if action_name == action:
            return message
    return f"(no handler yet for action: {action})"


# ---------------------------------------------------------------------------
# STEP 5 — Log every decision made
# ---------------------------------------------------------------------------
def log_decision(reading, rule_name, action):
    """Append one line to LOG_FILE with the reading, rule fired, and action."""
    # TODO: open(LOG_FILE, "a") and write a line
    with open(LOG_FILE, "a") as f:
        f.write(f"Reading: {reading}, Rule Fired: {rule_name}, Action: {action}\n")
    pass


# ---------------------------------------------------------------------------
# STEP 6 — Add a second sensor to the system
# TODO: add e.g. "current" to generate_sensor_data(), then use it in a rule
# ---------------------------------------------------------------------------


def main():
    machine_alert=[0]*5
    max_count=0
    for machine in range(5):
        count=0
        for tick in range(1, 11):
            reading = generate_sensor_data()
            rule_name, action = evaluate_rules(reading, RULES)
            outcome = take_action(action)

            print(f"[Tick {tick:02d}] SENSE -> {reading}")
            print(f"           THINK -> {rule_name}")
            print(f"           ACT   -> {outcome}\n")

            if action != "CONTINUE_NORMAL" and action != "WARNING":
                count+=1

            log_decision(reading, rule_name, action)
            time.sleep(0.2)
        if count >= max_count:
            max_count=count
            machine_alert[machine]=count

    print("Immediate action required on Machine",*[i+1 for i in range(len(machine_alert)) if machine_alert[i]==max_count])


if __name__ == "__main__":
    main()
