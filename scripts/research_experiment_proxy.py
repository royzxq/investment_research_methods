"""Loopback-only observation proxy for isolated DeepSeek Messages experiments.

This module has no production-runner integration and never publishes research.  It
does not retain prompts, response text, thinking, credentials, or HTTP headers.
Only configured arms and the fixed DeepSeek Flash Messages/count routes work.

The independent per-arm request/token budgets stop *subsequent* requests, not
provider billing. In-flight requests can exceed a budget. Unknown accounting
remains null, with a disclosed conservative reservation and bounded tolerance;
one arm's interrupted response never consumes the other arm's allowance.
The estimate is a peak-price token upper bound, not a bill; Search/Fetch and other
non-token charges are not priced.  Cache accounting must be calibrated by a small
probe before choosing input_tokens_semantics='total' or 'uncached'.
"""

from __future__ import annotations

import hashlib
import copy
import json
import math
import re
import socket
import threading
import time
import uuid
from collections import Counter
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


MODEL = "deepseek-flash"
UPSTREAM = "https://api.deepseek.com"
UPSTREAM_PATH = "/anthropic/v1/messages"
TOKEN_COUNT_PATH = UPSTREAM_PATH + "/count_tokens"
PEAK_INPUT_USD_PER_MILLION = 0.30
PEAK_OUTPUT_USD_PER_MILLION = 1.20
PRICING_SOURCE = "https://api-docs.deepseek.com/quick_start/pricing/"
PRICING_DATE = "2026-10-21"
_NAME = re.compile(r"[A-Za-z0-9_.:-]{1,128}\Z")
_MODEL_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:/\[\]-]{0,127}\Z")
_ARM = re.compile(r"[a-z][a-z0-9_-]{0,31}\Z")
_HOP = frozenset({"connection", "keep-alive", "proxy-authenticate",
                  "proxy-authorization", "te", "trailer", "transfer-encoding",
                  "upgrade", "host", "content-length"})
_KNOWN_USAGE = frozenset({"input_tokens", "output_tokens", "prompt_tokens",
                        "completion_tokens", "cache_read_input_tokens",
                        "cache_creation_input_tokens", "prompt_cache_hit_tokens",
                        "prompt_cache_miss_tokens", "total_tokens",
                        "cache_creation", "server_tool_use", "service_tier"})
_USAGE_METADATA = frozenset({"service_tier"})


def _counter(value):
    return value if isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= 2**63 - 1 else None


def estimate_flash_peak_cost(usage, *, input_tokens_semantics=None):
    """Estimate known token usage without guessing ambiguous cache semantics.

    ``prompt_tokens`` is a total.  DeepSeek hit+miss fields also identify a total.
    Plain Anthropic input_tokens with non-zero cache splits is ambiguous here;
    choose 'total' or 'uncached' only after observing the upstream's accounting.
    All counted input uses the higher cache-miss price, so cache hits do not earn
    an assumed discount.  No requested max_tokens value enters this calculation.
    """
    if input_tokens_semantics not in (None, "total", "uncached"):
        raise ValueError("invalid input token semantics")
    result = {"status": "unknown", "usd_upper_bound": None,
              "input_tokens_total": None, "output_tokens": None, "reasons": [],
              "pricing_date": PRICING_DATE, "pricing_source": PRICING_SOURCE,
              "input_usd_per_million": PEAK_INPUT_USD_PER_MILLION,
              "output_usd_per_million": PEAK_OUTPUT_USD_PER_MILLION,
              "input_tokens_semantics": input_tokens_semantics,
              "scope": "peak-price token estimate; excludes non-token charges",
              "usage_metadata": {},
              "non_token_usage": None,
              "non_token_pricing_note": "Server-side Search/Fetch are free in the 2026-10-21 official pricing snapshot; charging begins 2026-11-01 00:00 Asia/Shanghai. Counts not reported remain unknown. Other non-token charges are not estimated."}
    if not isinstance(usage, dict):
        result["reasons"].append("missing_usage")
        return result
    reasons = result["reasons"]
    if any(not isinstance(key, str) for key in usage):
        reasons.append("invalid_usage_keys")
        return result
    unknown = sorted(set(usage) - _KNOWN_USAGE)
    if unknown:
        reasons.append("unrecognized_usage_fields:" + ",".join(unknown))
    for key, value in usage.items():
        if key in _KNOWN_USAGE - {"cache_creation", "server_tool_use"} - _USAGE_METADATA and _counter(value) is None:
            reasons.append("invalid_counter:" + key)
    result["usage_metadata"] = {key: _safe_usage_metadata(usage[key])
                                for key in _USAGE_METADATA if key in usage}
    cache_read = _counter(usage.get("cache_read_input_tokens"))
    cache_create = _counter(usage.get("cache_creation_input_tokens"))
    cache_read = 0 if cache_read is None else cache_read
    cache_create = 0 if cache_create is None else cache_create
    nested_create = usage.get("cache_creation")
    if nested_create is not None:
        if not isinstance(nested_create, dict) or set(nested_create) - {"ephemeral_5m_input_tokens", "ephemeral_1h_input_tokens"}:
            reasons.append("unrecognized_cache_creation_accounting")
        elif any(_counter(v) is None for v in nested_create.values()):
            reasons.append("invalid_cache_creation_counter")
        else:
            nested_total = sum(nested_create.values())
            if "cache_creation_input_tokens" in usage and cache_create != nested_total:
                reasons.append("conflicting_cache_creation_counters")
            else:
                cache_create = nested_total
    server_tools = usage.get("server_tool_use")
    result["non_token_usage"] = _numeric_usage(server_tools)
    if server_tools is not None and (not isinstance(server_tools, dict) or any(_counter(v) is None for v in server_tools.values())):
        result["non_token_pricing_note"] += " Non-token counters have unsupported values and remain unknown; this does not change the known token estimate."
    prompt = _counter(usage.get("prompt_tokens"))
    hit = _counter(usage.get("prompt_cache_hit_tokens"))
    miss = _counter(usage.get("prompt_cache_miss_tokens"))
    inp = _counter(usage.get("input_tokens"))
    if prompt is not None:
        total_input = prompt
        if hit is not None and miss is not None and hit + miss != prompt:
            reasons.append("conflicting_prompt_counters")
        if hit is not None and hit > prompt:
            reasons.append("cache_hit_exceeds_prompt_total")
        if cache_read + cache_create > prompt:
            reasons.append("cache_split_exceeds_prompt_total")
        allowed_input = {prompt, prompt - cache_read - cache_create}
        if miss is not None:
            allowed_input.add(miss)
        if inp is not None and inp not in allowed_input:
            reasons.append("conflicting_input_counters")
    elif hit is not None and miss is not None:
        total_input = hit + miss
        if inp is not None and inp not in (total_input, miss):
            reasons.append("conflicting_input_counters")
    elif inp is not None:
        if cache_read or cache_create:
            if input_tokens_semantics == "total":
                total_input = inp
                if cache_read + cache_create > total_input:
                    reasons.append("cache_split_exceeds_input_total")
            elif input_tokens_semantics == "uncached":
                total_input = inp + cache_read + cache_create
            else:
                total_input = None
                reasons.append("ambiguous_anthropic_cache_accounting")
        else:
            total_input = inp
        if hit is not None or miss is not None:
            reasons.append("incomplete_deepseek_cache_split")
    else:
        total_input = None
        reasons.append("missing_input_tokens")
    output = _counter(usage.get("output_tokens"))
    completion = _counter(usage.get("completion_tokens"))
    if output is None:
        output = completion
    elif completion is not None and completion != output:
        reasons.append("conflicting_output_counters")
    if output is None:
        reasons.append("missing_output_tokens")
    all_tokens = _counter(usage.get("total_tokens"))
    if all_tokens is not None and total_input is not None and output is not None and all_tokens != total_input + output:
        reasons.append("conflicting_total_tokens")
    result["input_tokens_total"], result["output_tokens"] = total_input, output
    if not reasons and total_input is not None and output is not None:
        result["status"] = "estimated"
        result["usd_upper_bound"] = (total_input * PEAK_INPUT_USD_PER_MILLION + output * PEAK_OUTPUT_USD_PER_MILLION) / 1_000_000
    return result


