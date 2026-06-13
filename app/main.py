import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.routers import auth, consultation, search, patients, clinical, letters

app = FastAPI(title="EMR4 Centaur API", version="0.1.0")

app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static/audio", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(clinical.router)
app.include_router(letters.router)
app.include_router(consultation.router)
app.include_router(search.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "EMR4 Centaur API"}
