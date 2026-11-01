"""INERT trusted-factory composition: Account + existing appointments + Patient.

No engine, listener, migration or role is created. Default composition is the
unchanged narrow app with Account/Patient absent. An admitted isolated factory
owns all injected engines, dependency sessions, cleanup and signing secret.
"""


def build_patient_account_appointments_app(*, enabled=False, auth_engine=None,
        patient_engine=None, signing_secret=None, expected_database=None, expected_port=None):
    from stage1_account_http_adapter import build_account_appointments_app

    if enabled is not True:
        if (enabled is not False or auth_engine is not None or patient_engine is not None
                or signing_secret is not None or expected_database is not None or expected_port is not None):
            raise ValueError("patient composition disabled")
        return build_account_appointments_app()

    # Auth engine guards/environment remain in the unchanged Account factory.
    # This service additionally checks the separately injected tenant endpoint,
    # NullPool, hidden parameters, exact database and per-call SQL identities.
    from app.services.patient_registration import PatientRegistrationService
    service = PatientRegistrationService(patient_engine, enabled=True,
        signing_secret=signing_secret, expected_database=expected_database, expected_port=expected_port)
    app = build_account_appointments_app(enabled=True, auth_engine=auth_engine,
        expected_database=expected_database, expected_port=expected_port)
    from app.routers.patient_registration import router
    from fastapi import APIRouter
    from fastapi.routing import APIRoute
    expected = {
        "/api/v1/patients/search": "GET",
        "/api/v1/patients/registrations/prepare": "POST",
        "/api/v1/patients/registrations/confirm": "POST",
        "/api/v1/patients/registrations/{command_key}": "GET",
        "/api/v1/patients/{patient_id}": "GET",
    }
    selected = list(router.routes)
    if (len(selected) != len(expected)
            or any(not isinstance(route, APIRoute) or route.path not in expected
                   or route.methods != {expected[route.path]} for route in selected)
            or {route.path for route in selected} != set(expected)):
        raise ValueError("patient route set changed")
    if any(getattr(route, "path", "").startswith("/api/v1/patients") for route in app.router.routes):
        raise ValueError("patient route collision")
    subset = APIRouter()
    subset.routes.extend(selected)
    app.include_router(subset)
    app.state.patient_registration_service = service
    return app
