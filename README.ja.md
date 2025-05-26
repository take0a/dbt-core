<p align="center">
  <img src="./etc/dbt-core.svg" alt="dbt logo" width="750"/>
</p>
<p align="center">
  <a href="https://github.com/dbt-labs/dbt-core/actions/workflows/main.yml">
    <img src="https://github.com/dbt-labs/dbt-core/actions/workflows/main.yml/badge.svg?event=push" alt="CI Badge"/>
  </a>
</p>

**[dbt](https://www.getdbt.com/)** を使用すると、データ アナリストやエンジニアは、ソフトウェア エンジニアがアプリケーションの構築に使用するのと同じ手法を使用してデータを変換できます。

![architecture](./etc/dbt-transform.png)

## dbt を理解する

dbt を使用するアナリストは、SELECT ステートメントを記述するだけでデータを変換できます。dbt は、これらのステートメントをデータウェアハウス内のテーブルやビューに変換します。

これらの SELECT ステートメント、つまり「モデル」が dbt プロジェクトを構成します。モデルは多くの場合、互いに重ねて構築されます。dbt を使用すると、モデル間の [関係性の管理](https://docs.getdbt.com/docs/ref) や [関係性の視覚化](https://docs.getdbt.com/docs/documentation) が容易になり、さらに [テスト](https://docs.getdbt.com/docs/testing) を通じて変換の品質を確保できます。

![dbt dag](https://raw.githubusercontent.com/dbt-labs/dbt-core/6c6649f9129d5d108aa3b0526f634cd8f3a9d1ed/etc/dbt-dag.png)

## はじめに

- [dbt Core をインストール](https://docs.getdbt.com/docs/get-started/installation)するか、[dbt Cloud CLI](https://docs.getdbt.com/docs/cloud/cloud-cli-installation)をお試しください。これは、[dbt Cloud](https://docs.getdbt.com/docs/cloud/about-cloud/dbt-cloud-features) を基盤としたコマンドラインインターフェースで、コラボレーションを強化します。
- [概要](https://docs.getdbt.com/docs/introduction/)と[viewpoint](https://docs.getdbt.com/docs/about/viewpoint/)をお読みください。

## dbtコミュニティに参加しましょう

- [dbtコミュニティSlack](http://community.getdbt.com/)で会話に参加しましょう
- [dbtコミュニティDisc​​ourse](https://discourse.getdbt.com)で詳細をご覧ください

## バグ報告とコード貢献

- バグ報告や機能リクエストがありましたら、[issue](https://github.com/dbt-labs/dbt-core/issues/new/choose) をオープンしてご連絡ください。
- dbt の開発にご協力いただけませんか？[貢献ガイド](https://github.com/dbt-labs/dbt-core/blob/HEAD/CONTRIBUTING.md) をご覧ください。

## 行動規範

dbt プロジェクトのコードベース、課題追跡システム、チャットルーム、メーリングリストで交流するすべての人は、[dbt 行動規範](https://community.getdbt.com/code-of-conduct) に従うことが求められます。
