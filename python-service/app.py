"""Minimal dependency-free HTTP status service for the Python container."""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit


class StatusHandler(BaseHTTPRequestHandler):
    server_version = "PythonStatusService/1.0"
    sys_version = ""

    def _send_json(
        self,
        status_code: int,
        payload: dict[str, str],
        extra_headers: tuple[tuple[str, str], ...] = (),
        include_body: bool = True,
    ) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        for name, value in extra_headers:
            self.send_header(name, value)
        self.end_headers()
        if include_body:
            self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        path = urlsplit(self.path).path
        if path == "/":
            self._send_json(
                200,
                {
                    "service": "python-api",
                    "status": "working",
                    "message": "Python HTTP request is working; container is working.",
                },
            )
        elif path == "/health":
            self._send_json(200, {"service": "python-api", "status": "healthy"})
        else:
            self._send_json(404, {"service": "python-api", "status": "not_found"})

    def _method_not_allowed(self, include_body: bool = True) -> None:
        self.close_connection = True
        self._send_json(
            405,
            {"service": "python-api", "status": "method_not_allowed"},
            extra_headers=(("Allow", "GET"), ("Connection", "close")),
            include_body=include_body,
        )

    def do_HEAD(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        self._method_not_allowed(include_body=False)

    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        self._method_not_allowed()

    def do_PUT(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        self._method_not_allowed()

    def do_PATCH(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        self._method_not_allowed()

    def do_DELETE(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        self._method_not_allowed()

    def do_OPTIONS(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        self._method_not_allowed()

    def do_TRACE(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        self._method_not_allowed()

    def do_CONNECT(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        self._method_not_allowed()

    def log_message(self, format_string: str, *args: object) -> None:
        # Omit request paths, which can contain sensitive query parameters.
        print(f"{self.log_date_time_string()} {self.client_address[0]} request handled", flush=True)


def main() -> None:
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer((host, port), StatusHandler)
    print(f"Python status service listening on {host}:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
