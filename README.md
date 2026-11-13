# smp-tracker
ML classifier + coaching layer. Predicts daily goal achievement and provides personalised feedback. 
# File: README.md

# SMP Tracker

A daily performance tracker for the Self-Made Protocol (SMP) fitness program.
Logs sleep, water intake, and step count. Predicts goal achievement using a
trained Random Forest classifier and generates a coaching message.

## What It Does

- Accepts daily check-in data (sleep hours, water glasses, steps)
- Predicts whether the 10,000-step goal will be hit
- Returns a confidence score and a direct coaching message
- Exports a weekly summary report as JSON

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```python
from tracker import analyze_day

result = analyze_day(sleep_hr=7.5, water_glasses=9,  steps= 10,000, bench_kg=88)
print(result["coaching"])
```

## Sample Output

```
Prediction: HIT GOAL (88% confidence)
Coach: Strong inputs, strong output. Baseline is locked in. Keep this pattern consistent.
```

## Stack

Python, scikit-learn, pandas, FastAPI
