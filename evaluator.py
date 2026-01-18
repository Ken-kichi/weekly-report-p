"""LLM-based evaluator that scores generated reports."""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import re
from dotenv import load_dotenv
import os
from state import WeeklyReportState

load_dotenv()

llm = ChatOpenAI(
    model="gpt-5",
    api_key=os.getenv("OPENAI_KEY")
)


def _build_prompt(state: WeeklyReportState) -> list:
    """Create the evaluation prompt demanding a numeric score and feedback."""
    # 評価観点と出力フォーマットを厳密に指定
    system_prompt = """
あなたは厳密で公平なレビュー担当者です。
以下の週報をレビューし、必ず数値評価を行ってください。

評価観点：
1. 技術的な正確さ
2. 内容のわかりやすさ
3. 情報量の適切さ
4. 業務週報としての完成度

各観点を総合して、0〜100点でスコアをつけてください。
"""
    human_prompt = f"""
【週報本文】
{state["report_draft"]}

【出力形式（必ず守る）】
Score: <0-100の整数>
Feedback:
- 指摘1
- 指摘2
- 指摘3
"""
    return [
        SystemMessage(content=system_prompt.strip()),
        HumanMessage(content=human_prompt.strip())
    ]


def _parse_score(text: str) -> int:
    """Extract an integer score from the evaluator LLM output."""
    # LLM出力からスコアを抽出し、0〜100にクリップ
    match = re.search(f"Score:\s*(\d+)", text)
    if not match:
        raise ValueError("Score が見つかりません")
    score = int(match.group(1))
    return max(0, min(100, score))


def evaluate_weekly_report(state: WeeklyReportState) -> WeeklyReportState:
    """Run the evaluator chain, append the review, and update the score."""
    # 評価を実行し、Stateへスコアとフィードバックを保存
    messages = _build_prompt(state)
    response = llm.invoke(messages)
    content = response.content
    score = _parse_score(content)

    state["reviews"].append(content)
    state["average_score"] = score
    return state


def evaluate_report_file(report_path: str) -> dict:
    """Evaluate an existing report file and return the score and feedback."""
    # 既存の週報ファイルを評価し、スコアとフィードバックを返す
    with open(report_path, "r", encoding="utf-8") as f:
        report_content = f.read()

    state = WeeklyReportState(
        report_draft=report_content,
        reviews=[],
        average_score=0,
    )

    evaluated_state = evaluate_weekly_report(state)

    return {
        "score": evaluated_state["average_score"],
        "feedback": evaluated_state["reviews"][-1],
    }
