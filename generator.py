"""LLM-backed generator node that produces or rewrites weekly reports."""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from state import WeeklyReportState
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatOpenAI(
    model="gpt-5",
    api_key=os.getenv("OPENAI_KEY")
)


def _build_prompt(state: WeeklyReportState) -> list:
    """Construct the system/human prompts depending on iteration count."""
    # iteration 0 は初回生成、以降は再生成として扱う
    if state["iteration"] == 0:
        system_prompt = """
あなたは優秀なソフトウェアエンジニアです。
以下の git の変更履歴をもとに、社内向けの週報を作成してください。

・技術的に正確であること
・読み手（上司・チーム）が理解しやすいこと
・簡潔だが情報不足にならないこと
"""
        human_prompt = f"""
【git diff / log】
{state["git_diff_text"]}

上記をもとに、以下の構成で週報を書いてください。

- 今週やったこと
- 技術的なポイント
- 課題・懸念点
"""
    else:
        system_prompt = """
あなたはレビュー指摘を的確に反映できるシニアエンジニアです。
前回の週報を改善してください。
"""
        human_prompt = f"""
【前回の週報】
{state["report_draft"]}

【レビュー指摘】
{state["reviews"]}

上記の指摘をすべて反映し、
より完成度の高い週報に書き直してください。
"""
    return [
        SystemMessage(content=system_prompt.strip()),
        HumanMessage(content=human_prompt.strip())
    ]


def _invoke_llm(state: WeeklyReportState) -> WeeklyReportState:
    """LLM を実行して draft と iteration を更新する内部共通処理。"""
    # プロンプトを組み立てて LLM を呼び出す
    messages = _build_prompt(state)
    response = llm.invoke(messages)
    state["report_draft"] = response.content
    # 生成回数をインクリメントしてループ制御に使う
    state["iteration"] += 1
    return state


def generate_weekly_report(state: WeeklyReportState) -> WeeklyReportState:
    """LangGraph node that invokes the LLM and updates the report draft."""
    if state["iteration"] != 0:
        # 予期せぬ呼び出しでも整合性を保つため警告的に扱う
        state["iteration"] = 0
    next_iter = state["iteration"] + 1
    print(f"[{next_iter}/{state['max_iteration']}] Generate report (initial)")
    return _invoke_llm(state)


def regenerate_weekly_report(state: WeeklyReportState) -> WeeklyReportState:
    """再生成ノード。レビュー指摘を反映した上で再度LLMを実行する。"""
    if state["iteration"] == 0:
        # 再生成なのに初回扱いにならないよう最低1回目として扱う
        state["iteration"] = 1
    next_iter = state["iteration"] + 1
    print(f"[{next_iter}/{state['max_iteration']}] Regenerate report with feedback")
    return _invoke_llm(state)
