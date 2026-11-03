# P00 — Setup and safe service checks

## What this preparation establishes

**SUPPLEMENTARY PRACTICE — 60 minutes.** P00 is preparation for the approved course. Continue afterward with L01.

By the end, you should identify the Python environment running your code, execute a non-LLM graph, reject unsupported service URLs, and propose safe recovery steps without exposing credentials. An LLM is a large language model accessed through a local model or remote provider. P00 needs neither. Its code never reads `.env` and never checks a real account.

Three kinds of evidence must remain separate. A local graph run proves that Python and LangGraph can execute this example. Public configuration validation proves only that proposed strings meet the teaching policy. A real service check can establish a response or trace acknowledgment, but that is a separate, authorized operation. A green local result cannot prove authentication or dashboard visibility.

## Prepare the interpreter, not just the editor

A virtual environment holds a project's interpreter and packages separately from other projects. Activating it changes which executable the shell finds as `python`; it does not install the course. Python documents a more reliable check: `sys.prefix != sys.base_prefix` indicates a virtual environment, even when activation was skipped [1].

Work from the supplied project root. `course_lessons` holds demonstrations; `exercises/starters` contains your editable tasks; `exercises/solutions` contains teacher references; `tests/lessons` contains checks. Module execution with `python -m ...` preserves these package imports. Do not run a nested file by its filesystem path.

If the instructor has already prepared `.venv`, reuse it. On macOS, activate it with `source .venv/bin/activate`. On Windows PowerShell use `.\.venv\Scripts\Activate.ps1`; if activation is restricted, use `.\.venv\Scripts\python.exe` explicitly instead of changing a managed machine's security policy. The equivalent macOS executable is `.venv/bin/python`. Windows commands here are documentation-based, not Windows-tested [1].

For a genuinely new environment, these are **setup instructions, not offline exercise commands**. Creation needs an existing Python 3.12 installation; installing dependencies may require network access or an instructor-provided package cache.

```bash
# macOS, only when an environment does not already exist
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.lock.txt
```

```powershell
# Windows PowerShell, only when an environment does not already exist
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
```

Use the course's pinned lock file, not an unreviewed upgrade command copied from a website. Then inspect the selected interpreter without inspecting secrets:

```bash
python -c "import sys; print(sys.version.split()[0]); print(sys.prefix != sys.base_prefix)"
python -m pip check
```

The first command should show Python 3.12.x and `True`. `pip check` checks installed dependency consistency, not credentials or network connectivity. A missing distribution is an environment problem; an invalid key is a different problem. The demonstration inventories versions through local package metadata and reports missing packages without installing anything.

## Follow a graph with no model

A graph organizes work into nodes connected by edges. Here each node is an ordinary Python function. State is a dictionary passed through that work. `TypedDict` documents expected keys for readers and type checkers; it does not automatically validate every runtime value. P00 explicitly checks that a synthetic learner label is not blank.

The builder registers `check_label` and `finish_setup`. Explicit edges connect START to the first node, then the second node, then END. START and END mark boundaries; they do not call services. `compile()` produces the executable graph; `invoke()` runs it. Nodes return partial updates rather than mutate the supplied input dictionary. This usage follows the current Graph API and does not require an agent or chat-model wrapper [2].

**Concept diagram:** the connected local demonstration and workbook paths are separate from the disconnected, instructor-authorized real-service path.

<!-- ORIGINAL_DIAGRAM -->

## Guided practice: prove the local boundary

1. Run `python -m course_lessons.p00 --backend none`. No `.env` file, model name, API key, or internet connection is needed once packages are installed. The shared CLI may create an empty run directory under `.work/student-runs/p00`; P00 itself writes no report file.
2. Inspect `result.environment`. `python_supported`, `virtual_environment`, and `missing_packages` explain local readiness. An outer `status: passed` means the demonstration's behavioral assertions completed; inspect the inner `ready` flag separately.
3. Find `graph_checks`. They must be `label_checked` followed by `graph_completed`; the normalized label is `learner`. Predict why a blank label raises a clear error rather than producing a success sentence.
4. Find `supported_endpoints` and `unsafe_examples_rejected`. Three deliberately unsuitable examples are rejected locally. Neither acceptance nor rejection sends a request.
5. Confirm `remote_checked` and `environment_file_read` are both false. Do not add `--live` or a tracing backend: P00 rejects them before the shared CLI could initialize a service.
6. Run `python -m pytest tests/lessons/test_p00.py -q`. These focused tests deliberately block configuration loading, environment-file reads, DNS resolution, and socket connections. They test actual Python and graph behavior, not a simulated model presented as a real call.

The exact tested demonstration source is inserted here:

<!-- EXAMPLE_CODE -->

<!-- EXECUTION_FIGURES -->

## Validate an origin, not an attractive-looking URL

An origin identifies a scheme, host and optional port. P00 allows HTTPS with no port or literal `:443`, then returns a canonical origin without a port or trailing slash. Blank values use the service default. Surrounding whitespace is stripped. Embedded whitespace/control characters, credentials, backslashes, query or fragment delimiters, and non-root paths are rejected. Errors use fixed text rather than echoing a possibly sensitive URL.

