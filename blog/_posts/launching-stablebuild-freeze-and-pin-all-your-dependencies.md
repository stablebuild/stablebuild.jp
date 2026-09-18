---
title: 同じ Dockerfile から同じコンテナはできない - すべての依存性を凍結・ピン止めする
date: 2024-02-15
category: 記事
description: Dockerfile は一見再現性があるように見えて、実際には5つの外部サービスに依存しています。Docker イメージ、OS パッケージ、Python パッケージ、任意のファイルを凍結・ピン止めする方法を解説します。
hero: https://cdn.prod.website-files.com/6558cb02ceb72f12e74052f7/6576de74b938b86ccc25baa5_toying-with-stablebuild-cube3.005.png
en_url: https://www.stablebuild.com/blog/launching-stablebuild-freeze-and-pin-all-your-dependencies
---

[StableBuild](/) は、Docker イメージ、OS パッケージ、Python パッケージ、そして任意のビルド依存性を簡単に凍結・ピン止めできるようにすることで、信頼できる再現性の高いビルドを実現するためのツール群です。

なぜそれが必要になるのか、よくある Dockerfile を例に見ていきます。

## Docker とビルドの再現性

Docker は、アプリケーションとその依存性（OS から Python パッケージまで）を1つのデプロイ可能なコンテナにまとめられるようにしたことで、アプリケーションコードの配布を圧倒的に簡単にしました。さらに Dockerfile によって、そのアプリケーションをどうビルドすべきかという仕様を人間が読める形で持てるようになりました。

しかし、ここに大きな問題が1つあります。Dockerfile は一見すると再現性がある（同じ Dockerfile から同じコンテナができる）ように思えますが、実際には無数のミラー、パッケージレジストリ、リポジトリに依存しており、そのどれもがいつでも変わり得ます。たとえば次の Dockerfile を見てください。

```
# このDockerfileはUbuntu 20.04をベースにする
FROM ubuntu:20.04

# OSレベルのパッケージをインストール
RUN apt update && apt install -y curl software-properties-common

# 新しいPythonが必要なので、Deadsnakes PPAから取得する
RUN add-apt-repository -y ppa:deadsnakes/ppa && \
    apt update && \
    apt install -y python3.9 python3.9-distutils

# pip（Pythonのパッケージ管理ツール）をインストール
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3.9 get-pip.py

# pipでPythonパッケージをインストール
RUN pip3 install onnx==1.14.0
```

この Dockerfile は、実は5つの別々のサービスに依存しています。

- **Docker Hub からベースイメージをプルしている**。Docker Hub のイメージは不変ではありません。このベースイメージは新しい OS バージョンで上書きされることも、削除されてしまうこともあります。
- **Ubuntu パッケージレジストリから `apt` でパッケージをインストールしている**。このレジストリは常に更新されているため、`curl` と `software-properties-common` について、インストールされるのはその時点で最新のバージョンです。
- **サードパーティのパッケージレジストリ（PPA）から新しい Python を取得している**。こちらも常に更新されているため、入手できるのは Python 3.9.x 系の最新版です。加えて、PPA が今後も存在し続ける保証はありません。
- **インターネットから `get-pip.py` をダウンロードしている**。この URL がいつ別のファイルを返すようになるか、いつ削除されるかはわかりません。
- **`pip` で Python パッケージレジストリからパッケージをインストールしている**。ここでは onnx のバージョンを指定していますが、onnx は `protobuf>=3.20.2` に依存しているため、protobuf はその時点で最新のバージョンが入ります。

**つまり、同じ Dockerfile でも、ビルドした時期によってまったく違うコンテナができあがるということです。** 今日 Dockerfile を書き、アプリケーションをテストして、すべて順調。翌日、同じ Dockerfile からコンテナを再ビルドすると（コードを更新したかった、依存性を1つ追加したかった、などの理由で）、新しい OS バージョン、`apt` からの新しいパッケージ、新しい Python バージョン、そして新しい Python パッケージが入ります。`get-pip.py` の URL については、今までどおり解決してくれることを祈るしかありません。動くかもしれませんし、動かないかもしれません。

これは規模の大きな開発チームにとって多大な保守負担になります。しかも、すべてが後手に回るという点が厄介です。誰かがコードベースに一見些細な変更を加え、ビルドサーバーがコンテナをゼロからビルドし、そしてまったく無関係なエラーでビルドが壊れます。ビルドが壊れているのですから、新しい依存性に合わせてアプリケーションをすぐに直すしかありません。

## StableBuild が解決します

