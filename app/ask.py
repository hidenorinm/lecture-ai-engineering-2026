"""第1回: 素のLLMに1回だけ質問するスクリプト（Claude API 版）。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 質問を省略すると、講座に固有の質問をする
    uv run python -m app.ask --chat     # 会話履歴を保って続けて質問（空行か exit で終了）

    # モデルを切り替えるとき
    AIE_MODEL=claude-sonnet-5-5 uv run python -m app.ask "LoRAとは何ですか？"

ツールも会話履歴も持たない「素の」呼び出し。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）

変更点（自分の fork のみ）:
    Gemini API のプロジェクトが停止されたため、Claude API で呼び出すように書き換えた。
    API キーは環境変数 ANTHROPIC_API_KEY（Codespaces secret）から読む。
    モデルは環境変数 AIE_MODEL で切り替える（未設定なら claude-haiku-5-5）。
"""

import argparse
import os

import anthropic

from app.config import api_error_message

# 既定モデル。app/config.py の既定（Gemini）は使わず、ここで Claude のモデルを決める
DEFAULT_MODEL = "claude-haiku-5-5"
MODEL = os.getenv("AIE_MODEL", DEFAULT_MODEL)

# Claude API では出力の上限トークン数の指定が必須
MAX_TOKENS = 1024

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def get_api_key() -> str:
    """環境変数 ANTHROPIC_API_KEY を返す。未設定なら手順を表示して終了する。"""
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise SystemExit(
            "環境変数 ANTHROPIC_API_KEY が見つかりません。\n"
            "1. GitHub の Settings → Codespaces → Secrets に ANTHROPIC_API_KEY を登録し、\n"
            "   使う repository に自分の fork を選んでください。\n"
            "2. Codespaces を起動したあとに登録した場合は、Codespaces を再起動してください。\n"
            "   （左下の「Codespaces」→「Stop Current Codespace」→ 再度開く）"
        )
    return key


def ask(question: str, history: list[dict] | None = None) -> str:
    """質問して回答を返す。history を渡すと会話履歴として使い、成功した回だけ追記する。"""
    client = anthropic.Anthropic(api_key=get_api_key())
    messages = (history or []) + [{"role": "user", "content": question}]
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=messages,
    )

    # 第1回 演習: 入力トークン数と出力トークン数を表示する
    usage = response.usage
    print(f"[tokens] 入力: {usage.input_tokens} / 出力: {usage.output_tokens}\n")

    # 応答は複数のブロックで返ることがあるので、テキストだけをつなげる
    text = "".join(block.text for block in response.content if block.type == "text")

    # 成功した回だけ履歴に残す（例外のときはここに到達しない）
    if history is not None and text:
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": text})
    return text


def chat(first_question: str | None = None) -> None:
    """会話履歴を保ったまま続けて質問する。空行か exit で終了。"""
    history: list[dict] = []
    question = first_question
    try:
        while True:
            if question is None:
                try:
                    question = input("> ").strip()
                except EOFError:
                    break
            if not question or question.lower() == "exit":
                break
            try:
                print(ask(question, history))
                print()
            except anthropic.APIStatusError as e:
                print(api_error_message(e.status_code, e.message))
            except anthropic.APIConnectionError:
                print("Claude API に接続できませんでした。ネットワークを確認してください。")
            question = None
    except KeyboardInterrupt:
        # Ctrl-C は静かに終了する（プロンプトの行を閉じるため改行だけ出す）
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?", default=None)
    parser.add_argument("--chat", action="store_true", help="会話履歴を保って続けて質問する")
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    if args.chat:
        print("会話モード: 空行か exit で終了します。\n")
        chat(args.question)
        return

    question = args.question or DEFAULT_QUESTION
    print(f"[質問] {question}\n")
    try:
        print(ask(question))
    except anthropic.APIStatusError as e:
        print(api_error_message(e.status_code, e.message))
        raise SystemExit(1)
    except anthropic.APIConnectionError:
        print("Claude API に接続できませんでした。ネットワークを確認して再実行してください。")
        raise SystemExit(1)


if __name__ == "__main__":
    main()