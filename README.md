# KeyCommit — Deterministic Change Summaries for Fast, Trusted Delivery

## 1) Problem

Engineering and product teams lose time and context because commit messages, PR descriptions, and change notes are:
- **Inconsistent**: style, depth, and terminology vary by author and time pressure.
- **Costly to review**: reviewers must parse large diffs without a reliable overview.
- **Hard to trust** with AI: LLM outputs can be non‑deterministic and hard to cache or reproduce.
- **Difficult to reuse**: the same change context is summarized repeatedly across tools (PRs, release notes, changelogs, status updates).

**Impact today**
- Slower reviews and merges, more rework, and fragile release notes.
- Duplication of effort as summaries are regenerated—sometimes inconsistently.
- Low confidence when AI outputs drift between runs.

---

## 2) Solution (MVP)

**KeyCommit** provides a **deterministic pipeline** for change intelligence:

1. **Canonicalise** the input (diff/text/JSON) → a stable, formatting‑agnostic string.  
2. Produce a **SHA‑256 content key** → enables **idempotent caching**, change detection, and provenance.  
3. Call an **AI adapter**:
4. Emit a minimal **schema‑checked summary object** (title, bullet points, risk flags, components touched), safe to persist and re‑use.

**Design principles**
- **Determinism first**: same input → same canonical form → same key → same (stub) summary.
- **Small surface**: pure functions; dependency‑light; easy to test in isolation.
- **Replaceable adapters**: the API stays stable while providers change.
- **Content‑addressable**: keys enable caching, deduplication, and reproducible builds/docs.

---

## 4) Target users & jobs‑to‑be‑done

- **Engineers**: glanceable, deterministic summaries that speed up reviews.
- **Product/Release managers**: auto‑curated release notes from trusted, reproducible summaries.
- **Tech leads**: stable signals to spot risky changes (files/components touched, size/risk flags).

---

## 5) How it works (high‑level)

```mermaid
flowchart TD
  A[Raw Input (diff/text/JSON)] --> B[canonicalise()]
  B --> C[sha256_hex()]
  C -->|key| D[AI Adapter]
  D --> E[Summary (schema-validated)]
  E --> F[Store/Compare/Publish]