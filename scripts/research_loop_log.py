"""Durable JSONL events compatible with the shared research-loop journal."""
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import fcntl
import json
import os
import re


def _clean(value):
    if isinstance(value, dict):
        return {k: '[redacted]' if re.search(r'token|secret|password|authorization|credential|api_key',k,re.I)
                else _clean(v) for k,v in value.items()}
    if isinstance(value, (list,tuple)):
        return [_clean(v) for v in value]
    if isinstance(value, str):
        return re.sub(r'(?i)(bearer\s+|(?:token|secret|password|api_key)\s*[=:]\s*)[^\s,;]+',
                      lambda m:m.group(1)+'[redacted]',value)
    return value


def record(path, *, repository, stage, event, **fields):
    """Fail visibly on journal IO errors; fsync under a cross-process lock."""
    path=Path(path)
    row=dict(schema_version='research-loop-event/v1',
             ts=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds'),
             repository=repository,stage=stage,event=event,**_clean(fields))
    raw=(json.dumps(row,ensure_ascii=False,allow_nan=False)+'\n').encode()
    path.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_APPEND,0o600)
    with os.fdopen(fd,'ab') as stream:
        fcntl.flock(stream,fcntl.LOCK_EX)
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
