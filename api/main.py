from fastapi import FastAPI

from api.routes.predict import router as predict_router

app = FastAPI(
    title="Healthcare Claim AI System",
    version="1.0.0"
)

app.include_router(predict_router)

@app.get("/")
def health_check():
    return {
        "status": "running"
    }
