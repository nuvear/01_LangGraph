# U1 — Thread memory and durable SQLite checkpoints

## Explain: what changes after L08?

**SUPPLEMENTARY / CURRENT-API UPDATE.** This 60-minute lab follows L08. It has no source-video start or end time. For context, the source's conversation-history section is 01:42:54–02:03:20, beginning at [the L08 video boundary](https://youtu.be/jGg_1h0qzaM?t=6174). The whole-track review confirms its recap continues briefly beyond that editorial boundary. The presenter demonstrates accumulated messages and text logging; this added lab teaches a different persistence mechanism, not an unshown original assignment.

After this lesson you should be able to continue a conversation under a stable thread ID, inspect its saved state, reopen its SQLite file, and show that another thread does not inherit its messages. You need basic Python functions, `with` blocks, and L08's human/AI-message distinction. The course environment also needs `langgraph-checkpoint-sqlite`, a separately distributed backend. Do not change shared dependencies during class without the instructor's setup instructions.

A Python list provides memory only while that list exists. A text transcript can outlive the process, but the program must parse and reload it before it becomes usable graph state. A **checkpointer** performs a different job: it serializes graph state at execution boundaries and retrieves that state for later runs. LangGraph calls this thread-scoped, short-term memory even when its storage is durable. “Short-term” describes its conversational scope, not a promise that the bytes disappear when Python exits. Cross-thread application memory uses a separate store concept.[1201]

## Illustrate: state, reducer, thread, and file

`MessagesState` is a ready-made state schema with a `messages` field using the `add_messages` reducer. A **reducer** decides how a new field update combines with an existing value. `add_messages` adds new messages and can replace a message with the same ID. It does not mean “concatenate arbitrary lists forever.” Our normal turn has one new human message on input and one new AI message in the node's output. We do not manually append the old history again.[1206]

The thread ID selects one sequence of saved checkpoints. It belongs inside invocation configuration, not inside the conversation text. `execution_config("project-a")` preserves the course's selected callbacks and recursion bound while setting `configurable.thread_id`. Reusing that ID and the same database lets the graph load earlier state. Changing the ID selects another conversation. A checkpoint ID identifies one particular snapshot inside that thread; it is not a substitute for the conversational thread ID.[1202]

The SQLite database is the durable container. Both `project-a` and `project-b` live in the same file, but their checkpoint keys differ. This is logical isolation, not authentication: anyone permitted to read the file may inspect its data. A real multi-user service must authorize access to IDs and protect storage independently.

The original diagram below separates the connection lifetime from the conversation lifetime. Its fresh-interpreter read has no model and receives no Python conversation list from the first run.

<!-- ORIGINAL_DIAGRAM -->

## Demonstrate: four calls and two recovery checks

Activate the prepared environment and work at the repository root. Run:

```bash
python -m course_lessons.u1 --live --backend none
```

`--live` explicitly permits four real Anthropic calls through the shared runtime. Without it, this model-dependent demonstration rejects execution rather than inventing answers. The default output directory is a unique child of `.work/student-runs/u1`; `--output-dir` can select another directory. Each run creates a new UUID-named database so repeating the command does not silently reuse yesterday's conversation.

Read the tested source at this point, particularly the indentation of both `with` blocks:

<!-- EXAMPLE_CODE -->

The first invocation teaches `project-a` the synthetic project code `ORCHID-42`. A second asks for that code under the same ID. Two completed turns mean four stored messages, alternating human and AI. The third call asks the same question under `project-b`, which has never received the introduction. That thread should contain just its question and its own answer. The system instruction asks for `UNKNOWN` rather than a guessed code.

Next, the first `SqliteSaver` context exits and closes its connection. A subprocess starts a fresh Python interpreter, opens the database, and reads the saved checkpoint through `get_tuple`. That worker does not create a model, read configuration, or make a paid request. Its four-message count and exact human inputs provide evidence that persisted data, rather than the original graph's Python objects, supplied the result.

Finally, the parent process enters a second saver context and compiles a new graph. `get_state` returns a **StateSnapshot**: `values` holds restored state, `config` identifies the checkpoint, and `next` describes scheduled work. For our completed first phase, `next == ()`. Reading this snapshot makes no model request. Sending a new human question does: the final primary thread has six messages, while the other remains at two.[1202]

The demo checks the reopened snapshot's checkpoint ID against the earlier saved ID. It also checks the recovered answer includes the supplied code. These are different checks: stored-state recovery is deterministic; a model's answer is probabilistic. Exact prose is not required. A failed recall assertion should be investigated, not replaced with a canned answer or reported as success.

<!-- EXECUTION_FIGURES -->

## Guided practice: inspect the boundaries deliberately

