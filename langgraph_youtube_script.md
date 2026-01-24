# LangGraph週報CLI：実装しながら学ぶYouTube台本

- 想定尺：20分前後（冒頭1分はショート兼用）
- 進行：article.mdの章立てと同じ順番で、実装→解説→実行デモの流れ
- 収録スタイル：VS Code画面で実装しつつ、要所でスライド／ホワイトボードを差し込み

---

## 0:00〜1:00　ショート兼オープニング（第1章の導入）
- **映像**：IDEでLangGraphのノード図が描かれる→CLI実行→スコアログが流れるモンタージュ
- **セリフ**  
  「生成AIで週報を書いても、結局レビューで手直し…そんな人向けに“評価される週報”を自動で回すLangGraph CLIを作ります。状態管理・分岐・再生成までコードで表現して、80点を超えるまでAIに書き直させましょう。今から20分、実装しながら仕組みを腹落ちさせます。」
- **CTA**：「動画を保存して、一緒にコードを写経しながら進めましょう。」

---

## 1:00〜3:30　第1章｜なぜLangGraphなのか（否定から入る）
- **映像**：ホワイトボードで `if` / `while` のネスト図→State Machine図へ切り替え
- **セリフ要旨**
  1. 「週報を一度生成するだけならLangGraphは不要。単発プロンプトで終わります。」
  2. 「でも“生成→評価→修正”のループになると、状態が追えずコードが破綻します。」
  3. 「今日のゴールは、Stateを持った評価ループをLangGraphで表現すること。」
- **操作**：VS Codeで article.md の第1章を開き、要点をマーカーしつつ話す。

---

## 3:30〜6:00　第2章＋環境構築｜全体アーキテクチャを掴む
- **映像**：article.mdのフロー図→ターミナルに切り替え
- **実装手順**
  1. `mkdir weekly-report && cd weekly-report`
  2. `uv init && uv venv && source .venv/bin/activate`
  3. `touch cli.py build_graph.py state.py git_loader.py generator.py evaluator.py multi_evaluator.py main.py`
  4. `uv add typer langchain langgraph openai langchain_openai python-dotenv`
- **セリフ**：「ファイル一覧は責務ごとに分けます。graphはbuild_graph.pyだけで管理。report/は後で自動生成。」
- **補足**：`.env` の役割を説明し、OPENAI_KEYをコメントだけで紹介（キーは伏せる）。

---

## 6:00〜8:30　第3章｜CLI UX実装（cli.py）
- **映像**：VS Codeで `cli.py` を開き、articleのコードを貼りながら解説
- **実装ポイント**
  - Typerアプリ定義、`generate` / `evaluate` コマンドを実装
  - `uv run main.py generate` のシンプルさを強調
  - `--since`, `--repo`, `--max-iteration` のオプションをコピペではなくタイピング
- **セリフ**：「CLIは入口だけ。ロジックはGraphに丸投げ。ログ表示で“LangGraphが仕事をしている感”を出します。」

---

## 8:30〜11:00　第4章｜State設計（state.py）
- **映像**：`state.py` をゼロから入力
- **実装順**
  1. `ReviewResult`, `GitDiffEntry` のTypedDictを定義
  2. `WeeklyReportState` に article通りのフィールドを追加
  3. コメントで「State=業務フローの写し鏡」と一言補足
- **セリフ**：「LangGraphは“関数を繋ぐ”ツールではなく“Stateを変化させる”ツール。ここで迷うと全体が崩れます。」
- **Tips**：iteration / max_iteration / is_approved の役割を具体的なループ例で紹介。

---

## 11:00〜14:30　第5章｜生成エージェント（generator.py）
- **映像**：`generator.py` を実装しながら、articleの考え方を口頭で実演
- **ステップ**
  1. `load_dotenv` と `ChatOpenAI` 初期化
  2. `_build_prompt` で初回と再生成のプロンプトを分岐
  3. `_invoke_llm`, `generate_weekly_report`, `regenerate_weekly_report` を実装
