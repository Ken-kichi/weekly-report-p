# weekly-report-p

LangGraph と LangChain を使って、`git log -p` から週報を自動生成する CLI ツールです。  
単に文章を出力するのではなく、**生成 → 複数視点での評価 → 条件付き再生成 → 合格した週報を保存** というループをコードで表現しています。

- 複数リポジトリや `--since` 指定に対応した差分取得
- Tech / Manager / Writer の 3 ロールによる重み付きレビュー
- 80 点未満なら再生成、上限回数に達したら強制停止
- 最終稿を `report/weekly-report-YYYY_MM_DD_hh-mm.md` として保存

## 必要環境

- Python 3.10 以上
- [uv](https://github.com/astral-sh/uv)
- OpenAI API キー（`gpt-5` 互換モデルを使用）

## セットアップ

```bash
uv venv
source .venv/bin/activate
uv sync  # pyproject.toml の依存をインストール
```

`.env` を作成し、OpenAI API キーを設定します。

```env
OPENAI_KEY="sk-/////////////////////////////"
```

## 使い方

### 週報を生成する

```bash
uv run main.py generate \
  --since "last monday" \
  --repo ~/work/service-a \
  --repo ~/work/service-b
```

- `--since/-s` … `git log --since` に渡す日付またはショートカット
- `--repo/-r` … 差分を取りたいリポジトリパス（複数指定可）。未指定ならカレントリポジトリを使用
- `--max-iteration/-m` … 再生成を許可する最大回数（デフォルト 3）

実行中は以下のようなログが流れ、今どのフェーズか・なぜ終了したかが分かります。

```
[1/3] Generate report (initial)
[Review:tech] Score: 72
[Review] Score: 72
→ REJECT（80点未満。残り 2 回の再生成を実行）
...
[Review] Score: 84
→ ACCEPT（2回目でスコア 84 点に到達）
```

合格した週報は `report/weekly-report-YYYY_MM_DD_hh-mm.md` に Markdown で保存されます。

### 既存の週報を評価する

```bash
uv run main.py evaluate report/weekly-report-2026_01_18_10-27.md
```

LLM による評価だけを再実行したいときに使用します。`--repo` や `--since` は指定できません。

## 主なファイル

```text
├── cli.py            # Typer ベースの CLI 定義
├── build_graph.py    # LangGraph の構築とレポート保存処理
├── git_loader.py     # git log -p の収集（複数リポジトリ/期間対応）
├── generator.py      # 週報の下書き生成・再生成ノード
├── multi_evaluator.py# 複数ロールによる重み付き評価
├── evaluator.py      # 単体ファイル評価用のユーティリティ
└── report/           # 生成された週報 Markdown の保管先
```

## アイデア拡張

- 過去週報との比較評価
- チームごとの評価プロファイル
- 承認済み週報の学習データ化
- Slack / GitHub 等との連携

State を 1 つ追加するだけで、これらも LangGraph に自然に組み込めます。  
あなたの現場に合わせた **レビューされる AI** を作ってみてください。
