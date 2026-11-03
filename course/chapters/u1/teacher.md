# U1 — Thread memory and durable SQLite checkpoints

## Explain: scope, preparation, and teaching sequence

This is a **SUPPLEMENTARY / CURRENT-API UPDATE**, placed after L08, with a 60-minute teaching allocation. There is no U1 source-video interval. L08's contextual source is 01:42:54–02:03:20, starting at [the memory section](https://youtu.be/jGg_1h0qzaM?t=6174). Its recap crosses the editorial boundary; do not suggest missing source homework. The SQLite exercise and original diagram are newly authored additions, not claims about the presenter's implementation.

The sequence is Explain → Illustrate → Demonstrate → Guided practice → Independent exercise → Review. Before teaching, confirm Python 3.12, the prepared course environment, and `langgraph-checkpoint-sqlite`. Live work uses the shared Anthropic runtime and synthetic facts only. Never project credentials or open configuration during the lesson. If access is unavailable, teach with the named offline doubles and explicitly label the evidence as offline; do not report a real model pass.

Allocate minutes 0–8 to the process-memory limitation, 8–15 to the state/thread/file illustration, 15–27 to the four-call demonstration, 27–35 to guided inspection, 35–53 to the independent travel notebooks, and 53–60 to assessment and recovery. Avoid spending the whole hour debugging provider setup: P00 owns that prerequisite.

Ask, “What survives if the Python process disappears?” Expected responses distinguish an in-memory list from a saved file. Add the crucial qualification: a text file is durable data, but it is not automatically restored graph state. A checkpointer saves and loads state at graph execution boundaries. Thread-scoped short-term memory can therefore survive restart; the term does not mean RAM-only.[1211]

## Illustrate: point to four separate responsibilities

Use the diagram to distinguish the message reducer, thread selector, database, and connection lifetime. `MessagesState` manages message updates. A checkpointer persists them. A thread ID selects a conversation within that storage. The `with` block owns an open SQLite connection. None of these is an authorization system.

<!-- ORIGINAL_DIAGRAM -->

Have learners predict two completed turns: human, AI, human, AI. The expected answer is four messages, not two “turn objects.” Explain that `add_messages` merges using message IDs; a same-ID update can replace an existing message. Resending history is not a sound substitute for a well-defined delta, even if stable IDs sometimes hide the mistake. The node returns only its new AI message, and the caller submits only its new human message.[1215]

Clarify that `StateSnapshot.next == ()` means this captured run has no scheduled next node. It does not prove the answer is correct or establish future fault tolerance. `values` and checkpoint IDs establish what state was restored.[1212]

## Demonstrate: a timed four-call walkthrough

At minute 15, run:

```bash
python -m course_lessons.u1 --live --backend none
```

At minutes 16–19, locate `send_turn` and the first saver context. Predict the three initial calls: teach `project-a` `ORCHID-42`, ask `project-a`, then ask uninformed `project-b`. Counts are 2, 4, and 2 respectively for those returned states. The other thread's answer should contain `UNKNOWN`, and its state must not contain the code. Assess the structural state separately from generated wording.

At minutes 19–23, locate the first context exit and fresh-process helper. The subprocess invokes only a checkpoint reader. It receives a database path and thread string, not a model or history list. It must recover four messages and the two exact human inputs. This is actual fresh-interpreter disk-read evidence, not a second reference to an existing graph object. It does not test operating-system reboot, abrupt power failure, or production crash recovery.

At minutes 23–27, locate the second context and newly compiled graph. Before any fourth call, the restored checkpoint ID must equal the saved ID, with four messages and no pending node. The fourth real call asks for the code again, taking `project-a` to six messages; `project-b` remains at two. The saver factory must be entered as a context manager, as the official API demonstrates.[1213]

The live response may include punctuation or introductory wording. Accept the exact supplied code appearing within an answer; do not assert a whole generated sentence. The summary's booleans describe assertions in that run, not pre-existing publication evidence. Parent validation supplies actual execution captures for the handbook.

<!-- EXECUTION_FIGURES -->

## Guided practice: make the reasoning visible

Use `python -m pytest -q tests/lessons/test_u1.py` for the focused offline run. Explain that `ProjectRecallDouble` and `DestinationRecallDouble` are deterministic test doubles, never Anthropic calls. A SQLite dependency skip is unfinished validation. In-memory tests cover node/reducer and validation contracts only; the disk tests use the actual SQLite saver and include a new interpreter.

Ask learners to read `get_state` before `send_turn` and identify the paid operation. Expected response: snapshot retrieval loads existing state without executing the response node; `send_turn` schedules model work. Ask them to compare database paths, not just thread labels, when diagnosing missing history. Preserve `execution_config(thread_id)` rather than reconstructing configuration and accidentally dropping callbacks or the recursion bound.

