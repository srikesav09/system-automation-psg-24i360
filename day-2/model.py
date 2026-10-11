import csv
import pandas as pd
from pathlib import Path
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


DATA_FILE = Path(__file__).parent / "data" / "day2_sample.csv"


def train_model():
    df=pd.read_csv(DATA_FILE)
    X = df[["temperature", "pressure", "vibration", "rpm", "current"]]
    Y = df["state"]

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.25, random_state=42,stratify=Y)
    model = RandomForestClassifier(n_estimators=200,max_depth=8,class_weight="balanced",random_state=42)
    model.fit(X_train, Y_train)

    acc= accuracy_score(Y_test, model.predict(X_test))
    print(f"Model trained. Hold-out accuracy: {acc:.0%}\n")
    return model

def main():
    model = train_model()

if __name__ == "__main__":
    main()