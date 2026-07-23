# syntax=docker/dockerfile:1
ARG NODE_IMAGE=node:24-bookworm-slim

FROM ${NODE_IMAGE} AS broker
LABEL org.opencontainers.image.title="EMR4 Ariadne one-use DeepSeek broker" \
      emr4.ariadne.role="broker" \
      emr4.ariadne.protocol="deepseek-in-cell-generated-draft-v1"
WORKDIR /opt/ariadne
COPY ariadne_deepseek_one_use_broker.mjs /opt/ariadne/broker.mjs
USER node
CMD ["node", "/opt/ariadne/broker.mjs"]

FROM ${NODE_IMAGE} AS work-cell
ARG CLAUDE_CODE_VERSION=2.1.201
LABEL org.opencontainers.image.title="EMR4 Ariadne DeepSeek work cell" \
      emr4.ariadne.role="work-cell" \
      emr4.ariadne.protocol="deepseek-in-cell-generated-draft-v1" \
      emr4.ariadne.claude-code-version="${CLAUDE_CODE_VERSION}"
RUN npm install --global --omit=dev "@anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}" \
    && claude --version \
    && npm cache clean --force
ENV CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 \
    DISABLE_AUTOUPDATER=1 \
    DISABLE_ERROR_REPORTING=1 \
    DISABLE_TELEMETRY=1
WORKDIR /work
COPY ariadne_deepseek_work_cell_launcher.mjs /opt/ariadne/launcher.mjs
COPY attempt.json /opt/ariadne/attempt.json
COPY output.schema.json /opt/ariadne/output.schema.json
USER node
CMD ["node", "/opt/ariadne/launcher.mjs"]