StableBuild はこの問題を解決します。StableBuild は、コンテナのビルドを信頼できる再現性の高いものにするためのミラーとパッケージレジストリの集合です。要するに、StableBuild を使えば任意の依存性を凍結できるため、同じ Dockerfile から同じコンテナが得られるようになります。現時点では次のものに対応しています。

- **Docker ベースイメージ**: Docker Hub、GitHub Container Registry、NVIDIA NGC の不変のミラーを運用しています。
- **Ubuntu、Debian、Alpine の各パッケージレジストリにあるすべてのパッケージ**（つまり `apt` や `apk` でインストールするもの全般）: パッケージレジストリ全体の日次ミラーを作成しています。
- **Deadsnakes（Python 向け）や NVIDIA の CUDA レジストリなど、主要なサードパーティパッケージレジストリ（PPA）**: 完全な日次ミラーを作成しています。
- **PyPI の Python パッケージ**: PyPI インデックス全体を毎日取り込み、実際にインストールされたパッケージはオンデマンドでキャッシュします。
- **インターネット上の任意の URL やファイル**: ファイルミラーを通して対応します。

## 5分で問題を解決

StableBuild は、既存のビルドツールチェーンに5分で組み込めます。たとえば、先ほどと同じ Dockerfile を、StableBuild 経由で完全にキャッシュしてビルドすると次のようになります。

```
# StableBuildの不変のDocker Hubミラーからubuntu:20.04をプルする
FROM your-prefix.dockermirror.stablebuild.com/ubuntu:20.04

# aptパッケージをこの日付に固定する。レジストリ全体の日次コピーを
# 作成しているため、常にまったく同じパッケージが返される
ARG APT_PIN_DATE=2024-02-14T10:40:01Z
ARG SB_API_KEY=your-prefix

# Ubuntuパッケージレジストリとdeadsnakes PPAを読み込む
COPY ./sb-apt.sh /opt/sb-apt.sh
RUN bash /opt/sb-apt.sh load-apt-sources ubuntu deadsnakes

# OSレベルのパッケージをインストール（いつもと同じ）
RUN apt update && apt install -y curl software-properties-common

# 新しいPythonが必要なので、Deadsnakes PPAから取得する
# （リポジトリを手動で追加する必要はもうない）いつもと同じ
RUN apt update && apt install -y python3.9 python3.9-distutils

# 任意のURLの先頭にStableBuildのファイルミラーのURLを付けるだけで
# 自動的にキャッシュされる。追加の依存性はStableBuildのPyPIミラーから
RUN curl https://your-prefix.httpcache.stablebuild.com/my-first-tutorial/https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3.9 get-pip.py -i https://your-prefix.pypimirror.stablebuild.com/2024-02-14/

# pipでPythonパッケージをインストール（2024-02-14に固定）。
# その日付時点のパッケージ一覧がインストールされる
RUN pip3 install \
    -i https://your-prefix.pypimirror.stablebuild.com/2024-02-14/ \
    onnx==1.14.0
```

これだけです。このコンテナは完全にピン止めされ、常に同じ OS バージョン、同じパッケージ一覧、同じ Python 依存性がインストールされます。🎉

## 導入したチームでは

お客様の開発現場では、依存性の変化によって数週間おきにビルドが壊れる様子を目にしてきました。頻度としては多くないように聞こえるかもしれませんが、いつも時間との勝負です。本番デプロイが止まっているのでビルドはすぐに直さなければならず、その対応ができるのはたいてい非常に経験豊富なエンジニアだけで、しかも更新された依存性が自動テストのない部分を壊していないかを入念に検証する必要があります。

StableBuild は、お客様のそうした課題を解消しました。もちろん依存性の更新自体は必要です（私たちもセキュリティ修正は歓迎します）。ただ、お客様はそれを自分たちのタイミングで、時間に追われることなく行えるようになりました。

## まずはお試しください

無料の Community プランでは、すべてのリポジトリとミラーにアクセスでき、トラフィック 1TB とファイルストレージ 30GB が含まれます。[料金ページ](/pricing)でプランをご確認のうえ、[ダッシュボード](https://dashboard.stablebuild.com/?lang=ja)からご登録ください。有料プランは月額199ドルからです。

足りないものがあれば（別の OS でビルドしている、別の PPA が欲しいなど）、contact@stablebuild.jp までお気軽にご連絡ください。対応を追加します。StableBuild がどのようにビルドを安定させ、再現性を高めるのかをもっと詳しく知りたい方は、[ドキュメント](https://stablebuild.gitbook.io/ja)をご覧ください。
