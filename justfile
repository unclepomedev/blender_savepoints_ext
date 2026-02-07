sync-vendor:
    uv run python tools/sync_vendor.py

fmt:
    uv run ruff format savepoints_ext tests