# 01 — Requirements & Capacity Estimation

## 1. Problem Statement

Design and build a URL shortening service. A user submits a long URL and
receives a short one. Visiting the short URL redirects the browser to the
original long URL. This is the classic system design interview problem
(Alex Xu, *System Design Interview*, Chapter 8) — here we build it, not just
whiteboard it.

## 2. Functional Requirements

| # | Requirement | Notes |
|---|-------------|-------|
| 1 | Create a short URL from a long URL | `POST /api/v1/urls` |
| 2 | Redirect a short URL to its original URL | `GET /{short_code}` → 302 |
| 3 | Optional custom alias | User supplies their own short code instead of a generated one |
| 4 | URL expiration | Short URLs can have a TTL / expiry date, after which they 410/404 |
| 5 | Basic analytics | Click count, timestamp, coarse geo/device info per short code |

Explicitly **out of scope** for v1 (we may revisit later): user accounts /
auth, link editing after creation, QR code generation, bulk import, custom
domains. Keeping v1 narrow is deliberate — it's what lets us get to a working
system fast and iterate.

## 3. Non-Functional Requirements

| Property | Target / stance | Why it matters here |
|---|---|---|
| **Low redirect latency** | Redirect should feel instant (target: single-digit ms server-side once cached, low tens of ms uncached) | The redirect is the *hot path*. Every extra millisecond is paid by 10x more requests than writes, and users have zero tolerance for a slow redirect — it's on the critical path of someone else's product (a link in an email, a tweet, an ad). |
| **High availability** | Redirects should keep working even if a dependency degrades | A short URL is often embedded somewhere permanent (a printed flyer, an old tweet). If it 500s, that link is dead forever from the clicker's point of view. |
| **Durability** | A short URL, once created, must not silently disappear or repoint | It's a promise: this code maps to this URL, indefinitely (or until its stated expiry). |
| **Scalability** | Must handle growth in both storage (URLs accumulate forever) and traffic (reads dominate and can spike) | 100M new URLs/month compounds — by year 5 we're storing billions of rows. |
| **Security** | Prevent abuse: enumeration of short codes, phishing/malware redirects, SSRF via submitted URLs | The redirect endpoint is a generic "point anywhere" primitive — that's attractive to attackers, not just legitimate users. Deferred to Phase 18 but stated as a requirement now. |
| **Observability** | We must be able to tell *why* the system is slow or wrong, not just *that* it is | Impossible to reason about caching, scaling, or failure behavior later without metrics/traces from day one — introduced progressively from Phase 12. |

Consistency stance (stated now, revisited when we build the DB layer): we
need **strong consistency on write** (a create must not silently fail or
double-allocate a code) but only need **eventual consistency is acceptable
for analytics** (a click counter can lag by seconds). This split matters a
lot for our architecture later — it's why analytics gets pulled off the
critical path in Phase 10–11.

## 4. Read/Write Ratio and Why It Drives the Architecture

We're told to assume:

- **100,000,000 new URLs created per month** (writes)
- **10:1 read/write ratio** (redirects vs. creations)

This single ratio is the most important number in the whole design. A
system that is 10x read-heavy is architected completely differently from a
write-heavy one (e.g., a logging/ingestion pipeline):

- Reads can be **cached** aggressively — the mapping `short_code →
  original_url` is close to immutable once created (it only changes on
  delete/expire), which is the ideal shape for a cache.
- Reads can be served from **replicas** — we don't need every read to see
  the absolute latest write with zero lag.
- The **hot path to optimize first is the redirect**, not the create — 10x
  more traffic flows through it.
- Because reads dominate, a small percentage of *popular* short codes will
  receive a disproportionate share of traffic (power-law / Zipfian
  distribution in the real world) — this is what makes caching so effective,
  and it's also what creates "hot key" problems later (Phase 7).

If the ratio were closer to 1:1, or write-heavy, caching would be far less
valuable and we'd instead focus on write throughput (batching, sharding for
writes, etc.). Read-heavy is the easier and more common case for this kind
of system, but it's easy to get complacent about — we'll deliberately break
the cache in Phase 8 to make sure "it's just an optimization" isn't wishful
thinking.

## 5. Capacity Estimation

