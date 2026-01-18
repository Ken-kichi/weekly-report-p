"""CLIで指定されたすべてのリポジトリから git diff を取得するノード。"""

from pathlib import Path
import subprocess
import typer
from state import WeeklyReportState

LOG_PREFIX = "[load_git]"


def load_git_diff(state: WeeklyReportState) -> WeeklyReportState:
    """Stateにリポジトリ別の diff と連結テキストを格納する。"""
    # CLIでリポジトリが指定されていなければカレントディレクトリを使う
    repo_paths = state["selected_repos"] or [str(Path.cwd())]
    typer.echo(
        f"{LOG_PREFIX} fetching diffs from {len(repo_paths)} repo(s)...")

    diffs = []
    for repo in repo_paths:
        # 各リポジトリで git log -p を実行して差分を取得
        repo_path = Path(repo).expanduser().resolve()
        typer.echo(f"{LOG_PREFIX} running git log -p in {repo_path}")
        cmd = [
            "git",
            "-C",
            str(repo_path),
            "log",
            "-p",
        ]
        if state["since"]:
            cmd.extend(["--since", state["since"]])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        diffs.append(
            {
                "repo_path": str(repo_path),
                "diff": result.stdout.strip()
            }
        )
    stitched = "\n\n".join(
        f"### Repository: {Path(entry['repo_path']).name}\n{entry['diff']}"
        for entry in diffs
        if entry['diff']
    )

    # LangGraph状態へ diff の生データと LLM向けテキストの両方を保存
    state["git_diffs"] = diffs
    state["git_diff_text"] = stitched.strip()
    typer.echo(
        f"{LOG_PREFIX} collected {len([d for d in diffs if d['diff']])} repo diffs")
    return state
