"use strict";

const assert = require("node:assert/strict");
const { after, before, test } = require("node:test");
const { createServer } = require("../server");

let server;
let baseUrl;

before(async () => {
  server = createServer();
  await new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", resolve);
  });
  baseUrl = `http://127.0.0.1:${server.address().port}`;
});

after(async () => {
  await new Promise((resolve, reject) => {
    server.close((error) => (error ? reject(error) : resolve()));
  });
});

test("root confirms request and container are working", async () => {
  const response = await fetch(`${baseUrl}/`);
  const payload = await response.json();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type"), /application\/json/);
  assert.equal(payload.service, "node-api");
  assert.equal(payload.status, "working");
  assert.match(payload.message, /container is working/);
});

test("health endpoint reports healthy", async () => {
  const response = await fetch(`${baseUrl}/health`);
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), { service: "node-api", status: "healthy" });
});

test("unknown route returns JSON 404", async () => {
  const response = await fetch(`${baseUrl}/missing`);
  assert.equal(response.status, 404);
  assert.deepEqual(await response.json(), { service: "node-api", status: "not_found" });
});

test("non-GET method is rejected", async () => {
  const response = await fetch(`${baseUrl}/`, { method: "POST", body: "{}" });
  assert.equal(response.status, 405);
  assert.equal(response.headers.get("allow"), "GET");
  assert.deepEqual(await response.json(), { service: "node-api", status: "method_not_allowed" });
});
