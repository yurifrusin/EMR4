FROM docker.io/library/python@sha256:a190708a2dec1bd18b1decb539f8e8f5407abaa9bf39cacda583f7f8c11db322

LABEL org.opencontainers.image.title="Reception One Bureau Model Text Fixture Cell"
LABEL org.opencontainers.image.description="Disposable credential-free authored-synthetic model-output fixture cell"
LABEL org.opencontainers.image.source="https://github.com/sarashera/emr4"
LABEL reception.one.cell.id="reception-one-bureau-model-text-lane-v1"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /workspace
COPY --chown=65532:65532 . /workspace

USER 65532:65532
ENTRYPOINT ["python", "/workspace/cell.py"]
