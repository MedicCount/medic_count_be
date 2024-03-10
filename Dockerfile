FROM python:3.10.13
WORKDIR /app
COPY . /app
RUN pip install -r ./app/requirements.txt