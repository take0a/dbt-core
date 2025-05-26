# dbt/artifacts

## 概要

このディレクトリは、`dbt-core` 内部の他の部分から独立した（かつ上流に位置する）軽量モジュールです。

主な役割は、dbt が実行時に JSON ファイルとして書き込むバージョン管理されたアーティファクトスキーマを表すシンプルなデータクラスを定義することです。

将来的には、このモジュールはスタンドアロンパッケージ（例：`dbt-artifacts`）としてリリースされ、dbt アーティファクトの安定したプログラム解析をサポートする予定です。

`dbt/artifacts` は、アーティファクトの「スキーマ」と「リソース」に分かれています。スキーマは最終的にシリアル化されたアーティファクトオブジェクトを表し、リソースはそれらのスキーマ内のより小さなコンポーネントを表します。

### dbt/artifacts/schemas

`dbt/artifacts/schema` 配下のスキーマの各メジャーバージョンは、対応する `dbt/artifacts/schema/<artifact-name>/v<version>` ディレクトリに定義されています。`dbt/artifacts` より前のアーティファクトスキーマは常にインプレースで変更されていたため、古いアーティファクトにはクラス定義が欠落しています。

現在、`dbt/artifact/schemas` には 4 つのアーティファクトスキーマが定義されています。

| Artifact name | File             | Class                            | Latest definition                 |
|---------------|------------------|----------------------------------|-----------------------------------|
| manifest      | manifest.json    | WritableManifest                 | dbt/artifacts/schema/manifest/v12 |
| catalog       | catalog.json     | CatalogArtifact                  | dbt/artifacts/schema/catalog/v1   |
| run           | run_results.json | RunResultsArtifact               | dbt/artifacts/schema/run/v5       |
| freshness     | sources.json     | FreshnessExecutionResultArtifact | dbt/artifacts/schema/freshness/v3 |


### dbt/artifacts/resources

既存のリソースはすべて `dbt/artifacts/resources/v1` の下に定義されています。

## dbt/artifacts に変更を加える

### すべての変更

すべてのフィールドへの変更には、[dbt-jsonschema](https://github.com/dbt-labs/dbt-jsonschema) を手動で更新し、ライブチェックが引き続き機能するようにする必要があります。

### 非破壊的な変更

最新のメジャーバージョン（マイナーバージョンまたはパッチバージョン）に対して、自由に増分的な非破壊的な変更をインプレースで行うことができます。完全な前方互換性と後方互換性が確保される変更は以下のみとなります。
* デフォルトを設定した新しいフィールドの追加
* デフォルトを設定したフィールドの削除これはシリアライズとデシリアライズに関しては互換性がありますが、それでも予期せぬ動作につながる可能性があります。
* フィールドの存在に依存するアーティファクトコンシューマーの場合（例：`manifest["deleted_field"]` は、アクセスが安全に実装されていない限り動作を停止します）。
* 削除されたフィールドの値に依存する古いコード（例：dbt-core 内）は、新しいスキーマからインスタンス化される際にデフォルト値のみが設定されるため、予期せぬ動作を引き起こす可能性があります。

このような軽微で互換性に影響のない変更は、[tests/unit/artifacts/test_base_resource.py::TestMinorSchemaChange](https://github.com/dbt-labs/dbt-core/blob/main/tests/unit/artifacts/test_base_resource.py) によってテストされています。


#### [schemas.getdbt.com](https://schemas.getdbt.com) の更新

アーティファクトスキーマへの非破壊的変更には、[schemas.getdbt.com](https://schemas.getdbt.com) に公開されている対応する jsonschemas の更新が必要です。これらの jsonschemas は https://github.com/dbt-labs/schemas.getdbt.com で定義されています。更新手順は以下のとおりです。
この更新は、コアプルリクエストのマージ後に行う必要があります。そうしないと、解決できない競合が発生し、ベースプルリクエストのマージ前に無効なスキーマが生成される可能性があります。ベースプルリクエストのマージ前に schemas.getdbt.com プルリクエストを作成することはできますが、マージはベースプルリクエストのマージ後に行ってください。
1. https://github.com/dbt-labs/schemas.getdbt.com に、アーティファクトのスキーマ変更を反映する PR を作成します。非破壊的変更の場合は、スキーマをインプレースで更新できます。例: https://github.com/dbt-labs/schemas.getdbt.com/pull/39
2. https://github.com/dbt-labs/schemas.getdbt.com の PR をマージします。

注: [schemas.getdbt.com](https://schemas.getdbt.com) のスキーマを使用した `jsonschema` 検証は推奨されておらず、正式にサポートされていません。ただし、スキーマが更新されても `jsonschema` 検証は引き続き機能するはずです。これは、スキーマが上位互換性を持っているため、以前のマイナーバージョンのスキーマを検証するために使用できるためです。

### 破壊的変更

破壊的変更とは、以下のいずれかの変更を指します。
* 必須フィールドの削除
* 既存フィールドの名前または型の変更
* 既存フィールドのデフォルト値の削除

これらの変更は、可能な限り避けるべきです。必要に応じて、複数の破壊的変更をまとめて行うことで、dbtメタデータを活用するツールのエコシステム全体への影響を最小限に抑えることができます。

互換性のない変更を加える場合は、新しいバージョン管理されたアーティファクトを次のように作成する必要があります。
1. `dbt/artifacts/schemas/<artifact>/v<next-artifact-version>/<artifact>.py` の下に、新しいアーティファクトスキーマを定義する新しいバージョンディレクトリとファイルを作成します。
2. リソースに互換性のない変更が導入されている場合は、`dbt/artifacts/resources/v<next-resource-version>/<resource>.py` の下に、新しいリソーススキーマを定義する新しいリソースクラスを作成します。
3. 新しいバージョン管理されたアーティファクトクラスにアップグレードパスを実装し、同じアーティファクトの以前のバージョンの辞書表現を指定して構築できるようにします。
    * TODO: サンプルは公開され次第リンクします。
4. アーティファクトクラスの以前のすべてのバージョンにダウングレードパスを実装し、新しいアーティファクトスキーマの辞書表現を指定しても構築できるようにします。
    * TODO: サンプルは公開され次第リンクします。
5. アーティファクトの新しいバージョンを指すように「latest」エイリアスを更新します。リソース:
    * アーティファクト: `dbt/artifacts/schemas/<artifact>/__init__.py `
    * リソース: `dbt/artifacts/resources/__init__.py `

最新のエイリアスからインポートする下流のコンシューマー（例: `dbt-core`）は、互換性を破る変更の影響を受けやすいです。理想的には、これらのシステムでは静的型チェックによって非互換性が検出されるべきです。しかし、コンシューマーが `dbt.artifacts.schemas.<artifact>.v<prev-version>` を介してインポートを以前のバージョンに固定することは常に可能です。
