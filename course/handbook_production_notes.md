# Handbook production notes

The user approved expansion of the complete training index on 3 November 2026. The latest saved index was read in place; the index is preserved rather than overwritten.

The three new manuals are the Student Handbook, Teacher Handbook, and Exercise Workbook. Each is produced in Word, HTML, and Markdown. Lesson IDs and commands are shared across all editions. The eleven video-aligned core lessons are followed by the clearly labeled implementation updates U1/U2, observability modules S1/S2, and capstone C01; each core chapter points to useful insertion locations for the added labs.

Source attribution: Vaibhav Mehra, *LangGraph Complete Course for Beginners – Complex AI Agents with Python*, published on the freeCodeCamp YouTube channel, https://youtu.be/jGg_1h0qzaM. Publisher context: Beau Carnes, 20 May 2025, https://www.freecodecamp.org/news/learn-langgraph-and-build-conversational-ai-with-python/. The publisher describes the five foundational projects, AI workflows, and RAG. Precise exercise attribution follows the whole caption review rather than assuming every section contains separately assigned homework.

The entire timestamped caption track and 36 source-video frames were reviewed in the index phase. New handbook illustrations use small timestamped source stills with attribution, alongside original, reproducible diagrams. Full source media/captions remain private working inputs, not repository deliverables.

Model-dependent validation explicitly opts into real Anthropic requests using the local `.env`; no provider keys are stored in graph state or documentation. Tests using injected models are identified as offline tests, not substitutes for real execution. Final validation executed every demonstration and independent exercise solution, captured actual stdout, and screenshotted that evidence without synthesizing output. Source-video stills are never described as screenshots of the adapted code.

The validated RAG stack uses a real local ONNX embedding model through Chroma, with persistent indexing and source/page metadata. This avoids an additional paid embedding key. Its first download still requires Internet access. SQLite provides the separately labeled durable-checkpoint example. Windows command and platform behavior remain explicitly untested until actually run on Windows.

## Completed course production — 3 November 2026

All 17 modules and all three matched chapter sets are complete. All 34 demonstration/reference executions passed, including 20 real Anthropic-enabled cases. The final offline suite and clean native runtime both passed 860 tests with 9 intentional unfinished-starter acceptance skips. Current source hashes match the recorded runs. Real local ONNX/Chroma retrieval, SQLite reopen/fresh-process reading, interrupt/resume, bounded revision/approval and actual saved-artifact checks are covered.

Live validation exposed unsupported forced named-tool selection on the configured model; L11/S2 now use automatic selection with explicit instructions and strict checks for actual tool execution. The U1 restoration-order and L11 mixed-source citation gaps found in editorial integration were corrected and regression-tested.

The inspected final Word renderings have 141 student pages, 140 teacher pages, and 50 workbook pages. Each handbook embeds 62 distinct images: 11 attributed source stills, 17 original diagrams/overviews, and all 34 genuine execution captures. Complete detailed Mermaid diagrams remain available beside eleven compact print overviews. All 331 actual pages were rendered, all contact sheets reviewed, and representative full pages inspected. The final page checker clears old draft renders and fingerprints DOCX/PDF files; no overflow or sparse-page warning remains.

The original open training-index Word file was not replaced. Canonical handbooks, HTML/Markdown sources, code and evidence live in the repository; the local complete export retains their relative dependencies. Private environment values, downloaded complete media/captions, virtual environments and QA working files are excluded. Windows execution, visual remote dashboard inspection, and optional design extensions remain explicitly untested rather than implied passes. See `course/validation_report.md` for the definitive scope and evidence limits.
