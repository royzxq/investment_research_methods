#!/usr/bin/env python3
"""极简 MCP stdio server:Google 搜索(Gemini grounding)。

Developer API 直调(快、grounding_chunks 结构化来源,计费走预付 credits),
失败自动重试一次;仍失败则**快速返回失败标记**,让 Codex 改用内置网页搜索兜底
(配合 Codex AGENTS.md 里的路由指令)。

- 只暴露一个工具 gemini_web_search(query)
- API key 从环境变量 GEMINI_API_KEY 读取(Codex 配置用 env_vars 继承)
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

API_KEY = os.environ.get("GEMINI_API_KEY", "")
API_MODEL = os.environ.get("GEMINI_SEARCH_MODEL", "gemini-3.1-flash-lite")
API_TIMEOUT_S = int(os.environ.get("GEMINI_SEARCH_API_TIMEOUT", "90"))

TOOL = {
    "name": "gemini_web_search",
    "description": (
        "Google web search via Gemini grounding. Especially good for Chinese-language "
        "queries and fresh news. Returns a synthesized answer with sources."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query (Chinese or English)"},
        },
        "required": ["query"],
    },
}


def search_via_api(query: str) -> str:
    """Developer API 直调:google_search grounding,返回正文 + 结构化来源。失败抛异常。"""
    body = json.dumps({
        "contents": [{"parts": [{"text": query}]}],
        "tools": [{"google_search": {}}],
        # 官方建议 grounding 用 temperature 1.0
        "generationConfig": {"temperature": 1.0},
    }).encode("utf-8")
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{API_MODEL}:generateContent",
        data=body,
        headers={"x-goog-api-key": API_KEY, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=API_TIMEOUT_S) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    cand = data["candidates"][0]
    text = "".join(p.get("text", "") for p in cand["content"]["parts"]).strip()
    if not text:
        raise RuntimeError("empty response text")

    chunks = (cand.get("groundingMetadata") or {}).get("groundingChunks", [])
    if chunks:
        lines = [text, "", "来源:"]
        for i, ch in enumerate(chunks, 1):
            web = ch.get("web", {})
            lines.append(f"{i}. {web.get('title', 'Untitled')} — {web.get('uri', '')}")
        return "\n".join(lines)
    return text


def run_search(query: str) -> str:
    api_err = "GEMINI_API_KEY 未设置"
    if API_KEY:
        for attempt in (1, 2):  # 瞬时抖动(429/5xx/网络)重试一次
            try:
                return search_via_api(query)
            except urllib.error.HTTPError as e:
                detail = ""
                try:
                    detail = json.loads(e.read().decode("utf-8"))["error"]["message"]
                except Exception:
                    pass
                api_err = f"HTTP {e.code} {redact_error(detail)[:150]}"
                if e.code in (400, 401, 403, 404):
                    break  # key/模型问题,重试无意义
            except Exception as e:  # 网络、解析、空响应等
                api_err = redact_error(str(e))[:200]
            if attempt == 1:
                time.sleep(2)

    # 快速失败:返回明确标记,让调用方(Codex)改用内置网页搜索兜底
    return (
        f"[SEARCH_FAILED] gemini_web_search 本次不可用({api_err})。"
        "请改用当前会话内置网页搜索完成本次搜索。"
    )


def redact_error(message: str) -> str:
    """上游错误可能包含凭据，截断前先移除完整 key。"""
    return message.replace(API_KEY, "[REDACTED]") if API_KEY else message


def reply(msg_id, result):
    sys.stdout.write(json.dumps(
        {"jsonrpc": "2.0", "id": msg_id, "result": result}, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        method = msg.get("method")
        msg_id = msg.get("id")
        if method == "initialize":
            reply(msg_id, {
                "protocolVersion": msg.get("params", {}).get("protocolVersion", "2024-11-05"),
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "gemini-search", "version": "2.1.0"},
            })
        elif method == "tools/list":
            reply(msg_id, {"tools": [TOOL]})
        elif method == "tools/call":
            params = msg.get("params", {})
            query = params.get("arguments", {}).get("query", "")
            if params.get("name") != TOOL["name"]:
                text = "[SEARCH_FAILED] unknown tool"
            elif not isinstance(query, str) or not query.strip():
                text = "[SEARCH_FAILED] query must be a non-empty string"
            else:
                text = run_search(query)
            reply(msg_id, {
                "content": [{"type": "text", "text": text}],
                "isError": text.startswith("[SEARCH_FAILED]"),
            })
        elif method == "ping":
            reply(msg_id, {})
        elif msg_id is not None:
            # 未知的带 id 请求,返回方法不存在
            sys.stdout.write(json.dumps({
                "jsonrpc": "2.0", "id": msg_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }) + "\n")
            sys.stdout.flush()
        # 通知类消息(notifications/*)直接忽略


if __name__ == "__main__":
    main()
