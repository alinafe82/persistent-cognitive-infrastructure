#!/usr/bin/env bash
set -euo pipefail

docker compose -f deployments/docker-compose.yml up --build

