# U1 — Thread memory and durable SQLite checkpoints

## Your task: recover three travel notebooks

**SUPPLEMENTARY PRACTICE.** This exercise extends the conversation-history concepts from L08 with durable SQLite checkpoints. Allow about 18 minutes for the first implementation, then use review time to investigate failed assertions.

Build a small travel notebook that stores three logically isolated conversations in one local SQLite file. The important outcome is not a polished answer: it is recovery after a real connection close, with evidence that each thread receives only its own human inputs. Use synthetic destinations only. A checkpoint database contains conversation data and needs protection even when tracing is off.

Your starter is `exercises/starters/u1.py`. Your teacher's independent reference is `exercises/solutions/u1.py`; do not import it or the demonstration into your work. The three TODOs are deliberately separated so you can test graph construction, invocation, and persistence orchestration independently.

## Commands and baseline observations

From the repository root, with the prepared environment active:

```bash
python -m exercises.starters.u1
python -m pytest -q tests/lessons/test_u1.py
python -m course_lessons.u1 --live --backend none
```

The unmodified starter must exit successfully with `STARTER_NOT_COMPLETED`. That message is not a passing assessment. After implementing its TODOs, rerun the same starter command: it exercises your functions with the explicitly named `StarterDestinationDouble` in a temporary SQLite file and labels its output `OFFLINE_SELF_CHECK_ONLY`. The temporary file is removed afterward; use the live reference for a retained comparison artifact. The focused tests exercise the delivered demonstration and reference solution, not your edited starter. The live reference command, for comparison after attempting the task, is:

```bash
python -m exercises.solutions.u1 --live
```

This reference makes five real Anthropic calls. The project-code demonstration makes four. Neither command should be described as offline. If the optional SQLite dependency is skipped, arrange environment setup before claiming persistence completion.

## Implement the three functions

1. Complete `build_notebook(model, checkpointer)`. Use `MessagesState`, one response node, and explicit `START`/`END` edges. Pass `NOTEBOOK_RULE` followed by the restored messages to the injected model, forwarding `config`. Require an `AIMessage` response. Return only that new message and compile with the supplied checkpointer.
2. Complete `ask(graph, thread_id, text)`. Reject non-string or whitespace-only IDs and text with `ValueError`, before graph invocation. For valid text, preserve its exact characters. Submit one new `HumanMessage` with `config=execution_config(thread_id)`; do not resubmit the existing history.
3. Complete `run_lab(model, database)`. Require a new database path, raising `FileExistsError` for an existing file. Create its parent directory. Import `SqliteSaver` from `langgraph.checkpoint.sqlite`, then use its `from_conn_string` context manager for both connection lifetimes.[1221]

In the first context, send `My destination is Kyoto. Remember it.` to `trip-a` and `My destination is Oslo. Remember it.` to `trip-b`. After each turn, require two messages and a completed snapshot. Save the snapshot's checkpoint ID. Exit the context completely.

In the second context, reopen the **same file** and build a **new graph**. Before recall, require each thread to have its original two messages, no pending work, and its original checkpoint ID. Ask `What is my destination?` in `trip-a`, `trip-b`, and new `trip-c`. Do not seed the third thread with a city.

Require the first two answers to include their own city and exclude the other city. Require the third to include `UNKNOWN` and neither city. Generated wording may vary: compare case-insensitive city inclusion, not an entire model sentence. Verify `trip-a`'s human texts are exactly its Kyoto introduction and question; `trip-b`'s are exactly its Oslo introduction and question; `trip-c` has only the question. Final total-message counts must be `{"trip-a": 4, "trip-b": 4, "trip-c": 2}`.

Return a JSON-serializable dictionary with `database`, `closed_and_reopened`, `recovered_checkpoint_ids_match`, `thread_isolation`, `message_counts`, `answers`, and `model_calls` equal to 5. Set success flags only after assertions pass. Keep model construction out of these functions so offline tests can inject a double.

## Three progressive hints

### Hint 1: separate responsibilities

The reducer merges messages, the saver stores state, and configuration selects the thread. A global conversation list would defeat this separation. Look at the type of the node's output: it is an update dictionary, not a replacement graph or a text answer alone.

### Hint 2: prove restoration before another call

Use `graph.get_state(execution_config(thread_id))` inside the reopened context. Its `values`, `next`, and `config` let you inspect the state without another model request. Check the saved checkpoint ID before sending a new question, because a completed new call creates newer checkpoints.[1222]

### Hint 3: isolate inputs as well as answers

Select human messages by `isinstance(item, HumanMessage)` and compare their text to the exact expected list. Count both human and AI messages. If an unrelated city appears, investigate reused IDs, shared lists, or manually supplied history before blaming SQLite.

## Record evidence and check completion

Record your database path and the two recovered checkpoint-ID comparisons. Note the final counts for `trip-a`, `trip-b`, and `trip-c`, and describe the exact human inputs seen in each thread. Record whether your evidence used offline doubles or real Anthropic, including the command used; do not treat one as proof of the other.

Completion requires all three functions, an actual closed/reopened file, matching pre-recall snapshot IDs, counts 4/4/2, no crossed facts, third-thread unknown behavior, rejection of blank inputs and pre-existing databases, and a truthful returned summary. Explain why an isolated thread is not a security boundary. Preserve a failed database for diagnosis instead of hiding an API failure behind a manufactured response.

## Stretch task

Add a fresh-interpreter checkpoint read between the contexts without invoking a model. Pass only the database path and thread ID to the worker, and compare the saved human inputs. Explain why this strengthens restart evidence but still does not test power-loss recovery, backup restoration, or authorization. Do not weaken the core acceptance conditions to finish the extension.

## References

[1221]: https://reference.langchain.com/python/langgraph.checkpoint.sqlite/SqliteSaver/from_conn_string "File-backed SqliteSaver context-manager usage"
[1222]: https://docs.langchain.com/oss/python/langgraph/checkpointers "Inspecting checkpoints and StateSnapshot fields"
