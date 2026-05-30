# Containerized MCP server for the CLI-Anything · ArcGIS Pro live bridge.
#
# The server is stdlib-only, so this image needs nothing but Python. It starts and
# answers MCP introspection (initialize, tools/list) on its own — handy for Glama
# scoring / discovery. Actual tool *calls* forward to the in-Pro add-in bridge, so
# point ARCGIS_BRIDGE_URL at a reachable ArcGIS Pro host to drive a live session,
# e.g.  -e ARCGIS_BRIDGE_URL=http://host.docker.internal:5005/
FROM python:3.12-slim

WORKDIR /app
COPY mcp_server.py /app/mcp_server.py

# Default points at the host loopback; override at runtime for a remote bridge.
ENV ARCGIS_BRIDGE_URL=http://127.0.0.1:5005/

ENTRYPOINT ["python", "mcp_server.py"]
