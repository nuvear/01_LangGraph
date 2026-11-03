# C01 — Document-grounded drafting capstone

## Independent task: approve the current draft, not an earlier version

**SUPPLEMENTARY · 180-minute capstone session.** This added exercise combines drafting and retrieval ideas with explicit approval and bounded execution. Complete L01–L11, U1–U2 and S1–S2 before starting.

Your client wants a short teammate briefing based only on the supplied L11 synthetic teaching document, `data/rag_teaching_handbook.pdf`. A reviewer may ask for one revision, reject the draft or approve its current contents. Saving must require explicit approval of the current draft. The finished file must include a reproducible inventory of the evidence the assistant retrieved. Do not add another knowledge base, paid provider, global draft buffer or unbounded tool loop.

Use `exercises/starters/c01.py`. The independent instructor reference is `exercises/solutions/c01.py`; compare it only after your attempt. The baseline demonstration is `course_lessons/c01.py`. Keep the provided scaffold and implement its three TODO functions instead of importing another implementation.

## Establish the baseline

From the repository root with the prepared Python environment active:

```bash
python -m exercises.starters.c01
python -m pytest tests/lessons/test_c01.py -q
```

Before implementation, the starter must report `STARTER_NOT_COMPLETED` and exit successfully without paid calls or model downloads. The test suite checks the complete baseline and reference using named offline doubles; the dedicated learner-acceptance test skips while TODOs remain. This is not a completed capstone or proof of live services.

## Implement the three functions

1. **`assess_citations(draft, hits)`.** Return false for blank text, any case-insensitive occurrence of `INSUFFICIENT_EVIDENCE`, or no citation markers. Collect markers matching `r"\[[^\[\]\n]+ p\.\d+\]"`. Every collected marker must be exactly `citation(hit)` for one of the retrieved records. At least one is required. Preserve the helper's source and one-based page. This function checks reference integrity, not semantic truth.

2. **`decide_review(payload, draft, revisions)`.** Always return the keys `approved`, `feedback` and `status`. The default is `False`, an empty string and `invalid_review`. Non-dictionaries remain invalid. An `approve` action requires `payload['fingerprint'] == fingerprint(draft)`; only then return `approved=True` with status `approved`. A `reject` action returns `rejected`, without approval. A `revise` action allows stripped string feedback of 1–500 characters when `revisions < 1`, returning `revision_requested` and that feedback. If a revision already occurred, return `revision_limit`. All malformed decisions must fail closed.

3. **`render_artifact(draft, hits)`.** Start with `draft.strip()`, then a blank line and the literal heading `Evidence inventory`. Deduplicate tuples `(source, page, id)` from every retrieved chunk, sort those tuples and format each line as `- [SOURCE p.PAGE] (chunk ID)`. End with a newline. Include retrieved chunks even when the model did not cite them; distinguish available evidence from evidence actually used. Do not change save behavior to overwrite an existing file.

The scaffold already performs actual L11 retrieval, checks tool IDs and metadata, isolates state with checkpoint thread IDs, interrupts for clarification/review, resets approval after revision and limits successful threads to three model calls. Leave these controls intact.

## Three progressive hints

**Hint 1:** Turn both citation collections into Python sets. Check that the found set is nonempty before using `issubset`. Otherwise an uncited draft could pass because the empty set is a subset of every set.

**Hint 2:** Construct the default review dictionary first. Return a new update only when one of the allowed decisions is validated. Do not use truthiness such as `bool(payload)` as approval, and do not reuse the pre-revision fingerprint.

**Hint 3:** Build an inventory set of tuples before sorting. Sorting strings containing page numbers can order page 10 before page 2; keep the page as an integer in the sorting tuple. Formatting belongs after sorting.

## Check your completed starter

```bash
python -m exercises.starters.c01
python -m pytest tests/lessons/test_c01.py -q -k implemented_starter_acceptance
python -m pytest tests/lessons/test_c01.py -q
```

The targeted acceptance test must **pass, not skip**. It checks your three functions, the approved save, the revision limit and stale approval using explicit offline dependencies. After completing the functions and receiving live-call authorization, run your actual starter and the separate instructor reference:

```bash
python -m exercises.starters.c01 --live
python -m exercises.solutions.c01 --live
```

Each needs L11's actual helper, local embeddings and Anthropic access. Use a fresh output directory for each run. Neither command should silently replace a failed live call with scripted output. The teaching driver supplies explicit review decisions; inspect the draft yourself rather than treating the script as an authenticated human interface.

## Record observed results

Record your targeted-test outcome and whether it passed or skipped: __________. Record the actual fixture source/page you inspected and a supported claim: __________. Record the real saved artifact path and verify its fingerprint-approved draft plus inventory: __________. Record the status returned for stale approval, a second revision and an unsafe filename: __________.

Run the same synthetic scenario with each configured tracing backend separately. Record the backend, server-side trace identifier and where the retrieval/tool result appears: __________. If unavailable, write the concrete blocker rather than inventing an identifier. Never record credentials.

## Completion criteria and stretch task

Completion requires a passing learner-acceptance test; real retrieval and an Anthropic tool round trip; inspectable valid citations; no saved file before approval; stale-approval rejection; one bounded revision; two-thread isolation; a correctly formatted new file inside the allowed directory; and documented failure behavior. Submit the actual artifact and test/live evidence, not an exact expected model sentence. Explain why an in-memory checkpoint does not survive restart and why citation formatting alone cannot establish grounding.

For a stretch task, design an authenticated review interface that displays the current fingerprint and requires a named reviewer to confirm it. Sketch how a durable checkpoint backend and crash-recovery policy would prevent confusing a pre-existing artifact with a newly completed save. Do not implement unattended approval or introduce private documents. Use the [official interrupt semantics](https://docs.langchain.com/oss/python/langgraph/interrupts) and [Anthropic client-tool protocol](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview) when explaining the design.
