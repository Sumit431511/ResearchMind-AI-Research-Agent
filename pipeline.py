from __future__ import annotations

from orchestrator import run_research_pipeline


def _print_progress(step: str, message: str) -> None:
    print(f"[{step.upper()}] {message}")


def run_cli_pipeline(topic: str) -> dict:
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
    run_cli_pipeline(topic)
