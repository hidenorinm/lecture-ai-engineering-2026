# 第6回 解答

## 演習

<!-- [tool call] の行は、表示された行をそのまま貼り付けてください。終わらなかった STEP は、空欄のままでかまいません。 -->

- STEP 1 のツールの名前：glossary_search_glossary
- STEP 2 の [tool call]：glossary_search_glossary({"query": "3レベル"})
- STEP 3 の [tool call]：fetch_fetch({"url": "https://modelcontextprotocol.io/"})
- STEP 4 の [tool call]：aws_aws___search_documentation({"search_phrase": "Amazon S3 versioning", "topics": ["general"], "limit": 3})、glossary_search_glossary({"query": "S3 バージョニング"})（1回目の応答で2つを同時に呼んだ）
- 気づき・疑問：
  - 環境：Gemini API が使えないため、app/mcp_agent.py の build_model() に Claude を使う分岐を足し、claude-haiku-5-5 で実行した（pyproject.toml と uv.lock に anthropic==1.17.0 を追加）
  - app.agent と app.mcp_agent のツール一覧は、どちらも名前・説明文・引数の同じ形だった。MCP 版は名前の前に glossary_ が付き、引数に "title": "Query" が加わっていた
  - fetch の説明文には、モデルに向けた文（インターネットにアクセスできるようになった、という内容）が含まれていた。外部のサーバーの説明文も、そのままモデルに渡る
  - fetch は取得の前に robots.txt を確認し、転送先のページをたどって取得した
  - 入力トークンは STEP 2 が 1,713（ツール1個）、STEP 3 が 3,931（2個とページ本文）、STEP 4 が 10,901（7個と検索結果）と増えた
  - STEP 4 の出典は、公式のユーザーガイドではなく AWS のブログ記事だった

## 宿題

<!-- 基礎・実装・発展のどれか1つに取り組めば完了です。 -->

### 基礎

- 取り組んだレベル：基礎
- やったこと：app/mcp_server.py の TODO の下に server.tool()(tools.get_lecture_summary) を1行足した。エージェント側（app/mcp_agent.py・app/mcp_servers.json）は変えていない（git status で app/mcp_server.py だけが変わったことを確認）
- 結果：
  - --list-tools の一覧に glossary_get_lecture_summary が増え、ツールが7個から8個になった
  - 「第2回では何を学びますか？」の [tool call]：glossary_get_lecture_summary({"lecture": 2})。search_glossary は呼ばれず、モデル応答は2回、入力 9,743 tokens / 出力 620 tokens
  - 回答は第2回の内容（LoRA、Colab での演習、FAQ にない質問への答え方は学習で直らないこと）と合っていた
  - uv run pytest -q は 21 件すべて成功
- 気づき・疑問：
  - エージェントは起動のたびにサーバーへツールの一覧を問い合わせるので、サーバー側を変えるだけで新しいツールが使えた
  - 「第2回」という質問に対して、モデルは引数に数値の 2 を入れていた。引数の型は関数の型ヒントから作られている
  - 指示文の「回の内容を聞かれたら get_lecture_summary を使う」のとおり、用語集の検索は呼ばれなかった
  - 入力トークンは演習の STEP 2（ツール1個、1,713）より大きく増えた

### 実装

- 取り組んだレベル：実装
- やったこと：第3回（lec03）で作った make_quiz を app/tools.py に移し、app/mcp_server.py で公開した。用語がない回のときのメッセージを、「第N回の用語はありません。」から、理由と指定できる回を示す形に直した。指定できる回の一覧は、用語集から毎回作る（第5回の用語は用語集にないので、一覧に入らない）
- 結果：
  - 一覧に glossary_make_quiz が増え、ツールが9個になった
  - 「第99回のクイズを作って」の [tool call]：glossary_make_quiz({"lecture": 99})
  - （最初の版：文字列で返した）[tool return]：第99回の確認問題は作れません。用語集に第99回の用語がないためです。lecture には、用語がある回の番号（第1回、第2回、第3回、第4回、第6回）のどれかを指定してください。
  - モデルは別の回で呼び直さず、指定できる回の一覧を示して「どの回のクイズを作りましょうか」と聞き返した。モデル応答は2回、入力 9,324 tokens / 出力 191 tokens
  - uv run pytest -q は 21 件すべて成功
- 気づき・疑問：
  - メッセージに理由と指定できる回を書いたので、モデルはそれをそのまま使って、ユーザーに選んでもらう形で答えた
  - モデルは、呼ぶ前に範囲を自分で確かめず、聞かれた回のままツールを呼んだ。範囲の確認はツール側に任せる形になる
- 追加で試したこと（範囲外のときに、エラーとして返す）：
  - ふつうの例外（ValueError）で返すと、モデルに届いた文は「Error executing tool make_quiz」だけで、理由と直し方は消えた（MCP の SDK が、予期しない例外の中身をサーバーの記録にだけ残すため）。モデルは理由が分からないまま make_quiz をもう一度呼んで再び失敗し、Pydantic AI の呼び直しの上限（1回）を超えて、回答を返さずに実行全体が止まった（exceeded max retries count of 1）。2回目の引数は、止まったため表示されなかった
  - mcp の ToolError で返すと、isError: true で、メッセージの全文が届いた。最終的にこの形にした
  - ToolError の版で同じ質問をすると、trace は [tool error] になった。モデルの動きは文字列で返したときと同じで、別の回で呼び直さず、指定できる回を示して聞き返した（モデル応答2回、入力 9,354 tokens / 出力 255 tokens）。どちらも1回ずつの結果
  - 今回の MCP の Python SDK では、エラーの直し方を書いても、ふつうの例外ではモデルに届かない。届けたいときは、意図して出すエラー（ToolError）を使う必要がある