- **セリフ**：「初回は網羅性を重視、再生成は指摘反映にフォーカス。iterationでモードを切り替えます。」
- **画面演出**：VS Code splitでプロンプトの差分をハイライト。

---

## 14:30〜17:00　第6章｜単体評価ノード（evaluator.py）
- **映像**：`evaluator.py` を実装。スコア抽出の正規表現を入力
- **解説**
  - 「コメントだけでは制御できないので、Score: 0-100を強制」
  - `_parse_score` で0〜100にクリップ
  - `evaluate_report_file` に触れて CLI `evaluate` を実演する伏線
- **操作**：`uv run python -m cli evaluate report/sample.md` 風のダミー実行（ダミーの結果を口頭で説明）。

---

## 17:00〜20:00　第7章｜複数評価（multi_evaluator.py）
- **映像**：`multi_evaluator.py` でROLE定義→ループ処理を実装
- **セリフ要旨**
  1. 「tech / manager / writer の3ロール、それぞれ重み付き」
  2. 「`_evaluate_by_role` で独立実行→Stateにフィードバックを蓄積」
  3. 「平均スコアを算出し、ログでACCEPT/REJECTを宣言」
- **演出**：ターミナルに模擬ログ `[Review:tech] Score: 72` を走らせる（テキスト貼り付けでもOK）。

---

## 20:00〜23:30　第8章｜LangGraph構築（build_graph.py）
- **映像**：`build_graph.py` を一気に書き上げる。右側にarticleのMermaidを表示
- **実装順**
  1. `StateGraph` のインポートとノード登録
  2. `should_continue` 関数で `approve / stop / regenerate` を返す
  3. `graph.add_conditional_edges("evaluate", …)` で分岐設定
  4. `_save_report` で `report/weekly-report-YYYY_MM_DD_hh-mm.md` を保存
  5. `run_graph` で初期Stateを用意し `graph.invoke`
- **セリフ**：「条件分岐はノード内部ではなくGraph側に置く。だから設計図のままコードになる。」

---

## 23:30〜25:00　第9章｜main.pyと実行デモ
- **映像**：`main.py` を数行で書き、CLIを実行
- **デモ手順**
  1. `uv run main.py generate --since "last monday"` を実行
  2. ログで `[1/3] Generate...` → `[Review:tech] Score: 72` → `→ REJECT`
  3. 2回目で `→ ACCEPT` するまでをノーカットで見せる（APIコール時間は早送り可）
  4. `cat report/weekly-report-****.md` で出力例を表示
- **セリフ**：「ログ自体がLangGraphの遷移。何回目で合格したかが丸わかり。」

---

## 25:00〜27:00　第10章｜応用アイデアと締め
- **映像**：スライドで「PR説明文／議事録／提案書」アイコンを順に表示
- **セリフ**  
  - 「Stateを差し替えるだけでPR説明文や議事録にも流用できます。」
  - 「評価軸を決めるのが人間の仕事。LangGraphはそれを忠実に回す装置。」
  - 「次回はSlack通知や部分合格（最低点ガード）を追加していきます。」
- **CTA**：「概要欄のリポジトリとサンプル.envを使って、あなたの評価フローをLangGraphに落とし込んでみてください。質問はコメントへ！」

---

## プロダクションTips
- 章タイトルのテロップには article.md と同じ番号を表示して視聴者が資料と同期しやすくする
- コーディング画面はNeovim/VS Codeどちらでも良いが、差分がわかるようにサイドバーを開いたまま進める
- LLMコールは事前にキャッシュしたレスポンスを使い、録画時は `.env` を黒塗り
- ログ撮影時に `uv run main.py generate` が長引く場合は速度調整で 1.5x にするが、REJECT→REGENERATEの切替瞬間だけは等速で残す
