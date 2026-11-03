"use strict";

const http = require("node:http");

function sendJson(response, statusCode, payload, extraHeaders = {}) {
  const body = JSON.stringify(payload);
  response.writeHead(statusCode, {
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": Buffer.byteLength(body),
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
    ...extraHeaders,
  });
  response.end(body);
}

function createServer() {
  return http.createServer((request, response) => {
    if (request.method !== "GET") {
      request.resume();
      sendJson(
        response,
        405,
        { service: "node-api", status: "method_not_allowed" },
        { Allow: "GET" },
      );
      return;
    }

    const path = new URL(request.url || "/", "http://localhost").pathname;
    if (path === "/") {
      sendJson(response, 200, {
        service: "node-api",
        status: "working",
        message: "Node.js HTTP request is working; container is working.",
      });
    } else if (path === "/health") {
      sendJson(response, 200, { service: "node-api", status: "healthy" });
    } else {
      sendJson(response, 404, { service: "node-api", status: "not_found" });
    }
  });
}

function main() {
  const host = process.env.HOST || "0.0.0.0";
  const port = Number.parseInt(process.env.PORT || "3000", 10);
  if (!Number.isInteger(port) || port < 1 || port > 65535) {
    throw new Error("PORT must be an integer between 1 and 65535");
  }

  const server = createServer();
  server.listen(port, host, () => {
    console.log(`Node.js status service listening on ${host}:${port}`);
  });

  const shutdown = () => server.close(() => process.exit(0));
  process.on("SIGTERM", shutdown);
  process.on("SIGINT", shutdown);
}

if (require.main === module) {
  main();
}

module.exports = { createServer };
