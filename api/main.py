# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.predict import router as predict_router
from api.routes.auth_routes import router as auth_router

app = FastAPI(title="Healthcare Claim AI System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(predict_router)

@app.get("/")
def health_check():
    return {"status": "running"}