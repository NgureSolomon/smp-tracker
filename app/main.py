#FASTAPI app

from fastapi import FastAPI
from pydantic import BaseModel, Field
import csv
from pathlib import Path
import pandas as pd
from datetime import datetime

app= FastAPI(
    title= "SMP Tracker API",
    description= "A daily performance tracker for the Self-Made Protocol (SMP) fitness program." \
    " Logs sleep, water intake, and step count." \
    " Predicts goal achievement using a trained Random Forest classifier and generates a coaching message. ",
    version= "1.0.0",
)

class DailyCheckIn(BaseModel):
    sleep_hours: float = Field(ge=0, le=24)
    water_intake: int = Field(ge=0, le=10)
    steps: int = Field(ge=0, le=100000)

# Location where daily check-ins will be stored
CSV_FILE = Path("data/checkins.csv")

# Create the data folder if it doesn't exist
CSV_FILE.parent.mkdir(parents=True, exist_ok=True)

@app.get("/")
def home():
    return{
        "message": "Welcome to SMP Tracker API",
        "status": "running"
    }

@app.post("/DailyCheckIn")
def create_checkin(checkin: DailyCheckIn):

    # Get the current date and time
    recorded_at = datetime.now().isoformat(timespec="seconds")

    # Check whether the CSV file exists
    file_exists = CSV_FILE.exists()

    # Add the date column to an existing CSV if necessary
    if file_exists:
        df = pd.read_csv(CSV_FILE)

        if "recorded_at" not in df.columns:
            df["recorded_at"] = ""
            df.to_csv(CSV_FILE, index=False)

    # Open the CSV file in append mode
    with open(CSV_FILE, mode="a", newline="") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "sleep_hours",
                "water_intake",
                "steps",
                "recorded_at"
            ]
        )

        # Write headings for a new file
        if not file_exists:
            writer.writeheader()

        # Save the check-in with its timestamp
        data = checkin.model_dump()
        data["recorded_at"] = recorded_at

        writer.writerow(data)

    return {
        "message": "Daily check-in received",
        "data": data
    }

@app.get("/daily_checkins")
def get_checkins():
    if not CSV_FILE.exists():
        return{
            "message": "No check-ins found",
            "data": []
        }
    df = pd.read_csv(CSV_FILE, keep_default_na=False)
    return{
             "total_checkins": len(df),
            "data": df.to_dict()
    }
@app.get("/weeklySummary")
def weekly_summary():
   
    if not CSV_FILE.exists():
        return {
            "message": "No check-ins available",
            "data": {}
        }

    df = pd.read_csv(CSV_FILE, keep_default_na=False)

    # Remove records without timestamps
    df = df.dropna(subset=[
    "recorded_at",
    "sleep_hours",
    "water_intake",
    "steps"
])

    df = df[df["recorded_at"].astype(str).str.strip() != ""]
    if df.empty:
        return {
            "message": "No dated check-ins available",
            "data": {}
        }

    # Convert timestamps into datetime values
    df["recorded_at"] = pd.to_datetime(df["recorded_at"])

    # Get the current week's records (Monday to Sunday)
    today = pd.Timestamp.today().normalize()
    week_start = today - pd.Timedelta(days=today.weekday())

    weekly_data = df[
        (df["recorded_at"] >= week_start) &
        (df["recorded_at"] < week_start + pd.Timedelta(days=7))
    ]

    if weekly_data.empty:
        return {
            "message": "No check-ins recorded this week",
            "data": {}
        }

    return {
        "message": "Weekly summary generated successfully",
        "data": {
            "week_start": str(week_start.date()),
            "week_end": str((week_start + pd.Timedelta(days=6)).date()),
            "total_checkins": len(weekly_data),
            "days_with_checkins": weekly_data["recorded_at"].dt.date.nunique(),
            "average_sleep": round(weekly_data["sleep_hours"].mean(), 2),
            "average_water_intake": round(weekly_data["water_intake"].mean(), 2),
            "total_steps": int(weekly_data["steps"].sum()),
            "average_steps": round(weekly_data["steps"].mean(), 2),
            "goal_achievements": int((weekly_data["steps"] >= 10000).sum()),
            "goal_achievement_percentage": round(
    (weekly_data["steps"] >= 10000).mean() * 100, 2
)
        }
    }