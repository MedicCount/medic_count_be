from fastapi import FastAPI, File, UploadFile
from PIL import Image
import numpy as np
import io
import os
import subprocess

import tensorflow as tf

app = FastAPI()

model_path = 'app/model/best.pt'

def detect_count_image(image):
    pil_image = Image.open(io.BytesIO(image))
    pil_image.save('app/model/image/tmp.jpg')
    image_path = 'app/model/image/tmp.jpg'
    
    command = f"python app/model/yolov5/detect.py --source \"{image_path}\" --weights {model_path} --save-txt"
    subprocess.run(command, shell=True)
    return 1123


@app.get("/")
async def read_root():
    return {"message": "Hello MediCount !"}

@app.post("/detect_count/")
async def detect_count(file: UploadFile = File(...)):
    image = await file.read()
    count = detect_count_image(image)
    return {"count": count}