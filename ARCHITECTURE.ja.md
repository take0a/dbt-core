dbt の中核機能は、SQL のコンパイルと実行です。ユーザーは、SQL ファイルと YAML ファイルで定義された dbt リソース（モデル、テスト、シード、スナップショットなど）のプロジェクトを作成し、dbt を呼び出して関連するビューやテーブルを作成、更新、またはクエリします。現在、dbt は Jinja2 を多用して SQL のテンプレート化を可能にし、プロジェクト内のすべてのリソースから DAG (有向非巡回グラフ) を構築しています。ユーザーは、「パッケージ」と呼ばれる他のプロジェクトからリソース（Jinja マクロを含む）をインストールすることで、プロジェクトを拡張することもできます。

## dbt-core

リポジトリ内の Python コードのほとんどは `core/dbt` ディレクトリ内にあります。
- [`単一の Python ファイル`](core/dbt/README.md): 'compilation.py' や 'exceptions.py' などの個別のファイルが多数あります。

core/dbt の主なサブディレクトリ:
- ~~[`adapters`](core/dbt/adapters/README.md): データベース間で異なる可能性のある動作の基本クラスを定義します。~~
- [`clients`](core/dbt/clients/README.md): 依存関係 (agate、jinja) またはオペレーティングシステム間のインターフェースを作成します。
- [`config`](core/dbt/config/README.md): 接続プロファイル、プロジェクトファイル、および Jinja マクロからユーザーが指定した構成を調整します。
- [`context`](core/dbt/context/README.md): dbt 固有の Jinja 機能を構築して公開します。
- [`contracts`](core/dbt/contracts/README.md): dbt が作成および検証することを想定している Python オブジェクト (データクラス) を定義します。
- [`deps`](core/dbt/deps/README.md): パッケージのインストールと依存関係の解決を行います。
- [`events`](core/dbt/events/README.md): イベントのログ記録
- [`graph`](core/dbt/graph/README.md): プロジェクトリソースの `networkx` DAG を生成し、ユーザーが指定した条件に基づいてリソースを選択します。
- [`include`](core/dbt/include/README.md): スタータープロジェクトのスキャフォールドをセットアップします。
- [`parser`](core/dbt/parser/README.md): プロジェクトファイルの読み取り、検証、Python オブジェクトの構築を行います。
- [`task`](core/dbt/task/README.md): dbt が起動時に実行できるアクションを定義します。

レガシーテストは「test」ディレクトリにあります。
- [`unit tests`](core/dbt/test/unit/README.md): ユニットテスト
- [`integration tests`](core/dbt/test/integration/README.md): 統合テスト

### dbt の呼び出し

「タスク」はトップレベルの dbt コマンドにマッピングされます。つまり、`dbt run` => task.run.RunTask などです。一部は抽象基底クラスに近いもの（GraphRunnableTask など）もありますが、task 以外の具体的な型はすべてタスクにマッピングされます。現在、一度に実行されるのは 1 つだけです。タスクは「ランナー」を起動し、それらは並列に実行されます。並列処理は GraphRunnableTask 内のスレッドプールによって管理されます。

core/dbt/task/docs/index.html
これはドキュメント Web サイトのコードです。dbt-docs リポジトリから取得され、リリースがパッケージ化される際に生成されます。

## アダプタ

dbt は、アダプタプラグインパターンを使用して、さまざまなデータベース、ウェアハウス、クエリエンジンなどへのサポートを拡張します。
注: dbt-postgres は以前は dbt-core に存在していましたが、現在は [dbt-adapters リポジトリ](https://github.com/dbt-labs/dbt-adapters/tree/main/dbt-postgres) にあります。

各アダプタは、Python、Jinja2、SQL を組み合わせて構築されています。アダプタコードでは、SQL 機能のモジュール化されたチャンクをラップし、デフォルトの実装を定義し、プラグインによるオーバーライドを可能にするために、Jinja2 を多用しています。

各アダプタプラグインはスタンドアロンの Python パッケージで、以下のものが含まれています。

- `dbt/include/[name]`: YAML および SQL ファイルで構成される「サブグローバル」dbt プロジェクト。アダプタでサポートされている SQL 構文を使用するために Jinja マクロを再実装します。
- `dbt/adapters/[name]`: dbt-core で定義されている基本アダプタクラスを継承し、必要に応じて再実装する Python モジュール。
- `setup.py`

Postgres アダプタコードは最も中心的なコードであり、その実装の多くは dbt-core グローバルプロジェクトで定義されているデフォルトとして使用されます。データテクノロジーと Postgres の距離が遠いほど、アダプタプラグインの再実装が必要になる可能性があります。

## dbt のテスト

[`test/`](test/) サブディレクトリには、オープンなプルリクエストに対する継続的インテグレーションチェックとして実行される単体テストと統合テストが含まれています。単体テストでは、特定の Python 関数のモック入力と出力をチェックします。統合テストでは、実際のアダプタ (Postgres、Redshift、Snowflake、BigQuery) に対してエンドツーエンドの dbt 呼び出しを実行し、結果が期待どおりであることを確認します。ローカル開発およびテスト環境の構築手順については、[コントリビューションガイド](CONTRIBUTING.md) をご覧ください。

## その他すべて

- [docker](docker/): すべての dbt バージョンは DockerHub で Docker イメージとして公開されています。このサブフォルダには、`Dockerfile` (定数) と `requirements.txt` (バージョンごとに 1 つ) が含まれています。
- [etc](etc/): README 用のイメージ
- [scripts](scripts/): テスト、リリース、JSON スキーマの生成のためのヘルパースクリプトです。これらは dbt のディストリビューションには含まれておらず、厳密にテストもされていません。dbt のメンテナー向けの便利なツールとして提供されています :)
