FROM node:24-bookworm-slim@sha256:235600a8101ab264e117b1768e925532262668dc9b581ef1dd7d96ced463b8e7

ENV NODE_ENV=production \
    PORT=8080

WORKDIR /srv/raisa
COPY --chown=65532:65532 server.mjs ./server.mjs
COPY --chown=65532:65532 public ./public

USER 65532:65532
EXPOSE 8080
CMD ["node", "server.mjs"]
