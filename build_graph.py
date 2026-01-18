"""LangGraph wiring for the weekly report generation workflow."""

from langgraph.graph import StateGraph, END

from state import WeeklyReportState
from git_loader import load_git_diff
from generator import generate_weekly_report, regenerate_weekly_report
from multi_evaluator import multi_evaluate_weekly_report


def should_continue(state: WeeklyReportState) -> str:
    """評価結果と試行回数に応じて次の遷移を返す。"""
    if state["average_score"] >= 80:
        return "approve"

    if state["iteration"] >= state["max_iteration"]:
        return "stop"

    return "regenerate"


def build_graph():
    """週報生成フローの StateGraph を構築して返す。"""
    graph = StateGraph(WeeklyReportState)

    # 各ノードをグラフに登録
    graph.add_node("load_git", load_git_diff)
    graph.add_node("generate", generate_weekly_report)
    graph.add_node("regenerate", regenerate_weekly_report)
    graph.add_node("evaluate", multi_evaluate_weekly_report)

    # エントリーポイントを設定
    graph.set_entry_point("load_git")

    # 直列の遷移
    graph.add_edge("load_git", "generate")
    graph.add_edge("generate", "evaluate")

    # 評価結果に基づく条件分岐
    graph.add_conditional_edges(
        "evaluate",
        should_continue,
        {
            "approve": END,
            "regenerate": "regenerate",
            "stop": END
        }
    )

    graph.add_edge("regenerate", "evaluate")

    return graph.compile()


def run_graph(
        since: str | None = None,
        max_iteration: int = 3,
        repos: list[str] | None = None
):
    """CLI などから呼ばれる実行ラッパー。"""
    graph = build_graph()

    # LangGraph 初期状態
    initial_state = WeeklyReportState(
        git_diffs=[],
        git_diff_text="",
        report_draft="",
        reviews=[],
        average_score=0,
        iteration=0,
        max_iteration=max_iteration,
        selected_repos=repos or [],
        since=since,
        is_approved=False,
    )

    # 実際にグラフを実行
    final_state = graph.invoke(initial_state)

    return final_state
