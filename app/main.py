import fastapi
import uvicorn

app = fastapi.FastAPI()

@app.get("/")
def test_get():
    return {"message": "Hello, Medicine"}