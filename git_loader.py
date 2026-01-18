"""Utility node that fetches git diffs for every requested repository."""

from pathlib import Path
import subprocess
import typer
from state import WeeklyReportState

LOG_PREFIX = "[load_git]"


def load_git_diff(state: WeeklyReportState) -> WeeklyReportState:
    """Populate `git_diffs` and `git_diff_text` based on the repositories in state."""
    # CLIで指定されたリポジトリがなければカレントディレクトリを対象にする
    repo_paths = state["selected_repos"] or [str(Path.cwd())]
    typer.echo(
        f"{LOG_PREFIX} fetching diffs from {len(repo_paths)} repo(s)...")

    diffs = []
    for repo in repo_paths:
        # リポジトリごとに log -p を実行し raw diff を取得
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
