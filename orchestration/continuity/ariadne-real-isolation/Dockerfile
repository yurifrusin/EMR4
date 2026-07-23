FROM docker.io/library/python@sha256:a190708a2dec1bd18b1decb539f8e8f5407abaa9bf39cacda583f7f8c11db322

LABEL org.opencontainers.image.title="Ariadne Real-Isolation Rehearsal"
LABEL org.opencontainers.image.description="Disposable authored-synthetic isolation rehearsal"
LABEL org.opencontainers.image.source="https://github.com/docker-library/python.git"
LABEL org.opencontainers.image.revision="3362634339580d3232e65a66dd5a36c47ae7ff14"
LABEL org.opencontainers.image.base.name="docker.io/library/python@sha256:a190708a2dec1bd18b1decb539f8e8f5407abaa9bf39cacda583f7f8c11db322"
LABEL ariadne.rehearsal.id="ariadne-real-isolation-rehearsal-v1"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /workspace
COPY --chown=65532:65532 . /workspace

USER 65532:65532
ENTRYPOINT ["python", "/workspace/scripts/ariadne_real_isolation_payload.py"]
