# Tests as behavior evidence and documentation as authority

## Tests

- Choose the narrowest test that proves the accepted behavior, then add integration or contract coverage when the behavior crosses a real boundary.
- For a defect, add or update a regression test that fails for the pre-fix behavior and passes after the correction when practicable.
- Test observable behavior and the relevant edge and failure paths. Avoid assertions coupled only to implementation details unless that detail is itself contractual.
- Verify that a test would fail if the protected behavior broke. A passing test that cannot detect the defect is not evidence.
- Keep tests deterministic, readable, and actionable enough to identify what behavior failed.
- Use coverage to locate untested risk, not as proof of correctness or a completion score.
- Never disable, skip, or weaken a test to make a run pass. If a test is wrong, fix the test with evidence that the new expectation is the contract.

## Documentation

- Update affected API or reference documentation, source comments, configuration examples, setup and runbook instructions, and migration notes in the same change as the behavior they describe.
- Remove false or obsolete material, or explicitly mark it as superseded when history must be retained. Do not leave contradictory instructions in place.
- Prefer names, types, schemas, and tests for facts they can express. Use comments for non-obvious intent, constraints, trade-offs, and safety reasoning rather than narrating mechanics. Remove commented-out code.
- Keep each fact in one authoritative location and link to it instead of copying it. Verify changed commands and examples when practicable.
- Create or update a decision record only for a durable, consequential choice whose context and trade-offs would otherwise be lost. Follow the project's convention, keep it short, and supersede prior decisions explicitly rather than silently rewriting history.
