# L07 — Anthropic stateless bot

## Assignment: a stateless help-desk session

Build a bounded session controller around a single-node model graph. This is **added practice**, not original video homework. The source's [01:31:01–01:42:54 section](https://youtu.be/jGg_1h0qzaM?t=5461) demonstrates a bot and a failed name-recall test but assigns no exercise. Your goal is to prove which messages are sent, not to obtain a particular Claude sentence. Allow approximately 20 minutes after the guided practice.

Work in `exercises/starters/l07.py`. The baseline demonstration is `course_lessons/l07.py`; the teacher reference is `exercises/solutions/l07.py`. Do not import either implementation into your starter. You may use shared runtime helpers. Use synthetic data only; credentials do not belong in state, worksheets, or screenshots.

Start from the repository root in the prepared environment:

```bash
python -m exercises.starters.l07
python -m pytest tests/lessons/test_l07.py -q
```

The starter initially reports `STARTER_NOT_COMPLETED`. Its exit code is not a passing grade. The focused test file checks the delivered demo and reference solution with explicit offline doubles; it does not automatically assess your modified starter. Use the learner-side harness below for that.

## Required functions and behavior

1. Implement `classify_entry(raw)`. Reject non-string entries with `TypeError`. Return `exit` when `raw.strip().casefold()` is `exit`, `skip` for whitespace-only text, and `send` otherwise. Normalize only for these decisions; preserve original submitted text.
2. Implement `build_bot(model)`. Create `START → respond → END`, without history, tools, or a checkpointer. Its input is `{'prompt': raw}`. Reject blank/exit prompts even if someone bypasses the session controller. Construct exactly one new `HumanMessage`; invoke the injected model with the node's `config`. Require an `AIMessage` with nonempty displayable text. Return `reply`, `sent_messages` containing just the original prompt, and `usage` from `usage_metadata`, using `{}` if absent. Use `message_text`, not a dump of all content blocks.
3. Implement `run_session(graph, entries, *, max_entries=6)`. Return a dictionary containing `turns`, `skipped`, `inspected`, and `stop_reason`. Reject noninteger or nonpositive budgets with `ValueError`, including booleans. Inspect at most that many raw entries; blank and exit entries consume budget. Count each inspected entry, skip blanks, and stop before invoking on exit. Invoke with fresh state and `execution_config()` for each sent prompt. Store results only for the report, never as later input. Stop reasons are `exit`, `limit` when budget is reached, and `exhausted` when the source ends earlier. Reaching the budget takes precedence over detecting coincident source exhaustion.

Use exactly this assessment sequence:

```python
entries = [
    "  ",
    "My name is Mira. Say hello briefly.",
    "What is my name?",
    " ExIt ",
    "This must never be sent.",
]
```

## Check your starter without a paid request

After completing the TODOs, paste the following into a Python shell from the repository root. This is an explicit offline double, not Claude and not evidence of live integration. It supplies test responses only; it does not contain your solution's graph or controller logic.

```python
from langchain_core.messages import AIMessage, HumanMessage
from exercises.starters import l07 as learner

class OfflineWorkbookModel:
    def __init__(self):
        self.requests = []

    def invoke(self, messages, config=None):
        assert len(messages) == 1
        assert isinstance(messages[0], HumanMessage)
        assert config["recursion_limit"] == 40
        self.requests.append([m.content for m in messages])
        return AIMessage(content="OFFLINE TEST response")

entries = ["  ", "My name is Mira. Say hello briefly.",
           "What is my name?", " ExIt ", "This must never be sent."]
model = OfflineWorkbookModel()
graph = learner.build_bot(model)
report = learner.run_session(graph, entries)
assert model.requests == [[entries[1]], [entries[2]]]
assert report["inspected"] == 4 and report["skipped"] == 1
assert report["stop_reason"] == "exit" and len(report["turns"]) == 2
assert all(t["reply"].strip() and t["usage"] == {} for t in report["turns"])
assert [t["sent_messages"] for t in report["turns"]] == model.requests
```

Also test `[]` for `exhausted`, two blanks with `max_entries=2` for `limit`, and `"  Hello  "` for preservation of spaces. Check that a zero budget raises `ValueError`. Explain why reusing the same `graph` in these tests does not introduce context into its requests.

## Three progressive hints

### Hint 1: separate decisions from payloads

Use a normalized temporary value to recognize exit. Keep `raw` unchanged for `HumanMessage(content=raw)`. Do not make a model call to decide whether an entry is blank.

### Hint 2: separate configuration from state

Accept `config: RunnableConfig` in the nested node and pass it to `model.invoke`. The session invokes the graph with `execution_config()`. A key, model object, or callback is not a state field.

### Hint 3: bound consumption, not just successful turns

`islice(entries, max_entries)` can cap inspected entries without consuming an extra iterator item. Increment `inspected` before handling skip/exit. A loop `else` can distinguish normal exhaustion/budget completion from an exit `break`.

## Record observed results

Record the actual request lists, inspected count, skipped count, turn count, and stop reason from your harness in a short paragraph. Then record your empty-source and budget-limit observations. State explicitly that these are offline-double results. Add one sentence predicting the second live request's context without predicting its exact answer.

For an authorized real comparison, the delivered implementations are runnable with:

```bash
python -m course_lessons.l07 --live --backend none
python -m exercises.solutions.l07 --live
```

Both make two logical model calls using synthetic prompts. Their output validates those delivered implementations, not your starter. Record whether you actually ran them, any real error, and available usage metadata; do not invent a passed live result. See [ChatAnthropic](https://docs.langchain.com/oss/python/integrations/chat/anthropic) for message/usage representation and [Anthropic's stateless contract](https://platform.claude.com/docs/en/build-with-claude/working-with-messages).

## Completion criteria and stretch

Completion requires all three functions implemented independently; exact two one-message payloads for the assessment sequence; one skip, four inspected entries, two turns, and exit; no processing after exit; correct blank/limit/exhausted handling; preserved raw text; callback forwarding; nonempty textual replies; and no history or credentials in state. Demonstrate these with recorded evidence rather than changing the starter's status string.

For a stretch task, add learner-owned offline tests for a non-string entry, an empty `AIMessage`, a simulated provider exception, and a source iterator whose unread tail remains untouched after the cap. Keep all failures honest: no canned answer fallback in production. Do not add memory; that deliberately changes the problem and belongs to L08/U1.
