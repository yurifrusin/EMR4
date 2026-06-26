import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.routers import auth, consultation, search, patients, clinical, letters, appointments, diary, bernie_dev
from app.config import settings

app = FastAPI(title="EMR4 Centaur API", version="0.1.0")

app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static/audio", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/taskpane", StaticFiles(directory="EMR4 Sidebar/src/taskpane", html=True), name="taskpane")

app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(clinical.router)
app.include_router(letters.router)
app.include_router(consultation.router)
app.include_router(search.router)
app.include_router(appointments.router)
app.include_router(diary.router)
app.include_router(bernie_dev.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "EMR4 Centaur API"}
