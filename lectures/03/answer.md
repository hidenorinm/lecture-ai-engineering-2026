# 第3回 解答

## 演習

- 第1回（素のLLM）とエージェントの回答の違い：
  - 同じモデルと同じ質問で比較。
  - 第1回の app.ask は「講座の内容は把握していない」と答え、正解を出せなかった。
  - 第3回の app.agent は、search_glossary で用語集を検索してから、基礎・実装・発展の3段階、どれか1つで完了、原則として採点しない、と data/glossary.json の homework-levels の定義どおりに答え、最後に「関係する回: 第1回」を示した。
  - モデルは同じなので、差を生んだのはツールとループ（ハーネス）機能と考察。入力トークンは約50倍に増えていた。
- `--trace` で見えたツール呼び出し（ツール名と引数）：
  - 「3レベル」：search_glossary({"query": "3レベル"}) の1回
  - 「LoRA とQLoRAの違いは？」：search_glossary({"query": "LoRA"}) と search_glossary({"query": "QLoRA"}) を1回の応答でまとめて依頼
  - 「第2回の内容から確認問題を1問出して」：make_quiz({"lecture": 2}) → search_glossary({"query": "ファインチューニング"}) の順
- 1つの質問での LLM 呼び出し回数（`requests`）：
  - 「3レベル」2回、「LoRA と QLoRA」2回（tool_calls=2）、確認問題 3回（tool_calls=2）
  - 互いの結果を使わない検索はまとめて呼ばれて回数が増えず、前の結果を使う呼び出しは順番になって回数が増えた。
- 追加したツールと、docstring に書いた説明：
  - make_quiz(lecture: int) -> str：用語集から指定した回の用語を1つ選び、{"question": "「用語」の意味は？", "answer": 定義} を JSON で返す。該当する用語が無い回（0 や 99）は「第N回の用語はありません。」を返す（pytest がダミー引数 0 で全ツールを呼ぶため）。
  - docstring：「指定した回の用語から確認問題を1問作り、問題と答えを返す。確認問題・復習問題を求められたときに使う。lecture は回の番号（1始まりの整数）。」
  - INSTRUCTIONS を変えずに、docstring だけで make_quiz が選ばれた。一方で、INSTRUCTIONS の「必ず search_glossary で確認する」に従って同じ用語を検索し直し、呼び出しが1回増えた。また、問題と答えを同時に表示した。
- 補足：
  - Gemini API が使えないため、Claude API（claude-haiku-5-5）で実施した。AIE_MODEL が claude で始まるときだけ Claude を使う分岐を app/config.py と app/agent.py に追加した。pydantic-ai-slim 2.57.0 と anthropic 2.x は組み合わせると動かないため、anthropic を 1.17.0 に固定した。

## 宿題

- 取り組んだレベル：基礎 / 実装 / 発展
- やったこと：
- 結果：
- 気づき・疑問：
