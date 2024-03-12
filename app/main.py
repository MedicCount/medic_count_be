from fastapi import FastAPI, File, UploadFile
from PIL import Image
import numpy as np
import io

import tensorflow as tf
import joblib

app = FastAPI()

# load detection model
# loaded_model = joblib.load("model.joblib")

def detect_count_image(image):
    return 112

    pil_image = Image.open(io.BytesIO(image))
    pil_image = pil_image.resize((224, 224))
    resized_image = np.array(pil_image)
    resized_image = resized_image.reshape(-1, 224, 224, 3)

    # detection = loaded_model.predict(resized_image).tolist()[0]
    # return detection


@app.get("/")
async def read_root():
    return {"message": "Hello MediCount !"}

@app.post("/detect_count/")
async def detect_count(file: UploadFile = File(...)):
    image = await file.read()
    count = detect_count_image(image)
    return {"count": count}