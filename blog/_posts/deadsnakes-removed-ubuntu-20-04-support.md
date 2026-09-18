---
title: Deadsnakes が Ubuntu 20.04 のサポートを終了。既存のビルドはどうなる？
date: 2026-09-04
category: 記事
description: Deadsnakes が Focal 向けパッケージを削除したことで、Ubuntu 20.04 上のビルドが動かなくなりました。バージョンを固定していても依存性が消えれば再現できない理由と、その対処法を解説します。
hero: https://cdn.prod.website-files.com/6558cb02ceb72f12e74052f7/662148cbc8852cc271c70ecf_pypi-frozen-2.png
en_url: https://www.stablebuild.com/blog/deadsnakes-removed-ubuntu-20-04-support
---

2025年に Ubuntu 20.04 が標準サポートを終了したことに伴い、Deadsnakes は Focal 向けのパッケージを削除しました。

その影響は [Stack Exchange](https://unix.stackexchange.com/questions/800941/python3-9-install-on-ubuntu-20-04-focal) などで見ることができます。かつてこれらのパッケージに依存していた環境を、もう一度構築しようとして行き詰まっている人たちがいます。

Deadsnakes を使う Dockerfile には、たとえば次のような記述が含まれているでしょう。

```
RUN apt update && apt install -y software-properties-common
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt update && apt install -y python3.11
```

これは Deadsnakes が Ubuntu 20.04 向けに Python 3.11 を配布していた間は問題なく動いていました。

Deadsnakes はコミュニティによって維持されており、Launchpad のストレージにも上限があります。そのため、Ubuntu のリリースがサポート終了を迎えるとパッケージは削除されます。現在の PPA は新しい Ubuntu リリースには対応していますが、古い Focal 向けパッケージはもう含まれていません。

同じインストールを今実行すると、次のような結果になります。

```
E: Unable to locate package python3.11
```

ビルドが要求しているパッケージは以前とまったく同じです。ただ、それが現在の PPA から手に入らなくなっただけです。

## ピン止めも、パッケージが存在してこそ

パッケージのバージョンを厳密に指定することは、ビルドの再現性を高めるうえで重要です。しかし APT には、ダウンロード元が必要です。

そのバージョンがリポジトリから削除されてしまっていれば、正確なバージョンがわかっていてもあまり役に立ちません。

そしてこれは APT だけの話ではありません。ビルドはたいてい、Docker イメージ、リリースファイル、パッケージレジストリ、そしてただのダウンロード URL にも依存しています。

それらを使っているコードが変わっていなくても、参照先は変わり続けます。

## Deadsnakes に落ち度はない

Deadsnakes は、恒久的なアーカイブであると約束したことなど一度もありません。

サポートが終了したすべての Ubuntu リリース向けに、すべての Python パッケージを永久に保持し続ける。これを個人のサイドプロジェクトに期待するのは、いささか無理があります。

一方で、古いビルドは、配布先が新しいリリースへ移ったあとも長くそのパッケージを必要とし続けることがあります。

そして、それに気づくのはたいてい、もう一度ビルドしなければならなくなったときです。

## アップグレードすればいいのでは？

多くの場合、Ubuntu をアップグレードするのが正しい選択です。

ただ、アップグレードの前に古い環境が必要になる場面も少なくありません。古いリリースで報告されたバグを再現する、顧客がまだ使っているバージョンに修正を当てる、大規模な移行を始める前に既存バージョンをビルドし直す、といったケースです。

また Ubuntu を変えると、システムライブラリや Python、その他の依存性も同時に変わることになります。小さな修正のはずが、あっという間に大きな作業へと膨らみます。

既存の環境をそのまま再ビルドできれば、Ubuntu のアップグレードとは切り離して対処できます。

## StableBuild で古い Deadsnakes パッケージを使う

StableBuild は、Deadsnakes を含むパッケージリポジトリの日次スナップショットを過去の分まで保持しています。

今回のケースでは、Focal 向けパッケージが削除される前の日付を APT に指定すればよいだけです。以下は、2025年4月14日時点の Deadsnakes リポジトリを使う Dockerfile の例です。

```
FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive
ARG SB_API_KEY=...
ARG APT_PIN_DATE=2025-04-14T10:40:01Z

COPY ./sb-apt.sh /opt/sb-apt.sh
RUN bash /opt/sb-apt.sh load-apt-sources ubuntu deadsnakes

RUN apt update && apt install -y python3.11
```

StableBuild ダッシュボードの Ubuntu セクションで Ubuntu と Deadsnakes を選び、`sb-apt.sh` をダウンロードします。スナップショットの日付はビルド内の `APT_PIN_DATE` で指定します。

あとは `sb-apt.sh` が、APT の参照先をその日付の Ubuntu と Deadsnakes のスナップショットに切り替えてくれます。それ以降は `apt update` と `apt install` が今までどおり動きます。

StableBuild は、コンテナイメージ、Python パッケージ、URL からダウンロードするファイルなど、その他のビルド依存性にも対応しています。

Deadsnakes が Focal のサポートを終えたこと自体は、ごく普通のメンテナンスです。古いビルドにとっての問題は、単に「どこか別の場所で誰かが何かを変えた」という点にあります。

同じことは今後も起こります。パッケージリポジトリかもしれませんし、イメージレジストリかもしれませんし、ビルドが依存している別の何かかもしれません。StableBuild はそうした依存性を利用可能な状態で保持し、古いビルドが上流の変更にすべて追従しなくても済むようにします。

自分のビルドをピン止めして試すだけなら、[無料の StableBuild アカウント](/pricing)で十分です。
