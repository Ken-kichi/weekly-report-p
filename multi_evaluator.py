"""Multiple-role evaluator that aggregates weighted review scores."""

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

LOG_PREFIX = "[evaluate]"

# 重み付きで評価するロールの定義
REVIEWERS = [
    {
        "name": "tech",
        "system_prompt": """
あなたはシニアエンジニアです。
技術的な正確性・専門性の観点から週報をレビューしてください。
""",
        "weight": 0.4,
    },
    {
        "name": "manager",
        "system_prompt": """
あなたは開発マネージャです。
進捗のわかりやすさ・報告としての妥当性の観点から週報をレビューしてください。
""",
        "weight": 0.3,
    },
    {
        "name": "writer",
        "system_prompt": """
あなたは技術文章の編集者です。
読みやすさ・構成・文章品質の観点から週報をレビューしてください。
""",
        "weight": 0.3,
    },
]


def _build_prompt(system_prompt: str, report: str) -> list:
    """Create the per-role evaluation prompt with a fixed output format."""
    human_prompt = f"""
【週報本文】
{report}

【出力形式（必ず守る）】
Score: <0-100の整数>
Feedback:
- 指摘1
- 指摘2
"""

    return [
        SystemMessage(content=system_prompt.strip()),
        HumanMessage(content=human_prompt.strip()),
    ]


def _parse_score(text: str) -> int:
    """Extract and clamp the integer score returned by a reviewer LLM."""
    match = re.search(f"Score:\s*(\d+)", text)
    if not match:
        raise ValueError("Score が見つかりません")
    score = int(match.group(1))
    return max(0, min(100, score))


def _evaluate_by_role(role: dict, report: str) -> dict:
    """Run the LLM for a single reviewer role and return the structured result."""
    messages = _build_prompt(
        system_prompt=role["system_prompt"],
        report=report
    )

    response = llm.invoke(messages)
    content = response.content
    score = _parse_score(content)

    return {
        "role": role["name"],
        "score": score,
        "weight": role["weight"],
        "feedback": content
    }


def multi_evaluate_weekly_report(
        state: WeeklyReportState
) -> WeeklyReportState:
    """Iterate through all reviewers, aggregate weighted scores, store feedback."""
    results: list[dict] = []

    for role in REVIEWERS:
        # ロールごとに独立して評価を実行
        result = _evaluate_by_role(
            role=role,
            report=state["report_draft"]
        )
        results.append(result)
        print(f"{LOG_PREFIX} {role['name']} score={result['score']}")

    # 重み付き平均で総合スコアを算出
    weighted_socre = sum(
        r["score"] * r["weight"] for r in results
    )

    state["average_score"] = round(weighted_socre)
    # レビュー結果は再生成プロンプトなどで再利用する
    state["reviews"].extend(
        [
            f"[{r['role'].upper()} REVIEW]\n{r['feedback']}"
            for r in results
        ]
    )
    print(f"{LOG_PREFIX} weighted average score={state['average_score']}")

    return state
