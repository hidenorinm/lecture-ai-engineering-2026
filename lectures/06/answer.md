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
