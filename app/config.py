"""講座全体で共通の設定。

APIキーやモデル名はコードに書かず、環境変数から読み込む。
"""

import os

# 既定モデル。環境変数 AIE_MODEL を設定すると切り替えられる。
#   例: export AIE_MODEL=gemini-3.5-flash
#   "claude" で始まる名前（例: claude-haiku-5-5）なら Claude を使う（ANTHROPIC_API_KEY が必要）
DEFAULT_MODEL = "gemini-3.5-flash-lite"
MODEL = os.getenv("AIE_MODEL", DEFAULT_MODEL)


def api_error_message(status: int, detail: str = "") -> str:
    """HTTPステータスコードを、受講生向けの日本語の説明にする（ask.py と agent.py で共用）。"""
    if status == 429:
        return "レート制限に達しました。1分ほど待ってから再実行してください。"
    if status == 503:
        return "モデルが混み合っています（503）。少し待ってから再実行してください。"
    if status in (400, 401, 403, 404):
        return f"APIキーかモデル名に問題があります（{status}）: {detail}"
    return f"APIエラー（{status}）: {detail}"


def is_claude(model: str) -> bool:
    """モデル名が "claude" で始まるなら Claude（Anthropic）、それ以外は Gemini として扱う。"""
    return model.startswith("claude")


def get_api_key(model: str = "") -> str:
    """モデルに合う API キーを環境変数から返す。未設定なら手順を表示して終了する。

    Claude のモデル名なら ANTHROPIC_API_KEY、それ以外（引数なしを含む）は GEMINI_API_KEY。
    """
    name = "ANTHROPIC_API_KEY" if is_claude(model) else "GEMINI_API_KEY"
    key = os.getenv(name)
    if not key:
        raise SystemExit(
            f"環境変数 {name} が見つかりません。\n"
            f"1. GitHub の Settings → Codespaces → Secrets に {name} を登録し、\n"
            "   使う repository に自分の fork を選んでください。\n"
            "2. Codespaces を起動したあとに登録した場合は、Codespaces を再起動してください。\n"
            "   （左下の「Codespaces」→「Stop Current Codespace」→ 再度開く）"
        )
    return key
