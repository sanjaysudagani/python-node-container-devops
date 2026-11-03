FROM node:26.13.0-bookworm-slim

ENV NODE_ENV=production \
    PORT=3000

WORKDIR /app

COPY --chown=node:node server.js ./server.js

USER node
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD ["node", "-e", "fetch('http://127.0.0.1:3000/health').then((response) => process.exit(response.ok ? 0 : 1)).catch(() => process.exit(1))"]

CMD ["node", "server.js"]
