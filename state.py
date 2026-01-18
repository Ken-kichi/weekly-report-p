"""LangGraph で扱う状態を TypedDict で明示する。"""

# LangGraph 全体で共有する状態構造を TypedDict で明示する

from typing import TypedDict


class ReviewResult(TypedDict):
    """単一の評価者が出力するスコアとフィードバック。"""

    # 単一レビューアーが出力するメタ情報
    reviewer: str  # reviewer role (e.g. tech / manager / writer)
    score: int  # 0〜100
    feedback: str  # 改善コメント


class GitDiffEntry(TypedDict):
    """1つのリポジトリから取得した `git log -p` の内容。"""

    # リポジトリパスとその差分テキストの組
    repo_path: str
    diff: str


class WeeklyReportState(TypedDict):
    """週報生成フロー全体で共有する状態。"""

    # 入力
    git_diffs: list[GitDiffEntry]  # リポジトリごとの差分（生データ）
    git_diff_text: str  # LLMに渡す連結済みテキスト（見出し付き）

    # 生成物
    report_draft: str  # 現在の週報ドラフト

    # 評価結果
    reviews: list[ReviewResult]  # 各評価者の評価
    average_score: float  # 平均スコア

    # 制御用
    iteration: int  # 現在の生成回数
    max_iteration: int  # 最大生成回数

    # 補助情報（任意）
    selected_repos: list[str]  # CLIで指定されたリポジトリ一覧
    since: str | None  # git log の基準日
    is_approved: bool  # 承認済みかどうか
