# P00 — Setup and safe service checks

## Teaching purpose and preparation

**SUPPLEMENTARY PRACTICE — 60 minutes.** P00 is preparation for the approved course. Its environment audit, public-profile exercise and safety controls establish a foundation for later lessons.

The outcome is disciplined diagnosis, not a wall of green service indicators. Learners must distinguish executable local code, syntactically acceptable settings, real authenticated requests, persisted telemetry, and dashboard inspection. They may complete P00 without an account or internet connection once dependencies are provisioned. The independent task is exactly the three-function public-profile checker described in the workbook; do not replace it with an API-call assignment.

Before class, select the supplied Python 3.12 environment and ensure the pinned dependencies are available. Do not reinstall a healthy environment during the timed lab. The P00 implementation was checked locally using Python 3.12.13 and focused offline tests; that is not a Windows compatibility claim. Windows activation instructions follow the [Python documentation](https://docs.python.org/3.12/library/venv.html) but remain unexecuted on Windows.

Run only the following lesson-specific checks:

```bash
python -m course_lessons.p00 --backend none
python -m exercises.starters.p00
python -m exercises.solutions.p00 --backend none
python -m pytest tests/lessons/test_p00.py -q
```

Expect an honest unfinished-starter message. Keep the reference solution separate until review. No `.env`, service dashboard, key clipboard, or debug logging is needed on the teaching display. Parent integration supplies genuine execution figures later; do not substitute an illustrative terminal image or claim dashboard checks have occurred.

## Timed demonstration: explain, illustrate, demonstrate

### Minutes 0–7: establish the evidence boundary

Ask, “If a local graph succeeds, which remote service has been authenticated?” The correct response is “None.” Invite learners to name what else a real check needs: approved credentials, a supported endpoint, resource access, and connectivity. Explain that backend selection describes where telemetry may leave the process; it is not just a cosmetic display preference.

Show the concept diagram. Walk the local demonstration path, then the workbook path. Point out that the separate instructor-authorized connection CLI is disconnected from both. In the workbook, `backend: both` is inert profile data. Actual P00 command-line tracing remains `none`.

<!-- ORIGINAL_DIAGRAM -->

### Minutes 7–17: inspect the environment

Run the short Python version/prefix check from the student chapter. Expected properties are Python 3.12.x and virtual-environment detection equal to `True`. Explain that activation is convenient, not mandatory: using the environment's interpreter path is sufficient. Use `python -m pip check` to distinguish package consistency from service connectivity.

Demonstrate `inspect_environment()` in the source. It uses installed-distribution metadata, not `.env` or credential variables. A missing package becomes `not_installed` with an entry in `missing_packages`. Readiness requires the approved Python minor version, isolation and all inventoried packages. This audit does not compare every version against the lock file; the pinned provisioning process and dependency consistency check remain important.

### Minutes 17–30: execute and explain the graph

Run the demonstration command. Identify the two node functions, the three edges and the compile/invoke distinction. Expected responses: a node is ordinary Python work; START and END are boundaries; compilation creates an executable; partial updates preserve untouched state. The [current LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview) explicitly supports mixing deterministic and model-driven work; no model is required here.

Read the actual summary rather than memorizing terminal spacing. The check sequence must be `label_checked`, `graph_completed`. The message uses the normalized synthetic label. Three unsuitable URL examples must be rejected. Both `remote_checked` and `environment_file_read` must be false. The outer CLI `passed` concerns internal assertions, not the inner inventory's readiness or an account check.

Show how `--live` and non-none backend options are rejected before shared CLI initialization. Full option names are required because argparse abbreviations could otherwise bypass a superficial option guard. Never demonstrate a forbidden option by removing the guard or invoking the shared connection checker.

<!-- EXECUTION_FIGURES -->

## Minutes 30–42: guide the independent exercise

Ask learners to run the unchanged starter before editing. It exits successfully with `STARTER_NOT_COMPLETED`, preserving an approachable starting point without falsely reporting success. The only TODO functions are `validate_endpoint`, `check_profile`, and `classify_failure`. The supplied graph wrapper and fixtures are not TODOs.

For endpoint validation, require exact allowlisted hosts, HTTPS, root-only paths, no user information or query/fragment delimiters, and canonical output. Whitespace stripping applies outside the URL only. Reject malformed ports, embedded control characters and backslashes before parser normalization can hide them. `:443` is allowed; `:0443` and a dangling colon are deliberately outside this teaching policy. Exception messages must not echo the supplied input.

For profile validation, unknown keys short-circuit to `unsupported_fields`; otherwise non-string values short-circuit to `invalid_value_type`. Neither path returns any endpoint. For ordinary profiles, preserve the workbook's issue order. Validate both tracing origins even if backend is `none`. Only LangWatch-selected plans apply key-kind/project rules. These are public assertions about a proposed configuration, not key inspection.

Use the hints progressively. First ask what must never enter graph state. Then ask which parsing results need separate checks. Only then suggest constructing the ordered issue list. Avoid exposing the full reference early.

## Minutes 42–51: solution walkthrough and observed outcomes

Run `python -m exercises.solutions.p00 --backend none`. This is an independent implementation, not an import of the demonstration. READY_PROFILE returns `ready`, no issues, canonical EU LangSmith and default LangWatch origins, and `Local profile ready.` REPAIR_PROFILE returns `needs_attention` and exactly `model_invalid`, `langsmith_endpoint_invalid`, `langwatch_project_required`, in that order. Its endpoint map contains only the valid LangWatch origin.

Explain the precedence rules. A project-bound key does not require an explicit project ID in this exercise; personal/service keys do when LangWatch is selected. This follows the [LangWatch integration guide](https://langwatch.ai/docs/integration/python/guide), but the local checker cannot determine whether a real key actually belongs to that category. Unknown credential-like fields are rejected before graph invocation, and only the sanitized report enters state. A syntactic model match is not a list of authorized or existing models.

The final function maps simulated failure codes to fixed safe advice. Review all six specified scenarios and the fallback. None triggers a request or retry. On a real 429, inspect rate/spend limits and `Retry-After` where present. The [official error reference](https://platform.claude.com/docs/en/api/errors) includes other billing and spend-limit statuses, so do not teach “all account problems are rate limits.”

<!-- SOLUTION_CODE -->

## Minutes 51–60: assessment answers and reasoning

### Knowledge check 1

Outer `status: passed` means the example's graph and validation assertions completed. `environment.ready: false` means a local prerequisite failed. Inspect `python_supported`, `virtual_environment`, `missing_packages`, and installed versions; verify the chosen interpreter and ask for the pinned environment to be restored if necessary. Calling Anthropic cannot repair the wrong interpreter. Award credit only if the learner separates behavioral success from prerequisite readiness.

### Knowledge check 2

`https://smith.langchain.com` is the dashboard origin, not one of the supported LangSmith API origins. The query-bearing LangWatch URL can carry data and is not a bare origin. HTTPS alone does not establish the correct destination or safe configuration. The [LangSmith cloud reference](https://docs.langchain.com/langsmith/cloud) lists the regional API hosts; use the organization's actual region. Do not accept suffix matching or a copied dashboard URL.

### Knowledge check 3

For a LangWatch-selected plan with personal key kind and blank project ID, report `langwatch_project_required`. After repair, `remote_checked: false` still prevents claims of valid credentials, existing model access, network success, trace ingestion or dashboard visibility. Correct syntax and declared scope are necessary but insufficient evidence.

## Marking and recovery

Use ten marks: three for endpoint validation and canonicalization, three for the profile's exact ready/repair outputs and issue precedence, two for the required failure mappings, and two for safety plus clear evidence interpretation. Require all safety conditions before sign-off: no file/environment loading, network calls, secret echoing, or actual tracing. The learner's starter self-checks assess their edited functions. The supplied pytest file principally validates the demonstration and reference solution, plus starter scaffolding; it is not automatic proof that every learner implementation is correct. Inspect learner edge cases separately.

If imports fail, confirm the project root and interpreter before changing code. If issue order differs, compare each validation step against the workbook. If queries or credential-bearing URLs pass, return to the exact-origin policy rather than widening the allowlist. If the starter still reports incomplete, identify the remaining `NotImplementedError`; if it raises an assertion, repair that behavior instead of replacing the success message.

Distinguish a later checker's missing-key `configuration_error` from server-side 401 authentication rejection. Verify required fields privately without displaying configuration.

Real connection checks are a later instructor-authorized activity through `course_support.check_connections`, one service at a time. That CLI reads private configuration and makes actual requests. Its LangSmith path includes synthetic write/readback; LangWatch checks server acknowledgment. Neither substitutes for separate visual dashboard inspection. Keep this distinction intact in screenshots, student evidence and publication notes.
