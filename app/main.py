from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.graphql.router import graphql_router
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.middleware.shadow_instrumentation import ShadowAfterSendMiddleware
from app.routers import application_auth, auth, consultation, search, patients, clinical, letters, appointments, diary, diary_events, practice, practice_administration
from app.config import settings, REPO_ROOT
from app.services.diary.shadow_instrumentation import shadow_instrumentation_runtime

# Canonical deployment profile resolved by app.config.Settings ("dev" |
# "staging" | "production"). All serving decisions below consume this value;
# unknown profiles fail closed during Settings construction, before the app
# below is built.
is_dev = settings.environment == "dev"

app = FastAPI(
    title="EMR4 Centaur API",
    version="0.1.0",
    docs_url="/docs" if is_dev else None,
    redoc_url="/redoc" if is_dev else None,
    swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect" if is_dev else None,
)

app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Deprecation"],
)
app.add_middleware(
    ShadowAfterSendMiddleware,
    runtime=shadow_instrumentation_runtime,
)

if is_dev:
    app.mount("/taskpane", StaticFiles(directory=str(REPO_ROOT / "EMR4 Sidebar" / "src" / "taskpane"), html=True), name="taskpane")

app.include_router(auth.router)
app.include_router(application_auth.router)
app.include_router(patients.router)
app.include_router(clinical.router)
app.include_router(letters.router)
app.include_router(consultation.router)
app.include_router(search.router)
app.include_router(appointments.router)
app.include_router(diary.router)
app.include_router(diary_events.router)
if is_dev:
    from app.routers import bernie_dev
    app.include_router(bernie_dev.router)
app.include_router(practice.router)
app.include_router(practice_administration.router)
app.include_router(graphql_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "EMR4 Centaur API"}
