---
title: Debian Testing を使った再現可能なビルド
date: 2026-11-26
category: 記事
description: Debian Testing では新しいパッケージを利用できますが、リポジトリの内容は継続的に変化します。StableBuild で Docker ベースイメージと APT リポジトリを特定の日時に固定し、同じ依存関係でビルドを再現する方法を紹介します。
hero: https://cdn.prod.website-files.com/6558cb02ceb72f12e74052f7/6b07b5787575da62ef9825f0_debian_icecube_2.png
en_url: https://www.stablebuild.com/blog/reproducible-builds-with-debian-testing
---

Debian Stable には、必要なバージョンのパッケージがないことがあります。

Python を例にしてみましょう。Debian 13（Trixie）には Python 3.13 が含まれていますが、Debian Testing では、[テンプレート文字列リテラル（t-string）](https://docs.python.org/3.14/whatsnew/3.14.html#template-string-literals)などの機能が追加された Python 3.14 をすでに利用できます。

新しいバージョンの Python だけを個別にインストールすることもできますが、Debian Testing を使えば、より新しいパッケージで構成されたディストリビューション全体を利用できます。新しいシステムライブラリやツールチェーンを使ってソフトウェアを開発する場合や、次期 Debian リリースとの互換性をテストする場合には、特に便利です。

しかし、ビルドが動くようになった後も、同じ依存関係一式を使い続けたい場合はどうすればよいでしょうか。

## 変化し続けるリポジトリを使ったビルド

Debian Testing は、Debian の次期安定版が形作られる場所です。パッケージは、依存関係、テストの失敗、リリースクリティカルバグに関するチェックを通過した後、[Unstable から Testing に移行します](https://www.debian.org/devel/testing)。

Debian Stable とは異なり、Testing には上流の新しいバージョンのパッケージが定期的に取り込まれます。そのため、1週間後に同じ `apt install` コマンドを実行すると、異なる依存関係がインストールされる可能性があります。

Dockerfile で個々のパッケージのバージョンを指定することはできますが、それらのパッケージにも依存関係があります。すべてのバージョンを固定したとしても、新しいバージョンに置き換えられると、古いバージョンはリポジトリから消えることがあります。

新しい依存関係が必要なことと、依存関係が継続的に変わることは別の問題です。

特定のコンパイラ、ライブラリ、ランタイムが必要で Debian Testing を選んだのであれば、CI パイプラインを実行するたびに、関係のない依存関係まで変わる必要はありません。

## StableBuild で Debian Testing を固定する

StableBuild は、お客様からの要望を受けて、Debian Testing に対応しました。

ほかの Debian リポジトリと同様に、Testing も毎日ミラーし、リポジトリのインデックスとパッケージ本体の両方を保存します。個々のパッケージのバージョンを指定する代わりに、リポジトリ全体を特定の日時に固定できます。

StableBuild が保存した3つの Debian Testing スナップショットでは、`curl` のバージョンが次のように変化しました。

| APT スナップショット | `curl` のバージョン |
| --- | --- |
| 2026年11月11日 | `8.22.0-1` |
| 2026年11月13日 | `8.22.0-1` |
| 2026年11月24日 | `8.23.0-2` |

APT リポジトリを11月11日のスナップショットに固定すれば、Debian Testing がその後も更新される一方で、ビルドでは同じバージョンのパッケージを引き続き利用できます。

依存関係を更新する準備ができたら、固定する日時を変更してテストを実行し、その変更をほかのコードと一緒にコミットできます。更新によって問題が発生した場合は、以前のスナップショットに戻せます。

## はじめ方

StableBuild で Debian Testing の Docker ベースイメージと APT リポジトリの両方を固定する方法を示す、小さな[サンプルリポジトリ](https://github.com/stablebuild/example-debian-testing)を用意しました。

```dockerfile
ARG SB_API_KEY=stablebuild-pub-debtesting-ex

FROM ${SB_API_KEY}.dockermirror.stablebuild.com/debian:testing-20261104

ARG SB_API_KEY
ARG APT_PIN_DATE=2026-11-11T08:40:01Z

COPY ./sb-apt.sh /opt/sb-apt.sh
RUN bash /opt/sb-apt.sh load-apt-sources debian-testing

RUN apt update && apt install -y curl
```

すでに StableBuild で Debian リポジトリを固定している場合は、見慣れた設定でしょう。主な違いは、`sb-apt.sh` に `debian` ではなく `debian-testing` を渡すことです。

`APT_PIN_DATE` で APT スナップショットを選択します。ベースイメージは別に固定します。APT でパッケージをインストールする方法を変える必要はありません。

## Debian パッケージ以外の依存関係

Debian は、[snapshot.debian.org](https://snapshot.debian.org/) で過去のリポジトリのスナップショットをすでに提供しています。Debian リポジトリの状態だけを保存できればよい場合は、これだけで十分かもしれません。

しかし、一般的な Docker ビルドは、Debian パッケージ以外にも依存していることがよくあります。Docker Hub からベースイメージをプルしたり、PyPI から Python パッケージをインストールしたり、サードパーティの APT リポジトリを利用したり、GitHub からファイルを直接ダウンロードしたりする場合があります。

StableBuild では、これらすべてを同じサービスで保存できます。また、リポジトリごとに別々の履歴ミラーを管理する代わりに、OS パッケージと StableBuild が対応しているサードパーティの APT リポジトリを、1つの日時でまとめて固定できます。

Debian Testing も、同じ仕組みで利用できるようになりました。

この機能は、StableBuild の[すべての有料プラン](/pricing)で利用できます。[StableBuild ダッシュボード](https://dashboard.stablebuild.com/)で APT リポジトリを設定する際に、Debian Testing を選択してください。
