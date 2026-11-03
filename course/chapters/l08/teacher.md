# L08 — Conversation history and logging

## Explain: establish the evidence and learning goal

Teach this 125-minute lesson after L07. Learners should leave able to trace a human/AI message list, distinguish an ordinary state replacement from a reducer update, export unchanged raw input, and explain why neither a text file nor a message reducer creates restart-durable memory. Success is a correct data path, not a particularly fluent model sentence.

Use the name-recall demonstration, prediction pause, restart-loss distinction, and logging example to establish the learning goal. The delivered implementation uses finite scripted calls, Anthropic, safe new files, and a bounded-prompt exercise. Its terminal loop and logging behavior should be taught from the runnable implementation described below.

Check that the P00 environment is ready before class. Do not ask students to expose keys during debugging. Use only the synthetic names and inputs provided. Parent/instructor validation must separately record real demo and solution execution: offline doubles establish orchestration behavior, not Anthropic access, model recall, screenshots, or telemetry delivery.

## Illustrate: timed teaching sequence

Use minutes 0–12 to contrast L07's independent requests with caller-carried history. Ask, “Where does Steve's name physically appear before the second model call?” The expected response is “In the earlier human message that Python sends again,” not “inside a permanent model memory.” At minutes 12–20 draw `H1, A1, H2` and explain the separate full-history and prompt-window paths.[806]

<!-- ORIGINAL_DIAGRAM -->

At minutes 20–35 perform the demonstration. Minutes 35–45 are guided inspection and prediction. Reserve minutes 45–100 for the independent task, 100–110 for offline checks and artifact inspection, and 110–125 for the three knowledge checks and review. These periods total 125 minutes.

A concept diagram can contrast the history/state path with the logging path. The diagram supports explanation; execution evidence comes from the runnable command and the checks below.

<!-- CONCEPT_FIGURE -->

## Demonstrate: run and inspect rather than narrate an imagined result

From the activated repository environment use:

```bash
python -m course_lessons.l08 --live --backend none
```

Pause before the second response and ask students to predict three input messages, then four returned messages. Identify `run_turn` as the human-message insertion point and the node as the AI-response insertion point. The demonstration's plain `TypedDict` has no reducer, so its partial update contains the complete replacement list. Show the exact response object being retained, rather than rebuilding an AI message and discarding metadata.

The default output directory is unique. Open the reported `conversation.txt`, check `Human:` and `AI:` labels, and locate `gud morning!` unchanged. The three logical model invocations comprise a two-turn conversation and a fresh-history request. Shared-client retries may involve additional HTTP attempts. Show the fresh answer but distinguish its two-message state assertion from a semantic guarantee about every possible generated sentence.

The runner's fresh call simulates reset in the same process. For an actual restart explanation, close the command and inspect the new invocation's initialization. A rerun repeats the scripted introduction; its later correct answer cannot prove it recalled the preceding process. No file is reloaded. U1 adds the durable checkpoint experiment.[807]

<!-- EXECUTION_FIGURES -->

## Guided practice: expected observations

Have each learner explain why a completed second turn has roles human, AI, human, AI. Require them to point to the retained first pair and the newly added pair. Ask another learner to locate `execution_config()` on the graph call and the config passed through to the injected model. This preserves selected callbacks rather than creating an unrelated trace route.

When checking logs, use the entire raw human string, not a normalized comparison. A student who calls `.strip()` to validate nonblank input may still store the original string; a student who stores `.strip()` has changed the input. Discuss multiline or role-looking content: this plain-text layout remains readable but is not an unambiguous machine reload format.

Run the focused checks, not the whole concurrently developed course suite:

```bash
python -m pytest tests/lessons/test_l08.py -q
```

The delivered checks use `RecordingChatModel` and `RaisingChatModel`, block credential loading/network, and disable tracing. Describe any resulting success as offline evidence only. They test delivered demo/reference code and starter status; they do not automatically grade students' completed TODOs.

## Independent exercise: reference walkthrough

The student's exact task is “bounded prompt, complete transcript” in `exercises/starters/l08.py`, with three TODOs. Do not replace it with a generic chatbot or durable memory task. The independent reference is:

```bash
python -m exercises.solutions.l08 --live --backend none
```

