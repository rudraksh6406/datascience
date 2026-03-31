"""CLI entry point: python -m opus6 'your prompt'"""

import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from .opus import Opus6


def main():
    console = Console()

    if len(sys.argv) < 2:
        console.print(Panel(
            "[bold]Opus 6.0[/bold] — Smarter. Better.\n\n"
            "Usage: python -m opus6 \"your prompt here\"\n"
            "       python -m opus6 -v \"your prompt\"  (verbose mode)",
            border_style="bright_cyan",
        ))
        sys.exit(1)

    verbose = "-v" in sys.argv or "--verbose" in sys.argv
    args = [a for a in sys.argv[1:] if a not in ("-v", "--verbose")]
    prompt = " ".join(args)

    console.print(Panel(
        f"[bold bright_cyan]OPUS 6.0[/bold bright_cyan]",
        subtitle="thinking...",
        border_style="bright_cyan",
    ))

    opus = Opus6(quality_threshold=7)
    result = opus.run(prompt, verbose=verbose)

    # Show score
    score = result["score"]
    score_color = "green" if score >= 7 else "yellow" if score >= 5 else "red"
    iterations = result["iterations"]

    console.print()
    if result.get("plan"):
        console.print(f"[dim]Plan: {len(result['plan'])} steps | "
                      f"Refined: {iterations}x | "
                      f"Score: [{score_color}]{score}/10[/{score_color}][/dim]")
    else:
        console.print(f"[dim]Refined: {iterations}x | "
                      f"Score: [{score_color}]{score}/10[/{score_color}][/dim]")
    console.print()
    console.print(Markdown(result["answer"]))


if __name__ == "__main__":
    main()
