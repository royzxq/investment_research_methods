"""Read-only stdio MCP probes against an explicitly installed AKTools runtime.

The input JSON declares the exact calls. Writes new files only, never config.
Run with --python <isolated-venv>/bin/python --manifest file --output new-dir.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import select
import subprocess
import time


def result_object(response):
    if not isinstance(response, dict) or 'error' in response or not isinstance(response.get('result'), dict):
        raise RuntimeError('MCP returned an error or invalid result envelope')
    return response['result']


def run(python, manifest, output):
    output.mkdir(parents=True, exist_ok=False)
    env = {k: os.environ[k] for k in ('PATH', 'LANG', 'TMPDIR') if k in os.environ}
    env.update(HOME=str(output / 'home'), PYTHONUNBUFFERED='1', AKTOOLS_TIMEOUT='20', AKTOOLS_CACHE_TTL='60')
    (output / 'home').mkdir()
    (output / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    (output / 'driver.json').write_text(json.dumps(dict(
        driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        python=str(python), network_timeout_seconds=20, cache_ttl_seconds=60,
        rpc_timeout_seconds=60, isolated_python=True), indent=2) + '\n')
    with (output / 'stderr.log').open('w') as stderr:
        process = subprocess.Popen([str(python), '-I', '-B', '-m', 'aktools.mcp_server'], env=env,
            cwd=output, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr, bufsize=0)
        pending = b''
        seq = 0
        def rpc(method, params):
            nonlocal seq, pending
            seq += 1
            process.stdin.write((json.dumps(dict(jsonrpc='2.0', id=seq, method=method, params=params)) + '\n').encode())
            process.stdin.flush()
            deadline = time.monotonic() + 60
            while time.monotonic() < deadline:
                if b'\n' in pending:
                    line, pending = pending.split(b'\n', 1)
                    message = json.loads(line)
                    if message.get('id') == seq:
                        return message
                else:
                    ready, _, _ = select.select([process.stdout], [], [], max(0, deadline - time.monotonic()))
                    if not ready:
                        break
                    chunk = os.read(process.stdout.fileno(), 65536)
                    if not chunk:
                        raise RuntimeError('MCP server closed its output')
                    pending += chunk
            raise TimeoutError('MCP request deadline exceeded')
        try:
            hello = rpc('initialize', dict(protocolVersion='2025-03-26', capabilities={},
                        clientInfo=dict(name='research-isolated-evaluation', version='1')))
            (output / 'initialize.json').write_text(json.dumps(hello, indent=2))
            initialization = result_object(hello)
            if initialization.get('protocolVersion') != '2025-03-26':
                raise RuntimeError('MCP initialization did not agree to the requested protocol')
            process.stdin.write(b'{"jsonrpc":"2.0","method":"notifications/initialized"}\n')
            process.stdin.flush()
            tools = rpc('tools/list', {})
            (output / 'tools.json').write_text(json.dumps(tools, ensure_ascii=False, indent=2))
            listed = result_object(tools).get('tools')
            if not isinstance(listed, list) or not {'search_interfaces', 'describe_interface', 'get_data'}.issubset(
                    {tool.get('name') for tool in listed if isinstance(tool, dict) and isinstance(tool.get('name'), str)}):
                raise RuntimeError('MCP did not advertise the expected AKTools capabilities')
            for i, call in enumerate(manifest['calls']):
                started = time.monotonic()
                row = dict(call=call)
                try:
                    row['response'] = rpc('tools/call', call)
                    result = result_object(row['response'])
                    row['ok'] = result.get('isError', False) is False and bool(result.get('content') or result.get('structuredContent'))
                except (TimeoutError, RuntimeError, ValueError) as exc:
                    row.update(ok=False, error=type(exc).__name__)
                row['duration_seconds'] = round(time.monotonic() - started, 3)
                (output / f'call-{i:02d}.json').write_text(json.dumps(row, ensure_ascii=False, indent=2))
                print(json.dumps(dict(index=i, name=call['name'], ok=row['ok'], seconds=row['duration_seconds'])), flush=True)
                if row.get('error'):
                    break
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            finally:
                process.stdin.close()
                process.stdout.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--python', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.python.absolute(), json.loads(args.manifest.read_text()), args.output.absolute())
