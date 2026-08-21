from __future__ import annotations

import os

from orchestrator import run_research_pipeline
from auth import verify_api_key


def _print_progress(step: str, message: str) -> None:
    print(f"[{step.upper()}] {message}")


def run_cli_pipeline(topic: str, api_key: str | None = None) -> dict:
    # ---- AUTH CHECK ----------------------------------------------------
    if api_key is None:
        raise PermissionError("An API key must be supplied via --api-key.")
    if not verify_api_key(api_key):
        raise PermissionError("Invalid API key.")
    # -------------------------------------------------------------------

    state = run_research_pipeline(topic, progress_callback=_print_progress)

    print("\n" + "=" * 50)
    print("Sources used")
    print("=" * 50)
    for item in state.search_results:
        print(f"- {item.title} ({item.url})")

    print("\n" + "=" * 50)
    print("Final report")
    print("=" * 50)
    print(state.report)

    print("\n" + "=" * 50)
    print("Critic feedback")
    print("=" * 50)
    print(state.critique.raw if state.critique else "No critique generated.")

    return state.model_dump()


if __name__ == "__main__":
    topic = input("\nEnter a research topic: ")
    # Try to obtain API key from environment, otherwise prompt the user.
    api_key = os.getenv("RESEARCH_PIPELINE_API_KEY")
    if not api_key:
        api_key = input("Enter API key: ")
    try:
        run_cli_pipeline(topic, api_key=api_key)
    except PermissionError as exc:
        print(f"❌ Authentication failed: {exc}")
        exit(1)
