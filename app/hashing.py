# app/hashing.py
from __future__ import annotations

import base64
import hashlib
import json
from datetime import date, datetime, timezone
from typing import Any, Mapping, Iterable


def _to_canonicalable(obj: Any) -> Any:
    """Convert arbitrary Python objects into JSON-serialisable, deterministic structures."""
    # datetime / date
    if isinstance(obj, datetime):
        # normalise TZ-aware datetimes to UTC ISO; naive datetimes keep as-is ISO
        if obj.tzinfo is not None and obj.tzinfo.utcoffset(obj) is not None:
            obj = obj.astimezone(timezone.utc)
        return obj.isoformat()
    if isinstance(obj, date):
        return obj.isoformat()

    # bytes → base64
    if isinstance(obj, (bytes, bytearray, memoryview)):
        return {"__bytes__": base64.b64encode(bytes(obj)).decode("ascii")}

    # strings → normalise newlines only
    if isinstance(obj, str):
        return obj.replace("\r\n", "\n").replace("\r", "\n")

    # mappings → sort keys lexicographically, recurse values
    if isinstance(obj, Mapping):
        return {str(k): _to_canonicalable(v) for k, v in sorted(obj.items(), key=lambda kv: str(kv[0]))}

    # sets → sorted list (by canonical string) for determinism
    if isinstance(obj, set):
        items = [(_canonical_string(v), _to_canonicalable(v)) for v in obj]
        items.sort(key=lambda t: t[0])
        return [v for _, v in items]

    # sequences (list/tuple) → preserve order
    if isinstance(obj, tuple):
        return [_to_canonicalable(v) for v in obj]
    if isinstance(obj, list):
        return [_to_canonicalable(v) for v in obj]

    # primitives (int/float/bool/None) are fine; everything else fallback to str()
    try:
        json.dumps(obj)  # probe serialisability
        return obj
    except TypeError:
        return str(obj)


def _canonical_string(obj: Any) -> str:
    """Return a compact JSON string with sorted keys and stable formatting."""
    transformed = _to_canonicalable(obj)
    return json.dumps(transformed, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def canonicalise(obj: Any) -> str:
    """Public API: produce a deterministic string for any Python object."""
    return _canonical_string(obj)


def sha256_hex(text: str) -> str:
    """Return the SHA‑256 hex digest of `text`."""
    if not isinstance(text, str):
        raise TypeError("sha256_hex() expects a str")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()