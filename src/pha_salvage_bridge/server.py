"""
Standalone HTTP Server & Interactive 3D Showpiece Dashboard for `PHA × SALVAGE-AI` Bridge (`server.py`).

Runs on port 8790 (`http://127.0.0.1:8790`) so it never conflicts with the
`spatial-clinical-router` server on port 8780.
"""

from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import sys
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pha_salvage_bridge.benchmark import run_bidirectional_pha_benchmark

STATIC_LANDING_PATH = Path(__file__).resolve().parent / "static" / "landing.html"


class PHABridgeRequestHandler(BaseHTTPRequestHandler):
    benchmark_cache = None

    @classmethod
    def get_benchmark(cls) -> dict:
        if cls.benchmark_cache is None:
            cls.benchmark_cache = run_bidirectional_pha_benchmark()
        return cls.benchmark_cache

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/landing", "/index.html"):
            body = STATIC_LANDING_PATH.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif parsed.path == "/api/benchmark":
            data = self.get_benchmark()
            body = json.dumps(data, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif parsed.path.startswith("/api/scenario/"):
            sc_id = parsed.path.split("/api/scenario/", 1)[1].strip().upper()
            data = self.get_benchmark()
            match = next((s for s in data.get("flagship_scenarios", []) if s["scenario_id"] == sc_id), None)
            if match is None:
                self.send_error(404, f"Scenario {sc_id} not found")
                return
            body = json.dumps(match, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404, "Not Found")


def main() -> None:
    parser = argparse.ArgumentParser(description="Standalone PHA x SALVAGE-AI Bridge Server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8790)
    args = parser.parse_args()
    server = HTTPServer((args.host, args.port), PHABridgeRequestHandler)
    print(f"[PHA x SALVAGE-AI Bridge] Interactive 3D Showpiece Server listening on http://{args.host}:{args.port}/landing")
    server.serve_forever()


if __name__ == "__main__":
    main()