First walk through `select_prompt`: validate a nonnegative integer, explicitly rejecting Boolean values because Python treats `bool` as an integer subclass. Require an odd, nonempty sequence of alternating human/AI messages ending in a pending human. Reject tool calls. Select a new list with the last `2 * max_pairs + 1` entries. With a valid odd-length sequence, that slice starts on a human and preserves complete pairs. With zero pairs it keeps only the pending human.

Next walk through `build_graph`. Validate the limit before execution, but do not call the model while constructing the graph. `MessagesState` already uses `add_messages`. The node sends only the window to the model and returns one AI delta; the reducer preserves full state. No checkpointer exists, so the orchestration must still seed each new invocation with caller-held history. Returning only the newest human as graph input would reproduce stateless behavior, despite using a reducer.[806]

Finally inspect `format_transcript`. It consumes full history, not the window, and exports every message with exact labels and separators. Writing is delegated to the provided runner and shared no-overwrite helper. The fixed Mira scenario gives prompt lengths 1, 3, 3 and full lengths 2, 4, 6. The second input is two lines. A fourth logical call is separate fresh history and is intentionally absent from the six-message log.

The reference asserts Mira in the second answer while the introduction remains in its prompt. The third prompt excludes the original human introduction by message ID. Do not claim that proves forgetting: the retained second AI answer can repeat Mira. This is a valuable example of information moving through assistant output. Message count is also not a token limit; provider token counting is a remote API operation, not something to add to these offline checks.[808]

<!-- SOLUTION_CODE -->

## Review: complete answers to the student's three checks

### 1. Predict state and explain the two node returns

Before the answer, `H1, A1, H2` has three messages and roles human, AI, human. Afterward `H1, A1, H2, A2` has four. The demonstration returns the complete list under `messages` because the ordinary channel replaces its previous value. The exercise returns only `[A2]` because `MessagesState` merges that delta with its current list. Matching message IDs update existing entries; newly reconstructed entries with new IDs can duplicate history. Do not teach that returning any full list always duplicates: ID handling matters.

### 2. Explain the saved file and reset

No prior turns reach the model when the caller supplies an empty history. Only the new human request is initially supplied, and its new AI response forms a separate pair. Writing a transcript does not implement reading, message reconstruction, thread isolation, or checkpoint restoration. U1 addresses thread/checkpoint memory and restart-durable storage. A reducer alone provides none of those durable-storage properties.

### 3. Evaluate the bounded window

The selected prompt is `H2, A2, H3`. After the reply the full history is `H1, A1, H2, A2, H3, A3`: six entries. Only model input is trimmed. Tokens remain unbounded because message lengths vary, and full-history RAM/log growth remains unbounded. Forgetting is not guaranteed because retained messages can contain earlier facts. Credit both limitations; “the bot forgets everything older than one pair” is incorrect.

## Marking criteria, misconceptions, and recovery

Award ten points: three for valid pair selection and error cases, three for reducer-based graph/configuration and correct deltas, two for exact full-transcript formatting, and two for observed counts, reset explanation, and honest evidence. Require all critical properties before completion: 1/3/3 prompts, 2/4/6 states, preserved multiline raw input, six logged messages, and no automatic reload. Do not award completion merely because the unfinished starter exits zero: its message explicitly says `STARTER_NOT_COMPLETED`.

If histories collapse, identify plain replacement versus reducer use. If history duplicates, inspect fresh IDs and double insertion. If the first prompt lacks the introduction, inspect caller state before changing the model. If a request fails, retain the failure and use P00 connection diagnosis rather than substituting canned responses. If file writing fails, do not mark success or overwrite evidence; select a fresh output directory. If time runs short, finish the deterministic window/format functions offline and defer paid validation. This preserves the task rather than weakening it into an outline.

## References

[806]: https://docs.langchain.com/oss/python/langgraph/graph-api "LangGraph Graph API: reducers, IDs, and MessagesState"
[807]: https://docs.langchain.com/oss/python/langgraph/add-memory "LangGraph memory: checkpoints versus selected model input"
[808]: https://docs.langchain.com/oss/python/integrations/chat/anthropic "ChatAnthropic: response blocks, usage, and remote token counting"
