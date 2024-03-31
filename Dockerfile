FROM python:3.10.7
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
RUN pip install -r ./app/requirements.txt
RUN apt-get update && apt-get install -y libgl1-mesa-glx
RUN apt-get update
RUN apt-get install 'ffmpeg'\
    'libsm6'\ 
    'libxext6'  -y