## Independent exercise: solution walkthrough

The workbook requires a separate three-function travel notebook, not a renamed demonstration. Its solution is `exercises/solutions/u1.py`, independently implemented without importing the demo. The completed starter runs an explicitly labeled offline self-check, deleting its temporary database afterward. Run the retained live reference with:

```bash
python -m exercises.solutions.u1 --live
```

`build_notebook` compiles `START → answer → END` with `MessagesState`. Its node adds `NOTEBOOK_RULE` only to model input, forwards the graph configuration, requires an `AIMessage`, and returns that one update. `ask` rejects non-string or whitespace-only inputs with `ValueError`, while preserving valid text exactly. These are the same focused functions named in the starter.

`run_lab` requires a new database, raising `FileExistsError` if one already exists. Its first context seeds `trip-a` with `My destination is Kyoto. Remember it.` and `trip-b` with `My destination is Oslo. Remember it.` Each completed snapshot has two messages; save both checkpoint IDs. Close that connection before constructing the second saver and graph.

The reopened graph verifies the snapshots and IDs before recall. It asks `What is my destination?` in both seeded threads and in fresh `trip-c`. Require Kyoto without Oslo in `trip-a`, Oslo without Kyoto in `trip-b`, and `UNKNOWN` without either city in `trip-c`. Check exact human histories as well. Final counts are 4, 4, and 2; total model calls are five. The independent exercise proves close/reopen recovery; the demonstration additionally includes the fresh-process reader.

<!-- SOLUTION_CODE -->

## Review: exact knowledge-check answers

1. **Recovering after Python closes.** Reopen the same durable database path and use the same `thread_id`; compile a compatible graph with that saver. The path locates the storage, and the thread ID selects the conversation within it. The same label in a different new file cannot retrieve the original messages. A checkpoint ID is needed only when selecting a particular historical snapshot, not the latest conversation state.
2. **Message updates and counts.** The caller submits only the new human message and the model node returns only the new AI message because `MessagesState` already merges updates into restored history. Two completed turns produce four messages. `add_messages` uses message IDs and can replace a same-ID message, so it is more precise than unconditional list concatenation. Manually replaying the whole history risks repeated inputs and obscures the state contract.
3. **Strength of evidence and access control.** A fluent answer can be a guess. A reopened saver and a fresh process demonstrate retrieval independent of the old connection and Python history; an uninformed separate thread and inspected model inputs establish that the other conversation was not supplied. These are separate properties. Thread IDs do not authorize users: file permissions and application-level access checks remain necessary.

## Marking, misconceptions, and recovery

Award 10 points: two for the injectable single-response graph and delta updates; one for input validation; two for a genuinely closed/reopened file with matching snapshot IDs; two for exact per-thread human histories and city isolation; one for the third-thread unknown behavior; one for final counts and a truthful JSON-friendly summary; one for safe clean-run handling and explaining limits. Require at least 8/10, with durable reopen and isolation both mandatory. Do not award persistence credit for `InMemorySaver` or `:memory:`.

Common misconceptions are “thread means operating-system thread,” “the model remembers independently,” and “durable means unlimited.” Here a thread is a checkpoint key; the node explicitly passes restored messages to the model. History and checkpoint growth require separate context and retention policies.[1214] SQLite's lightweight synchronous scope is appropriate for this lab, not a claim of production-scale multi-worker support.

For missing history, compare the resolved file and thread ID first. For closed-connection errors, restore `with` indentation and compile inside each new context. For an API exception, inspect whether only a human input remains with pending work; do not append a fake AI success. Use a new run file for a clean retry, preserving the failed artifact for diagnosis. For recall mismatch, inspect synthetic model inputs and the system rule without weakening structural assertions. Never claim live calls, Windows behavior, dashboards, hard-crash recovery, migrations, or backups were tested without corresponding parent evidence.

## References

[1211]: https://docs.langchain.com/oss/python/langgraph/persistence "Thread-scoped checkpointer memory and separate stores"
[1212]: https://docs.langchain.com/oss/python/langgraph/checkpointers "StateSnapshot and checkpoint inspection"
[1213]: https://reference.langchain.com/python/langgraph.checkpoint.sqlite/SqliteSaver/from_conn_string "SqliteSaver context-manager lifetime"
[1214]: https://docs.langchain.com/oss/python/langgraph/add-memory "Message context and memory-management limits"
[1215]: https://docs.langchain.com/oss/python/langgraph/graph-api "MessagesState reducer and message-ID update semantics"