def _safe_name(value):
    return value if isinstance(value, str) and _NAME.fullmatch(value) else "<other>"


def _safe_model_name(value):
    if value is None:
        return None
    return value if isinstance(value, str) and _MODEL_NAME.fullmatch(value) else "<other>"


def _safe_usage_metadata(value):
    # Service tier is provider metadata, not a token counter. Preserve its null
    # or short identifier value without retaining arbitrary response content.
    return None if value is None else _safe_name(value)


def _numeric_usage(value):
    if isinstance(value, dict):
        return {_safe_name(str(k)): (_safe_usage_metadata(v) if k in _USAGE_METADATA else _numeric_usage(v))
                for k, v in value.items()}
    if value is None or isinstance(value, (bool, int)):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    return None


def _merge_usage(target, incoming, invalid_fields=None, prefix=""):
    if not isinstance(incoming, dict):
        return
    for raw_key, raw_value in incoming.items():
        key = _safe_name(str(raw_key))
        field = prefix + key
        prior_known = _counter(target.get(key)) is not None
        value = (_safe_usage_metadata(raw_value) if key in _USAGE_METADATA else _numeric_usage(raw_value))
        if isinstance(value, dict):
            if not isinstance(target.get(key), dict):
                target[key] = {}
            _merge_usage(target[key], raw_value,
                         None if key == "server_tool_use" else invalid_fields,
                         field + ".")
        elif value is not None or key not in target:
            target[key] = value
        if (invalid_fields is not None and key not in _USAGE_METADATA | {"server_tool_use"}
                and not isinstance(raw_value, dict) and _counter(raw_value) is None
                and not (raw_value is None and prior_known)):
            # A null SSE placeholder retains an earlier known count. A first
            # null count remains unknown; malformed strings/bools never become 0.
            invalid_fields.add(field)


