import glob
import json
import os
import time
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Create "responses" folder if it doesn't exist
os.makedirs("responses", exist_ok=True)


class InputData(BaseModel):
    message: str
    job_id: str
    lockit_url: str
    consumed_chars: int | None = None # optional, defaults to None
    average_score: float | None = None # optional, defaults to None


def delete_old_files():
    maximum_age = 2
    for root, dirs, files in os.walk("responses"):
        for file in files:
            file_path = os.path.join(root, file)
            age_days = get_file_age(file_path)
            if age_days is not None:
                print(f"File: {file_path}")
                print(f"The file is {int(age_days)} days old")
                if age_days > maximum_age:
                    try:
                        os.remove(file_path)
                        print(f"File '{file_path}' has been deleted.")
                    except FileNotFoundError:
                        print(f"File '{file_path}' not found.")
                    except PermissionError:
                        print(f"Permission denied: Cannot delete '{file_path}'.")
                    except Exception as e:
                        print(f"An error occurred while trying to delete the file: {e}")


def get_file_age(file_path):
    try:
        current_time = time.time()
        last_modified_time = os.path.getmtime(file_path)
        file_age_seconds = current_time - last_modified_time
        file_age_days = file_age_seconds / (24 * 3600)  # Convert to days
        return file_age_days
    except FileNotFoundError:
        print(f"The file '{file_path}' does not exist.")
        return None, None


@app.post("/delivery")
async def save_json(data: InputData):
    try:
        # Generate a timestamp-based filename
        filename = datetime.now().strftime("%Y%m%d%H%M%S%f") + ".json"
        filepath = os.path.join("responses", filename)

        # Save the JSON data
        with open(filepath, "w") as f:
            json.dump(data.model_dump(), f, indent=4)

        return {"message": "Data saved successfully", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    delete_old_files()


@app.get("/jobs")
async def get_job_ids() -> list:
    # get a list of JSON files in the 'responses' directory
    json_files = glob.glob("responses/*.json")

    # Extract job_id values
    job_ids = []
    for file in json_files:
        with open(file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if "job_id" in data:
                    job_ids.append(data["lockit_url"])
            except json.JSONDecodeError:
                print(f"Warning: Could not parse {file}")

    # print job IDs (equivalent to grep output)
    return sorted(job_ids)
