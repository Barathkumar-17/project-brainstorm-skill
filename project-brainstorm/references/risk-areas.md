# Risk Areas

Every way a project can lose value. Go through every row. Give each one a status:

- **Mitigated:** name the control and link the FR, NFR or ADR that delivers it.
- **Accepted:** state the reason and the impact if it happens.
- **Not relevant:** state why in one line.

If no row in a group applies, mark the whole group Not relevant in one line with the reason, instead of going row by row. If even one row applies, go through that group row by row.

Record the result as the risk register in `05-threat-model.md`. Add project-specific areas at the end if the project has risks this list doesn't cover.

## Core

| Area | How value is lost | Check |
|---|---|---|
| Functional correctness | Core flow fails, gives wrong results, or misses edge cases | Every core FR has acceptance criteria and edge cases listed |
| Problem fit | Solution misses the real problem or the main user | Core FRs trace to the stated problem; nothing core is missing |
| Data integrity | Corrupt, duplicate or inconsistent data | Constraints, transactions, validation at every write |
| Data loss | Deleted or lost data with no recovery | Backup method, frequency, restore test, recovery point target |

## Performance and resources

| Area | How value is lost | Check |
|---|---|---|
| Response time | Slow screens or API calls | Latency target per key action (for example p95) |
| CPU use | Heavy computation blocks or drains the host or device | Expensive work identified; moved off the request path or optimised |
| Memory use | Leaks, crashes, out-of-memory on low-end devices | Memory budget per target device; large data streamed or paged |
| Storage use | Unbounded growth of database, files or logs | Growth estimate, retention and cleanup rules |
| Network use | Excess payloads, chatty calls, poor results on slow networks | Payload limits, pagination, caching, compression |
| Startup time | Slow first load or app launch | Startup target; lazy loading where useful |
| Battery (mobile) | Background work or polling drains the device | Background tasks batched; push instead of polling |

## Reliability and scale

| Area | How value is lost | Check |
|---|---|---|
| Availability | Downtime when users need it | Availability target; single points of failure named |
| Fault tolerance | One failure cascades | Timeouts, retries with backoff, graceful degradation |
| Scalability | Breaks as users or data grow | Expected load stated; bottleneck identified and handled |
| Concurrency | Race conditions, double submits, lost updates | Locking or idempotency on shared writes |
| Offline and poor network | Unusable or data lost without a connection | Offline behaviour defined; sync and conflict rules |
| External dependencies | A third-party API or service changes or fails | Fallback behaviour; dependency isolated behind an interface |

## Security and privacy

| Area | How value is lost | Check |
|---|---|---|
| Authentication | Account takeover, weak login | Standards-core security section applied |
| Authorization | Users reach data or actions they shouldn't | Role and ownership checks on every protected action |
| Input handling | Injection, XSS, file-upload abuse | Server-side validation and output encoding |
| Secrets | Keys leaked in code, logs or client | Secrets kept server-side in environment config |
| Abuse | Spam, scraping, brute force, resource exhaustion | Rate limits, quotas, CAPTCHA where needed |
| Supply chain | Vulnerable or abandoned packages | Maintained packages only; vulnerability scanning |
| Privacy | Over-collection, leaks, no deletion path | Standards-core privacy section applied |
| Auditability | No record of who did what | Audit log for sensitive actions |

## Usability and reach

| Area | How value is lost | Check |
|---|---|---|
| Usability | Users can't finish the core task | Core flow has the fewest steps possible; clear errors |
| Accessibility | Excludes users with disabilities | WCAG 2.2 AA applied |
| Compatibility | Breaks on some browsers, OS versions or screen sizes | Supported targets listed and tested |
| Localisation | Wrong language, dates, currency or text direction | Locales stated; formats not hard-coded |

## Maintainability and operations

| Area | How value is lost | Check |
|---|---|---|
| Maintainability | Hard to change without breaking things | Modular structure; clear boundaries between components |
| Testability | Can't verify behaviour | Every requirement has a test; components testable in isolation |
| Observability | Failures go unnoticed or can't be diagnosed | Structured logs, error tracking, health check |
| Deployment | Broken releases, no rollback | Repeatable deploy, rollback path, config per environment |
| Upgrades and migrations | Schema or API changes break existing data or clients | Versioned API; migration plan for schema changes |

## AI and ML (applies when the project uses models)

| Area | How value is lost | Check |
|---|---|---|
| Output quality | Wrong, made-up or inconsistent answers | Accuracy target; evaluation set; human check on critical outputs |
| Prompt injection and misuse | Untrusted input steers the model | Inputs separated from instructions; outputs validated before acting |
| Bias and fairness | Unfair results for some groups | Evaluation across user groups |
| Inference cost and speed | Slow or resource-heavy model calls | Model size matched to the task; caching of repeat requests |
| Data drift | Quality drops as real data changes | Monitoring plan for output quality |
