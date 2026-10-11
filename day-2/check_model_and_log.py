import pandas as pd
from pathlib import Path

from history_data_generator import RULES, evaluate_rules, take_action
from model import train_model


HISTORY_FILE = Path(__file__).parent.parent / "history.csv"
FEATURES = ["temperature", "pressure", "vibration", "rpm", "current"]


def combine_decisions(rule_action, ml_state):
    ml_state = str(ml_state).strip().lower()

    if rule_action == "STOP_MACHINE" and ml_state != "normal":
        return "STOP_MACHINE"

    if ml_state == "warning":
        return "WARNING"

    return "CONTINUE_NORMAL"



def main():
    model = train_model()

    history = pd.read_csv(HISTORY_FILE)


    reading = history[FEATURES].sample(n=1).iloc[0].to_dict()
    
    rule_name, rule_action = evaluate_rules(reading, RULES)

    input_data = pd.DataFrame([reading], columns=FEATURES)
    ml_state = model.predict(input_data)[0]

    final_action = combine_decisions(rule_action, ml_state)

    print("Sensor reading:", reading)
    print("Rule result:", rule_name, "->", rule_action)
    print("ML prediction:", ml_state)
    print("Combined result:", take_action(final_action))


if __name__ == "__main__":
    main()