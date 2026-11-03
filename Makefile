PYTHON ?= python3
NODE ?= node

.PHONY: test test-python test-node compose-config up down logs ps smoke

test: test-python test-node

test-python:
	cd python-service && $(PYTHON) -m unittest discover -s tests -v

test-node:
	cd node-service && $(NODE) --test

compose-config:
	docker compose config --quiet

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs --tail=100 -f

ps:
	docker compose ps

smoke:
	curl --fail --silent --show-error http://localhost:$${PYTHON_PORT:-8001}/health
	curl --fail --silent --show-error http://localhost:$${NODE_PORT:-3001}/health
