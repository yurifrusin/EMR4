FROM docker.io/library/python@sha256:a190708a2dec1bd18b1decb539f8e8f5407abaa9bf39cacda583f7f8c11db322 AS relay
LABEL org.opencontainers.image.title="EMR4 A3/B3 Vertex one-use relay"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /workspace
COPY --chown=65532:65532 relay.py /workspace/relay.py
USER 65532:65532
ENTRYPOINT ["python", "/workspace/relay.py"]

FROM docker.io/library/python@sha256:a190708a2dec1bd18b1decb539f8e8f5407abaa9bf39cacda583f7f8c11db322 AS work-cell
LABEL org.opencontainers.image.title="EMR4 A3/B3 Vertex credential-free work cell"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /workspace
COPY --chown=65532:65532 cell.py /workspace/cell.py
COPY --chown=65532:65532 cell-request.json /workspace/cell-request.json
USER 65532:65532
ENTRYPOINT ["python", "/workspace/cell.py"]
