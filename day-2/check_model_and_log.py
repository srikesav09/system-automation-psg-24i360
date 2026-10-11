import pandas as pd
from pathlib import Path

from history_data_generator import RULES, evaluate_rules, take_action
from model import train_model


HISTORY = Path(__file__).parent.parent / "history.csv"


def combine_decisions(rule_action, ml_state):
    ml_state = str(ml_state).strip().lower()

    if rule_action == "STOP_MACHINE":
        return "STOP_MACHINE"

    if rule_action == "WARNING" or ml_state == "warning":
        return "WARNING"

    return "CONTINUE_NORMAL"

FEATURES = ["temperature", "pressure", "vibration", "rpm", "current"]

def main():
    model = train_model()

    if not HISTORY.exists():
        raise FileNotFoundError(f"History file not found: {HISTORY}")

    history = pd.read_csv(HISTORY)

    missing_columns = [column for column in FEATURES if column not in history.columns]
    if missing_columns:
        raise ValueError(
            f"history.csv is missing columns: {', '.join(missing_columns)}"
        )

    if history.empty:
        raise ValueError("history.csv contains no readings.")

    index = history.sample(n=1).index[0]
    reading = history.loc[index, FEATURES].to_dict()

    rule_name, rule_action = evaluate_rules(reading, RULES)
    input_data = pd.DataFrame([reading], columns=FEATURES)
    ml_state = model.predict(input_data)[0]
    final_action = combine_decisions(rule_action, ml_state)

    print(f"\n{'=' * 40}")
    print(f"Random history row: {index}")
    print(f"Temperature: {reading['temperature']} °C")
    print(f"Pressure:    {reading['pressure']}")
    print(f"Vibration:   {reading['vibration']}")
    print(f"RPM:         {reading['rpm']}")
    print(f"Current:     {reading['current']} A")
    print("-" * 40)
    print(f"Rule:        {rule_name} -> {rule_action}")
    print(f"ML result:   {ml_state}")
    print("-" * 40)
    print(f"Decision:    {take_action(final_action)}")
    print("-" * 40)


if __name__ == "__main__":
    main()