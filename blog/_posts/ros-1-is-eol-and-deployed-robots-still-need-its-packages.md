---
title: ROS 1 は EOL に。それでも稼働中のロボットには ROS 1 のパッケージが必要
date: 2026-09-25
category: 記事
description: ROS 1 Noetic は EOL を迎えましたが、稼働中のロボットでは今も ROS 1 のパッケージが必要です。APT リポジトリの変化がビルドの再現性に与える影響と、ROS 1 と ROS 2 のリポジトリを日時で固定する方法を紹介します。
hero: https://cdn.prod.website-files.com/6558cb02ceb72f12e74052f7/6ab5c2884676aa29ab650ddb_ROS_icecube.png
en_url: https://www.stablebuild.com/blog/ros-1-is-eol-and-deployed-robots-still-need-its-packages
---

[ROS 1 Noetic は2025年5月31日に EOL を迎えました](https://www.ros.org/blog/noetic-eol/)。

これにより、ROS チームからセキュリティアップデート、不具合修正、更新版バイナリが提供されることはなくなりました。とはいえ、ROS 1 で動くロボットまで一緒に姿を消したわけではありません。

既存のロボティクススタックを移行するのは、大がかりなプロジェクトになることがあります。ROS 1 から ROS 2 への移行では、ビルドツール、パラメータ、nodelet、ノード間通信などに変更が必要になる場合があります。

これは何年も前から問題になっています。[2022年の ROS コミュニティでの議論](https://discourse.openrobotics.org/t/our-and-your-plan-for-the-ros1-ros2-migration/28584)では、あるロボティクス企業が、通常の製品開発を止めることなく、100以上の相互接続された ROS ノードを持つシステムの移行に取り組んでいると説明していました。

そして、この問題は今も続いています。2026年8月には、ある開発者が、大規模なレガシー ROS 1 スタックを一度にすべて書き換えるのではなく、段階的に移行するための [Docker 化された ROS 1 Noetic と ROS 2 Jazzy のブリッジ](https://discourse.openrobotics.org/t/bridging-the-gap-a-dockerized-ros-1-noetic-ros-2-jazzy-bridge-ubuntu-24-04-for-gradual-migration/57681)を公開しました。

私たちのもとにも、Noetic が EOL を迎えた直後、Ubuntu Focal 上で ROS 1 を使い続けており、ROS リポジトリへのアクセスを維持したいというロボティクスチームから相談がありました。

こうしたシステムでは、古い環境を再ビルドできることが今も重要です。

そのためには、ソースコードを残しておくだけでは足りません。

## ROS パッケージは APT リポジトリに依存する

Ubuntu 上の ROS パッケージは、一般的に APT を使ってインストールされます。

ROS 1 Noetic のパッケージは、次のリポジトリから提供されていました。

```text
http://packages.ros.org/ros/ubuntu
```

ROS 2 では、次のリポジトリが使われます。

```text
http://packages.ros.org/ros2/ubuntu
```

[ROS 2 の公式インストールドキュメント](https://docs.ros.org/en/galactic/Installation/Ubuntu-Install-Debians.html)でも、ROS パッケージをインストールする前に、`packages.ros.org/ros2/ubuntu` を APT の取得元として設定しています。

ROS 1 Noetic が EOL を迎えた際、Open Robotics は、[既存の ROS 1 バイナリを引き続き `packages.ros.org` で提供すると明言しました](https://www.ros.org/blog/noetic-eol/)。

ありがたい対応ですが、リポジトリの内容は一定ではありません。

新しいバージョンが公開され、リポジトリから取得できるパッケージも時間とともに入れ替わります。

パッケージを特定のバージョンに固定していても、これは問題になります。

## ROS パッケージのバージョンを固定しても利用できなくなることがある

[Autoware プロジェクトは、2026年に再現可能なビルドに取り組むなかで、この問題に直面しました](https://github.com/orgs/autowarefoundation/discussions/6861)。

Autoware では、開発環境を構成する複数の要素をすでに固定していました。しかし、ROS パッケージとシステムパッケージは、その時点のリポジトリから動的に解決されていました。そのため、同じコミットからビルドしても、実行した時期によって異なる環境が作られる可能性がありました。

議論のなかで、ROS のビルドファームは通常、各パッケージの最新バージョンだけをリポジトリに残していると、あるコントリビューターが指摘しました。

たとえば、次のようなバージョンを指定したとします。

```text
ros-jazzy-rviz2=14.1.19-1noble.20260126.201007
```

バージョンを厳密に特定した指定です。

しかし、そのバージョンのパッケージがリポジトリから取得できなくなっていれば、APT はインストールできません。

固定されているのはバージョン番号です。そのバージョンのパッケージ本体まで保存されているとは限りません。

Autoware の[再現可能なビルドに向けた実装計画](https://github.com/autowarefoundation/autoware/issues/6862)には、ROS パッケージで `snapshots.ros.org` を利用するための対応が含まれています。

## リポジトリの状態も重要

公式 ROS Docker イメージに対して最近報告された Issue では、同じ問題が別の形で現れています。

2026年8月、[`ros:lyrical-*` イメージでは ROS パッケージのバージョンが固定されている一方、APT の取得元には現在の ROS リポジトリが指定されたままになっている](https://github.com/osrf/docker_images/issues/897)ことが報告されました。

そのため、後から別の ROS パッケージをインストールすると、既存のイメージに新しいバイナリが取り込まれる可能性がありました。

報告者の再現手順では、それによって ABI の不一致が発生し、最終的に次のエラーが出ました。

```text
double free or corruption (out)
```

報告者は、日付を指定した ROS のスナップショットを使ってイメージを再ビルドし、同じ再現手順が正常に完了することを確認しました。

問題は、単にどのバージョンのパッケージを指定したかだけではありません。イメージが参照していたリポジトリの状態そのものが変わっていたのです。

パッケージを固定すれば、APT にどのバージョンを使うか指定できます。しかし、そのバージョンが今後も取得できることや、依存関係全体が後からも同じ状態であることまでは保証できません。

## ROS にはすでにスナップショットが用意されている

ROS は、ROS パッケージリポジトリの過去の状態を保存する独自のスナップショット基盤を [snapshots.ros.org](https://snapshots.ros.org/) で提供しています。

ROS リポジトリだけを保存できればよいビルドにとっては、有効な選択肢です。

しかし、ROS のビルドは通常、ROS だけに依存しているわけではありません。

ベースとなる Ubuntu パッケージに加えて、ほかの APT リポジトリ、Python パッケージ、コンテナ、CUDA パッケージ、ビルド中に直接ダウンロードするファイルなどに依存している可能性があります。

ライフサイクルは提供元ごとに異なります。

再現可能なビルドという観点では、ROS リポジトリの保存は環境全体の保存の一部にすぎません。

## StableBuild は ROS 1 と ROS 2 に対応

StableBuild は、Ubuntu とサードパーティの APT リポジトリを指定した日時の状態で保存し、ROS 1 と ROS 2 の両方に対応しています。

Ubuntu 20.04 上の ROS 1 では、次のように設定します。

```dockerfile
FROM ubuntu:20.04

ARG SB_API_KEY=...
ARG APT_PIN_DATE=2026-07-23T10:40:01Z

COPY ./sb-apt.sh /opt/sb-apt.sh
RUN bash /opt/sb-apt.sh load-apt-sources ubuntu ros1

RUN apt update && apt install -y python3-rosdep
```

StableBuild の ROS 1 対応は Ubuntu 20.04 Focal が前提です。StableBuild では、Ubuntu 20.04 について2026年7月23日までのスナップショットを利用できます（[ドキュメント](https://stablebuild.gitbook.io/ja/mirrors-and-caches/os-package-registry-ubuntu-debian-alpine)を参照）。そのため、ROS 1 のビルドでは同日以前の日時を指定する必要があります。

ROS 2 も同じ仕組みで利用できます。たとえば、次のように設定します。

```dockerfile
FROM ubuntu:22.04

ARG SB_API_KEY=...
ARG APT_PIN_DATE=2026-09-01T08:40:01Z

COPY ./sb-apt.sh /opt/sb-apt.sh
RUN bash /opt/sb-apt.sh load-apt-sources ubuntu ros2

RUN apt update && apt install -y ros-dev-tools
```

重要なのは、日時の指定です。

後から同じビルドを実行したときも、APT は現在の上流リポジトリではなく、指定した日時のリポジトリ状態を使って依存関係を解決できます。

## 古いロボットには今も古いソフトウェアが必要

ROS 2 が登場してから、すでに何年も経っています。[ROS 2 初の正式リリースである Ardent Apalone は、2017年12月に公開されました](https://www.ros.org/news/2017/12/ros-2-ardent-apalone-released.html)。ROS 1 からの移行も、長い間推奨されてきました。

しかし、既存のロボットのソフトウェアを置き換えるのは、新しいプロジェクトで ROS 2 を選ぶのとは訳が違います。

ロボットには、ROS 1 を軸に何年もテストを重ねてきたコード、ドライバー、ハードウェア連携、運用上の前提があります。スタック全体の移行には時間がかかり、その間も古い環境を再ビルドしなければならない場面があります。

ROS 2 に移行しても、根本的な依存関係の問題がなくなるわけではありません。Autoware の再現可能なビルドへの取り組みと、最近の ROS Docker イメージの Issue は、どちらも ROS 2 に関するものでした。

古いビルドを再現可能な状態で残すには、ソースコードを保存するだけでは不十分です。

そのビルドが依存していたパッケージも必要です。

StableBuild には[無料の Community プラン](/pricing)があります。ROS と Ubuntu のリポジトリを特定の日時に固定して試してみてください。