1. Run the focused offline tests with `python -m pytest -q tests/lessons/test_u1.py`. Named model doubles verify orchestration without Anthropic. A dependency skip means SQLite behavior has not been tested in that environment; it is not a persistence pass.
2. Locate the single-new-message input in `send_turn`. Predict the model's human-message histories across its four calls: one introduction; introduction plus question; isolated question; introduction plus two questions. System instructions are added for each model call, not saved as another conversational turn.
3. Locate the first context exit. Explain why the code cannot safely keep invoking the old graph afterward: its saver owns a closed connection. Build the new graph only with the newly opened saver.[1203]
4. Compare `inspect_checkpoint` with `send_turn`. The former reads persisted data; the latter executes a model node. Do not count snapshot reads or the subprocess read as extra Anthropic calls.
5. Check that both recovered threads use the same absolute database path. If you move the file, update the path deliberately. A new directory plus the same thread string is not the same persisted conversation.

The two in-memory tests are intentionally narrower: they check message merging and input validation, not disk recovery. Durable acceptance depends on the SQLite-specific tests and the fresh-process check. The selected saver is synchronous, suitable for this lightweight local lab; its official documentation does not position it as a scalable multi-worker production backend.[1204]

## Independent task: three travel notebooks

Implement the separate starter `exercises/starters/u1.py`. Do not import the demonstration or reference solution. Its three TODO functions are `build_notebook(model, checkpointer)`, `ask(graph, thread_id, text)`, and `run_lab(model, database)`. The workbook gives the exact steps and acceptance properties.

Use one new SQLite file. Before closing the first connection, seed `trip-a` with `My destination is Kyoto. Remember it.` and `trip-b` with `My destination is Oslo. Remember it.` Capture each completed snapshot's checkpoint ID. Exit the context. Reopen the same file, compile a new graph, and verify both snapshots and IDs before invoking either thread again.

Then ask `What is my destination?` in `trip-a`, `trip-b`, and fresh `trip-c`. The first two answers must contain their own city, not the other city's name. The third must contain `UNKNOWN` and neither city. Final message counts must be 4, 4, and 2. Check the exact human histories too, since a plausible answer alone cannot establish isolation. Reject an existing database instead of contaminating this clean-run exercise. Validate blank thread IDs and blank text before invocation, but preserve valid text exactly. This task uses five model calls, unlike the four-call project demonstration.

## Review: three knowledge checks

1. After one completed turn in `trip-a`, you close Python. What two identifiers must a new graph use to recover the current conversation, and why is the thread ID alone insufficient?
2. Why do `ask` and its model node each return or submit only their new message? What message count should two completed turns produce, and how do message IDs affect `add_messages`?
3. Why are a closed/reopened connection, a fresh-process state read, and an isolated thread stronger evidence than a single fluent recall answer? Does logical thread isolation authorize access for different users?

## Troubleshooting and recovery limits

A missing `langgraph.checkpoint.sqlite` import means the optional backend is absent from the active interpreter. Ask the instructor to finish environment setup; never substitute `:memory:` and call it durable. `SqliteSaver.from_conn_string` is a context manager. Pass its yielded saver to `compile`, not the unentered context-manager object.[1203]

A closed-database error usually means a graph escaped its saver context. Missing history usually means a changed file path, a changed thread ID, or the wrong environment. Duplicate-looking turns often come from resending already accumulated history. A model error may leave the human input checkpointed with pending work, not a completed AI turn. Inspect `next` before retrying; this lesson does not implement a general retry or exactly-once side-effect system.

Persistence does not create unlimited context. This node sends the accumulated thread history to the model, so token usage grows. Trimming model input differs from deleting stored messages or checkpoint retention. Those policies need deliberate design.[1205] Protect the SQLite file as conversational data; only synthetic facts belong in this lab or its optional traces. Backup, deletion, crash recovery under power loss, schema migration, and concurrent writers are not validated here.

## References and current-API differences

Unlike the source's process-local history and text-log workflow, this original added lab uses `MessagesState`, explicit thread configuration, and a file-backed `SqliteSaver` context. Official pages were checked during development; publication evidence for real requests is recorded separately by the parent validation process.

[1201]: https://docs.langchain.com/oss/python/langgraph/persistence "LangGraph persistence: checkpointers versus stores"
[1202]: https://docs.langchain.com/oss/python/langgraph/checkpointers "LangGraph checkpointers, threads, and StateSnapshot inspection"
[1203]: https://reference.langchain.com/python/langgraph.checkpoint.sqlite/SqliteSaver/from_conn_string "SqliteSaver context-manager examples for memory and disk"
[1204]: https://reference.langchain.com/python/langgraph.checkpoint.sqlite/SqliteSaver "SqliteSaver synchronous lightweight scope"
[1205]: https://docs.langchain.com/oss/python/langgraph/add-memory "Manage thread memory and growing message histories"
[1206]: https://docs.langchain.com/oss/python/langgraph/graph-api "MessagesState and add_messages ID-aware reducer"
