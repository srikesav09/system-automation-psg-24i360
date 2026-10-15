from __future__ import annotations
import argparse
import csv
import math
import re
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier

HERE = Path(__file__).resolve().parent
DATA_FILE = HERE / "data" / "historical_joint_readings.csv"
LOG_FILE = HERE / "maintenance_log.txt"
FEATURES = ["torque_nm", "temperature_c", "vibration_mm_s", "motor_current_a"]
JOINTS = ("shoulder", "elbow", "wrist")

HARD_LIMITS = {
    "torque_nm": 150.0,
    "temperature_c": 95.0,
    "vibration_mm_s": 12.0,
}
TORQUE_LIMITS = {"shoulder": 140.0, "elbow": 105.0, "wrist": 65.0}
TORQUE_PER_AMP = {"shoulder": 8.0, "elbow": 6.0, "wrist": 4.0}
SPOOF_TOLERANCE_NM = 18.0
WEAR_KEYWORDS = (
    "grinding", "backlash", "overheat", "overheating", "bearing noise",
    "unusual vibration", "oil leak", "lubrication", "loose joint", "wear",
)


def train_model(path: Path = DATA_FILE) -> RandomForestClassifier:
    """Train a wear-risk classifier from historical per-joint readings."""
    rows = list(csv.DictReader(path.open(encoding="utf-8", newline="")))
    if len(rows) < 50:
        raise ValueError("Historical dataset must contain at least 50 labeled readings.")
    model = RandomForestClassifier(n_estimators=160, random_state=24, class_weight="balanced")
    model.fit([[float(row[name]) for name in FEATURES] for row in rows],
              [int(row["wear_within_30_days"]) for row in rows])
    return model


def scan_notes(path: Path = LOG_FILE) -> dict[tuple[str, str], list[str]]:
    """Map (arm, joint) to relevant technician notes; ignore unrelated notes."""
    notes: dict[tuple[str, str], list[str]] = {}
    pattern = re.compile(r"arm\s*(\d+).*?\b(shoulder|elbow|wrist)\b", re.I)
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.search(line)
        if not match or not any(word in line.lower() for word in WEAR_KEYWORDS):
            continue
        key = (f"ARM-{int(match.group(1)):02d}", match.group(2).lower())
        notes.setdefault(key, []).append(line.strip())
    return notes


def check_reading(arm: str, joint: str, reading: dict[str, float]) -> tuple[bool, bool, list[str]]:
    """Return (danger, spoof_suspected, reasons)."""
    reasons: list[str] = []
    danger = False
    torque_limit = min(HARD_LIMITS["torque_nm"], TORQUE_LIMITS[joint])
    for feature, limit in (("torque_nm", torque_limit), ("temperature_c", HARD_LIMITS["temperature_c"]),
                           ("vibration_mm_s", HARD_LIMITS["vibration_mm_s"])):
        if reading[feature] >= limit:
            danger = True
            reasons.append(f"{feature}={reading[feature]:.1f} reached safety limit {limit:.1f}")
    expected_torque = reading["motor_current_a"] * TORQUE_PER_AMP[joint]
    spoof = abs(reading["torque_nm"] - expected_torque) > SPOOF_TOLERANCE_NM
    if spoof:
        reasons.append(f"torque/current mismatch ({reading['torque_nm']:.1f} Nm reported, {expected_torque:.1f} Nm expected)")
    return danger, spoof, reasons


def decide_arm(arm: str, readings: list[dict[str, float | str]], model: RandomForestClassifier,
               notes: dict[tuple[str, str], list[str]]) -> dict[str, object]:
    """Apply immediate hard stop first, then combine model, notes, and sensor trust."""
    assessed = []
    for item in readings:
        joint = str(item["joint"])
        reading = {name: float(item[name]) for name in FEATURES}
        danger, spoof, reasons = check_reading(arm, joint, reading)
        risk = float(model.predict_proba([[reading[name] for name in FEATURES]])[0][1])
        joint_notes = notes.get((arm, joint), [])
        assessed.append({"joint": joint, "danger": danger, "spoof": spoof, "risk": risk,
                         "notes": joint_notes, "reasons": reasons})

    if any(row["danger"] for row in assessed):
        decision = "EMERGENCY_STOP"
    elif any(row["spoof"] for row in assessed):
        decision = "SCHEDULE_MAINTENANCE"
    else:
        high_risk = any(row["risk"] >= 0.65 for row in assessed)
        note_signal = any(row["notes"] for row in assessed)
        moderate_risk = any(row["risk"] >= 0.30 for row in assessed)
        if high_risk or (note_signal and moderate_risk):
            decision = "SCHEDULE_MAINTENANCE"
        elif note_signal or moderate_risk:
            decision = "MONITOR"
        else:
            decision = "SAFE"

    reasons = [f"{row['joint']}: {reason}" for row in assessed for reason in row["reasons"]]
    reasons.extend(f"{row['joint']}: technician note: {note}" for row in assessed for note in row["notes"])
    if not reasons:
        reasons.append("No hard limit, spoof mismatch, elevated model risk, or relevant note.")
    return {"arm": arm, "decision": decision, "joints": assessed, "reasons": reasons}


def sample_readings(arm: str, *, torque: float = 50, temperature: float = 55,
                    vibration: float = 1.0, current: float = 6.25,
                    joint: str = "shoulder") -> list[dict[str, float | str]]:
    
    values = {
        "shoulder": (torque, temperature, vibration, current),
        "elbow": (35.0, 52.0, 0.9, 35.0 / TORQUE_PER_AMP["elbow"]),
        "wrist": (20.0, 48.0, 0.7, 20.0 / TORQUE_PER_AMP["wrist"]),
    }
    result = []
    for name, (t, temp, vib, amps) in values.items():
        if name == joint:
            t, temp, vib, amps = torque, temperature, vibration, current
        result.append({"joint": name, "torque_nm": t, "temperature_c": temp,
                       "vibration_mm_s": vib, "motor_current_a": amps})
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="show one example of every decision")
    args = parser.parse_args()
    model = train_model()
    notes = scan_notes()
    if args.demo:
        examples = [
            ("SAFE", "ARM-90", sample_readings("ARM-90")),
            ("MONITOR", "ARM-01", sample_readings("ARM-01")),
            ("SCHEDULE_MAINTENANCE", "ARM-02", sample_readings("ARM-02", torque=82, current=6.25)),
            ("EMERGENCY_STOP", "ARM-03", sample_readings("ARM-03", temperature=99)),
        ]
        for expected, arm, readings in examples:
            result = decide_arm(arm, readings, model, notes)
            print(f"Expected {expected:22} Got {result['decision']:22} {arm}")
        return
    for arm in sorted({key[0] for key in notes}):
        result = decide_arm(arm, sample_readings(arm), model, notes)
        print(f"{arm}: {result['decision']} — {'; '.join(result['reasons'])}")


if __name__ == "__main__":
    main()
