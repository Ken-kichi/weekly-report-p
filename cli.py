"""週報ジェネレーター用の CLI エントリーポイント。"""

import typer

app = typer.Typer(
    name="weekly-report",
    help="git log から週報を自動生成する CLI ツール",
)


@app.command()
def generate(
    since: str | None = typer.Option(
        None,
        "--since",
        "-s",
        help="git log --since に渡す日付/ショートカット（例: 'last monday'）",
    ),
    max_iteration: int = typer.Option(
        3,
        "--max-iteration",
        "-m",
        help="再生成の最大回数（超えると強制終了）",
    ),
    repos: list[str] = typer.Option(
        [],
        "--repo",
        "-r",
        help="git log を取得するリポジトリパス（複数指定可）",
    )
):
    # 週報生成フローを開始
    """指定リポジトリから週報を生成する"""
    typer.echo("週報生成を開始します")
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
        help="評価対象の週報 Markdown ファイルパス",
    )
):
    # 既存の週報に対して評価のみ実行
    """既存の週報ファイルのみを評価する"""
    typer.echo(f"Evaluating report: {report_path}")
    from evaluator import evaluate_report_file

    result = evaluate_report_file(report_path)

    typer.echo("- Evaluation Result -")
    typer.echo(f"Score   : {result['score']}")
    typer.echo(f"Feedback: {result['feedback']}")


def run():
    # `python -m` から呼び出されるエントリーポイント
    """`python -m` で呼び出される Typer エントリーポイント。"""
    app()
