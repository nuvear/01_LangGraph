"""Supplementary setup check: one real Anthropic call inside LangGraph.

Run: python -m examples.anthropic_graph --backend both
Uses a synthetic sentinel prompt. This consumes a small amount of API credit.
"""
from __future__ import annotations

import argparse
import json

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, MessagesState, StateGraph

from course_support.check_connections import values
from course_support.observability import BACKENDS, graph_tracing


def build_graph(model):
    def call_anthropic(state: MessagesState, config: RunnableConfig):
        reply = model.invoke(state["messages"], config=config)
        return {"messages": [reply]}

    builder = StateGraph(MessagesState)
    builder.add_node("call_anthropic", call_anthropic)
    builder.add_edge(START, "call_anthropic")
    builder.add_edge("call_anthropic", END)
    return builder.compile()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=BACKENDS, default="none")
    args = parser.parse_args()
    settings = values()
    key, model_id = settings.get("ANTHROPIC_API_KEY"), settings.get("ANTHROPIC_MODEL")
    if not key or not model_id:
        raise SystemExit("Set ANTHROPIC_API_KEY and ANTHROPIC_MODEL in the local .env first.")
    model = ChatAnthropic(model=model_id, api_key=key, max_tokens=64, timeout=45, max_retries=0)
    with graph_tracing(args.backend, name="LangGraph Course Anthropic Integration Check") as config:
        result = build_graph(model).invoke(
            {"messages": [HumanMessage(content="Reply with exactly LANGGRAPH_ANTHROPIC_OK and nothing else.")]},
            config=config,
        )
    reply = result["messages"][-1]
    text = reply.content if isinstance(reply.content, str) else "".join(
        block.get("text", "") for block in reply.content if isinstance(block, dict) and block.get("type") == "text"
    )
    assert text.strip() == "LANGGRAPH_ANTHROPIC_OK", "The model did not return the expected sentinel."
    assert len(result["messages"]) == 2, "MessagesState should retain the user message and append the AI reply."
    print(json.dumps({"backend": args.backend, "model": model_id, "message_count": len(result["messages"]),
                      "response_text": text, "usage": reply.usage_metadata, "assertions": "passed"}, indent=2))
    if args.backend != "none":
        print("Graph and LLM callbacks completed. Remote ingestion was checked separately; dashboards were not visually inspected.")


if __name__ == "__main__":
    main()
