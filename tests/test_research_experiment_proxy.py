import hashlib
import http.client
import json
import socket
import struct
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from scripts.research_experiment_proxy import ObservingProxy, estimate_flash_peak_cost


def message(usage=None):
    return {"id": "msg_test", "type": "message", "model": "DeepSeek-V4.1-Flash-1017",
            "content": [{"type": "text", "text": "PRIVATE RESPONSE"}],
            "usage": {"input_tokens": 100, "output_tokens": 20} if usage is None else usage}


def event(data):
    return ("event: " + data["type"] + "\ndata: " + json.dumps(data) + "\n\n").encode()


class CostTests(unittest.TestCase):
    def test_plain_tokens_peak_price(self):
        cost = estimate_flash_peak_cost({"input_tokens": 1_000_000, "output_tokens": 1_000_000})
        self.assertEqual(cost["status"], "estimated")
        self.assertAlmostEqual(cost["usd_upper_bound"], 1.5)

    def test_total_and_cache_split_do_not_double_count(self):
        usage = {"prompt_tokens": 100, "prompt_cache_hit_tokens": 90,
                 "prompt_cache_miss_tokens": 10, "input_tokens": 100,
                 "cache_read_input_tokens": 90, "output_tokens": 5}
        cost = estimate_flash_peak_cost(usage)
        self.assertEqual(cost["input_tokens_total"], 100)
        self.assertEqual(cost["status"], "estimated")

    def test_hit_and_miss_support_total_or_uncached_input(self):
        for input_value in (100, 10):
            cost = estimate_flash_peak_cost({"input_tokens": input_value,
                                            "prompt_cache_hit_tokens": 90,
                                            "prompt_cache_miss_tokens": 10,
                                            "output_tokens": 5})
            self.assertEqual(cost["input_tokens_total"], 100)
            self.assertEqual(cost["status"], "estimated")

    def test_ambiguous_anthropic_cache_remains_unknown(self):
        usage = {"input_tokens": 100, "cache_read_input_tokens": 90, "output_tokens": 5}
        self.assertEqual(estimate_flash_peak_cost(usage)["status"], "unknown")
        self.assertEqual(estimate_flash_peak_cost(usage, input_tokens_semantics="total")["input_tokens_total"], 100)
        self.assertEqual(estimate_flash_peak_cost(usage, input_tokens_semantics="uncached")["input_tokens_total"], 190)

    def test_cache_creation_nested_is_not_added_twice(self):
        usage = {"input_tokens": 10, "cache_read_input_tokens": 20,
                 "cache_creation_input_tokens": 30,
                 "cache_creation": {"ephemeral_5m_input_tokens": 10, "ephemeral_1h_input_tokens": 20},
                 "output_tokens": 5}
        self.assertEqual(estimate_flash_peak_cost(usage, input_tokens_semantics="uncached")["input_tokens_total"], 60)

    def test_missing_or_unsupported_usage_is_not_zero(self):
        for usage in (None, {}, {"input_tokens": 100},
                      {"input_tokens": True, "output_tokens": 1},
                      {"input_tokens": 1, "output_tokens": -1},
                      {"input_tokens": 1, "output_tokens": 1, "cache_read_input_tokens": None},
                      {"input_tokens": 1, "output_tokens": 1, "cache_read_input_tokens": True},
                      {"input_tokens": 1, "output_tokens": 1, "new_tokens": 10}):
            cost = estimate_flash_peak_cost(usage)
            self.assertEqual(cost["status"], "unknown", usage)
            self.assertIsNone(cost["usd_upper_bound"])
            self.assertTrue(cost["reasons"])

    def test_non_token_server_tool_counts_remain_separate(self):
        cost = estimate_flash_peak_cost({"input_tokens": 10, "output_tokens": 2,
                                         "server_tool_use": {"web_search_requests": 3, "web_fetch_requests": 1}})
        self.assertEqual(cost["status"], "estimated")
        self.assertEqual(cost["non_token_usage"], {"web_search_requests": 3, "web_fetch_requests": 1})
        self.assertIn("2026-11-01", cost["non_token_pricing_note"])
        self.assertIsNone(estimate_flash_peak_cost({"input_tokens": 1, "output_tokens": 1})["non_token_usage"])

    def test_real_deepseek_smoke_usage_service_tier_is_metadata(self):
        # smoke-01: 2026-10-21, CC request observed by the isolated proxy.
        for tier in (None, "standard"):
            usage = {"cache_creation_input_tokens": 0, "cache_read_input_tokens": 0,
                     "input_tokens": 1511, "output_tokens": 88, "service_tier": tier}
            cost = estimate_flash_peak_cost(usage)
            self.assertEqual(cost["status"], "estimated")
            self.assertEqual(cost["usage_metadata"], {"service_tier": tier})
            self.assertAlmostEqual(cost["usd_upper_bound"], 0.0005589)
            self.assertEqual(cost["reasons"], [])
        usage["unexpected_metered_tokens"] = 42
        self.assertEqual(estimate_flash_peak_cost(usage)["status"], "unknown")

    def test_conflicts_are_unknown(self):
        variants = [
            {"prompt_tokens": 100, "prompt_cache_hit_tokens": 90, "prompt_cache_miss_tokens": 50, "output_tokens": 1},
            {"input_tokens": 100, "output_tokens": 5, "completion_tokens": 4},
            {"input_tokens": 3, "cache_read_input_tokens": 10, "output_tokens": 1},
        ]
        for usage in variants:
            self.assertEqual(estimate_flash_peak_cost(usage, input_tokens_semantics="total")["status"], "unknown")


class ProxyTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.log = Path(self.temp.name) / "traffic.jsonl"
        self.received = []
        self.lock = threading.Lock()
        self.status = 200
        self.body = json.dumps(message()).encode()
        self.count_body = b'{"input_tokens":36}'
        self.count_status = 200
        self.content_type = "application/json"
        self.extra_headers = {}
        self.response_parts = None
        self.partial_length = None
        self.chunked_truncation = False
        self.before_headers_gate = None
        self.after_first_part_gate = None
        self.after_second_part_gate = None
        self.upstream_received = threading.Event()
        test = self

        class Upstream(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *_):
                pass

            def do_POST(self):
                raw = self.rfile.read(int(self.headers["Content-Length"]))
                with test.lock:
                    test.received.append({"path": self.path, "raw": raw,
                                          "headers": {k.lower(): v for k, v in self.headers.items()}})
                test.upstream_received.set()
                if test.before_headers_gate is not None:
                    test.before_headers_gate.wait(5)
                is_count = self.path.endswith("/count_tokens")
                body = test.count_body if is_count else test.body
                self.send_response(test.count_status if is_count else test.status)
                self.send_header("Content-Type", "application/json" if is_count else test.content_type)
                if test.chunked_truncation:
                    self.send_header("Transfer-Encoding", "chunked")
                else:
                    self.send_header("Content-Length", str(test.partial_length if test.partial_length is not None else len(body)))
                for key, value in test.extra_headers.items():
                    self.send_header(key, value)
                self.send_header("Connection", "close")
                self.end_headers()
                try:
                    if test.chunked_truncation:
                        # Declare more bytes than actually sent, then close.
                        self.wfile.write(("%x\r\n" % (len(body) + 10)).encode() + body)
                        self.wfile.flush()
                        self.close_connection = True
                        return
                    for index, part in enumerate(([body] if is_count else test.response_parts) or [body]):
                        self.wfile.write(part)
                        self.wfile.flush()
                        if index == 0 and test.after_first_part_gate is not None:
                            test.after_first_part_gate.wait(5)
                        if index == 1 and test.after_second_part_gate is not None:
                            test.after_second_part_gate.wait(5)
                        if test.response_parts:
                            time.sleep(0.005)
                except (BrokenPipeError, ConnectionResetError):
                    pass
                self.close_connection = True

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Upstream)
        self.server.daemon_threads = True
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.origin = "http://127.0.0.1:" + str(self.server.server_address[1])

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(2)
        self.temp.cleanup()

    def proxy(self, **kwargs):
        return ObservingProxy("REAL-KEY-DO-NOT-LOG", self.log, {"cc", "dsh"},
                              _test_upstream=self.origin, **kwargs)

    def request(self, proxy, *, arm="cc", suffix="/v1/messages?beta=true", payload=None,
                raw=None, headers=None, method="POST"):
        if payload is None:
            payload = {"model": "deepseek-flash", "max_tokens": 500,
                       "messages": [{"role": "user", "content": "PRIVATE PROMPT"}]}
        raw = json.dumps(payload).encode() if raw is None else raw
        request = Request(proxy.url(arm) + suffix, data=raw, method=method,
                          headers=headers or {"Content-Type": "application/json"})
        try:
            response = urlopen(request, timeout=5)
        except HTTPError as error:
            response = error
        with response:
            return response.status, dict(response.headers), response.read()

    def records(self, expected=1):
        # Closing a response can precede the handler's final log flush.
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            raw = self.log.read_text() if self.log.exists() else ""
            # A concurrent append may expose an unfinished final JSON line.
            rows = raw.split("\n")[:-1]
            if len(rows) >= expected:
                return [json.loads(line) for line in rows]
            time.sleep(0.005)
        self.fail("proxy did not flush expected records")

    def test_records_waits_for_complete_newline_terminated_json(self):
        record = {"request_id": "complete"}
        complete = json.dumps(record) + "\n"
        self.log.write_text("")
        for partial in ('{"request_id": "comp', complete.rstrip("\n")):
            with self.subTest(partial=partial):
                with patch.object(Path, "read_text", side_effect=[partial, complete]) as read:
                    self.assertEqual(self.records(), [record])
                    self.assertEqual(read.call_count, 2)
        with patch.object(Path, "read_text", return_value='{"request_id":\n'):
            with self.assertRaises(json.JSONDecodeError):
                self.records()

    def test_nonstream_forwarding_exact_body_and_safe_metadata(self):
        payload = {"model": "deepseek-flash", "max_tokens": 500,
                   "system": "PRIVATE SYSTEM", "thinking": {"type": "enabled", "budget_tokens": 200},
                   "output_config": {"effort": "high"},
                   "messages": [{"role": "user", "content": "PRIVATE PROMPT"}],
                   "tools": [{"name": "Read", "description": "PRIVATE TOOL DESCRIPTION"}]}
        raw = json.dumps(payload, indent=2).encode()
        with self.proxy() as proxy:
            status, _, body = self.request(proxy, payload=payload, raw=raw)
            row = self.records()[0]
            self.assertEqual(status, 200)
            self.assertEqual(body, self.body)
            self.assertEqual(self.received[0]["raw"], raw)
            self.assertEqual(self.received[0]["path"], "/anthropic/v1/messages")
            self.assertTrue(row["complete"])
            self.assertEqual(row["request_sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(row["observed_model"], "DeepSeek-V4.1-Flash-1017")
            self.assertEqual(row["thinking_type"], "enabled")
            self.assertEqual(row["output_effort"], "high")
            self.assertEqual(row["request_tool_names"], ["Read"])
            self.assertEqual(proxy.summary()["by_arm"]["cc"]["complete"], 1)
        text = self.log.read_text()
        for secret in ("REAL-KEY-DO-NOT-LOG", "PRIVATE PROMPT", "PRIVATE RESPONSE", "PRIVATE SYSTEM", "PRIVATE TOOL DESCRIPTION"):
            self.assertNotIn(secret, text)

    def test_client_auth_and_headers_never_leak(self):
        self.extra_headers = {"x-api-key": "UPSTREAM-KEY", "Authorization": "UPSTREAM-AUTH",
                              "Set-Cookie": "SECRET-COOKIE", "Connection": "x-secret",
                              "x-secret": "PRIVATE-HEADER"}
        headers = {"Authorization": "Bearer DUMMY", "x-api-key": "DUMMY",
                   "x-private": "PRIVATE-HEADER", "Cookie": "CLIENT-COOKIE",
                   "anthropic-version": "2023-06-01", "Connection": "anthropic-beta",
                   "anthropic-beta": "should-be-filtered", "Content-Type": "application/json"}
        with self.proxy() as proxy:
            parsed = proxy.url("cc").split(":")
            connection = http.client.HTTPConnection("127.0.0.1", int(parsed[2].split("/")[0]), timeout=5)
            connection.request("POST", "/cc/messages", json.dumps({"model": "deepseek-flash"}), headers)
            response = connection.getresponse()
            response_headers = dict(response.headers)
            response.read()
            connection.close()
            self.records()
        sent = self.received[0]["headers"]
        self.assertEqual(sent["authorization"], "Bearer REAL-KEY-DO-NOT-LOG")
        self.assertEqual(sent["x-api-key"], "REAL-KEY-DO-NOT-LOG")
        self.assertEqual(sent["accept-encoding"], "identity")
        self.assertEqual(sent["anthropic-version"], "2023-06-01")
        for key in ("cookie", "x-private", "anthropic-beta"):
            self.assertNotIn(key, sent)
        for key in ("x-api-key", "Authorization", "Set-Cookie", "x-secret"):
            self.assertNotIn(key, response_headers)
        self.assertNotIn("PRIVATE-HEADER", self.log.read_text())

    def test_allowed_route_forms(self):
        with self.proxy() as proxy:
            for suffix in ("/messages", "/v1/messages", "/v1/messages?beta=true"):
                self.assertEqual(self.request(proxy, arm="dsh", suffix=suffix)[0], 200)
            self.records(3)
        self.assertEqual(len(self.received), 3)

    def test_invalid_paths_queries_and_model_fail_closed(self):
        with self.proxy() as proxy:
            for suffix in ("/models", "/../messages", "/messages?key=SECRET", "/messages?beta=false",
                           "/messages?beta=true&key=SECRET", "/messages/", "/%2e%2e/messages", "/v2/messages"):
                self.assertEqual(self.request(proxy, suffix=suffix)[0], 404)
            for model in ("deepseek-flash[1m]", "deepseek-pro", "claude-sonnet", None):
                self.assertEqual(self.request(proxy, payload={"model": model})[0], 400)
            self.records(12)
        self.assertEqual(self.received, [])
        self.assertNotIn("SECRET", self.log.read_text())

    def test_unknown_arm_is_not_forwarded(self):
        with self.proxy() as proxy:
            with self.assertRaises(ValueError):
                proxy.url("other")
            origin = proxy.url("cc").rsplit("/", 1)[0]
            with self.assertRaises(HTTPError) as caught:
                urlopen(Request(origin + "/other/messages", data=b"{}"), timeout=5)
            self.assertEqual(caught.exception.code, 404)
            self.records()
        self.assertEqual(self.received, [])

    def test_rejected_model_keeps_only_bounded_public_metadata(self):
        payload = {"model": "claude-haiku-4-5-20251001", "max_tokens": 1024,
                   "thinking": {"type": "adaptive", "private": "PRIVATE THINKING"},
                   "output_config": {"effort": "high"}, "stream": True,
                   "messages": [{"role": "user", "content": "PRIVATE REJECTED PROMPT"}]}
        with self.proxy() as proxy:
            self.assertEqual(self.request(proxy, payload=payload)[0], 400)
            row = self.records()[0]
            self.assertEqual(row["error_class"], "ModelNotAllowed")
            self.assertEqual(row["model"], "claude-haiku-4-5-20251001")
            self.assertEqual(row["max_tokens"], 1024)
            self.assertEqual(row["thinking_type"], "adaptive")
            self.assertEqual(row["output_effort"], "high")
            self.assertTrue(row["streaming"])
            self.assertFalse(row["forwarded"])
            for index, model in enumerate(("deepseek-flash[1m]", "x" * 129, "PRIVATE MODEL WITH SPACES"), 2):
                payload["model"] = model
                self.assertEqual(self.request(proxy, payload=payload)[0], 400)
                rows = self.records(index)
                self.assertEqual(rows[-1]["model"], model if index == 2 else "<other>")
            self.assertEqual(proxy.summary()["forwarded_requests"], 0)
        self.assertEqual(self.received, [])
        text = self.log.read_text()
        for private in ("PRIVATE REJECTED PROMPT", "PRIVATE THINKING", "PRIVATE MODEL WITH SPACES", "x" * 129):
            self.assertNotIn(private, text)

    def test_offline_policy_blocks_all_server_types_before_forwarding(self):
        with self.proxy(allow_server_tools=False) as proxy:
            for index, tool_type in enumerate(("web_search_20250305", "web_fetch_20250910",
                                               "web_search", "unknown_server_tool", None), 1):
                payload = {"model": "deepseek-flash", "max_tokens": 100,
                           "messages": [{"role": "user", "content": "PRIVATE OFFLINE PROMPT"}],
                           "tools": [{"type": tool_type, "name": "WebSearch", "description": "PRIVATE TOOL DESCRIPTION"}]}
                raw = json.dumps(payload).encode()
                self.assertEqual(self.request(proxy, payload=payload, raw=raw)[0], 403)
                row = self.records(index)[-1]
                self.assertEqual(row["error_class"], "OfflineServerToolBlocked")
                self.assertFalse(row["forwarded"])
                self.assertEqual(row["cost"]["status"], "not_forwarded")
                self.assertEqual(row["model"], "deepseek-flash")
                self.assertEqual(row["request_sha256"], hashlib.sha256(raw).hexdigest())
                self.assertIsNotNone(row["messages_sha256"])
                self.assertFalse(row["allow_server_tools"])
            self.assertEqual(proxy.summary()["forwarded_requests"], 0)
            self.assertEqual(proxy.summary()["unknown_usage_requests"], 0)
            for index, tool in enumerate(({"name": "WebSearch", "input_schema": {"type": "object"}},
                                           {"type": "custom", "name": "WebSearch", "input_schema": {"type": "object"}}), 6):
                payload = {"model": "deepseek-flash", "tools": [tool]}
                raw = json.dumps(payload).encode()
                self.assertEqual(self.request(proxy, payload=payload, raw=raw)[0], 200)
                self.records(index)
                self.assertEqual(self.received[-1]["raw"], raw)
            self.assertFalse(proxy.summary()["allow_server_tools"])
            self.assertEqual(proxy.summary()["forwarded_requests"], 2)
        self.assertEqual(len(self.received), 2)
        self.assertNotIn("PRIVATE OFFLINE PROMPT", self.log.read_text())
        self.assertNotIn("PRIVATE TOOL DESCRIPTION", self.log.read_text())

    def test_default_policy_allows_server_tools(self):
        payload = {"model": "deepseek-flash", "tools": [{"type": "web_search_20250305", "name": "web_search"}]}
        with self.proxy() as proxy:
            self.assertEqual(self.request(proxy, payload=payload)[0], 200)
            row = self.records()[0]
            self.assertTrue(row["allow_server_tools"])
            self.assertTrue(row["forwarded"])

    def test_count_tokens_transparent_and_separate_from_generation_cost(self):
        self.count_body = b'{"input_tokens":36,"private":"PRIVATE COUNT BODY"}'
        payload = {"model": "deepseek-flash", "messages": [{"role": "user", "content": "PRIVATE COUNT PROMPT"}]}
        raw = json.dumps(payload, indent=2).encode()
        with self.proxy() as proxy:
            status, _, body = self.request(proxy, suffix="/v1/messages/count_tokens", payload=payload, raw=raw,
                                          headers={"x-api-key": "DUMMY", "Authorization": "Bearer DUMMY"})
            row = self.records()[0]
            self.assertEqual(status, 200)
            self.assertEqual(body, self.count_body)
            self.assertTrue(row["forwarded"])
            self.assertTrue(row["complete"])
            self.assertEqual(row["request_kind"], "token_count")
            self.assertEqual(row["input_tokens_count"], 36)
            self.assertIsNone(row["usage"])
            self.assertEqual(row["cost"]["status"], "not_disclosed")
            self.assertIsNone(row["cost"]["usd_upper_bound"])
            self.assertEqual(self.received[0]["path"], "/anthropic/v1/messages/count_tokens")
            self.assertEqual(self.received[0]["raw"], raw)
            self.assertEqual(self.received[0]["headers"]["x-api-key"], "REAL-KEY-DO-NOT-LOG")
            summary = proxy.summary()
            self.assertEqual(summary["token_count_forwarded_requests"], 1)
            self.assertEqual(summary["token_count_completed_requests"], 1)
            self.assertEqual(summary["generation_forwarded_requests"], 0)
            self.assertEqual(summary["known_token_usd_upper_bound"], 0)
            self.assertEqual(summary["token_count_fee_status"], "not_disclosed")
            self.assertEqual(proxy.summary()["unknown_usage_requests"], 0)
            self.assertEqual(self.request(proxy)[0], 200)
            rows = self.records(2)
            self.assertEqual(rows[1]["request_kind"], "generation")
            self.assertEqual(proxy.summary()["generation_forwarded_requests"], 1)
            self.assertGreater(proxy.summary()["known_token_usd_upper_bound"], 0)
        self.assertEqual(len(self.received), 2)
        for private in ("REAL-KEY-DO-NOT-LOG", "DUMMY", "PRIVATE COUNT BODY", "PRIVATE COUNT PROMPT"):
            self.assertNotIn(private, self.log.read_text())

    def test_count_routes_keep_flash_and_offline_tool_policy(self):
        with self.proxy(allow_server_tools=False) as proxy:
            self.assertEqual(self.request(proxy, suffix="/messages/count_tokens", payload={"model": "deepseek-pro"})[0], 400)
            self.records()
            self.assertEqual(self.request(proxy, suffix="/messages/count_tokens", payload={
                "model": "deepseek-flash", "tools": [{"type": "web_search_20250305", "name": "web_search"}]})[0], 403)
            rows = self.records(2)
            self.assertEqual(rows[-1]["error_class"], "OfflineServerToolBlocked")
            self.assertEqual(rows[-1]["request_kind"], "token_count")
            self.assertEqual(proxy.summary()["forwarded_requests"], 0)
            self.assertEqual(proxy.summary()["token_count_rejected_requests"], 2)
            self.assertEqual(self.request(proxy, suffix="/messages/count_tokens", payload={
                "model": "deepseek-flash", "tools": [{"name": "WebSearch", "input_schema": {"type": "object"}}]})[0], 200)
            self.records(3)
            self.assertEqual(proxy.summary()["token_count_completed_requests"], 1)
        self.assertEqual(len(self.received), 1)

    def test_failed_count_does_not_become_unknown_generation_usage(self):
        self.count_status = 400
        self.count_body = b'{"type":"error","error":{"message":"PRIVATE COUNT ERROR"}}'
        with self.proxy() as proxy:
            self.assertEqual(self.request(proxy, suffix="/messages/count_tokens")[0], 400)
            row = self.records()[0]
            self.assertFalse(row["complete"])
            self.assertIsNone(row["input_tokens_count"])
            self.assertEqual(row["cost"]["status"], "not_disclosed")
            self.assertEqual(proxy.summary()["token_count_failed_requests"], 1)
            self.assertEqual(proxy.summary()["unknown_usage_requests"], 0)
            self.assertEqual(self.request(proxy)[0], 200)
            self.records(2)
        self.assertNotIn("PRIVATE COUNT ERROR", self.log.read_text())

    def test_count_inflight_close_is_recorded_once_without_generation_charge(self):
        self.before_headers_gate = threading.Event()
        with self.proxy() as proxy:
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(self.request, proxy, suffix="/messages/count_tokens")
                try:
                    self.assertTrue(self.upstream_received.wait(3))
                    self.assertEqual(proxy.summary()["token_count_pending_requests"], 1)
                    self.assertEqual(proxy.summary()["generation_pending_requests"], 0)
                    proxy.close(drain_timeout=0.01)
                    row = self.records()[0]
                    self.assertEqual(row["error_class"], "ProxyClosedWithInFlightRequest")
                    self.assertEqual(row["request_kind"], "token_count")
                    self.assertEqual(row["cost"]["status"], "not_disclosed")
                    final = proxy.summary()
                    self.assertEqual(final["pending_requests"], 0)
                    self.assertEqual(final["token_count_pending_requests"], 0)
                    self.assertEqual(final["token_count_failed_requests"], 1)
                    self.assertEqual(final["unknown_usage_requests"], 0)
                finally:
                    self.before_headers_gate.set()
                try:
                    future.result(timeout=3)
                except (OSError, http.client.HTTPException):
                    pass
            self.assertEqual(len(self.records()), 1)
            self.assertEqual(proxy.summary(), final)

    def test_count_requests_keep_total_request_limit_and_fixed_routes(self):
        with self.proxy(max_requests=1) as proxy:
            self.assertEqual(self.request(proxy, suffix="/messages/count_tokens")[0], 200)
            self.records()
            self.assertEqual(self.request(proxy)[0], 429)
            self.records(2)
            for index, suffix in enumerate(("/v2/messages/count_tokens", "/messages/count_tokens/extra",
                                            "/messages/count_tokens?target=https://evil.invalid"), 3):
                self.assertEqual(self.request(proxy, suffix=suffix)[0], 404)
                self.records(index)
            self.assertEqual(proxy.summary()["forwarded_requests"], 1)
            self.assertEqual(proxy.summary()["generation_forwarded_requests"], 0)
        self.assertEqual(len(self.received), 1)

    def test_invalid_json_and_duplicate_keys(self):
        with self.proxy() as proxy:
            for raw in (b"broken", b'{"model":"deepseek-flash","x":NaN}',
                        b'{"model":"deepseek-flash","model":"deepseek-pro"}'):
                self.assertEqual(self.request(proxy, raw=raw)[0], 400)
            self.records(3)
        self.assertEqual(self.received, [])

    def test_oversized_request_and_wrong_method(self):
        with self.proxy(max_request_bytes=100) as proxy:
            self.assertEqual(self.request(proxy, raw=b"x" * 101)[0], 413)
            self.assertEqual(self.request(proxy, method="GET")[0], 405)
            self.records(2)
        self.assertEqual(self.received, [])

    def test_sse_usage_merge_tools_and_stop(self):
        parts = [event({"type": "message_start", "message": {"model": "deepseek-flash",
                          "usage": {"input_tokens": 100, "output_tokens": 0}}}),
                 event({"type": "content_block_start", "content_block": {"type": "tool_use", "name": "Read", "input": {"secret": "PRIVATE INPUT"}}}),
                 event({"type": "content_block_start", "content_block": {"type": "server_tool_use", "name": "WebSearch"}}),
                 event({"type": "content_block_delta", "delta": {"type": "thinking_delta", "thinking": "PRIVATE THINKING"}}),
                 event({"type": "message_delta", "usage": {"output_tokens": 7, "input_tokens": None}}),
                 event({"type": "message_delta", "usage": {"output_tokens": 9}}),
                 event({"type": "message_stop"})]
        self.body, self.response_parts = b"".join(parts), parts
        self.content_type = "text/event-stream"
        payload = {"model": "deepseek-flash", "stream": True,
                   "messages": [{"role": "user", "content": [{"type": "tool_result", "tool_use_id": "x", "is_error": True, "content": "PRIVATE ERROR"}]}]}
        with self.proxy() as proxy:
            status, _, body = self.request(proxy, payload=payload)
            row = self.records()[0]
            self.assertEqual(status, 200)
            self.assertEqual(body, self.body)
            self.assertTrue(row["complete"])
            self.assertEqual(row["usage"]["input_tokens"], 100)
            self.assertEqual(row["usage"]["output_tokens"], 9)
            self.assertEqual(row["cost"]["status"], "estimated")
            self.assertEqual(row["invalid_usage_fields"], [])
            self.assertEqual(row["response_tool_names"], {"Read": 1, "WebSearch": 1})
            self.assertEqual(row["response_tool_count"], 2)
            self.assertEqual(row["request_tool_result_is_error_count"], 1)
        for secret in ("PRIVATE INPUT", "PRIVATE THINKING", "PRIVATE ERROR"):
            self.assertNotIn(secret, self.log.read_text())

    def test_sse_truncated_and_error_are_incomplete(self):
        for ending in (b"", b'data: {"type":"message_stop"}',
                       event({"type": "error", "error": {"message": "PRIVATE ERROR"}}),
                       b"data: [DONE]\n\n"):
            with self.subTest(ending=ending):
                self.log.unlink(missing_ok=True)
                self.body = event({"type": "message_start", "message": {"model": "deepseek-flash", "usage": {"input_tokens": 1, "output_tokens": 1}}}) + ending
                self.content_type = "text/event-stream"
                with self.proxy() as proxy:
                    self.request(proxy, payload={"model": "deepseek-flash", "stream": True})
                    row = self.records()[0]
                    self.assertFalse(row["complete"])
                    self.assertIsNotNone(row["error_class"])
                    self.assertEqual(row["cost"]["status"], "unknown")
                    self.assertEqual(proxy.summary()["unknown_usage_requests"], 1)
                self.assertNotIn("PRIVATE ERROR", self.log.read_text())

    def test_valid_json_with_truncated_content_length_is_incomplete(self):
        self.partial_length = len(self.body) + 5
        with self.proxy() as proxy:
            # A transport truncation may be surfaced by the client before it
            # returns the otherwise valid JSON body.
            with self.assertRaises(http.client.IncompleteRead):
                self.request(proxy)
            row = self.records()[0]
            self.assertFalse(row["complete"])
            self.assertEqual(row["error_class"], "TruncatedHTTPBody")
            self.assertEqual(row["cost"]["status"], "unknown")

    def test_http_error_status_and_body_preserved(self):
        self.status = 429
        self.body = b'{"type":"error","error":{"message":"PRIVATE PROVIDER ERROR"}}'
        with self.proxy() as proxy:
            status, _, body = self.request(proxy)
            row = self.records()[0]
            self.assertEqual(status, 429)
            self.assertEqual(body, self.body)
            self.assertEqual(row["error_class"], "UpstreamHTTPError")
            self.assertFalse(row["complete"])
        self.assertNotIn("PRIVATE PROVIDER ERROR", self.log.read_text())

    def test_redirect_is_not_followed(self):
        self.status = 307
        self.extra_headers = {"Location": "http://not-allowed.invalid/steal"}
        self.body = b"redirect"
        with self.proxy() as proxy:
            status, headers, _ = self.request(proxy)
            row = self.records()[0]
            self.assertEqual(status, 307)
            self.assertNotIn("Location", headers)
            self.assertFalse(row["complete"])
        self.assertEqual(len(self.received), 1)

    def test_max_requests_is_hard_forwarding_limit(self):
        with self.proxy(max_requests=2) as proxy:
            for index in range(4):
                self.assertEqual(self.request(proxy)[0], 200 if index < 2 else 429)
                self.records(index + 1)
            self.assertEqual(proxy.summary()["forwarded_requests"], 2)
        self.assertEqual(len(self.received), 2)

    def test_known_budget_stops_subsequent_requests(self):
        self.body = json.dumps(message({"input_tokens": 1_000_000, "output_tokens": 1})).encode()
        with self.proxy(budget_usd=0.1) as proxy:
            self.assertEqual(self.request(proxy)[0], 200)
            self.records()
            self.assertEqual(self.request(proxy)[0], 429)
            self.records(2)
            self.assertGreater(proxy.summary()["known_token_usd_upper_bound"], 0.1)
        self.assertEqual(len(self.received), 1)

    def test_strict_unknown_policy_blocks_only_that_arm_without_zero(self):
        self.body = json.dumps(message({"input_tokens": 10})).encode()
        with self.proxy(max_unknown_usage_requests=1) as proxy:
            self.request(proxy)
            self.records()
            status, _, body = self.request(proxy)
            self.assertEqual(status, 429)
            self.assertIn(b"UnknownUsageLimitReached", body)
            self.records(2)
            self.assertEqual(proxy.summary()["unknown_usage_requests"], 1)
            self.assertFalse(proxy.summary()["subsequent_requests_blocked"])
            self.assertEqual(proxy.summary()["blocked_arms"], ["cc"])
        self.assertEqual(len(self.received), 1)

    def test_service_tier_preserved_and_does_not_block_later_request(self):
        self.body = json.dumps(message({"cache_creation_input_tokens": 0,
                                        "cache_read_input_tokens": 0,
                                        "input_tokens": 1511, "output_tokens": 88,
                                        "service_tier": "standard"})).encode()
        with self.proxy() as proxy:
            for index in range(2):
                self.assertEqual(self.request(proxy)[0], 200)
                rows = self.records(index + 1)
            self.assertEqual(rows[0]["usage"]["service_tier"], "standard")
            self.assertEqual(rows[0]["cost"]["usage_metadata"]["service_tier"], "standard")
            self.assertEqual(proxy.summary()["unknown_usage_requests"], 0)
        self.assertEqual(len(self.received), 2)

    def test_invalid_cache_usage_never_becomes_zero(self):
        for streaming in (False, True):
            for invalid in ("not-a-counter", True, None):
                with self.subTest(streaming=streaming, invalid=invalid):
                    self.log.unlink(missing_ok=True)
                    usage = {"input_tokens": 100, "output_tokens": 5,
                             "cache_read_input_tokens": invalid, "service_tier": "standard"}
                    self.content_type = "text/event-stream" if streaming else "application/json"
                    self.body = (event({"type": "message_start", "message": {"usage": usage}})
                                 + event({"type": "message_stop"}) if streaming else json.dumps(message(usage)).encode())
                    with self.proxy(max_unknown_usage_requests=1) as proxy:
                        self.assertEqual(self.request(proxy, payload={"model": "deepseek-flash", "stream": streaming})[0], 200)
                        row = self.records()[0]
                        self.assertEqual(row["cost"]["status"], "unknown")
                        self.assertIn("cache_read_input_tokens", row["invalid_usage_fields"])
                        self.assertNotIn("service_tier", row["invalid_usage_fields"])
                        self.assertEqual(row["usage"]["service_tier"], "standard")
                        self.assertEqual(self.request(proxy)[0], 429)
                        self.records(2)
                        self.assertEqual(proxy.summary()["unknown_usage_requests"], 1)
                    self.assertNotIn("not-a-counter", self.log.read_text())

    def test_close_journals_slow_stream_once_and_exposes_pending_unknown(self):
        first = event({"type": "message_start", "message": {"model": "deepseek-flash",
                       "usage": {"input_tokens": 100, "output_tokens": 0}}})
        self.response_parts = [first, event({"type": "message_stop"})]
        self.body = b"".join(self.response_parts)
        self.content_type = "text/event-stream"
        self.after_first_part_gate = threading.Event()
        consumed = threading.Event()

        def client(proxy):
            request = Request(proxy.url("cc") + "/messages", data=json.dumps({"model": "deepseek-flash", "stream": True}).encode())
            try:
                with urlopen(request, timeout=5) as response:
                    response.read1(len(first))
                    consumed.set()
                    response.read()
            except (OSError, http.client.HTTPException):
                pass

        with self.proxy() as proxy:
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(client, proxy)
                try:
                    self.assertTrue(consumed.wait(3))
                    pending = proxy.summary()
                    self.assertEqual(pending["pending_requests"], 1)
                    self.assertEqual(pending["pending_usage_status"], "unknown")
                    self.assertFalse(pending["budget_accounting_complete"])
                    self.assertFalse(proxy.drain(timeout=0.01))
                    started = time.monotonic()
                    proxy.close(drain_timeout=0.01)
                    self.assertLess(time.monotonic() - started, 2)
                    row = self.records()[0]
                    self.assertEqual(row["error_class"], "ProxyClosedWithInFlightRequest")
                    self.assertFalse(row["complete"])
                    self.assertEqual(row["usage"]["input_tokens"], 100)
                    self.assertEqual(row["cost"]["status"], "unknown")
                    final = proxy.summary()
                    self.assertEqual(final["pending_requests"], 0)
                    self.assertEqual(final["unknown_usage_requests"], 1)
                    self.assertEqual(final["unresolved_usage_requests"], 1)
                finally:
                    self.after_first_part_gate.set()
                future.result(timeout=3)
            self.assertTrue(proxy.drain(timeout=0))
            self.assertEqual(len(self.records()), 1)
            self.assertEqual(proxy.summary(), final)

    def test_close_before_upstream_headers_journals_unknown_once(self):
        self.before_headers_gate = threading.Event()
        with self.proxy() as proxy:
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(self.request, proxy)
                try:
                    self.assertTrue(self.upstream_received.wait(3))
                    proxy.close(drain_timeout=0.01)
                    row = self.records()[0]
                    self.assertEqual(row["error_class"], "ProxyClosedWithInFlightRequest")
                    self.assertIsNone(row["http_status"])
                    self.assertIsNone(row["usage"]["input_tokens"])
                    self.assertEqual(proxy.summary()["unknown_usage_requests"], 1)
                finally:
                    self.before_headers_gate.set()
                try:
                    future.result(timeout=3)
                except (OSError, http.client.HTTPException):
                    pass
            self.assertEqual(len(self.records()), 1)
            self.assertEqual(proxy.summary()["recorded_requests"], 1)

    def test_drain_waits_for_normal_completion(self):
        self.before_headers_gate = threading.Event()
        with self.proxy() as proxy:
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(self.request, proxy)
                try:
                    self.assertTrue(self.upstream_received.wait(3))
                    timer = threading.Timer(0.05, self.before_headers_gate.set)
                    timer.start()
                    self.assertTrue(proxy.drain(timeout=2))
                    self.assertEqual(future.result(timeout=3)[0], 200)
                finally:
                    self.before_headers_gate.set()
            self.assertTrue(self.records()[0]["complete"])
            self.assertEqual(proxy.summary()["pending_requests"], 0)
            self.assertEqual(proxy.summary()["unknown_usage_requests"], 0)

    def test_parallel_log_records_and_request_limit_are_atomic(self):
        with self.proxy(max_requests=5) as proxy:
            with ThreadPoolExecutor(max_workers=12) as pool:
                results = list(pool.map(lambda _: self.request(proxy)[0], range(12)))
            rows = self.records(12)
            self.assertEqual(results.count(200), 5)
            self.assertEqual(results.count(429), 7)
            self.assertEqual(len(rows), 12)
            self.assertEqual(len({row["request_id"] for row in rows}), 12)
            self.assertEqual(proxy.summary()["pending_requests"], 0)
        self.assertEqual(len(self.received), 5)

    def test_one_unknown_allows_native_recovery_and_preserves_fee_gap(self):
        self.body = json.dumps(message({"input_tokens": 10})).encode()
        with self.proxy() as proxy:
            self.assertEqual(self.request(proxy)[0], 200)
            first = self.records()[0]
            self.assertIsNone(first["cost"]["usd_upper_bound"])
            self.assertEqual(first["cost"]["status"], "unknown")
            pending = proxy.summary()["by_arm"]
            self.assertEqual(pending["cc"]["unknown_usage_requests"], 1)
            self.assertAlmostEqual(pending["cc"]["unknown_usage_reservation_usd"], .35)
            self.assertFalse(pending["cc"]["subsequent_requests_blocked"])
            self.assertEqual(pending["dsh"]["unknown_usage_reservation_usd"], 0)
            self.body = json.dumps(message()).encode()
            self.assertEqual(self.request(proxy)[0], 200)
            rows = self.records(2)
            self.assertEqual(len(self.received), 2)  # No implicit proxy replay.
            self.assertEqual(rows[0]["request_sha256"], rows[1]["request_sha256"])
            self.assertNotEqual(rows[0]["request_id"], rows[1]["request_id"])
            summary = proxy.summary()["by_arm"]["cc"]
            self.assertEqual(summary["unknown_usage_requests"], 1)
            self.assertFalse(summary["budget_accounting_complete"])
            self.assertGreater(summary["known_token_usd_upper_bound"], 0)
            self.assertIsNone(self.records(2)[0]["cost"]["usd_upper_bound"])

    def test_genuine_upstream_incomplete_read_does_not_cancel_pair(self):
        first = event({"type": "message_start", "message": {
            "model": "deepseek-flash", "usage": {"input_tokens": 100, "output_tokens": 0}}})
        self.body, self.content_type = first, "text/event-stream"
        self.chunked_truncation = True
        payload = {"model": "deepseek-flash", "stream": True, "max_tokens": 32768}
        with self.proxy() as proxy:
            self.assertEqual(self.request(proxy, payload=payload)[0], 200)
            row = self.records()[0]
            self.assertEqual(row["error_class"], "IncompleteRead")
            self.assertFalse(row["complete"])
            self.assertEqual(row["cost"]["status"], "unknown")
            self.assertIsNone(row["cost"]["usd_upper_bound"])
            self.assertEqual(row["usage"]["input_tokens"], 100)
            self.assertFalse(proxy.summary()["subsequent_requests_blocked"])
            self.chunked_truncation = False
            self.body = first + event({"type": "message_delta", "usage": {"output_tokens": 20}}) + event({"type": "message_stop"})
            self.assertEqual(self.request(proxy, payload=payload)[0], 200)
            self.assertEqual(self.request(proxy, arm="dsh", payload=payload)[0], 200)
            rows = self.records(3)
            self.assertEqual([row["complete"] for row in rows], [False, True, True])
            self.assertEqual(len(self.received), 3)
            self.assertEqual(proxy.summary()["by_arm"]["cc"]["unknown_usage_requests"], 1)
            self.assertEqual(proxy.summary()["by_arm"]["dsh"]["unknown_usage_requests"], 0)

    def test_client_disconnect_still_observes_final_provider_usage_without_replay(self):
        first = event({"type": "message_start", "message": {
            "model": "deepseek-flash", "usage": {"input_tokens": 100, "output_tokens": 0}}})
        filler = event({"type": "content_block_delta", "delta": {
            "type": "text_delta", "text": "PRIVATE STREAM " * 20000}})
        self.response_parts = [first, filler,
            event({"type": "message_delta", "usage": {"output_tokens": 21}}),
            event({"type": "message_stop"})]
        self.body, self.content_type = b"".join(self.response_parts), "text/event-stream"
        self.after_first_part_gate = threading.Event()
        with self.proxy() as proxy:
            request = Request(proxy.url("cc") + "/messages", data=json.dumps({
                "model": "deepseek-flash", "stream": True}).encode())
            try:
                with urlopen(request, timeout=3) as response:
                    self.assertEqual(response.read1(len(first)), first)
                    # A TCP reset makes the local downstream disconnect
                    # deterministic instead of relying on kernel FIN timing.
                    response.fp.raw._sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER,
                                                    struct.pack("ii", 1, 0))
            finally:
                self.after_first_part_gate.set()
            row = self.records()[0]
            self.assertFalse(row["complete"])
            self.assertTrue(row["provider_response_complete"])
            self.assertTrue(row["client_disconnected"])
            self.assertEqual(row["error_class"], "ClientDisconnected")
            self.assertEqual(row["cost"]["status"], "estimated")
            self.assertEqual(row["usage"]["output_tokens"], 21)
            self.assertEqual(proxy.summary()["unknown_usage_requests"], 0)
            self.assertEqual(len(self.received), 1)
            self.assertFalse(proxy.summary()["by_arm"]["dsh"]["subsequent_requests_blocked"])
        self.assertNotIn("PRIVATE STREAM", self.log.read_text())

    def test_disconnected_observation_has_wall_limit_despite_heartbeats(self):
        first = event({"type": "message_start", "message": {
            "model": "deepseek-flash", "usage": {"input_tokens": 100, "output_tokens": 0}}})
        filler = event({"type": "content_block_delta", "delta": {
            "type": "text_delta", "text": "PRIVATE STREAM " * 20000}})
        self.response_parts = [first, filler] + [event({"type": "ping"})] * 200 + [event({"type": "message_stop"})]
        self.body, self.content_type = b"".join(self.response_parts), "text/event-stream"
        self.after_first_part_gate = threading.Event()
        with self.proxy(request_timeout=.2) as proxy:
            request = Request(proxy.url("cc") + "/messages", data=json.dumps({
                "model": "deepseek-flash", "stream": True}).encode())
            try:
                with urlopen(request, timeout=3) as response:
                    self.assertEqual(response.read1(len(first)), first)
                    response.fp.raw._sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER,
                                                    struct.pack("ii", 1, 0))
            finally:
                self.after_first_part_gate.set()
            row = self.records()[0]
            self.assertTrue(row["client_disconnected"])
            self.assertFalse(row["provider_response_complete"])
            self.assertEqual(row["error_class"], "DisconnectedObservationTimeout")
            self.assertEqual(row["cost"]["status"], "unknown")
            self.assertIsNone(row["cost"]["usd_upper_bound"])
            self.assertLess(row["duration_seconds"], 1)
            self.assertEqual(proxy.summary()["unknown_usage_requests"], 1)
            self.assertEqual(len(self.received), 1)

    def test_disconnected_stalled_socket_uses_same_deadline_category(self):
        first = event({"type": "message_start", "message": {
            "model": "deepseek-flash", "usage": {"input_tokens": 100, "output_tokens": 0}}})
        filler = event({"type": "content_block_delta", "delta": {
            "type": "text_delta", "text": "PRIVATE STREAM " * 20000}})
        self.response_parts = [first, filler, event({"type": "message_stop"})]
        self.body, self.content_type = b"".join(self.response_parts), "text/event-stream"
        self.after_first_part_gate = threading.Event()
        self.after_second_part_gate = threading.Event()
        with self.proxy(request_timeout=.2) as proxy:
            request = Request(proxy.url("cc") + "/messages", data=json.dumps({
                "model": "deepseek-flash", "stream": True}).encode())
            try:
                with urlopen(request, timeout=3) as response:
                    self.assertEqual(response.read1(len(first)), first)
                    response.fp.raw._sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER,
                                                    struct.pack("ii", 1, 0))
                self.after_first_part_gate.set()
                row = self.records()[0]
                self.assertTrue(row["client_disconnected"])
                self.assertFalse(row["provider_response_complete"])
                self.assertEqual(row["error_class"], "DisconnectedObservationTimeout")
                self.assertEqual(row["cost"]["status"], "unknown")
                self.assertIsNone(row["cost"]["usd_upper_bound"])
                self.assertLess(row["duration_seconds"], 1)
                self.assertEqual(proxy.summary()["unknown_usage_requests"], 1)
                self.assertEqual(len(self.received), 1)
            finally:
                self.after_first_part_gate.set()
                self.after_second_part_gate.set()

    def test_upstream_idle_timeout_before_disconnect_keeps_original_category(self):
        self.before_headers_gate = threading.Event()
        with self.proxy(request_timeout=.1) as proxy:
            try:
                self.assertEqual(self.request(proxy)[0], 502)
                row = self.records()[0]
                self.assertEqual(row["error_class"], "TimeoutError")
                self.assertFalse(row["client_disconnected"])
                self.assertFalse(row["provider_response_complete"])
                self.assertEqual(row["cost"]["status"], "unknown")
                self.assertIsNone(row["cost"]["usd_upper_bound"])
                self.assertEqual(len(self.received), 1)
            finally:
                self.before_headers_gate.set()

    def test_unknown_retry_allowance_is_bounded_and_arm_local(self):
        self.body = json.dumps(message({"input_tokens": 10})).encode()
        with self.proxy() as proxy:
            for index in range(3):
                self.assertEqual(self.request(proxy)[0], 200)
                self.records(index + 1)
            self.assertEqual(self.request(proxy)[0], 429)
            rows = self.records(4)
            self.assertEqual(rows[-1]["error_class"], "UnknownUsageLimitReached")
            self.assertEqual(len(self.received), 3)
            state = proxy.summary()["by_arm"]["cc"]
            self.assertEqual(state["unknown_usage_requests"], 3)
            self.assertAlmostEqual(state["unknown_usage_reservation_usd"], 1.05)
            self.assertTrue(state["subsequent_requests_blocked"])
            self.body = json.dumps(message()).encode()
            self.assertEqual(self.request(proxy, arm="dsh")[0], 200)
            self.assertEqual(self.request(proxy, suffix="/messages/count_tokens")[0], 200)
            self.records(6)
            self.assertEqual(proxy.summary()["by_arm"]["dsh"]["unknown_usage_requests"], 0)
            self.assertEqual(proxy.summary()["by_arm"]["cc"]["token_count_completed_requests"], 1)
            self.assertFalse(proxy.summary()["subsequent_requests_blocked"])

    def test_request_and_known_token_budgets_are_independent_per_arm(self):
        with self.proxy(max_requests=1) as proxy:
            self.assertEqual(self.request(proxy)[0], 200)
            self.records()
            self.assertEqual(self.request(proxy)[0], 429)
            self.records(2)
            self.assertEqual(self.request(proxy, arm="dsh")[0], 200)
            self.records(3)
            summary = proxy.summary()
            self.assertEqual(summary["forwarded_requests"], 2)
            self.assertTrue(summary["subsequent_requests_blocked"])
            self.assertEqual(summary["blocked_arms"], ["cc", "dsh"])
        self.log.unlink()
        self.received.clear()
        self.body = json.dumps(message({"input_tokens": 1_000_000, "output_tokens": 1})).encode()
        with self.proxy(budget_usd=.1) as proxy:
            self.assertEqual(self.request(proxy)[0], 200)
            self.records()
            self.assertEqual(self.request(proxy)[0], 429)
            self.records(2)
            self.body = json.dumps(message()).encode()
            self.assertEqual(self.request(proxy, arm="dsh")[0], 200)
            self.records(3)
            summary = proxy.summary()
            self.assertEqual(summary["by_arm"]["cc"]["block_reason"], "TokenBudgetReached")
            self.assertIsNone(summary["by_arm"]["dsh"]["block_reason"])
            self.assertFalse(summary["subsequent_requests_blocked"])

    def test_inflight_reservation_is_atomic_and_does_not_consume_sibling(self):
        self.before_headers_gate = threading.Event()
        with self.proxy(budget_usd=.3) as proxy:
            with ThreadPoolExecutor(max_workers=2) as pool:
                first = pool.submit(self.request, proxy)
                second = None
                try:
                    self.assertTrue(self.upstream_received.wait(3))
                    self.assertEqual(self.request(proxy)[0], 429)
                    self.records()
                    second = pool.submit(self.request, proxy, arm="dsh")
                    deadline = time.monotonic() + 3
                    while proxy.summary()["by_arm"]["dsh"]["pending_requests"] != 1 and time.monotonic() < deadline:
                        time.sleep(.005)
                    state = proxy.summary()["by_arm"]
                    self.assertEqual(state["cc"]["pending_requests"], 1)
                    self.assertEqual(state["dsh"]["pending_requests"], 1)
                    self.assertAlmostEqual(state["cc"]["pending_usage_reservation_usd"], .35)
                    self.assertAlmostEqual(state["dsh"]["pending_usage_reservation_usd"], .35)
                finally:
                    self.before_headers_gate.set()
                self.assertEqual(first.result(timeout=3)[0], 200)
                self.assertEqual(second.result(timeout=3)[0], 200)
            self.records(3)
            state = proxy.summary()["by_arm"]
            self.assertEqual(state["cc"]["pending_usage_reservation_usd"], 0)
            self.assertEqual(state["dsh"]["pending_usage_reservation_usd"], 0)
            self.assertFalse(proxy.summary()["subsequent_requests_blocked"])

    def test_partial_usage_reservation_cannot_hide_a_larger_observed_amount(self):
        self.body = json.dumps(message({"input_tokens": 1_000_000, "output_tokens": 1_000_000})).encode()
        self.partial_length = len(self.body) + 1
        with self.proxy(budget_usd=1) as proxy:
            with self.assertRaises(http.client.IncompleteRead):
                self.request(proxy)
            row = self.records()[0]
            self.assertEqual(row["cost"]["status"], "unknown")
            self.assertIsNone(row["cost"]["usd_upper_bound"])
            self.assertAlmostEqual(row["cost"]["observed_partial_token_usd_peak_estimate"], 1.5)
            state = proxy.summary()["by_arm"]["cc"]
            self.assertAlmostEqual(state["unknown_usage_reservation_usd"], 1.5)
            self.assertEqual(state["block_reason"], "TokenBudgetReached")
            self.assertFalse(proxy.summary()["by_arm"]["dsh"]["subsequent_requests_blocked"])

    def test_requested_large_output_increases_policy_reservation_only(self):
        self.before_headers_gate = threading.Event()
        payload = {"model": "deepseek-flash", "max_tokens": 1_000_000}
        with self.proxy() as proxy:
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(self.request, proxy, payload=payload)
                try:
                    self.assertTrue(self.upstream_received.wait(3))
                    state = proxy.summary()["by_arm"]["cc"]
                    self.assertAlmostEqual(state["pending_usage_reservation_usd"], 1.5)
                    self.assertEqual(state["known_token_usd_upper_bound"], 0)
                finally:
                    self.before_headers_gate.set()
                self.assertEqual(future.result(timeout=3)[0], 200)
            row = self.records()[0]
            self.assertAlmostEqual(row["budget_reservation_usd"], 1.5)
            self.assertAlmostEqual(row["cost"]["usd_upper_bound"], .000054)

    def test_stop_arm_preserves_admitted_request_and_other_arm(self):
        self.before_headers_gate = threading.Event()
        with self.proxy() as proxy:
            with self.assertRaises(ValueError):
                proxy.stop_arm("other")
            with self.assertRaises(ValueError):
                proxy.stop_arm("cc", "PRIVATE STOP TEXT")
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(self.request, proxy)
                try:
                    self.assertTrue(self.upstream_received.wait(3))
                    proxy.stop_arm("cc", "ArmCancelled")
                    self.assertEqual(self.request(proxy)[0], 429)
                    self.records()
                    self.assertEqual(proxy.summary()["by_arm"]["cc"]["block_reason"], "ArmCancelled")
                    self.assertFalse(proxy.summary()["by_arm"]["dsh"]["subsequent_requests_blocked"])
                finally:
                    self.before_headers_gate.set()
                self.assertEqual(future.result(timeout=3)[0], 200)
            self.records(2)
            self.assertEqual(self.request(proxy, arm="dsh")[0], 200)
            rows = self.records(3)
            self.assertEqual(sum(row["complete"] for row in rows), 2)
            self.assertEqual(proxy.summary()["unknown_usage_requests"], 0)
        self.assertNotIn("PRIVATE STOP TEXT", self.log.read_text())

    def test_constructor_and_context_boundaries(self):
        for upstream in ("https://evil.example", "http://127.0.0.1/other", "http://user@127.0.0.1", "http://127.0.0.1?x=1"):
            with self.assertRaises(ValueError):
                ObservingProxy("key", self.log, {"cc"}, _test_upstream=upstream)
        for kwargs in ({"max_requests": 0}, {"budget_usd": 0}, {"budget_usd": float("nan")},
                       {"input_tokens_semantics": "guess"}, {"request_timeout": 0},
                       {"allow_server_tools": None}, {"max_unknown_usage_requests": 0},
                       {"max_unknown_usage_requests": True}, {"unknown_usage_reserve_usd": 0},
                       {"unknown_usage_reserve_usd": float("inf")},
                       {"unknown_usage_reserve_usd": True}):
            with self.assertRaises(ValueError):
                self.proxy(**kwargs)
        proxy = self.proxy()
        with self.assertRaises(RuntimeError):
            proxy.url("cc")
        with proxy:
            self.assertTrue(proxy.url("cc").startswith("http://127.0.0.1:"))
        with self.assertRaises(RuntimeError):
            proxy.url("cc")
        proxy.close()


if __name__ == "__main__":
    unittest.main()
