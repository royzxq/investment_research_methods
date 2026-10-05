"""Gemini MCP 的离线协议、来源和故障路由回归；不访问真实 API。"""
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
import urllib.error
from unittest.mock import patch


SERVER = Path(__file__).resolve().parents[1] / ".codex/mcp/gemini_search_mcp.py"
SPEC = importlib.util.spec_from_file_location("gemini_search_mcp", SERVER)
mcp = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mcp)


class SearchBehaviorTests(unittest.TestCase):
    def test_missing_credentials_returns_fallback_without_network(self):
        with patch.object(mcp, "API_KEY", ""), patch.object(mcp, "search_via_api") as api:
            result = mcp.run_search("public query")
        self.assertTrue(result.startswith("[SEARCH_FAILED]"))
        self.assertIn("内置网页搜索", result)
        api.assert_not_called()

    def test_grounded_answer_preserves_source_links(self):
        response = {
            "candidates": [{
                "content": {"parts": [{"text": "A public answer."}]},
                "groundingMetadata": {"groundingChunks": [{
                    "web": {"title": "Original source", "uri": "https://example.org/source"}
                }]},
            }]
        }
        with patch.object(mcp, "API_KEY", "test-key"), patch.object(
            mcp.urllib.request, "urlopen", return_value=io.BytesIO(json.dumps(response).encode())
        ) as transport:
            result = mcp.search_via_api("public query")
        self.assertIn("A public answer.", result)
        self.assertIn("Original source — https://example.org/source", result)
        request = transport.call_args.args[0]
        self.assertNotIn("test-key", request.full_url)
        self.assertEqual(request.get_header("X-goog-api-key"), "test-key")
        self.assertEqual(json.loads(request.data)["tools"], [{"google_search": {}}])

    def test_transient_failure_retries_once(self):
        with patch.object(mcp, "API_KEY", "test-key"), patch.object(
            mcp, "search_via_api", side_effect=[RuntimeError("temporary failure"), "answer"]
        ) as api, patch.object(mcp.time, "sleep") as pause:
            result = mcp.run_search("public query")
        self.assertEqual(result, "answer")
        self.assertEqual(api.call_count, 2)
        pause.assert_called_once_with(2)

    def test_auth_failure_does_not_retry_or_echo_credentials(self):
        key = "credential-used-only-in-this-test"
        error = urllib.error.HTTPError(
            "https://example.org", 403, "Forbidden", {},
            io.BytesIO(json.dumps({"error": {"message": f"Rejected key {key}"}}).encode()),
        )
        with patch.object(mcp, "API_KEY", key), patch.object(
            mcp, "search_via_api", side_effect=error
        ) as api, patch.object(mcp.time, "sleep") as pause:
            result = mcp.run_search("public query")
        self.assertTrue(result.startswith("[SEARCH_FAILED]"))
        self.assertIn("HTTP 403", result)
        self.assertIn("[REDACTED]", result)
        self.assertNotIn(key, result)
        api.assert_called_once()
        pause.assert_not_called()

    def test_redaction_happens_before_error_truncation(self):
        key = "credential-used-only-in-this-test"
        with patch.object(mcp, "API_KEY", key), patch.object(
            mcp, "search_via_api", side_effect=RuntimeError("x" * 190 + key)
        ), patch.object(mcp.time, "sleep"):
            result = mcp.run_search("public query")
        self.assertNotIn("credential", result)
        self.assertTrue(result.startswith("[SEARCH_FAILED]"))


class StdioProtocolTests(unittest.TestCase):
    def test_client_handshake_discovery_failures_and_ping(self):
        requests = [
            {"id": 1, "method": "initialize", "params": {"protocolVersion": "2025-03-26"}},
            {"method": "notifications/initialized"},
            {"id": 2, "method": "tools/list"},
            {"id": 3, "method": "tools/call", "params": {
                "name": "gemini_web_search", "arguments": {"query": "public query"}
            }},
            {"id": 4, "method": "tools/call", "params": {
                "name": "unknown", "arguments": {"query": "public query"}
            }},
            {"id": 5, "method": "tools/call", "params": {
                "name": "gemini_web_search", "arguments": {"query": "  "}
            }},
            {"id": 6, "method": "tools/call", "params": {
                "name": "gemini_web_search", "arguments": {"query": 123}
            }},
            {"id": 7, "method": "ping"},
            {"id": 8, "method": "unknown-method"},
        ]
        env = os.environ.copy()
        env.pop("GEMINI_API_KEY", None)
        env.pop("GEMINI_SEARCH_API_TIMEOUT", None)
        process = subprocess.run(
            [sys.executable, str(SERVER)], env=env,
            input="\n".join(json.dumps({"jsonrpc": "2.0", **r}) for r in requests) + "\n",
            capture_output=True, text=True, timeout=10, check=True,
        )
        replies = {r["id"]: r for r in map(json.loads, process.stdout.splitlines())}
        self.assertEqual(set(replies), set(range(1, 9)))
        self.assertEqual(replies[1]["result"]["protocolVersion"], "2025-03-26")
        self.assertEqual(replies[2]["result"]["tools"][0]["name"], "gemini_web_search")
        for request_id in (3, 4, 5, 6):
            self.assertTrue(replies[request_id]["result"]["isError"])
            self.assertTrue(replies[request_id]["result"]["content"][0]["text"].startswith("[SEARCH_FAILED]"))
        self.assertEqual(replies[7]["result"], {})
        self.assertEqual(replies[8]["error"]["code"], -32601)
        self.assertEqual(process.stderr, "")


if __name__ == "__main__":
    unittest.main()
