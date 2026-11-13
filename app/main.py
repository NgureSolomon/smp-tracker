#FASTAPI app

from fastapi import FastAPI
from pydantic import BaseModel, Field
import csv
from pathlib import Path

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
     # Check whether the CSV file already exists
    file_exists = CSV_FILE.exists()

    # Open the CSV file in append mode
    with open(CSV_FILE, mode="a",#opens the file in append mode
               newline="") as file:

      # Define the column names
        writer = csv.DictWriter(
            file,
            fieldnames=["sleep_hours", "water_intake", "steps"]
        )

        # Write column headings if this is a new file
        if not file_exists:
            writer.writeheader()

        # Save the submitted check-in
        writer.writerow(checkin.model_dump())
    return {
        "message": "Daily check-in received",
        "data": checkin
    }