All numbers below are computed explicitly so the arithmetic can be checked
and re-derived under different assumptions later (e.g., "what if traffic
grows 10x").

### 5.1 Request volume

**Writes (URL creations):**

```
100,000,000 writes / month
```

**Reads (redirects), at 10:1 read:write:**

```
100,000,000 × 10 = 1,000,000,000 reads / month
```

**Total requests / month:**

```
100,000,000 + 1,000,000,000 = 1,100,000,000 requests / month  (1.1B)
```

### 5.2 Per-day figures (using 30 days/month)

```
Writes/day = 100,000,000 / 30           ≈ 3,333,333  writes/day
Reads/day  = 1,000,000,000 / 30         ≈ 33,333,333 reads/day
Total/day  = 1,100,000,000 / 30         ≈ 36,666,667 requests/day
```

### 5.3 Average requests/sec (using 86,400 seconds/day)

```
Writes/sec (avg) = 3,333,333 / 86,400   ≈ 38.6  → ~39 writes/sec
Reads/sec  (avg) = 33,333,333 / 86,400  ≈ 385.8 → ~386 reads/sec
Total/sec  (avg) = 36,666,667 / 86,400  ≈ 424.4 → ~424 requests/sec
```

So on average, this is a *modest* traffic system — under 500 requests/sec
sustained. A single well-tuned Postgres instance could plausibly handle this
average load without caching at all. That's an important, humbling fact we
should hold onto: **the interesting engineering problems here come from
peaks, growth over time, and tail latency — not from average throughput.**

### 5.4 Peak requests/sec

Average traffic isn't evenly spread across the day — there's a diurnal
pattern (peak business hours vs. 3am), plus the possibility of a viral link
spiking traffic further. A common rule of thumb (and what we'll use) is a
**peak factor of ~3x average**, i.e. assume the busiest sustained second of
the day carries about 3x the average rate. This is an assumption, not a law
of physics — real systems derive this from actual traffic histograms once
they have them. We'll revisit it once we load-test in Phase 14.

```
Peak writes/sec ≈ 39  × 3  ≈ 117  → round to ~120 writes/sec
Peak reads/sec  ≈ 386 × 3  ≈ 1,158 → round to ~1,200 reads/sec
Peak total/sec  ≈ 424 × 3  ≈ 1,272 → round to ~1,300 requests/sec
```

We'll treat **~1,200–1,300 requests/sec, ~1,200 of them reads,** as our
rough peak design target for later load testing (Phase 14), while
acknowledging a single viral link could exceed this locally for one specific
short code — that's a *hot key* problem, not a *system throughput* problem,
and it's solved differently (Phase 7).

### 5.5 Storage estimation (5-year horizon)

Assume the business keeps growing at the same rate (a simplification — real
growth is rarely flat, but it's a reasonable planning baseline):

```
URLs/year  = 100,000,000 × 12 = 1,200,000,000  (1.2B/year)
URLs/5yr   = 1,200,000,000 × 5 = 6,000,000,000  (6B rows)
```

Estimate the size of one row. Fields: `id` (8 bytes bigint), `short_code`
(~7 chars ≈ 7 bytes + overhead), `original_url` (variable, assume ~200 bytes
average — most URLs are well under the 2048-byte practical max), `created_at`
/ `expires_at` (8 bytes each), `user_id` (8 bytes, nullable), `is_active` (1
byte). Including Postgres row/page overhead and a B-tree index on
`short_code`, a reasonable working estimate is **~500 bytes/row**.

```
Storage/5yr ≈ 6,000,000,000 × 500 bytes ≈ 3,000,000,000,000 bytes ≈ 3 TB
```

3 TB over 5 years is large but entirely within what a single well-provisioned
PostgreSQL instance (with appropriate disk, e.g. managed SSD storage) can
hold — this tells us we don't need to shard the database for storage
reasons alone at this scale. We'll revisit this explicitly in
`08-scalability.md` for the 100M → 1B → 10B URL growth path, where sharding
*does* eventually become necessary.

### 5.6 Bandwidth (sanity check, not a bottleneck here)

```
Write bandwidth ≈ 39 writes/sec  × ~500 bytes ≈ 19.5 KB/s
Read bandwidth  ≈ 386 reads/sec  × ~500 bytes ≈ 193 KB/s   (302 response is tiny)
```

Both are negligible — bandwidth is not a constraint for this system at this
scale. This is a useful contrast to storage/query-rate: **capacity
estimation isn't just "compute every number," it's identifying *which*
numbers are actually going to bind.** Here: request rate (esp. peak reads)
and long-term storage growth matter; raw bandwidth doesn't.

### 5.7 Cache sizing (preview — implemented in Phase 6)

Not needed yet, but worth previewing: if we assume an 80/20-style
distribution where a small fraction of short codes account for most redirect
traffic, we don't need to cache 6B rows to get a high cache hit ratio — we
only need to cache the "hot" working set. We'll measure this empirically in
Phase 6/7 rather than guess now.

## 6. Summary Table

| Metric | Value |
|---|---|
| New URLs / month | 100,000,000 |
| Reads / month | 1,000,000,000 |
| Total requests / month | 1,100,000,000 |
| Writes/sec (avg) | ~39 |
| Reads/sec (avg) | ~386 |
| Total/sec (avg) | ~424 |
| Writes/sec (peak, 3x) | ~120 |
| Reads/sec (peak, 3x) | ~1,200 |
| Total/sec (peak, 3x) | ~1,300 |
| Rows after 5 years | ~6,000,000,000 |
| Storage after 5 years | ~3 TB |
| Bandwidth (avg) | Negligible (<250 KB/s combined) |

## 7. What This Tells Us About the Architecture (Phase 1 Preview)

- Average load (~424 rps) is low enough that **Phase 1 needs no cache, no
  load balancer, no sharding** — a single FastAPI process talking to a
  single PostgreSQL instance is a legitimate, honest starting point, not a
  toy. We will *feel* it become insufficient later rather than being told so.
- The 10:1 read/write ratio tells us the system's defining challenge is
  **serving reads fast and cheaply at scale**, which points toward caching
  (Phase 6) and eventually read replicas (Phase 16) — but only once we've
  measured that we actually need them.
- Storage growth (billions of rows over years) tells us **indexing strategy
  and ID generation** (Phases 2–4) matter more than raw disk space — a
  missing index on `short_code` will hurt long before 3 TB of disk becomes a
  real problem.
- Peak vs. average (3x factor) tells us we should **load test for peak, not
  average** (Phase 14), and that a single popular link can create a
  workload spike that no amount of average-case capacity planning would
  catch — foreshadowing hot-key handling in Phase 7.

## 8. Open Questions to Revisit

These are intentionally left unanswered here and will be answered as we
build the corresponding phase:

- Exact short code length and alphabet → Phase 3
- How custom aliases interact with collision handling → Phase 3/5
- What "basic analytics" precisely stores, and whether it's synchronous →
  Phase 10
- Formal availability target (e.g. 99.9% vs 99.99%) → Phase 17/19, once we've
  seen concrete failure modes to reason about the cost/benefit of each nine
