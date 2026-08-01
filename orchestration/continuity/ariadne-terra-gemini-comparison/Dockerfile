# syntax=docker/dockerfile:1
ARG NODE_IMAGE=node:24-bookworm-slim

FROM ${NODE_IMAGE} AS broker
LABEL org.opencontainers.image.title="EMR4 Ariadne comparative one-use broker" \
      emr4.ariadne.role="broker" \
      emr4.ariadne.protocol="terra-gemini-comparative-rehearsal-v1"
WORKDIR /opt/ariadne
COPY ariadne_comparative_one_use_broker.mjs /opt/ariadne/broker.mjs
COPY ariadne_provider_contracts.mjs /opt/ariadne/ariadne_provider_contracts.mjs
USER node
CMD ["node", "/opt/ariadne/broker.mjs"]

FROM ${NODE_IMAGE} AS work-cell
LABEL org.opencontainers.image.title="EMR4 Ariadne provider-neutral work cell" \
      emr4.ariadne.role="work-cell" \
      emr4.ariadne.protocol="terra-gemini-comparative-rehearsal-v1"
WORKDIR /opt/ariadne
COPY ariadne_comparative_work_cell_launcher.mjs /opt/ariadne/launcher.mjs
COPY comparison-manifest.json /opt/ariadne/comparison-manifest.json
COPY shared-task.json /opt/ariadne/shared-task.json
COPY full-output.schema.json /opt/ariadne/full-output.schema.json
COPY provider-output.schema.json /opt/ariadne/provider-output.schema.json
USER node
CMD ["node", "/opt/ariadne/launcher.mjs"]
