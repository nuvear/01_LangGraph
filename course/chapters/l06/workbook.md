# L06 — Bounded loops and automatic higher/lower game

## Your task: automatic guessing, not human input

Build a LangGraph game that finds a synthetic target between 1 and 20 using automatic higher/lower feedback. The default maximum is seven guesses. The graph must also stop honestly when a smaller allowed budget is exhausted. Deterministic midpoints, validation, and a reduced-budget test are required teaching conditions; exact random output is not an acceptance criterion.

Use the separate starter at `exercises/starters/l06.py`. It does not import the answer. The reference solution is `exercises/solutions/l06.py`; consult it after attempting the task. The demonstration at `course_lessons/l06.py` teaches five bounded generations, not this game's solution. No model, API key, tracing service, `input()`, or additional package installation is needed for this prepared environment.

Run these commands from the repository root:

```bash
python -m course_lessons.l06 --backend none
python -m exercises.starters.l06
```

The unfinished starter should print `STARTER_NOT_COMPLETED` and exit successfully. That message means work remains; it is not a pass. After your three functions work, its self-check should print `STARTER_CHECKS_PASSED`. Do not replace the status message or remove assertions to make the command appear successful.

## Implement three focused functions

1. **Validate and reset in `reset_game`.** Accept a nonblank string `player_name`, an integer `target` from 1 through 20, and an integer `max_attempts` from 1 through 7. Reject booleans for the two integer fields. Invalid configuration must raise `ValueError` before any guessing. Preserve these three configuration values. Reset `lower=1`, `upper=20`, `guesses=[]`, `attempts=0`, `hint=""`, and `status="playing"`, even if stale derived values were supplied.
2. **Guess in `guess_node`.** Compute the integer floor midpoint of the inclusive bounds. Do not consult the target to choose it. Return a new guesses list with that midpoint appended and increase attempts by one. Do not mutate the incoming list, change bounds, or increment attempts elsewhere.
3. **Compare in `feedback_node`.** Read the latest guess. Equality means hint `correct` and status `won`. A smaller guess means hint `higher` and the new lower bound is the failed guess plus one. A larger guess means hint `lower` and the new upper bound is the failed guess minus one. After a miss, status is `lost` if attempts has reached the budget, otherwise `playing`. Correctness takes priority even on the last allowed attempt.

Keep the supplied topology: `START → reset → guess → feedback`, with a conditional route from feedback back to guess only while status is `playing`. Both `won` and `lost` route to `END`. Do not add an unconditional feedback-to-guess edge. The provided route returns labels; your node functions return partial update dictionaries.

## Run and record observable results

Rerun `python -m exercises.starters.l06` after each TODO. For additional experiments, import your starter's `build_graph` and `new_game`. Pass `config=execution_config()` to `invoke` or `stream`. Wrap interactive experiments in `with tracing_context(enabled=False):` using the import from `langsmith`, so ambient tracing remains disabled.

Record the following fields using observed state, not copied expected text:

- Target 17, budget seven: guesses ___; attempts ___; final hint ___; status ___. Explain one bound change: ___.
- Target 20, budget two: guesses ___; final inclusive bounds ___; hint ___; status ___. Did a third guess run? ___.
- Target 15, budget two: attempts ___; final status ___; why success takes priority ___.
- Every target 1–20, default budget: number successful ___; maximum attempts observed ___; any repeated guess within one game ___ .
- Dirty input with target 10, guesses `[999]`, attempts `-8`, and wrong bounds: final guesses ___; attempts ___; original caller list unchanged ___ .
- Invalid target 0 and invalid budget 8: exception type ___; why neither should start guessing ___ .

For the first case, expect `10, 15, 18, 16, 17` and a five-attempt win. For the two-attempt exhaustion case, expect `10, 15`, bounds 16–20, hint `higher`, and `lost`. The final-attempt case must win. These are predictions of the specified algorithm, not execution evidence.

## Three progressive hints

### Hint 1: isolate fresh-run fields

Configuration identifies the game; derived fields describe its progress. Reset only the derived fields. Use exact integer type checks where accepting `True` as target one would be misleading.

### Hint 2: separate choosing from judging

The midpoint needs only `lower` and `upper`. The feedback node needs the target. Exclude a missed midpoint from the next inclusive interval; otherwise the same candidate can survive narrowing.

### Hint 3: classify success before exhaustion

Write the equality branch first. Only a miss should be classified by the attempt cap. The router then reads status without changing it. A recursion-limit exception is not an alternative way to report a loss.

## Completion criteria and comparison

Your implementation must pass the starter self-check without deleting checks, win for all 20 valid targets within seven guesses, produce both required exit reasons, and preserve input lists. For each miss, the new bounds must still contain the target, exclude that guess, and strictly shrink. Check this by streaming updates if your result is unexpected. Invalid configuration must fail before guessing. An ordinary run must not end with `GraphRecursionError`.

After your attempt, compare with:

```bash
python -m exercises.solutions.l06 --backend none
python -m pytest tests/lessons/test_l06.py -q
```

Those focused tests validate the delivered demonstration and reference solution, not your edited starter. Record one difference between your implementation and the reference, with its behavioral effect: ___.

## Stretch task: make narrowing inspectable

Without changing required behavior, record each pre-guess interval and post-feedback interval in your own notes or a separate in-memory history field. Assert that every miss shrinks the interval and retains the target. Do not add network calls, an interactive player, or a larger budget. Explain why the execution safety guard counts graph super-steps rather than game guesses. The [official loop guide](https://docs.langchain.com/oss/python/langgraph/use-graph-api), verified on 3 November 2026, explains that distinction.
