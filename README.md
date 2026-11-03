# Python + Node.js Container Health Demo

A small, production-minded DevOps demo with two independent HTTP services:

- **Python API** on `http://localhost:8001`
- **Node.js API** on `http://localhost:3001`

Opening either root URL returns JSON confirming that the HTTP request reached the service and that its container is working. Each service also exposes `/health` for Docker and orchestration health checks.

## Quick start

Requirements: Docker Desktop (or Docker Engine) with the Docker Compose plugin.

```sh
docker compose up --build -d
```

Open these URLs in a browser, or use `curl`:

```sh
curl http://localhost:8001/
curl http://localhost:3001/
curl http://localhost:8001/health
curl http://localhost:3001/health
docker compose ps
```

Expected root response (service name differs):

```json
{
  "service": "python-api",
  "status": "working",
  "message": "Python HTTP request is working; container is working."
}
```

Stop the services with `docker compose down`. Host ports can be changed in `.env`; see `.env.example`.

## Endpoints

| Service | Host URL | `GET /` | `GET /health` |
| --- | --- | --- | --- |
| Python | `http://localhost:8001` | Service status JSON | `200` health JSON |
| Node.js | `http://localhost:3001` | Service status JSON | `200` health JSON |

Unknown paths return JSON `404`; non-GET methods return JSON `405` with an `Allow: GET` header. The apps bind to `0.0.0.0` inside the container, while Compose publishes ports only on the local host interface by default.

## Development and tests

The services use only their languages' standard libraries; there are no third-party runtime packages to install.

```sh
make test
make compose-config
make up
make smoke
make logs
make down
```

Or run tests directly:

```sh
(cd python-service && python3 -m unittest discover -s tests -v)
(cd node-service && node --test)
```

The Python tests need Python 3.9 or newer; the Node service targets Node.js 24. The containers themselves use the official Python 3.14 and Node.js 24 images.

## DevOps features

- Separate, small container images built from official base images.
- Non-root runtime users, read-only container root filesystems, dropped Linux capabilities, and `no-new-privileges` in Compose.
- Docker health checks for both services; Compose restart policy and process init.
- Localhost-only port publishing and bounded container PIDs/temp storage.
- Automated unit and container smoke tests on pushes and pull requests through GitHub Actions.
- Weekly Dependabot checks for base-image and GitHub Actions updates.
- No secrets, external services, databases, or third-party application dependencies are needed.

## Project layout

```text
.
├── .github/
│   ├── dependabot.yml
│   └── workflows/ci.yml
├── node-service/
│   ├── Dockerfile
│   ├── package.json
│   ├── server.js
│   └── test/server.test.js
├── python-service/
│   ├── Dockerfile
│   ├── app.py
│   └── tests/test_app.py
├── compose.yaml
├── Makefile
└── README.md
```

## Troubleshooting

- **Docker daemon unavailable:** start Docker Desktop, then rerun `docker compose up --build -d`.
- **Port already in use:** set `PYTHON_PORT` or `NODE_PORT` in `.env`, then recreate the services with `docker compose up --build -d`.
- **Check health/logs:** run `docker compose ps` and `docker compose logs --tail=100`.
- **Clean up:** `docker compose down` stops and removes only this project's containers and network.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the change and test workflow and [SECURITY.md](SECURITY.md) for reporting security concerns.
