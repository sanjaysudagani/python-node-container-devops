"""HTTP contract tests for the Python status service."""

import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from app import StatusHandler


class StatusHandlerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), StatusHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_root_confirms_request_and_container(self) -> None:
        with urlopen(f"{self.base_url}/", timeout=2) as response:
            payload = json.load(response)
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers.get_content_type(), "application/json")
        self.assertEqual(payload["service"], "python-api")
        self.assertEqual(payload["status"], "working")
        self.assertIn("container is working", payload["message"])

    def test_health_endpoint(self) -> None:
        with urlopen(f"{self.base_url}/health", timeout=2) as response:
            payload = json.load(response)
        self.assertEqual(payload, {"service": "python-api", "status": "healthy"})

    def test_unknown_route_returns_json_404(self) -> None:
        with self.assertRaises(HTTPError) as error:
            urlopen(f"{self.base_url}/missing", timeout=2)
        self.assertEqual(error.exception.code, 404)
        self.assertEqual(json.loads(error.exception.read()), {"service": "python-api", "status": "not_found"})

    def test_post_is_rejected(self) -> None:
        request = Request(f"{self.base_url}/", data=b"{}", method="POST")
        with self.assertRaises(HTTPError) as error:
            urlopen(request, timeout=2)
        self.assertEqual(error.exception.code, 405)
        self.assertEqual(error.exception.headers.get("Allow"), "GET")


if __name__ == "__main__":
    unittest.main()
