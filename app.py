"""
Core Lattice x Alexa — hackathon demo server (stdlib only).

Serves the web app from ./static and exposes the Core Lattice engine at
POST /api/chat  {"utterance": str, "session_id": str}
GET  /api/health -> {"status": "ok", ...}

Run:  python3 app.py [--port 8080]
"""

import json
import mimetypes
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from core_lattice import engine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")


class Handler(BaseHTTPRequestHandler):
    server_version = "CoreLatticeDemo/0.1"

    # ------------------------------------------------------------- routing
    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            return self._json({"status": "ok", "engine": "core-lattice-scaffold"})
        self._serve_static(path)

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/chat":
            return self._handle_chat()
        self._json({"error": "not found"}, status=404)

    # ---------------------------------------------------------------- chat
    def _handle_chat(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
        except ValueError:
            length = 0
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            body = {}
        utterance = str(body.get("utterance", ""))
        session_id = str(body.get("session_id", "default"))[:64]
        try:
            result = engine.process(utterance, session_id)
        except Exception as exc:  # scaffold must never 500 on stage
            result = {"text": f"Engine hiccup (scaffold): {exc}", "intent": "error"}
        self._json(result)

    # --------------------------------------------------------------- static
    def _serve_static(self, path):
        rel = path.lstrip("/") or "index.html"
        # block path traversal
        safe = os.path.normpath(rel)
        if safe.startswith("..") or os.path.isabs(safe):
            return self._json({"error": "forbidden"}, status=403)
        full = os.path.join(STATIC_DIR, safe)
        if os.path.isdir(full):
            full = os.path.join(full, "index.html")
        if not os.path.isfile(full):
            return self._json({"error": "not found"}, status=404)
        ctype, _ = mimetypes.guess_type(full)
        with open(full, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(data)

    # ------------------------------------------------------------------ io
    def _json(self, obj, status=200):
        data = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):  # quieter logs
        sys.stderr.write("demo: " + fmt % args + "\n")


def main():
    port = 8080
    if "--port" in sys.argv:
        try:
            port = int(sys.argv[sys.argv.index("--port") + 1])
        except (ValueError, IndexError):
            pass
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Core Lattice demo live at http://127.0.0.1:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()