For LangSmith, supported API hosts are `api.smith.langchain.com`, `eu.api.smith.langchain.com`, `apac.api.smith.langchain.com`, and `aws.api.smith.langchain.com`. Choose the region that actually hosts the organization; the teaching default is not a region recommendation. `smith.langchain.com` is a dashboard host, not the API origin [3].

LangWatch's cloud origin is `https://app.langwatch.ai` [4]. The course excludes arbitrary proxies and self-hosted URLs even though the product supports configurable endpoints. An allowlist is a course safety policy, not a statement that every other deployment is invalid. A suffix such as `.attacker.invalid` must not count as the official host. An API resource path such as `/v1/messages` belongs to a client operation, not this origin field.

## Independent task: public-profile readiness checker

Complete the three TODO functions in `exercises/starters/p00.py`, following the exact workbook specification: `validate_endpoint`, `check_profile`, and `classify_failure`. The graph wrapper is provided. It accepts only a sanitized report, never the original profile.

The supplied READY_PROFILE uses the synthetic model ID `claude-course-example`; matching its syntax does not mean that model exists. Its proposed backend `both` is data describing a future plan, not an instruction to turn on tracing. REPAIR_PROFILE has exactly three faults: a blank model, a LangSmith dashboard URL, and a blank LangWatch project ID for a service key. Expect `model_invalid`, `langsmith_endpoint_invalid`, and `langwatch_project_required`, in that order.

Project-bound LangWatch keys can already carry project scope. Settings-created personal/service keys require a project ID [4]. The exercise represents this difference using a public `langwatch_key_kind` field; it does not inspect or guess an actual key's kind. Never paste a key into the profile. Unknown fields are rejected without echoing names or values. Once complete, `python -m exercises.starters.p00` prints a local-only completion message. Until then it exits successfully with `STARTER_NOT_COMPLETED`, not a fake pass.

## Real connection checks: separate and explicitly authorized

Later AI lessons use private local configuration: `ANTHROPIC_API_KEY` and an instructor-approved `ANTHROPIC_MODEL`. Tracing adds backend keys, region and project/workspace scope. `.env.example` contains blank secret placeholders and safe public defaults, including a configurable tested model ID; a private `.env` must remain excluded from publication and version control. Do not display either actual credentials or a full configuration dump. P00 does not create or open these files.

Only after instructor approval, use the separate shared CLI, one service at a time:

```bash
python -m course_support.check_connections --service anthropic
python -m course_support.check_connections --service langsmith
python -m course_support.check_connections --service langwatch
```

**These are real requests and are not P00 exercise steps.** The CLI reads the private local `.env`. Anthropic sends a small paid model request; LangSmith writes synthetic data and reads it back; LangWatch submits synthetic telemetry and checks acknowledgment. Reports go to `.work/validation`. A report does not establish visual dashboard inspection. Do not run `--service all` merely to diagnose a missing Python package.

## Troubleshoot from the least invasive evidence

For `ModuleNotFoundError`, confirm the root directory and selected interpreter, then ask the instructor to restore the pinned environment. For a URL error, remove paths/query data and choose the correct official origin; do not broaden the allowlist to make a test pass.

For a later approved check, `configuration_error` can mean a required key is missing or a model identifier has invalid syntax. Verify required fields privately; never display the file. A 401 is different: the service rejected authentication, rather than the local checker finding a missing setting.

For a later real check, keep only a sanitized status, service, and request ID. Anthropic documents 401 for authentication, 403 for permissions, 404 for a missing resource, 429 for rate/cap limits, and 529 for overload [5]. Privately verify or rotate a key for 401; check workspace/model access for 403; verify model/resource identifiers for 404. A 429 requires inspecting rate and spend limits, honoring `Retry-After` when present—not an infinite retry loop. Use a bounded retry budget for overload. Network/TLS failures require checking connectivity and approved proxy settings, never disabling certificate verification. Other errors need the official reference; for example, not every billing or spend-limit issue is a 429 [5].

## Knowledge checks

1. The demonstration prints outer `status: passed`, but `environment.ready` is false. What has passed, and what should you inspect next?
2. Why reject both `https://smith.langchain.com` and `https://app.langwatch.ai?token=sample`, although both use HTTPS?
3. A proposed LangWatch configuration uses a personal key and a blank project ID. Which issue should the checker report? After repair, what does `remote_checked: false` still prevent you from claiming?

## References and current-API differences

P00's environment audit, safety policy and independent task provide preparation. Current official documentation was checked on 3 November 2026. The course uses explicit graph boundaries and partial updates; later model lessons use Anthropic. No model-price or account-access promises are made here.

[1]: https://docs.python.org/3.12/library/venv.html "Python 3.12 virtual environments"
[2]: https://docs.langchain.com/oss/python/langgraph/overview "LangGraph overview and deterministic graph example"
[3]: https://docs.langchain.com/langsmith/cloud "LangSmith cloud regional API endpoints"
[4]: https://langwatch.ai/docs/integration/python/guide "LangWatch Python configuration and project scope"
[5]: https://platform.claude.com/docs/en/api/errors "Claude API errors and request identifiers"
