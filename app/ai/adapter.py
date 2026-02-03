from __future__ import annotations

from typing import List, Protocol
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, timezone, timedelta

from app.hashing import canonicalise, sha256_hex


class Summary(BaseModel):
    """Schema for the output we will persist / reuse."""
    key: str = Field(..., description="Content-addressed key: sha256_hex(canonical_input)")
    title: str
    bullets: List[str]
    risks: List[str] = []
    components: List[str] = []
    # Deterministic ISO timestamp (StubAdapter sets this; no default here)
    created_at: str

    # Pydantic v2 style config (fixes the deprecation warning)
    model_config = ConfigDict(frozen=True)


class AIAdapter(Protocol):
    """Adapter interface (future: OpenAI, Azure, etc.)."""
    def summarize(self, text: str) -> Summary: ...


class StubAdapter:
    """
    Deterministic fake adapter.
    Same input → same canonical form → same key → same summary (byte-for-byte).
    """
    ADJ = ["Accurate", "Clear", "Concise", "Actionable", "Auditable", "Deterministic", "Reproducible"]
    NOUN = ["Commitment", "Change", "Decision", "Update", "Summary", "Outcome"]
    RISK = ["none", "timeline", "quality", "scope", "dependency"]

    def summarize(self, text: str) -> Summary:
        canonical = canonicalise(text)
        key = sha256_hex(canonical)

        # Use the hash to deterministically pick words
        seed = int(key[:8], 16)
        adj = self.ADJ[seed % len(self.ADJ)]
        noun = self.NOUN[(seed // 7) % len(self.NOUN)]
        risk = self.RISK[(seed // 13) % len(self.RISK)]

        bullets = [
            f"Content key: {key[:12]}…",
            f"Canonical bytes: {len(canonical.encode('utf-8'))}",
            f"Signal: {key[12:20]} → {key[20:28]}",
        ]
        components = [f"comp:{key[-6:-2]}"]
        title = f"{adj} {noun}"
        risks = [] if risk == "none" else [f"Risk: {risk}"]

        # ✅ Deterministic timestamp derived from the hash (no wall-clock)
        # Map first 8 hex digits → seconds in a day; add to a fixed epoch date.
        seconds = seed % (24 * 3600)
        created_dt = datetime(2000, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=seconds)
        created_at = created_dt.isoformat()

        return Summary(
            key=key,
            title=title,
            bullets=bullets,
            risks=risks,
            components=components,
            created_at=created_at,
        )
