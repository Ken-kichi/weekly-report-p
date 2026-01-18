"""Command line entrypoints for the weekly report generator."""

import typer

app = typer.Typer(
    name="weekly-report",
    help="CLI tool that generates weekly reports from git logs.",
)


@app.command()
def generate(
    since: str | None = typer.Option(
        None,
        "--since",
        "-s",
        help="Date or shortcut passed to git log --since (e.g. 'last monday').",
    ),
    max_iteration: int = typer.Option(
        3,
        "--max-iteration",
        "-m",
        help="Maximum number of regenerate cycles before aborting.",
    ),
    repos: list[str] = typer.Option(
        [],
        "--repo",
        "-r",
        help="Path(s) to git repositories to read (repeatable).",
    )
):
    # 週報生成フローを開始
    """Generate a weekly report from one or more git repositories."""
    typer.echo("Weekly report generation started.")
    from build_graph import run_graph
    _, report_path = run_graph(
        since=since,
        max_iteration=max_iteration,
        repos=repos,
    )

    typer.echo(f"Weekly report saved to {report_path}")
    typer.echo("Weekly report generation finished.")


@app.command()
def evaluate(
    report_path: str = typer.Argument(
        ...,
        help="Path to an existing weekly report Markdown file.",
    )
):
    # 既存の週報に対して評価のみ実行
    """Run the evaluator against an existing report file without regeneration."""
    typer.echo(f"Evaluating report: {report_path}")
    from evaluator import evaluate_report_file

    result = evaluate_report_file(report_path)

    typer.echo("- Evaluation Result -")
    typer.echo(f"Score   : {result['score']}")
    typer.echo(f"Feedback: {result['feedback']}")


def run():
    # `python -m` から呼び出されるエントリーポイント
    """Typer entrypoint used by python -m invocation."""
    app()
