# Adoption and evaluation

Use this reference when the request concerns the delivery process itself,
unattended jobs, or changing the configuration that steers an agent. Ordinary
implementation does not require this adoption exercise.

## Improve one observed bottleneck

Trace a representative completed change through the current records. Identify
where time or rework accumulated and who owns that transition. Preserve tools
that already provide authoritative requirements, review, or release evidence.
Propose one intervention with a baseline, expected benefit, evaluation window,
and removal/rollback condition. Do not deploy the entire lifecycle as a bundle.

Put durable conventions in the host's existing project instruction mechanism,
reusable procedures in skills, and mandatory controls in runtime/CI policy.
Avoid repeating the same rule in all three. Add instructions only for a recurring
need with a clear owner, and remove obsolete instructions when code or controls
make them unnecessary. A single incident is evidence to investigate, not an
automatic mandate for another permanent rule.

## Evaluate configurations before promoting them

Keep software regression tests and agent-behavior evaluations distinct. A model,
prompt, skill, tool, or permission change can affect delivery even if application
code is unchanged.

Use representative tasks with independently specified acceptance checks and a
baseline configuration. Include ordinary successes, missing capabilities, policy
boundaries, and recovery. Use disposable workspaces and reset state between runs.
For stochastic behavior, repeat the cases enough to characterize the relevant
failure rate; report the sample size and uncertainty rather than one perfect run.

Pin or record model identifiers, host/tool versions, instruction digests, fixture
revision, relevant parameters, budgets, and result evidence. Do not put private
transcripts or credentials in published results. Keep cases used for tuning
separate from the cases used to decide promotion.

Prefer executable acceptance checks. For judgments that need a rubric, define
acceptable, unacceptable, and insufficient-evidence outcomes and calibrate against
qualified review. A faster configuration does not pass if it violates a mandatory
boundary. Promotion requires the declared gates and existing decision authority;
retain a known baseline and a way to revert configuration changes.

## Introduce unattended execution only when authorized

Begin with a bounded read-only or proposal-producing job. Before enabling writes,
identify the real enforcement for allowed targets, operations, credentials, and
approval. Specify event identity/deduplication, queue/concurrency limits, retry and
cost budgets, cancellation, and routing for unresolved work. Prevent the job's own
updates from triggering an unbounded succession of new jobs.

When an operation times out, look up its authoritative state before resubmitting.
Pre-approval must cover the actual runbook, target, and conditions; a generic
approval of the process does not authorize arbitrary recovery actions. Exercise
recovery in a disposable or appropriate nonproduction environment before relying
on it. Escalate when the observed state falls outside the approved route.

Monitoring should use a detector suited to the metric's distribution, sample
volume, seasonality, and existing service objectives. Do not copy universal
standard-deviation thresholds into unrelated systems. Evaluate detection quality
and false positives before allowing the signal to trigger effects.

## Measure the outcome

Choose measures for the bottleneck, such as waiting time, rework, defects escaping
review, recovery time, human review effort, or total delivery cost. Define start
and stop events in the authoritative system. A commit timestamp cannot measure a
conversation that happened before the commit. Keep task mix and time window
comparable; more generated code or concurrent agents is not itself improvement.

Report baseline and candidate results together with failures and unmeasured
effects. Keep, revise, or remove the intervention from the observed evidence.
