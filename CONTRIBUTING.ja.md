# `dbt-core` への貢献

`dbt-core` はオープンソースソフトウェアです。コミュニティメンバーの皆様が問題を報告し、フィードバックを提供し、[ナレッジループへの貢献](https://www.getdbt.com/dbt-labs/values/)によって、今日の姿が実現しました。経験豊富なオープンソースコントリビューターの方でも、初めてコミッターとして参加される方でも、コード、ドキュメント、アイデア、あるいは問題ステートメントなど、このプロジェクトへの貢献を歓迎し、奨励いたします。

1. [About this document](#about-this-document)
2. [Getting the code](#getting-the-code)
3. [Setting up an environment](#setting-up-an-environment)
4. [Running dbt-core in development](#running-dbt-core-in-development)
5. [Testing dbt-core](#testing)
6. [Debugging](#debugging)
7. [Adding or modifying a changelog entry](#adding-or-modifying-a-changelog-entry)
8. [Submitting a Pull Request](#submitting-a-pull-request)
9. [Troubleshooting Tips](#troubleshooting-tips)

## About this document

`dbt-core` の継続的な開発に貢献する方法は数多くあります。例えば、ディスカッションや課題への参加などです。まずは、より詳細なドキュメントである [オープンソース貢献者への期待](https://docs.getdbt.com/docs/contributing/oss-expectations) をお読みください。

このドキュメントの残りの部分は、`dbt-core` (このリポジトリ) へのコード変更の貢献に関する、より詳細なガイドです。`dbt-core` の使用方法をガイドするものではなく、一部の内容は Python 開発 (virtualenvs、`pip` など) に関する一定の知識を前提としています。このガイド内の特定のコードスニペットは、macOS または Linux を使用しており、コマンドラインの操作に慣れていることを前提としています。

お困りの際は、お気軽にお問い合わせください。[dbt コミュニティ Slack](https://community.getdbt.com) の `#dbt-core-development` チャンネルまでご連絡ください。

### 注意事項

- **アダプタ:** 問題またはコード変更の提案は、特定の[データベースアダプタ](https://docs.getdbt.com/docs/available-adapters)に関連していますか？ もしそうであれば、そのアダプタのリポジトリで問題、プルリクエスト、ディスカッションを開いてください。
- **CLA:** `dbt-core`にコードを投稿する方は、[貢献者ライセンス契約](https://docs.getdbt.com/docs/contributor-license-agreements)に署名する必要があります。CLAに署名できない場合、`dbt-core`のメンテナーは残念ながらあなたのプルリクエストをマージできません。ディスカッションへの参加、問題の報告、既存の問題へのコメントを歓迎します。
- **ブランチ:** コミュニティ貢献者からのすべてのプルリクエストは、`main`ブランチ（デフォルト）を対象にする必要があります。変更が、既にリリースされている（または既にリリース候補となっている）dbt のマイナーバージョンへのパッチとして必要な場合、メンテナーが PR の変更を関連する「最新」リリースブランチ（`1.0.latest`、`1.1.latest`、...）にバックポートします。問題修正がリリースブランチに適用される場合は、まず開発ブランチにコミットし、次にリリースブランチにコミットする必要があります（まれに、リリースブランチの修正が `main` に適用されない場合があります）。
- **リリース**: Core の新しいマイナーバージョンをリリースする前に、一連のアルファ版とリリース候補版を用意し、ユーザー（特に dbt Labs の従業員）が新しいバージョンを実際の環境でテストできるようにします。これは重要な品質保証手順であり、新しいコードをさまざまな複雑なデプロイメントに公開することで、正式リリース前にバグが明らかになることがあります。リリースには、[サポートされているインストール方法](https://docs.getdbt.com/docs/core/installation-overview#install-dbt-core) からアクセスできます。

## Getting the code

### Git のインストール

`dbt-core` ソースコードをダウンロードして変更するには、`git` が必要です。macOS では、[Xcode](https://developer.apple.com/support/xcode/) をインストールするのが Git をダウンロードする最適な方法です。

### 外部コントリビューター

GitHub の `dbt-labs` 組織のメンバーでない場合は、`dbt-core` リポジトリをフォークすることで `dbt-core` に貢献できます。フォークの詳細な概要については、[GitHub のフォークに関するドキュメント](https://help.github.com/en/articles/fork-a-repo) をご覧ください。簡単に説明すると、以下の手順が必要です。

1. `dbt-core` リポジトリをフォークする
2. フォークしたリポジトリをローカルにクローンする
3. 提案する変更のための新しいブランチをチェックアウトする
4. フォークしたリポジトリに変更をプッシュする
5. フォークしたリポジトリから `dbt-labs/dbt-core` に対してプルリクエストを作成する

### dbt Labs の貢献者

GitHub の `dbt-labs` 組織のメンバーであれば、`dbt-core` リポジトリへのプッシュアクセス権があります。`dbt-core` をフォークして変更を加えるのではなく、リポジトリをクローンし、新しいブランチをチェックアウトして、そのブランチに直接プッシュするだけです。

## Setting up an environment

ローカル開発に役立つツールがいくつかあります。これは `dbt-core` 開発に関連するリストですが、これらのツールの多くはオープンソースの Python プロジェクトで広く使用されています。

### ツール

`dbt-core` の開発とテストで使用されるツールは次のとおりです。

- [`tox`](https://tox.readthedocs.io/en/latest/) は、Python の複数のバージョン間で仮想環境を管理します。現在、Python 3.8、3.9、3.10、3.11 の最新パッチリリースをターゲットにしています。
- [`pytest`](https://docs.pytest.org/en/latest/) : テストの定義、検出、実行
- [`flake8`](https://flake8.pycqa.org/en/latest/) : コードリンティング
- [`black`](https://github.com/psf/black) : コードフォーマット
- [`mypy`](https://mypy.readthedocs.io/en/stable/) : 静的型チェック
- [`pre-commit`](https://pre-commit.com) : これらのチェックを簡単に実行
- [`changie`](https://changie.dev/) : マージの競合なしで変更ログエントリを作成
- [`make`](https://users.cs.duke.edu/~ola/courses/programming/Makefiles/Makefiles.html) を使用すると、複数のセットアップ手順やテスト手順を組み合わせて実行できます。`make` の仕組みを本当に理解している人は誰もいませんので、心配する必要はありません。Makefile は非常にシンプルなものを目指しています。
- [GitHub Actions](https://github.com/features/actions) を使用すると、`dbt-core` リポジトリに PR をプッシュした後、テストとチェックを自動化できます。

`dbt-core` への効果的な貢献にこれらのツールの深い理解は必要ありませんが、各ツールについて詳しく知りたい場合は、添付のドキュメントを確認することをお勧めします。

#### 仮想環境

`dbt-core` でコードを開発する際は、仮想環境の使用を強くお勧めします。`dbt-core` リポジトリのルートに仮想環境を作成することをお勧めします。新しい仮想環境を作成するには、次のコマンドを実行します。

```sh
python3 -m venv env
source env/bin/activate
```

これにより、新しい Python 仮想環境が作成され、アクティブ化されます。

#### Docker と `docker-compose`

Docker と `docker-compose` はどちらもテストに使用されます。お使いの OS に応じた具体的な手順については、[こちら](https://docs.docker.com/get-docker/) をご覧ください。


#### Postgres (オプション)

テストや、このドキュメントの後の例では、データベースにアクセスして何が起こっているかを確認できるように、`psql` が使えるようにしておくと便利です。macOS では [homebrew](https://brew.sh/)、Linux ではパッケージマネージャーを使用することをお勧めします。Postgres クライアントは任意のバージョンをインストールできます。macOS では、homebrew をセットアップして次のコマンドを実行できます。

```sh
brew install postgresql
```

## Running `dbt-core` in development

### インストール

まず、[環境の設定](#環境の設定)の説明に従って `virtualenv` が設定されていることを確認してください。また、`pip install --upgrade pip` で最新バージョンの pip がインストールされていることを確認してください。次に、`dbt-core` (および依存関係) をインストールします。

```sh
make dev
```

または、代わりに：

```sh
pip install -r dev-requirements.txt -r editable-requirements.txt
pre-commit install
```

この方法でインストールすると、ソース コードのローカル コピーに加えた変更は、次回の `dbt` 実行時にすぐに反映されます。

### `dbt-core` の実行

仮想環境を有効にすると、`dbt` スクリプトは、マシンにクローンしたソースコードを参照するはずです。`which dbt` を実行することでこれを確認できます。このコマンドは、仮想環境内の実行ファイルへのパスを表示します。

ターゲットデータベースに接続するために、必要に応じて [プロファイル](https://docs.getdbt.com/docs/configure-your-profile) を設定してください。ローカルの Postgres インスタンス、または必要に応じてデータウェアハウス内の特定のテストサンドボックスを参照する新しいプロファイルを追加することをお勧めします。統合テストを実行する前に、必ずプロファイルを作成してください。

## Testing

コード変更が期待どおりに動作していることを手動でテストできるようになったら、既存の自動テストを実行するだけでなく、新しいテストも追加することが重要です。これらのテストにより、以下の点が保証されます。
- コード変更によって、既存の機能が予期せず中断されないこと
- コード変更によって、既知のすべてのエッジケースに対応できること
- 追加する機能が将来も動作し続けること

`dbt-core` はさまざまなデータベースで動作しますが、テスト環境ですべてのデータベースの認証情報を提供する必要はありません。`dbt-core` のコード変更のほとんどは、Python と Postgres でテストできます。

### 初期設定

Postgres は、現在ほとんどの `dbt-core` 機能をテストするための最も簡単な方法を提供しています。実行速度も設定も最も簡単です。Postgres の統合テストを実行するには、テストデータベースを設定するという追加の手順が必要です。

```sh
make setup-db
```

または、代わりに：

```sh
docker-compose up -d database
PGHOST=localhost PGUSER=root PGPASSWORD=password PGDATABASE=postgres bash test/setup_db.sh
```

### テストコマンド

ローカルでテストを実行する方法はいくつかあります。

#### Makefile

Makefile には、一般的なテストスイートとコードチェックを実行するための複数のターゲットがあります。主なものは次のとおりです。

```sh
# Runs unit tests with py38 and code checks in parallel.
make test
# Runs postgres integration tests with py38 in "fail fast" mode.
make integration
```

> これらのmakeターゲットは、単体テスト/統合テスト、およびコード品質チェックのための事前コミット用に、最新バージョンの[`tox`](https://tox.readthedocs.io/en/latest/)がローカルにインストールされていることを前提としています。
> ただし、テスト実行にDockerコンテナを使用する場合は除きます。詳細については、`make help`を実行してください。

他のよく使われるテストスイートを確認するには、Makefile 内の他のターゲットを確認してください。

#### `pre-commit`

[`pre-commit`](https://pre-commit.com) は、フォーマットとリンティングのためのすべてのコードチェックを実行します。`make dev` を実行して、ローカル環境に `pre-commit` をインストールします（このコマンドは、Python 仮想環境をアクティブにした状態で実行することをお勧めします）。このコマンドは、black、mypy、flake8 を含むいくつかの pip 実行ファイルをインストールします。インストールが完了すると、linter ベースの make ターゲットや、適切なフォーマットとリンティングを保証する git pre-commit フックを使用できるようになります。

#### `tox`

[`tox`](https://tox.readthedocs.io/en/latest/) は、テスト実行に必要な仮想環境とインストール依存関係の管理を行います。また、テストを並列実行することも可能です。例えば、`tox -p` を実行することで、Python 3.8、Python 3.9、Python 3.10、Python 3.11 の単体テストを並列実行できます。また、`tox -e py38` を実行することで、特定の Python バージョンの単体テストを実行することもできます。これらのテストの設定は `tox.ini` にあります。

#### `pytest`

最後に、[`pytest`](https://docs.pytest.org/en/latest/) を使って、特定のテストまたはテストグループを直接実行することもできます。virtualenv をアクティブにし、dev 依存関係をインストールしておくと、次のようなことができます。

```sh
# run all unit tests in a file
python3 -m pytest tests/unit/test_invocation_id.py
# run a specific unit test
python3 -m pytest tests/unit/test_invocation_id.py::TestInvocationId::test_invocation_id
# run specific Postgres functional tests
python3 -m pytest tests/functional/sources
```

> 便利なコマンドライン オプションの概要については、[pytest の使用法ドキュメント](https://docs.pytest.org/en/6.2.x/usage.html) を参照してください。

### ユニットテスト、統合テスト、機能テスト？

テストを追加する際の一般的なルールを以下に示します。
* ユニットテスト (`tests/unit`) はデータベースにアクセスする必要はありません。「純粋な Python」テストはユニットテストとして記述する必要があります。
* 機能テスト (`tests/functional`) は、データベースとやり取りするすべてのテスト、つまりアダプタテストをカバーします。

## Debugging

1. `dbt run` のログには、スタックトレースやその他のデバッグエラー情報が含まれます（プロジェクトディレクトリの `logs/dbt.log` に保存されます）。
2. `ipdb` などのデバッガーを使ってみてください。pytest の場合: `--pdb --pdbcls=IPython.terminal.debugger:pdb`
3. 場合によっては、シングルスレッドでデバッグする方が簡単です: `dbt --single-threaded run`
4. Jinja マクロから print ステートメントを作成するには: `{{ log(msg, info=true) }}`
5. `{{ debug() }}` ステートメントを追加することもできます。これにより、マクロによって書き込まれた自動生成コードが表示されます。
6. dbt の「アーティファクト」は、dbt プロジェクトの ‘target’ ディレクトリに書き出されます。これらはフォーマットされていない JSON 形式であるため、読みにくい場合があります。次のようにフォーマットします:
> python -m json.tool target/run_results.json > run_results.json

### 開発のヒント集

* `mypy` を無効にする必要がある行がある場合は、行末に `# type: ignore` を追加してください。
* flake8 が実際には問題のない行に対してエラーメッセージを表示することがあります。その場合は、# noqa や # noqa: ANNN のように、その行にコメントを追加できます。ANNN は flake8 が発行するエラーコードです。
* `CProfile` の出力を収集するには、`-r` オプションと出力ファイル名を指定して dbt を実行します（例：`dbt -r dbt.cprof run`）。解析結果のプロファイルだけが必要な場合は、`dbt -r dbt.cprof parse` を実行できます。出力を表示するには、`pip` で `snakeviz` をインストールします。`snakeviz dbt.cprof` を実行すると、ブラウザウィンドウに出力が表示されます。

## Adding or modifying a CHANGELOG Entry

`CHANGELOG` エントリの生成には [changie](https://changie.dev) を使用します。**注意:** `CHANGELOG.md` を直接編集しないでください。変更内容は失われます。

[`changie` をインストール](https://changie.dev/guide/installation/) の手順に従って、システムにインストールしてください。

changie がインストールされ、新機能の PR が作成されたら、以下のコマンドを実行するだけで、changie が changelog エントリの作成プロセスを案内します。

```shell
changie new
```

作成されたファイルをコミットすれば、変更ログエントリの作成は完了です！

既に開発中の機能に貢献する場合は、dbt/.changes/unreleased/ にある変更に関連する changie yaml ファイルを変更します。このファイルの場所がわからない場合は、プルリクエストのディスカッション内で質問してください。

変更がどの `dbt-core` バージョンに反映されるかを気にする必要はありません。`changie` で変更ログエントリを作成し、`main` ブランチに対して PR を開くだけです。マージされたすべての変更は、`dbt-core` の次のマイナーバージョンに含まれます。Core メンテナーは、古いマイナーバージョンにパッチを適用するために、特定の変更を「バックポート」する場合があります。その場合、メンテナーは PR をマージした後、新しいバージョンの `dbt-core` をリリースする前に、そのバックポートを処理します。

## Submitting a Pull Request

プルリクエストを開くことで、現在の開発ブランチ「main」にコードをマージできます。提案が適切な方向に向かっていると思われる場合、「dbt-core」のメンテナーがPRをトリアージし、「ready_for_review」としてラベル付けします。この時点で、2名のコードレビュアーが割り当てられ、約1週間以内にPRの更新に対応することを目指します。レビュアーは、スタイルや明瞭性に関するコードの修正を提案したり、ユニットテストや統合テストの追加を依頼したりすることもあります。これらは良いことです！少しの協力があれば、誰でも高品質なコードを提供できると信じています。マージされると、あなたの貢献は「dbt-core」の次のリリースで利用できるようになります。

自動テストはGitHub Actionsを介して実行されます。初めてコントリビューターになる場合は、すべてのテスト（コードチェックとユニットテストを含む）でメンテナーの承認が必要になります。「dbt-core」リポジトリに変更を加えると、Postgresに対する統合テストが実行されます。 dbt Labs は、他のアダプタのリポジトリへの PR をトリガーとして他のアダプタへの変更をテストするための CI 環境も提供しています。また、最新の `dbt-core` コード変更に合わせて各アダプタの定期的なメンテナンスチェックも提供しています。

すべてのテストに合格し、PR が承認されると、`dbt-core` のメンテナーが変更内容をアクティブな開発ブランチにマージします。これで完了です！開発を楽しみましょう :tada:

## Troubleshooting Tips

コンテンツライセンス契約の自動チェックボットが、ユーザーのエントリをリスト内に見つけられない場合があります。強制的に再実行する必要がある場合は、プルリクエストのコメントに `@cla-bot check` を追加してください。
