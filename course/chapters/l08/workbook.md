# L08 — Conversation history and logging

## Your task: bounded prompt, complete transcript

Build a text-chat graph that sends a bounded recent window to the model while retaining a complete process-local transcript. This is **added practice** based on the source's [01:42:54–02:03:20 history/logging demonstration][812], not a missing original homework assignment. The source code section begins at 01:43:58. Use Anthropic through the shared runtime, not an OpenAI client or a canned live response.

Work in `exercises/starters/l08.py`. The independent instructor reference is `exercises/solutions/l08.py`; consult it only after attempting the task. Do not import either that reference or `course_lessons/l08.py` to replace your implementation. The delivered demonstration and reference have different state-update strategies, even though both carry history between calls.

Before editing, run:

```bash
python -m exercises.starters.l08
```

Expect `STARTER_NOT_COMPLETED` and a successful process exit, with no model construction. This indicates an unfinished scaffold, not a passed exercise. Implement only the three TODO functions; the provided runner contains the acceptance scenario and safe file-writing behavior.

## Implement the three functions

1. **Select model input.** `select_prompt(history, max_pairs=1)` must accept alternating human/AI pairs followed by one pending human. Return a new list with the newest `max_pairs` complete pairs plus that human, without mutating the input. Zero keeps just the pending human. Raise `ValueError` for negative, Boolean, or noninteger limits; empty/even/nonalternating histories; and AI tool calls. This intentionally excludes system/tool conversations.
2. **Build the graph.** `build_graph(model, max_pairs=1)` must validate the limit at construction, compile `START → respond → END` with `MessagesState`, and invoke the injected model only inside the node. Forward the node's config. Return only the new `AIMessage` as a delta. Reject a wrong response role or tool call with `TypeError`, and empty visible text with `ValueError`. Do not use checkpoints or mutate state. Compilation with `model=None` must work for the starter readiness check.[809]
3. **Export full history.** `format_transcript(history)` must format every message as `<role>:\n<text>\n`, using `Human` or `AI`, and join entries with one extra newline. Return an empty string for an empty list; raise `TypeError` for other roles. Use `message_text` without correcting spelling or stripping stored content. Do not open files inside this function.

## Follow the fixed scenario

The provided runner introduces `Hi, my name is Mira. Please acknowledge briefly.` Its second human input is exactly:

```text
gud morning!
What name did I give you?
```

The third is `Reply with one short greeting.` Keep `max_pairs=1`. The runner should send 1, 3, then 3 messages, while retaining 2, 4, then 6. Its separate fourth call starts with no prior history, yielding two messages. Do not include that fresh conversation in the six-message log.

The second answer must mention Mira. Wording otherwise varies. The third prompt must exclude the first human message by ID, but you must not claim this guarantees forgetting: a retained AI answer can repeat Mira. A pair cap is not a token cap, nor a bound on full-history memory or log size.[810] Anthropic content can be block-structured, so use the shared text helper for display/export.[811]

## Test and record observations

For a small offline check, start `python` and paste this probe after implementing the TODOs. `WorkbookChatDouble` is explicitly a test double, not Anthropic evidence:

```python
from langchain_core.messages import HumanMessage, AIMessage
from langsmith import tracing_context
from exercises.starters import l08

class WorkbookChatDouble:
    def __init__(self):
        self.calls = []
    def invoke(self, messages, config=None):
        self.calls.append(list(messages))
        return AIMessage(content="offline reply")

model = WorkbookChatDouble()
graph = l08.build_graph(model, max_pairs=1)
history = []
with tracing_context(enabled=False):
    for text in ["first", "gud morning!\nraw", "third"]:
        history = l08.run_turn(graph, history, text)
assert [len(call) for call in model.calls] == [1, 3, 3]
assert len(history) == 6
assert "Human:\ngud morning!\nraw\n" in l08.format_transcript(history)
```

Exit the interpreter. Run the focused delivered-code tests:

```bash
python -m pytest tests/lessons/test_l08.py -q
```

Those checks validate the delivered demo/reference and starter status; they do not automatically grade your edited TODOs. When authorized for paid calls, validate your implementation:

```bash
python -m exercises.starters.l08 --live --backend none
```

For comparison, the instructor reference command is:

```bash
python -m exercises.solutions.l08 --live --backend none
```

Record actual observations, not invented replies: prompt counts **[observed]**; full-state counts **[observed]**; second answer **[observed]**; exact two-line input preserved **[yes/no and location]**; reported `log_path` **[observed]**; fresh-history count **[observed]**. Open `bounded-conversation.txt` at that path and verify three human and three AI entries. Default output directories are unique; a reused directory must not silently overwrite an existing log.

## Three progressive hints

### Hint 1: count the pending turn separately

An input window has `2 * max_pairs + 1` entries at most. Before selecting, validate the full input's shape. Python's `bool` is an `int` subclass, so an integer check alone accepts `True` accidentally.

### Hint 2: separate invocation input from node update

Without checkpoints, every invocation needs the caller's carried history. Within that invocation, `MessagesState` already preserves it through its reducer. Return only the new reply from the node; do not rebuild old messages with new IDs.

### Hint 3: choose the correct source for the log

The prompt window and full returned history are different lists. Export the full list and preserve the raw human string. Validation can inspect stripped text without storing the stripped version.

## Completion and stretch

Complete the task only when the implemented starter demonstrates the required counts, full six-message export, exact raw input, role labels, two-message reset simulation, and honest error behavior. Explain why no saved transcript is automatically reloaded. U1 is the separate durable-checkpoint lab; do not add persistence here.

For a stretch task, compare `max_pairs=0` and `2` using the offline double. Predict the three prompt counts before running, then discuss how a token-aware policy would also preserve valid message structure. Do not invoke a remote token-counting API as an “offline” check or claim trimming erases information from retained replies.

## References

[809]: https://docs.langchain.com/oss/python/langgraph/graph-api "LangGraph Graph API: MessagesState and reducer updates"
[810]: https://docs.langchain.com/oss/python/langgraph/add-memory "LangGraph memory: trimming model input versus retained state"
[811]: https://docs.langchain.com/oss/python/integrations/chat/anthropic "ChatAnthropic: messages, content blocks, and token counting"
[812]: https://youtu.be/jGg_1h0qzaM?t=6174 "Source video: conversation history at 01:42:54"
