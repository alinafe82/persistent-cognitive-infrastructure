#!/usr/bin/env python3
"""Validate local-only network publishing in Docker Compose's normalized JSON."""

import json
import sys


def boundary_errors(model):
    errors = []
    for name, service in model.get("services", {}).items():
        mode = service.get("network_mode", "")
        if mode == "host" or mode.startswith(("container:", "service:")):
            errors.append(
                f"{name}: shared network namespace bypasses the local boundary"
            )
        for port in service.get("ports", []):
            if port.get("host_ip") not in {"127.0.0.1", "::1"}:
                errors.append(f"{name}: published port must bind to loopback")
    return errors


if __name__ == "__main__":
    model = json.load(sys.stdin)
    if not model.get("services"):
        raise SystemExit("Compose model has no services")
    errors = boundary_errors(model)
    if errors:
        raise SystemExit("\n".join(errors))
    print("Compose published ports are restricted to loopback")
