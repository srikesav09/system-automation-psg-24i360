# Robotic Arm Joint Health Monitor

## Design and thresholds

The monitor checks every shoulder, elbow, and wrist reading before using the predictive model. A reading at or above 150 Nm torque, 95 °C, or 12 mm/s vibration triggers `EMERGENCY_STOP`. Torque also has a joint-specific operating cap: 140 Nm at the shoulder, 105 Nm at the elbow, and 65 Nm at the wrist. These are deliberately conservative demo limits, chosen below the example hard ceiling where a smaller joint has a lower load rating. In a real installation, the manufacturer’s rated loads, safe operating envelope, sensor accuracy, and a formal hazard analysis must set these numbers. The deterministic check does not call the model.

## Prediction and notes

`historical_joint_readings.csv` contains 72 synthetic labeled readings. A Random Forest estimates the chance that a joint develops wear within 30 days. Relevant free-text notes (backlash, bearing noise, grinding, vibration, leaks, and related terms) are scanned independently. Any hard limit means immediate stop. A torque spoof suspicion means maintenance is scheduled. Otherwise, high model risk (at least 0.65) schedules maintenance; a relevant note together with moderate model risk (at least 0.30) also schedules maintenance. A note or moderate risk alone yields `MONITOR`; neither signal yields `SAFE`. This conservative combination treats a note as corroboration for borderline model evidence.

## Spoof defense and limitations

The system cross-checks reported torque against an independent motor-current sensor and a per-joint torque-per-amp calibration (8 Nm/A shoulder, 6 Nm/A elbow, 4 Nm/A wrist). A difference greater than 18 Nm is flagged as spoofing and schedules maintenance; a hard-limit reading still takes precedence and stops the arm. This catches a torque-only falsification when the current sensor and calibration remain trustworthy. It does not catch coordinated spoofing of both torque and current, a compromised calibration, gradual falsification within the tolerance, or physical faults that do not affect this relationship. Production systems should use authenticated sensor channels, time-series plausibility checks, independent redundant sensors, and a safety-rated controller.

## Run it

From this folder, install the repository dependencies with `pip install -r ../../requirements.txt`, then run `python arm_health.py --demo`. The demo prints examples of all four decisions. Run `python arm_health.py` for decisions based on the included maintenance log.
