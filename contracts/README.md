# Shared contracts

These files are the single authoritative source for behavior that more than one package enforces. Packages stay self-contained by embedding a verbatim copy between marker comments; `scripts/validate_repo.py` fails when an embedded copy drifts from the file here.

| Contract | Owner file | Embedded by |
| --- | --- | --- |
| Task contract | [`task-contract.schema.json`](./task-contract.schema.json) | `cleancoding` (acceptance contract), `anti-loop` (task anchor), `temporal-tasks` (budget fields) |
| Repeated-attempt stop rule | [`loop-limit.md`](./loop-limit.md) | `cleancoding`, `anti-loop`; the `anti-loop` hook emits the same receipt |
| Handoff receipt | [`handoff-receipt.md`](./handoff-receipt.md) | `cleancoding`, `anti-amnesia` |

## Embedding rule

Copy the block between `<!-- contract:<name>:start -->` and `<!-- contract:<name>:end -->` exactly, markers included. Change the contract here first, then re-copy it into every embedding package in the same commit.

## Task contract fields

A task contract is derived from the request and inspected evidence, kept in working context, and not written to a file unless the user asks. The schema exists so hooks, evals, and skills agree on field names:

- `task_type`: `defect`, `incident`, `feature`, `refactor`, `review`, `research`, or `mixed`.
- `outcome`: the observable result the user asked for.
- `acceptance_checks`: the smallest checks that prove the outcome.
- `baseline`: current behavior or the exact failure evidence, when one exists.
- `non_goals`: adjacent work deliberately excluded.
- `surface`: files or subsystems expected to change.
- `constraints`: preserved behavior, contracts, and known consumers.
- `stop_condition`: when the work is complete.
- `budget`: optional difficulty score, confidence, expected range, and no-progress checkpoint.
