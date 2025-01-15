from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
from datetime import datetime

app = FastAPI()

# Create "responses" folder if it doesn't exist
os.makedirs("responses", exist_ok=True)

class InputData(BaseModel):
    foo: str
    baz: str

@app.post("/save-json")
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
