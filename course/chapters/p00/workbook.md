# P00 — Setup and safe service checks

## Your independent task

**SUPPLEMENTARY PRACTICE.** Build an offline public-profile readiness checker. Use basic Python dictionaries, functions and conditionals. The graph wrapper is supplied so you can focus on safe validation. No account, key, `.env`, model invocation or tracing export is part of this task.

Edit only `exercises/starters/p00.py`. Complete its three TODO functions without importing the demonstration or reference solution. Keep the supplied fixtures and graph wiring. The independent teacher reference is `exercises/solutions/p00.py`; the demonstration is `course_lessons/p00.py`.

From the project root, with the prepared Python 3.12 environment selected:

```bash
python -m course_lessons.p00 --backend none
python -m exercises.starters.p00
```

Before editing, the starter must exit successfully with `STARTER_NOT_COMPLETED`. This means work remains; it does not mean the exercise passed. Dependency installation belongs to preparation, not this offline activity.

## Step 1: implement `validate_endpoint`

Accept `service` and an optional string `value`, defaulting to blank. The starter's ORIGINS contains the exact supported hosts: Anthropic's API origin; the US, EU, APAC and AWS US LangSmith API origins; and LangWatch's cloud origin. An unsupported service raises `ValueError`.

Strip surrounding whitespace. Blank uses the first host for that service. Accept HTTPS, no port or literal `:443`, and either no path or one trailing slash. Reject unknown or lookalike hosts, credentials, other paths, malformed or other ports, dangling colons, backslashes, embedded control characters/whitespace, and any `?` or `#`, even when its component is empty. Return `https://HOST` without a port or slash. Use fixed exception text that does not echo the input.

For example, ` https://eu.api.smith.langchain.com:443/ ` canonicalizes to the EU API origin. `https://smith.langchain.com` and `https://app.langwatch.ai?token=sample` must fail. The former is a dashboard host; the latter is not a bare origin. See the official [LangSmith regional list](https://docs.langchain.com/langsmith/cloud).

## Step 2: implement `check_profile`

Accept a mapping and return exactly `status`, `issues`, `endpoints`, and `remote_checked`. Do not mutate or return the input. `remote_checked` is always false. Status is `ready` when there are no issues, otherwise `needs_attention`.

Only the six PUBLIC_FIELDS from the starter are allowed. Unknown keys produce only `unsupported_fields` with an empty endpoint map. Otherwise any non-string value produces only `invalid_value_type`, also with an empty map. Do not echo unknown keys or values, even in exceptions.

For an ordinary public profile, append issues in this exact order:

1. Append `model_invalid` unless the model fully matches `claude-[A-Za-z0-9_.:-]+`. Missing model is invalid. This is syntax only, not availability.
2. Append `backend_invalid` unless the backend is `none`, `langsmith`, `langwatch`, or `both`. A missing backend defaults to `none`.
3. Validate LangSmith then LangWatch origins, even when the proposed backend is `none`. Missing endpoint values default to blank. Retain only valid canonical origins; append `langsmith_endpoint_invalid` or `langwatch_endpoint_invalid` for failures.
4. Only for proposed `langwatch` or `both`, validate key kind: missing defaults to `project`; allowed kinds are `project`, `service`, and `personal`. Invalid kind appends `langwatch_key_kind_invalid`. Otherwise service/personal kind with a missing or whitespace-only project ID appends `langwatch_project_required`. Project-bound kind needs no explicit ID in this exercise.

The [LangWatch guide](https://langwatch.ai/docs/integration/python/guide) explains project scope. Your function does not examine a real key. The supplied wrapper validates before invoking its graph; only the safe report enters graph state. Proposed backend data never turns on tracing.

## Step 3: implement `classify_failure`

Return these exact fixed strings for simulated status inputs; perform no request, sleep or retry:

- `None`: `Check network, DNS, proxy and TLS; never disable certificate checks.`
- `401`: `Verify or rotate the key privately; do not print it.`
- `403`: `Check organization/workspace permissions and model access.`
- `404`: `Check the configured model ID and API resource path.`
- `429`: `Check rate and spend limits; honor Retry-After when present.`
- `529`: `Wait and retry within a bounded backoff budget.`
- Any other status: `Record a sanitized status and request ID; consult official errors.`

These teaching mappings are not a complete SDK error handler. Consult the [official Anthropic error reference](https://platform.claude.com/docs/en/api/errors) for other statuses.

## Run and observe

```bash
python -m exercises.starters.p00
python -m pytest tests/lessons/test_p00.py -q
# Teacher reference, after your attempt:
python -m exercises.solutions.p00 --backend none
```

The starter's self-checks assess your edited functions. The focused pytest file checks the demonstration/reference and starter scaffolding; its passing does not replace inspecting your implementation. Do not run the whole course suite.

READY_PROFILE must produce `ready`, no issues, and the canonical EU LangSmith/default LangWatch origins. REPAIR_PROFILE must produce exactly `model_invalid`, `langsmith_endpoint_invalid`, `langwatch_project_required`, in that order. Its status is `needs_attention`, and its endpoint map contains only LangWatch. The graph messages are respectively `Local profile ready.` and `Repair public settings.` Both reports retain `remote_checked: false`.

Record four concrete observations: your Python minor version and isolation result; the two ordered demonstration graph checks; the repaired profile's exact issue list before repair; and the reason a locally ready profile cannot prove authentication. Include sanitized values only.

## Three progressive hints

1. Start with unknown-field/type rejection. It prevents configuration data from leaking into a report or graph before detailed validation begins.
2. `urlsplit` separates components, but parsing is not validation. Inspect the exact host, raw delimiters, user information, path and port; catch malformed-port errors without echoing input.
3. Build one issue list in the specified order. Keep valid endpoints separately and derive status from whether that list is empty. A small dictionary can implement the fixed failure mappings.

## Completion and stretch

Completion requires three implemented functions, passing starter self-checks, both exact fixture outcomes, unchanged input profiles, secret-free errors, and no file/environment access or remote calls. Until completion retain the honest unfinished behavior; never replace TODOs with unconditional success. P00 rejects `--live` and actual non-none tracing options.

For a stretch, add your own offline assertions for a lookalike host, embedded tab, unknown credential field and personal key with blank project scope. Explain why a proposed `both` profile is not permission to export data. Do not turn the stretch into a real connection check: the separate shared CLI reads private configuration and makes actual requests only after instructor authorization.