def _json_bytes(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate key")
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite JSON")))


def _tool_result_errors(value):
    if isinstance(value, list):
        return sum(_tool_result_errors(item) for item in value)
    if not isinstance(value, dict):
        return 0
    result = int(value.get("type") == "tool_result" and value.get("is_error") is True)
    if isinstance(value.get("content"), (list, dict)):
        result += _tool_result_errors(value["content"])
    return result


class _ResponseObserver:
    def __init__(self, streaming):
        self.streaming = streaming
        self.usage = {}
        self.invalid_usage_fields = set()
        self._lock = threading.Lock()
        self.model = None
        self.tool_names, self.tool_types = Counter(), Counter()
        self.tool_result_errors = 0
        self.message_stop = False
        self.input_tokens_count = None
        self.error = None
        self._buffer = bytearray()
        self._event = []
        self._size = 0
        self._limit = 16 * 1024 * 1024

    def _block(self, block):
        if not isinstance(block, dict):
            return
        if block.get("type") in ("tool_use", "server_tool_use"):
            self.tool_names[_safe_name(block.get("name"))] += 1
            self.tool_types[block["type"]] += 1
        self.tool_result_errors += _tool_result_errors(block)

    def _object(self, data):
        if not isinstance(data, dict):
            self.error = "InvalidUpstreamJSON"
            return
        kind = data.get("type")
        if kind == "error":
            self.error = "UpstreamStreamError" if self.streaming else "UpstreamResponseError"
        elif kind == "message_stop":
            self.message_stop = True
        elif kind == "message_start":
            message = data.get("message", {})
            if isinstance(message, dict):
                if isinstance(message.get("model"), str):
                    self.model = _safe_name(message["model"])
                _merge_usage(self.usage, message.get("usage"), self.invalid_usage_fields)
        elif kind == "content_block_start":
            self._block(data.get("content_block"))
        if isinstance(data.get("model"), str):
            self.model = _safe_name(data["model"])
        _merge_usage(self.usage, data.get("usage"), self.invalid_usage_fields)
        if not self.streaming:
            if kind != "message":
                self.error = self.error or "InvalidUpstreamMessage"
            for block in data.get("content", []) if isinstance(data.get("content"), list) else []:
                self._block(block)

    def _dispatch(self):
        if not self._event:
            return
        payload = b"\n".join(self._event)
        self._event = []
        if payload == b"[DONE]":
            return  # Anthropic completion requires message_stop, not this sentinel.
        try:
            self._object(_strict_json(payload))
        except (ValueError, UnicodeError, RecursionError):
            self.error = "InvalidUpstreamJSON"

    def feed(self, chunk):
        with self._lock:
            self._feed(chunk)

    def _feed(self, chunk):
        if self.error == "ObservationLimitExceeded":
            return
        self._buffer.extend(chunk)
        if not self.streaming:
            if len(self._buffer) > self._limit:
                self._buffer.clear()
                self.error = "ObservationLimitExceeded"
            return
        while b"\n" in self._buffer:
            line, _, rest = self._buffer.partition(b"\n")
            self._buffer = bytearray(rest)
            line = line.rstrip(b"\r")
            if not line:
                self._dispatch()
                self._size = 0
            elif line.startswith(b"data:"):
                self._event.append(line[5:].lstrip(b" "))
                self._size += len(line)
            if self._size > self._limit:
                self._buffer.clear()
                self._event.clear()
                self.error = "ObservationLimitExceeded"
                break
        if len(self._buffer) > self._limit:
            self._buffer.clear()
            self._event.clear()
            self.error = "ObservationLimitExceeded"

    def finish(self):
        with self._lock:
            self._finish()

    def _finish(self):
        if self.error == "ObservationLimitExceeded":
            return
        if self.streaming:
            # A trailing incomplete SSE event is intentionally not dispatched.
            if self._buffer or self._event:
                self.error = self.error or "TruncatedSSE"
            elif not self.message_stop:
                self.error = self.error or "MissingMessageStop"
        else:
            try:
                self._object(_strict_json(self._buffer))
            except (ValueError, UnicodeError, RecursionError):
                self.error = self.error or "InvalidUpstreamJSON"

    def note_error(self, error):
        with self._lock:
            self.error = self.error or error

    def snapshot(self):
        with self._lock:
            return {"usage": copy.deepcopy(self.usage),
                    "invalid_usage_fields": sorted(self.invalid_usage_fields),
                    "observed_model": self.model,
                    "response_tool_names": dict(self.tool_names),
                    "response_tool_types": dict(self.tool_types),
                    "response_tool_count": sum(self.tool_names.values()),
                    "response_tool_result_is_error_count": self.tool_result_errors,
                    "input_tokens_count": self.input_tokens_count,
                    "message_stop": self.message_stop, "error_class": self.error}


class _TokenCountObserver(_ResponseObserver):
    """Observe only the disclosed count, never treating it as generated usage."""

    def __init__(self):
        super().__init__(False)

    def _object(self, data):
        if isinstance(data, dict) and data.get("type") == "error":
            self.error = "UpstreamResponseError"
            return
        if not isinstance(data, dict) or _counter(data.get("input_tokens")) is None:
            self.error = "InvalidTokenCountResponse"
            return
        self.input_tokens_count = data["input_tokens"]

class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class ObservingProxy:
    """Context-managed loopback proxy.  Constructing does not issue a request.

    ``_test_upstream`` accepts only a loopback HTTP origin and exists solely for
    offline tests.  Normal use cannot select an upstream or upstream path.
    ``url(arm)`` is the API base URL; clients append /v1/messages or /messages.
    Both spellings also support /count_tokens on the same fixed upstream. Its
    returned count is diagnostic, not billed generation usage; fees are unknown.
    ``allow_server_tools=False`` permits only custom client tool definitions;
    native provider-side Search/Fetch and every other server tool are blocked.
    """

    def __init__(self, api_key, log_path, arms, max_requests=200, budget_usd=3.0,
                 *, input_tokens_semantics=None, request_timeout=180,
                 max_request_bytes=16 * 1024 * 1024, allow_server_tools=True,
                 max_unknown_usage_requests=3, unknown_usage_reserve_usd=0.35,
                 _test_upstream=None):
        if not isinstance(api_key, str) or not api_key or any(c in api_key for c in "\r\n"):
            raise ValueError("nonempty in-memory API key required")
        if isinstance(arms, (str, bytes)):
            raise ValueError("arms must be a collection of safe identifiers")
        arms = frozenset(arms)
        if not arms or any(not isinstance(arm, str) or not _ARM.fullmatch(arm) for arm in arms):
            raise ValueError("invalid experiment arm")
        if _counter(max_requests) is None or max_requests < 1:
            raise ValueError("max_requests must be positive")
        if isinstance(budget_usd, bool) or not isinstance(budget_usd, (int, float)) or not math.isfinite(budget_usd) or budget_usd <= 0:
            raise ValueError("budget_usd must be positive and finite")
        if input_tokens_semantics not in (None, "total", "uncached"):
            raise ValueError("invalid input token semantics")
        if not isinstance(request_timeout, (int, float)) or isinstance(request_timeout, bool) or not math.isfinite(request_timeout) or request_timeout <= 0:
            raise ValueError("request timeout must be positive")
        if _counter(max_request_bytes) is None or max_request_bytes < 1:
            raise ValueError("max_request_bytes must be positive")
        if not isinstance(allow_server_tools, bool):
            raise ValueError("allow_server_tools must be boolean")
        if _counter(max_unknown_usage_requests) is None or max_unknown_usage_requests < 1:
            raise ValueError("max_unknown_usage_requests must be positive")
        if (isinstance(unknown_usage_reserve_usd, bool)
                or not isinstance(unknown_usage_reserve_usd, (int, float))
                or not math.isfinite(unknown_usage_reserve_usd)
                or unknown_usage_reserve_usd <= 0):
            raise ValueError("unknown_usage_reserve_usd must be positive and finite")
        upstream = UPSTREAM
        if _test_upstream is not None:
            parsed = urlsplit(_test_upstream)
            if parsed.scheme != "http" or parsed.hostname not in ("127.0.0.1", "::1", "localhost") or parsed.username or parsed.password or parsed.path not in ("", "/") or parsed.query or parsed.fragment:
                raise ValueError("test upstream must be a loopback HTTP origin")
            upstream = _test_upstream.rstrip("/")
        self._api_key = api_key
        self.log_path = Path(log_path)
        self.arms = arms
        self.max_requests, self.budget_usd = max_requests, float(budget_usd)
        self.input_tokens_semantics = input_tokens_semantics
        self.request_timeout, self.max_request_bytes = request_timeout, max_request_bytes
        self.allow_server_tools = allow_server_tools
        self.max_unknown_usage_requests = max_unknown_usage_requests
        self.unknown_usage_reserve_usd = float(unknown_usage_reserve_usd)
        self._upstream = upstream + UPSTREAM_PATH
        self._count_upstream = upstream + TOKEN_COUNT_PATH
        self._opener = build_opener(ProxyHandler({}), _NoRedirect())
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)
        self._close_lock = threading.Lock()
        self._records = []
        self._recorded_ids = set()
        self._inflight = {}
        self._forwarded = 0
        self._generation_forwarded = 0
        self._generation_pending = 0
        self._count_forwarded = 0
        self._count_pending = 0
        self._count_completed = 0
        self._count_failed = 0
        self._pending = 0
        self._cost = 0.0
        self._partial_cost = 0.0
        self._unknown = 0
        self._arm_state = {arm: {"forwarded": 0, "pending": 0,
                                "generation_forwarded": 0, "generation_pending": 0,
                                "count_forwarded": 0, "count_pending": 0,
                                "count_completed": 0, "count_failed": 0,
                                "known_cost": 0.0, "partial_cost": 0.0,
                                "unknown": 0, "unknown_reservation": 0.0,
                                "pending_reservation": 0.0,
                                "stop_reason": None}
                           for arm in arms}
        self._server = self._thread = None
        self._closed = False

    def __enter__(self):
        if self._server is not None or self._closed:
            raise RuntimeError("proxy cannot be started twice")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        proxy = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *_):
                pass

            def do_POST(self):
                proxy._handle(self)

            def do_GET(self):
                proxy._handle(self, method_allowed=False)

            do_PUT = do_DELETE = do_PATCH = do_OPTIONS = do_HEAD = do_GET

        class Server(ThreadingHTTPServer):
            request_queue_size = 128

        self._server = Server(("127.0.0.1", 0), Handler)
        self._server.daemon_threads = True
        self._server.block_on_close = False
        self._thread = threading.Thread(target=self._server.serve_forever,
                                        name="research-experiment-proxy", daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *_):
        self.close()

    def url(self, arm):
        if arm not in self.arms:
            raise ValueError("unknown arm")
        if self._server is None or self._closed:
            raise RuntimeError("proxy is not running")
        return f"http://127.0.0.1:{self._server.server_address[1]}/{arm}"

    def drain(self, timeout=5):
        """Wait at most timeout seconds for admitted requests to be journaled."""
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or not 0 <= timeout <= 10:
            raise ValueError("drain timeout must be between 0 and 10 seconds")
        deadline = time.monotonic() + timeout
        with self._condition:
            while self._pending:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return False
                self._condition.wait(remaining)
            return True

    @staticmethod
    def _cancel_transport(entry):
        # shutdown on sockets interrupts blocked reads without waiting for a
        # buffered response.close() lock held by another thread.
        sockets = [entry.get("connection")]
        response = entry.get("response")
        for _ in range(4):
            if response is None:
                break
            raw = getattr(response, "raw", None)
            sockets.append(getattr(raw, "_sock", None))
            response = getattr(response, "fp", None)
        for connection in sockets:
            if connection is not None:
                try:
                    connection.shutdown(socket.SHUT_RDWR)
                except (OSError, AttributeError):
                    pass

    @staticmethod
    def _set_response_timeout(response, timeout):
        # urllib's HTTP(S) response wraps the socket in fp/raw layers. Restrict
        # the remaining observation time after a client disconnect, including
        # streams that keep sending heartbeats and never hit an idle timeout.
        for _ in range(4):
            if response is None:
                break
            raw = getattr(response, "raw", None)
            connection = getattr(raw, "_sock", None)
            if connection is not None:
                try:
                    connection.settimeout(timeout)
                except OSError:
                    pass
            response = getattr(response, "fp", None)

    def close(self, drain_timeout=5):
        # Validate before changing state, including for a never-started proxy.
        if isinstance(drain_timeout, bool) or not isinstance(drain_timeout, (int, float)) or not math.isfinite(drain_timeout) or not 0 <= drain_timeout <= 10:
            raise ValueError("drain timeout must be between 0 and 10 seconds")
        with self._close_lock:
            if self._closed:
                return
            close_started = time.monotonic()
            with self._condition:
                self._closed = True  # No new API admissions while draining.
            if self._server is not None:
                self._server.shutdown()
                self._server.server_close()
                self._thread.join(timeout=0.5)
            # Leave room for forced journaling inside a short overall close.
            remaining = max(0, min(drain_timeout, 9 - (time.monotonic() - close_started)))
            if not self.drain(remaining):
                with self._condition:
                    unfinished = list(self._inflight.values())
                    for entry in unfinished:
                        entry["forced_closed"] = True
                for entry in unfinished:
                    self._cancel_transport(entry)
                    record = copy.deepcopy(entry["record"])
                    record["http_status"] = entry.get("http_status")
                    record["error_class"] = "ProxyClosedWithInFlightRequest"
                    record["complete"] = False
                    self._observe_record(record, entry["observer"])
                    record["ended_at"] = datetime.now(timezone.utc).isoformat()
                    record["duration_seconds"] = round(time.monotonic() - entry["started"], 6)
                    self._write_record(record, forced_closed=True)
            self._api_key = None

    def stop_arm(self, arm, reason="ArmStopped"):
        """Reject new requests for one arm; its process owner cancels that CLI.

        Admitted requests are still observed and journaled normally. The sibling
        arm and its active requests are unaffected. This never replays a request.
        """
        if arm not in self.arms:
            raise ValueError("unknown arm")
        if reason not in ("ArmStopped", "ArmCancelled", "ArmTimedOut", "ArmFinished"):
            raise ValueError("invalid arm stop reason")
        with self._condition:
            self._arm_state[arm]["stop_reason"] = reason
            self._condition.notify_all()

    def _block_reason(self, arm, request_kind="generation"):
        # Caller owns _lock. All limits are per arm, including count requests.
        if self._closed:
            return "ProxyClosed"
        return self._policy_block_reason(arm, request_kind)

    def _policy_block_reason(self, arm, request_kind="generation"):
        # Preserve the actual per-arm state even after the shared server closes.
        state = self._arm_state[arm]
        if state["stop_reason"]:
            return state["stop_reason"]
        if state["forwarded"] >= self.max_requests:
            return "RequestLimitReached"
        if request_kind == "generation":
            if state["unknown"] >= self.max_unknown_usage_requests:
                return "UnknownUsageLimitReached"
            if (state["known_cost"] + state["unknown_reservation"]
                    + state["pending_reservation"] >= self.budget_usd):
                return "TokenBudgetReached"
        return None

    def _admit(self, record, observer, handler, started):
        with self._condition:
            blocked = self._block_reason(record["arm"], record["request_kind"])
            if blocked:
                return blocked
            state = self._arm_state[record["arm"]]
            self._forwarded += 1
            self._pending += 1
            state["forwarded"] += 1
            state["pending"] += 1
            if record["request_kind"] == "token_count":
                self._count_forwarded += 1
                self._count_pending += 1
                state["count_forwarded"] += 1
                state["count_pending"] += 1
            else:
                self._generation_forwarded += 1
                self._generation_pending += 1
                state["generation_forwarded"] += 1
                state["generation_pending"] += 1
                # Policy reservation, never actual usage or estimated billing.
                # The floor covers a 1M-input/16K-output Flash request at the
                # frozen peak prices; larger requested output raises it. No
                # claim is made about undisclosed charges or a future alias.
                reserve = max(self.unknown_usage_reserve_usd,
                              PEAK_INPUT_USD_PER_MILLION
                              + (record["max_tokens"] or 0)
                              * PEAK_OUTPUT_USD_PER_MILLION / 1_000_000)
                record["budget_reservation_usd"] = reserve
                state["pending_reservation"] += reserve
            record["forwarded"] = True
            self._inflight[record["request_id"]] = {
                "record": copy.deepcopy(record), "observer": observer,
                "connection": handler.connection, "response": None,
                "started": started, "forced_closed": False}
        return None

    def _register_response(self, request_id, response):
        with self._condition:
            entry = self._inflight.get(request_id)
            if entry is None or entry["forced_closed"]:
                self._cancel_transport({"response": response})
                return False
            entry["response"] = response
            entry["http_status"] = response.status
            return True

    def _write_record(self, record, *, forced_closed=False):
        with self._condition:
            request_id = record["request_id"]
            entry = self._inflight.get(request_id)
            if request_id in self._recorded_ids or (entry and entry["forced_closed"] and not forced_closed):
                return False
            encoded = json.dumps(record, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n"
            # Persist before updating the in-memory accounting. An I/O error
            # stays visible rather than claiming an unjournaled request is done.
            with self.log_path.open("a", encoding="utf-8") as stream:
                stream.write(encoded)
                stream.flush()
            if record["forwarded"]:
                state = self._arm_state[record["arm"]]
                self._pending -= 1
                state["pending"] -= 1
                self._inflight.pop(request_id, None)
                if record["request_kind"] == "token_count":
                    self._count_pending -= 1
                    state["count_pending"] -= 1
                    if record["complete"]:
                        self._count_completed += 1
                        state["count_completed"] += 1
                    else:
                        self._count_failed += 1
                        state["count_failed"] += 1
                else:
                    self._generation_pending -= 1
                    state["generation_pending"] -= 1
                    state["pending_reservation"] = (max(
                        0.0, state["pending_reservation"] - record["budget_reservation_usd"])
                        if state["generation_pending"] else 0.0)
                    cost = record["cost"]
                    if cost["status"] == "estimated":
                        self._cost += cost["usd_upper_bound"]
                        state["known_cost"] += cost["usd_upper_bound"]
                    else:
                        self._unknown += 1
                        state["unknown"] += 1
                        partial = cost.get("observed_partial_token_usd_peak_estimate") or 0.0
                        self._partial_cost += partial
                        state["partial_cost"] += partial
                        state["unknown_reservation"] += max(
                            record["budget_reservation_usd"], partial)
            self._records.append(record)
            self._recorded_ids.add(request_id)
            self._condition.notify_all()
            return True

    def summary(self):
        with self._lock:
            by_arm = {}
            for arm in sorted(self.arms):
                state = self._arm_state[arm]
                records = [row for row in self._records if row["arm"] == arm]
                blocked = self._block_reason(arm)
                by_arm[arm] = {"requests": len(records),
                               "forwarded": sum(row["forwarded"] for row in records),
                               "forwarded_requests": state["forwarded"],
                               "pending_requests": state["pending"],
                               "generation_forwarded_requests": state["generation_forwarded"],
                               "generation_pending_requests": state["generation_pending"],
                               "generation_provider_completed_requests": sum(
                                   row["request_kind"] == "generation" and row["provider_response_complete"]
                                   for row in records),
                               "client_disconnected_requests": sum(row["client_disconnected"] for row in records),
                               "token_count_forwarded_requests": state["count_forwarded"],
                               "token_count_pending_requests": state["count_pending"],
                               "token_count_completed_requests": state["count_completed"],
                               "token_count_failed_requests": state["count_failed"],
                               "known_token_usd_upper_bound": state["known_cost"],
                               "observed_partial_token_usd_peak_estimate": state["partial_cost"],
                               "unknown_usage_requests": state["unknown"],
                               "unresolved_usage_requests": state["unknown"] + state["generation_pending"],
                               "budget_accounting_complete": not state["unknown"] and not state["generation_pending"],
                               "unknown_usage_reservation_usd": state["unknown_reservation"],
                               "pending_usage_reservation_usd": state["pending_reservation"],
                               "budget_committed_usd": state["known_cost"] + state["unknown_reservation"] + state["pending_reservation"],
                               "subsequent_requests_blocked": blocked is not None,
                               "block_reason": blocked,
                               "arm_stop_reason": state["stop_reason"],
                               "policy_block_reason": self._policy_block_reason(arm),
                               "max_requests": self.max_requests,
                               "budget_usd": self.budget_usd,
                               "complete": sum(row["complete"] for row in records),
                               "http_status_counts": dict(Counter(str(row["http_status"]) for row in records)),
                               "error_classes": dict(Counter(row["error_class"] for row in records if row["error_class"]))}
            return {"forwarded_requests": self._forwarded, "pending_requests": self._pending,
                    "generation_forwarded_requests": self._generation_forwarded,
                    "generation_pending_requests": self._generation_pending,
                    "generation_provider_completed_requests": sum(
                        row["request_kind"] == "generation" and row["provider_response_complete"]
                        for row in self._records),
                    "token_count_forwarded_requests": self._count_forwarded,
                    "token_count_completed_requests": self._count_completed,
                    "token_count_failed_requests": self._count_failed,
                    "token_count_pending_requests": self._count_pending,
                    "token_count_rejected_requests": sum(row["request_kind"] == "token_count" and not row["forwarded"] for row in self._records),
                    "token_count_fee_status": "not_disclosed",
                    "pending_usage_status": "unknown" if self._generation_pending else "none",
                    "unresolved_usage_requests": self._unknown + self._generation_pending,
                    "budget_accounting_complete": not self._generation_pending and not self._unknown,
                    "recorded_requests": len(self._records), "max_requests": self.max_requests,
                    "allow_server_tools": self.allow_server_tools,
                    "known_token_usd_upper_bound": self._cost,
                    "observed_partial_token_usd_peak_estimate": self._partial_cost,
                    "unknown_usage_requests": self._unknown, "budget_usd": self.budget_usd,
                    "max_unknown_usage_requests_per_arm": self.max_unknown_usage_requests,
                    "unknown_usage_reserve_usd_minimum_per_request": self.unknown_usage_reserve_usd,
                    "unknown_usage_reservation_usd": sum(s["unknown_reservation"] for s in self._arm_state.values()),
                    "pending_usage_reservation_usd": sum(s["pending_reservation"] for s in self._arm_state.values()),
                    "subsequent_requests_blocked": all(s["subsequent_requests_blocked"] for s in by_arm.values()),
                    "blocked_arms": [arm for arm, state in by_arm.items() if state["subsequent_requests_blocked"]],
                    "budget_scope": "independent per-arm request limits and generation token policy reservations; token_count endpoint fees not disclosed; not a prepaid absolute billing cap",
                    "retry_policy": "no proxy replay; native client retries share the same per-arm request, unknown-response and reservation limits; successful retries do not erase unknown earlier fees",
                    "reservation_policy": "pending and unresolved generation attempts reserve at least the configured minimum, or frozen 1M input plus requested output at peak token prices, or the larger observed partial estimate; reservations are policy amounts, not disclosed fees and not guaranteed billing bounds",
                    "policy_reservations_are_fees": False,
                    "request_timestamp_timezone": "UTC; each journal row retains started_at and ended_at for peak/off-peak repricing",
                    "client_disconnect_observation_max_seconds": self.request_timeout,
                    "by_arm": by_arm}

    def _observe_record(self, record, observer):
        observed = observer.snapshot()
        usage = observed.pop("usage")
        observed.pop("message_stop")
        observed.pop("error_class")
        record.update(observed)
        record["usage"] = {"input_tokens": None, "output_tokens": None,
                           "cache_read_input_tokens": None,
                           "cache_creation_input_tokens": None, **usage}
        if record["request_kind"] == "token_count":
            record["usage"] = None
            record["cost"] = {"status": "not_disclosed", "usd_upper_bound": None,
                              "scope": "token_count endpoint fee not disclosed; returned count is not generation usage"}
            return
        cost = estimate_flash_peak_cost(usage, input_tokens_semantics=self.input_tokens_semantics)
        if record["invalid_usage_fields"]:
            cost["status"] = "unknown"
            cost["usd_upper_bound"] = None
            cost["reasons"].append("invalid_observed_usage_fields:" + ",".join(record["invalid_usage_fields"]))
        if not record["provider_response_complete"]:
            cost["observed_partial_token_usd_peak_estimate"] = cost["usd_upper_bound"]
            cost["usd_upper_bound"] = None
            cost["status"] = "unknown"
            cost["reasons"].append("incomplete_response_usage_may_be_partial")
        record["cost"] = cost

    def _handle(self, handler, method_allowed=True):
        started = time.monotonic()
        record = {"request_id": uuid.uuid4().hex, "arm": None, "path": None,
                  "request_kind": None, "input_tokens_count": None,
                  "model": None, "thinking_type": None, "output_effort": None,
                  "max_tokens": None, "request_bytes": None, "request_sha256": None,
                  "budget_reservation_usd": None,
                  "messages_bytes": None, "messages_sha256": None,
                  "system_bytes": None, "system_sha256": None,
                  "request_tool_names": [], "request_tool_types": [],
                  "allow_server_tools": self.allow_server_tools,
                  "request_tool_result_is_error_count": 0, "streaming": None,
                  "started_at": datetime.now(timezone.utc).isoformat(),
                  "ended_at": None, "duration_seconds": None, "http_status": None,
                  "error_class": None, "forwarded": False, "complete": False,
                  "provider_response_complete": False, "client_disconnected": False,
                  "observed_model": None, "usage": None, "response_tool_names": {},
                  "invalid_usage_fields": [],
                  "response_tool_types": {}, "response_tool_count": 0,
                  "response_tool_result_is_error_count": 0,
                  "cost": {"status": "not_forwarded", "usd_upper_bound": None}}
        observer = None
        response_started = False
        disconnected_at = None

        def reject(status, error):
            nonlocal response_started
            record["http_status"], record["error_class"] = status, error
            body = _json_bytes({"type": "error", "error": {"type": "experiment_proxy_error", "message": error}, "request_id": record["request_id"]})
            handler.send_response(status)
            handler.send_header("Content-Type", "application/json")
            handler.send_header("Content-Length", str(len(body)))
            handler.send_header("Connection", "close")
            handler.end_headers()
            response_started = True
            if handler.command != "HEAD":
                handler.wfile.write(body)
                handler.wfile.flush()

        try:
            parsed = urlsplit(handler.path)
            match = re.fullmatch(r"/([a-z][a-z0-9_-]{0,31})/(v1/)?messages", parsed.path)
            count_match = re.fullmatch(r"/([a-z][a-z0-9_-]{0,31})/(v1/)?messages/count_tokens", parsed.path)
            candidate = match or count_match
            if parsed.scheme or parsed.netloc or parsed.fragment or parsed.query not in ("", "beta=true") or candidate is None or candidate[1] not in self.arms:
                reject(404, "RouteNotAllowed")
                return
            record["arm"], record["path"] = candidate[1], parsed.path
            record["request_kind"] = "token_count" if count_match else "generation"
            if not method_allowed:
                reject(405, "MethodNotAllowed")
                return
            if handler.headers.get("Transfer-Encoding") is not None:
                reject(400, "ChunkedRequestUnsupported")
                return
            lengths = handler.headers.get_all("Content-Length", [])
            if len(lengths) != 1 or not re.fullmatch(r"[0-9]+", lengths[0]):
                reject(411, "ContentLengthRequired")
                return
            length = int(lengths[0])
            if length > self.max_request_bytes:
                reject(413, "RequestTooLarge")
                return
            handler.connection.settimeout(self.request_timeout)
            raw = handler.rfile.read(length)
            if len(raw) != length:
                reject(400, "IncompleteRequestBody")
                return
            record["request_bytes"], record["request_sha256"] = len(raw), hashlib.sha256(raw).hexdigest()
            try:
                payload = _strict_json(raw)
            except (ValueError, UnicodeError, RecursionError):
                reject(400, "InvalidRequestJSON")
                return
            if isinstance(payload, dict):
                record["model"] = _safe_model_name(payload.get("model"))
                thinking = payload.get("thinking")
                if isinstance(thinking, dict):
                    record["thinking_type"] = thinking.get("type") if thinking.get("type") in ("enabled", "disabled", "adaptive") else "<other>"
                output_config = payload.get("output_config")
                if isinstance(output_config, dict):
                    effort = output_config.get("effort")
                    record["output_effort"] = effort if effort in ("low", "medium", "high", "max", "xhigh") else "<other>"
                record["max_tokens"] = _counter(payload.get("max_tokens"))
                record["streaming"] = payload.get("stream") is True
            if not isinstance(payload, dict) or payload.get("model") != MODEL:
                reject(400, "ModelNotAllowed")
                return
            for key in ("messages", "system"):
                content = _json_bytes(payload.get(key))
                record[key + "_bytes"] = len(content)
                record[key + "_sha256"] = hashlib.sha256(content).hexdigest()
            for tool in payload.get("tools", []) if isinstance(payload.get("tools"), list) else []:
                if isinstance(tool, dict):
                    record["request_tool_names"].append(_safe_name(tool.get("name")))
                    record["request_tool_types"].append(_safe_name(tool.get("type", "custom")))
            record["request_tool_result_is_error_count"] = _tool_result_errors(payload.get("messages"))
            if not self.allow_server_tools:
                tools = payload.get("tools")
                if tools is not None and (not isinstance(tools, list) or any(
                        not isinstance(tool, dict) or ("type" in tool and tool["type"] != "custom")
                        for tool in tools)):
                    reject(403, "OfflineServerToolBlocked")
                    return
            observer = (_TokenCountObserver() if record["request_kind"] == "token_count"
                        else _ResponseObserver(record["streaming"]))
            blocked = self._admit(record, observer, handler, started)
            if blocked:
                observer = None
                reject(429, blocked)
                return
            connection_tokens = {part.strip().lower() for part in handler.headers.get("Connection", "").split(",")}
            # Deliberate allowlist: client authentication and arbitrary custom
            # headers never reach the provider. Body bytes are passed unchanged.
            headers = {key: value for key, value in handler.headers.items()
                       if key.lower() in {"content-type", "anthropic-version", "anthropic-beta", "accept"}
                       and key.lower() not in _HOP | connection_tokens}
            with self._lock:
                entry = self._inflight.get(record["request_id"])
                if entry is None or entry["forced_closed"]:
                    return
                api_key = self._api_key
            headers.update({"Authorization": "Bearer " + api_key,
                            "x-api-key": api_key, "Accept-Encoding": "identity"})
            upstream_url = self._count_upstream if record["request_kind"] == "token_count" else self._upstream
            upstream_request = Request(upstream_url, data=raw, headers=headers, method="POST")
            try:
                upstream = self._opener.open(upstream_request, timeout=self.request_timeout)
            except HTTPError as error:
                upstream = error  # Preserve provider HTTP status and body.
                record["error_class"] = "UpstreamHTTPError"
            with upstream:
                if not self._register_response(record["request_id"], upstream):
                    return
                record["http_status"] = upstream.status
                try:
                    handler.send_response(upstream.status)
                    upstream_connection = {part.strip().lower() for part in upstream.headers.get("Connection", "").split(",")}
                    # Never send provider auth, cookies, or arbitrary headers back.
                    for key in ("Content-Type", "Content-Encoding", "Content-Length", "Retry-After"):
                        value = upstream.headers.get(key)
                        if value is not None and key.lower() not in upstream_connection:
                            handler.send_header(key, value)
                    handler.send_header("Connection", "close")
                    handler.end_headers()
                except (BrokenPipeError, ConnectionResetError):
                    record["client_disconnected"] = True
                    disconnected_at = time.monotonic()
                response_started = True
                response_bytes = 0
                while True:
                    if disconnected_at is not None:
                        remaining = self.request_timeout - (time.monotonic() - disconnected_at)
                        if remaining <= 0:
                            observer.note_error("DisconnectedObservationTimeout")
                            break
                        self._set_response_timeout(upstream, remaining)
                    try:
                        chunk = upstream.read1(65536) if hasattr(upstream, "read1") else upstream.read(65536)
                    except TimeoutError:
                        # The shortened socket timeout is another way the same
                        # disconnect observation deadline expires. Classify it
                        # consistently with the pre-read deadline check; a real
                        # upstream idle timeout before that deadline retains its
                        # original category and never acquires complete usage.
                        if (disconnected_at is not None
                                and time.monotonic() >= disconnected_at + self.request_timeout):
                            observer.note_error("DisconnectedObservationTimeout")
                            break
                        raise
                    if not chunk:
                        break
                    response_bytes += len(chunk)
                    observer.feed(chunk)
                    if not record["client_disconnected"]:
                        try:
                            handler.wfile.write(chunk)
                            handler.wfile.flush()
                        except (BrokenPipeError, ConnectionResetError):
                            # Keep observing this admitted response for its final
                            # usage. The idle socket timeout and close/drain cap
                            # still bound observation; no request is replayed.
                            record["client_disconnected"] = True
                            disconnected_at = time.monotonic()
                expected_bytes = upstream.headers.get("Content-Length")
                if expected_bytes is not None and (not expected_bytes.isdigit() or response_bytes != int(expected_bytes)):
                    observer.note_error("TruncatedHTTPBody")
            observer.finish()
            observed = observer.snapshot()
            record["error_class"] = record["error_class"] or observed["error_class"]
            record["provider_response_complete"] = (
                200 <= record["http_status"] < 300 and record["error_class"] is None
                and (observed["message_stop"] if observer.streaming else True))
            if record["client_disconnected"]:
                record["error_class"] = record["error_class"] or "ClientDisconnected"
            record["complete"] = record["provider_response_complete"] and not record["client_disconnected"]
        except (BrokenPipeError, ConnectionResetError) as error:
            if observer is not None and record["forwarded"]:
                # Downstream header/body writes are handled where they happen;
                # an uncaught socket error here belongs to the upstream path.
                record["error_class"] = "Upstream" + type(error).__name__
            else:
                record["error_class"] = "ClientDisconnected"
                record["client_disconnected"] = True
        except Exception as error:
            # Class names are safe diagnostic categories; exception messages and
            # repr may contain request URLs, credentials, or response content.
            record["error_class"] = _safe_name(type(error).__name__)
            if not response_started:
                try:
                    reject(502, record["error_class"])
                except (BrokenPipeError, ConnectionResetError):
                    pass
        finally:
            handler.close_connection = True
            if observer is not None:
                self._observe_record(record, observer)
            record["ended_at"] = datetime.now(timezone.utc).isoformat()
            record["duration_seconds"] = round(time.monotonic() - started, 6)
            self._write_record(record)
