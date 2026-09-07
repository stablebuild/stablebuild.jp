---
title: DeadsnakesがUbuntu 20.04のサポートを終了。既存のビルドはどうなる？
date: 2026-09-04
category: 記事
description: DeadsnakesがFocal向けパッケージを削除したことで、Ubuntu 20.04上のビルドが動かなくなりました。バージョンを固定していても依存性が消えれば再現できない理由と、その対処法を解説します。
hero: https://cdn.prod.website-files.com/6558cb02ceb72f12e74052f7/662148cbc8852cc271c70ecf_pypi-frozen-2.png
en_url: https://www.stablebuild.com/blog/deadsnakes-removed-ubuntu-20-04-support
---

2025年にUbuntu 20.04が標準サポートを終了したのに伴い、DeadsnakesはFocal向けのパッケージを削除しました。

その影響は[Stack Exchange](https://unix.stackexchange.com/questions/800941/python3-9-install-on-ubuntu-20-04-focal)などで見ることができます。かつてこれらのパッケージに依存していた環境を、もう一度構築しようとして詰まっている人たちがいます。

Deadsnakesを使うDockerfileには、たとえば次のような記述が含まれているでしょう。

```
RUN apt update && apt install -y software-properties-common
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt update && apt install -y python3.11
```

これはDeadsnakesがUbuntu 20.04向けにPython 3.11を配布していた間は問題なく動いていました。

Deadsnakesはコミュニティによって維持されており、Launchpadのストレージには上限があります。そのため、Ubuntuのリリースがサポート終了を迎えるとパッケージは削除されます。現在のPPAは新しいUbuntuリリースには対応していますが、古いFocal向けパッケージはもう含まれていません。

同じインストールを今実行すると、次のような結果になります。

```
E: Unable to locate package python3.11
```

ビルドが要求しているパッケージは以前とまったく同じです。ただ、それが現在のPPAから手に入らなくなっただけです。

## ピン止めも、パッケージが存在してこそ

パッケージのバージョンを厳密に指定することは、ビルドの再現性を高めるうえで重要です。しかしaptには、それをダウンロードしてくる場所が必要です。

そのバージョンがリポジトリから削除されてしまっていれば、正確なバージョンがわかっていてもあまり役に立ちません。

そしてこれはAPTだけの話ではありません。ビルドはDockerイメージ、リリースファイル、パッケージレジストリ、そして普通のダウンロードURLにも依存しているのが普通です。

それらを使っているコードが変わっていなくても、参照先は変わり続けます。

## Deadsnakesに落ち度はない

Deadsnakesは、恒久的なアーカイブであると約束したことは一度もありません。

サポートが終了したすべてのUbuntuリリース向けに、すべてのPythonパッケージを永久に保持し続ける。これを個人のサイドプロジェクトに期待するのは、いささか無理があります。

一方で、古いビルドは、公開元が新しいリリースへ移ったあとも長くそのパッケージを必要とし続けることがあります。

そして、それに気づくのはたいてい、もう一度ビルドしなければならなくなったときです。

## アップグレードすればいいのでは？

多くの場合、Ubuntuをアップグレードするのが正しい選択です。

ただ、先に古い環境が必要になる場面も少なくありません。古いリリースで報告されたバグを再現する、顧客がまだ使っているバージョンに修正を当てる、大規模な移行を始める前に既存バージョンをビルドし直す、といったケースです。

またUbuntuを変えると、システムライブラリやPython、その他の依存性も同時に変わることになります。小さな修正のはずが、あっという間に大きな作業へと膨らみます。

既存の環境をそのまま再ビルドできれば、その問題は切り離して対処できます。

## StableBuildで古いDeadsnakesパッケージを使う

StableBuildは、Deadsnakesを含むパッケージリポジトリの日次スナップショットを過去に遡って保持しています。

今回のケースでは、Focal向けパッケージが削除される前の日付をAPTに指定すればよいだけです。以下は、2025年4月14日時点のDeadsnakesリポジトリを使うDockerfileの例です。

```
FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive
ARG SB_API_KEY=...
ARG APT_PIN_DATE=2025-04-14T10:40:01Z

COPY ./sb-apt.sh /opt/sb-apt.sh
RUN bash /opt/sb-apt.sh load-apt-sources ubuntu deadsnakes

RUN apt update && apt install -y python3.11
```

StableBuildダッシュボードのUbuntuセクションでUbuntuとDeadsnakesを選び、`sb-apt.sh`をダウンロードします。スナップショットの日付はビルド内の`APT_PIN_DATE`で指定します。

あとは`sb-apt.sh`が、その日付のUbuntuとDeadsnakesのスナップショットをAPTに向けてくれます。それ以降は`apt update`と`apt install`が今までどおり動きます。

StableBuildは、コンテナイメージ、Pythonパッケージ、URLからダウンロードするファイルなど、その他のビルド依存性にも対応しています。

DeadsnakesがFocalを切ったこと自体は、ごく普通のメンテナンスです。古いビルドにとっての問題は、単に「どこか別の場所で誰かが何かを変えた」という点にあります。

同じことは今後も起こります。パッケージリポジトリかもしれませんし、イメージレジストリかもしれませんし、ビルドが依存している別の何かかもしれません。StableBuildはそうした依存性を利用可能な状態で保持し、古いビルドが上流の変更にすべて追従しなくても済むようにします。

自分のビルドをピン止めして試すだけなら、[無料のStableBuildアカウント](/pricing)で十分です。
