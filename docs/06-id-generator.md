# ID Generation Strategies — Comparison

Four approaches to generating a unique short code, and the trade-off each one makes.

| Strategy | Uniqueness guarantee | Coordination required | Typical length | Sortable by time | Predictable/enumerable | Infra dependency |
|---|---|---|---|---|---|---|
| DB sequence + Base62 (Phase 3) | Guaranteed (DB primary key) | One authoritative database | ~7 chars | Yes (increasing) | Yes — the core weakness | Postgres |
| Random Base62 + retry | Guaranteed (unique constraint + retry) | Database, to detect collisions | 7 chars (fixed) | No | No | Postgres |
| UUID v4 + Base62 | Probabilistic (collision astronomically unlikely) | None | ~22 chars | No | No | None |
| Snowflake-style | Guaranteed, if machine IDs are assigned correctly | Machine ID assignment only (not per-ID) | ~11 chars | Yes (increasing) | Partially — reveals approximate creation time | A machine-ID allocation mechanism (e.g. config, ZooKeeper in the original design) |

## Notes

- The DB-sequence approach is the only one of the four that cannot generate an ID without a live database connection — every other strategy is a pure function.
- Snowflake gets sortability *and* no per-ID database round-trip, but pays for it with an operational requirement: every running instance needs a machine ID nobody else is using, decided out of band.
- UUID is the only approach here with zero uniqueness guarantee in the strict sense — it's a probability, not a proof — but the probability is low enough that no real system has ever reported a genuine UUID v4 collision in practice.
- None of the four fully solve predictability; only random and UUID avoid leaking creation order.