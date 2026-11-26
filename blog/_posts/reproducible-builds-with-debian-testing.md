---
title: Debian Testing でビルドの再現性を保つ
date: 2026-11-26
category: 記事
description: StableBuild が Debian Testing に対応しました。日々更新される Testing の APT リポジトリを日時で固定し、新しいパッケージを使いながら、同じ依存関係でビルドを再現する方法を紹介します。
hero: https://cdn.prod.website-files.com/6558cb02ceb72f12e74052f7/6b07b5787575da62ef9825f0_debian_icecube_2.png
en_url: https://www.stablebuild.com/blog/reproducible-builds-with-debian-testing
---

Debian Stable では、必要なバージョンのパッケージが手に入らないことがあります。そうしたときに便利なのが Debian Testing ですが、リポジトリの中身が日々入れ替わるため、同じ Dockerfile でもビルドするたびに違う依存関係が入ってしまいます。お客様からの要望を受けて、StableBuild ではこの Debian Testing も日時で固定できるようにしました。

## Debian Testing を使う理由

たとえば Python の場合、Debian 13（Trixie）に含まれているのは Python 3.13 ですが、Debian Testing ではすでに Python 3.14 が使えます。3.14 では[テンプレート文字列リテラル（t-string）](https://docs.python.org/3.14/whatsnew/3.14.html#template-string-literals)などの機能が追加されています。

Python だけなら新しいバージョンを個別にインストールする手もありますが、Testing ならシステムライブラリやツールチェーンまで含めて、ディストリビューション全体が新しくなります。新しいライブラリを前提にソフトウェアを開発するときや、次の Debian リリースとの互換性を確かめたいときには特に便利です。

## 日々変わるリポジトリの問題

Debian Testing は、次の Debian 安定版に向けてパッケージが集められるディストリビューションです。Unstable にアップロードされたパッケージは、依存関係が満たされているか、テストに失敗していないか、リリースクリティカルバグがないかといったチェックを通ると、[Testing に移行します](https://www.debian.org/devel/testing)。Stable と違って上流の新しいバージョンが次々に入ってくるので、同じ `apt install` でも、1週間後には別のバージョンがインストールされるかもしれません。

Dockerfile で各パッケージのバージョンを指定しても、そのパッケージが依存するパッケージまでは固定できません。仮にすべてのバージョンを書き出したとしても、新しいバージョンに置き換わった時点で、古いバージョンはリポジトリから消えてしまうことがあります。

特定のコンパイラやライブラリ、ランタイムが必要で Testing を選んだのであって、CI を実行するたびに関係のない依存関係まで変わってほしいわけではないはずです。新しいパッケージを使いたいことと、依存関係が変わり続けることは、本来別の話です。

## リポジトリ全体の日時固定

StableBuild は、ほかの Debian リポジトリと同じように Testing も毎日ミラーし、リポジトリのインデックスとパッケージ本体の両方を保存しています。そのため、パッケージを1つずつバージョン指定しなくても、リポジトリ全体をある日時の状態に固定できます。

StableBuild に保存されている Debian Testing のスナップショット3つで `curl` のバージョンを比べると、次のようになっていました。

| APT スナップショット | `curl` のバージョン |
| --- | --- |
| 2026年11月11日 | `8.22.0-1` |
| 2026年11月13日 | `8.22.0-1` |
| 2026年11月24日 | `8.23.0-2` |

APT リポジトリを11月11日のスナップショットに固定しておけば、Debian Testing 側が更新されても、ビルドでは同じバージョンを使い続けられます。

依存関係を更新するときは、固定日時を進めてテストを実行し、その変更をほかのコードと一緒にコミットします。更新で問題が起きた場合は、以前のスナップショットに戻せます。

## 使い方

Debian Testing の Docker ベースイメージと APT リポジトリを StableBuild で固定する[サンプルリポジトリ](https://github.com/stablebuild/example-debian-testing)を用意しました。Dockerfile は次のとおりです。

```dockerfile
ARG SB_API_KEY=stablebuild-pub-debtesting-ex

FROM ${SB_API_KEY}.dockermirror.stablebuild.com/debian:testing-20261104

ARG SB_API_KEY
ARG APT_PIN_DATE=2026-11-11T08:40:01Z

COPY ./sb-apt.sh /opt/sb-apt.sh
RUN bash /opt/sb-apt.sh load-apt-sources debian-testing

RUN apt update && apt install -y curl
```

StableBuild ですでに Debian リポジトリを固定している方には、見覚えのある設定だと思います。主な違いは、`sb-apt.sh` に `debian` ではなく `debian-testing` を渡す点です。

APT のスナップショットは `APT_PIN_DATE` で選び、ベースイメージは `FROM` のタグ（`testing-20261104`）で別に固定します。`apt install` の書き方を変える必要はありません。

## Debian パッケージ以外の依存関係

過去の Debian リポジトリの状態であれば、Debian 自身も [snapshot.debian.org](https://snapshot.debian.org/) で提供しています。ただ、snapshot.debian.org は不安定になることがあります。

それに、実際の Docker ビルドが依存しているのは Debian のパッケージだけではありません。Docker Hub からベースイメージをプルし、PyPI から Python パッケージをインストールし、サードパーティの APT リポジトリを追加し、GitHub から直接ファイルをダウンロードする、といったことはよくあります。

StableBuild なら、これらをすべて1つのサービスで保存できます。リポジトリごとに過去の状態を別々に管理しなくても、OS のパッケージと、StableBuild が対応しているサードパーティの APT リポジトリを、1つの日時でまとめて固定できます。Debian Testing も、今回からこの仕組みで使えるようになりました。

Debian Testing は StableBuild の[すべての有料プラン](/pricing)で利用できます。[ダッシュボード](https://dashboard.stablebuild.com/?lang=ja)で APT リポジトリを設定するときに、Debian Testing を選んでください。
