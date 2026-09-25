---
title: ROS 1はEOLを迎えました。それでも稼働中のロボットにはROS 1のパッケージが必要です
date: 2026-09-25
category: 記事
description: ROS 1 NoeticはEOLを迎えましたが、稼働中のロボットでは今もROS 1のパッケージが必要です。APTリポジトリの変化がビルドの再現性に与える影響と、ROS 1とROS 2のリポジトリを日時で固定する方法を紹介します。
hero: https://cdn.prod.website-files.com/6558cb02ceb72f12e74052f7/6ab5c2884676aa29ab650ddb_ROS_icecube.png
en_url: https://www.stablebuild.com/blog/ros-1-is-eol-and-deployed-robots-still-need-its-packages
---

[ROS 1 Noeticは2025年5月31日にEOLを迎えました](https://www.ros.org/blog/noetic-eol/)。

これにより、ROSチームからセキュリティアップデート、不具合修正、更新版バイナリが提供されることはなくなりました。しかし、ROS 1で動いているロボットが同時になくなったわけではありません。

既存のロボティクススタックを移行するのは、大がかりなプロジェクトになることがあります。ROS 1からROS 2への移行では、ビルドツール、パラメータ、nodelet、ノード間通信などに変更が必要になる場合があります。

これは何年も前から問題になっています。[2022年のROSコミュニティでの議論](https://discourse.openrobotics.org/t/our-and-your-plan-for-the-ros1-ros2-migration/28584)では、あるロボティクス企業が、通常の製品開発を止めることなく、100以上の相互接続されたROSノードを持つシステムの移行に取り組んでいると説明していました。

そして、この問題は今も続いています。2026年8月には、ある開発者が、大規模なレガシーROS 1スタックを一度にすべて書き換えるのではなく、段階的に移行するための[Docker化されたROS 1 NoeticとROS 2 Jazzyのブリッジ](https://discourse.openrobotics.org/t/bridging-the-gap-a-dockerized-ros-1-noetic-ros-2-jazzy-bridge-ubuntu-24-04-for-gradual-migration/57681)を公開しました。

私たちのもとにも、NoeticがEOLを迎えた直後、Ubuntu Focal上でROS 1を使い続けており、ROSリポジトリへのアクセスを維持したいというロボティクスチームから相談がありました。

こうしたシステムでは、古い環境を再びビルドできることが今も重要です。

そのためには、ソースコードを残しておくだけでは足りません。

## ROSパッケージはAPTリポジトリに依存する

Ubuntu上のROSパッケージは、一般的にAPTを使ってインストールされます。

ROS 1 Noeticのパッケージは、次のリポジトリから提供されていました。

```text
http://packages.ros.org/ros/ubuntu
```

ROS 2では、次のリポジトリが使われます。

```text
http://packages.ros.org/ros2/ubuntu
```

[ROS 2の公式インストールドキュメント](https://docs.ros.org/en/galactic/Installation/Ubuntu-Install-Debians.html)でも、ROSパッケージをインストールする前に、`packages.ros.org/ros2/ubuntu`をAPTの取得元として設定しています。

ROS 1 NoeticがEOLを迎えた際、Open Roboticsは、[既存のROS 1バイナリを引き続き`packages.ros.org`で提供すると明言しました](https://www.ros.org/blog/noetic-eol/)。

これは助かりますが、リポジトリの内容は固定ではありません。

新しいバージョンが公開され、リポジトリから取得できるパッケージも時間とともに入れ替わります。

パッケージを特定のバージョンに固定していても、これは問題になります。

## ROSパッケージのバージョンを固定しても利用できなくなることがある

[Autowareプロジェクトは、2026年に再現可能なビルドに取り組むなかで、この問題に直面しました](https://github.com/orgs/autowarefoundation/discussions/6861)。

Autowareでは、開発環境を構成する複数の要素をすでに固定していました。しかし、ROSパッケージとシステムパッケージは、その時点のリポジトリから動的に解決されていました。そのため、同じコミットからビルドしても、実行した時期によって異なる環境が作られる可能性がありました。

議論のなかで、ROSのビルドファームは通常、各パッケージの最新バージョンだけをリポジトリに残していると、あるコントリビューターが指摘しました。

たとえば、次のようなバージョンを指定したとします。

```text
ros-jazzy-rviz2=14.1.19-1noble.20260126.201007
```

これは十分に具体的な指定です。

しかし、そのバージョンのパッケージがリポジトリから取得できなくなっていれば、APTはインストールできません。

固定されているのはバージョン番号です。そのバージョンのパッケージ本体まで保存されているとは限りません。

Autowareの[再現可能なビルドに向けた実装計画](https://github.com/autowarefoundation/autoware/issues/6862)には、ROSパッケージで`snapshots.ros.org`を利用するための対応が含まれています。

## リポジトリの状態も重要

公式ROS Dockerイメージに対して最近報告されたIssueでは、同じ問題が別の形で現れています。

2026年8月、[`ros:lyrical-*`イメージではROSパッケージのバージョンが固定されている一方、APTの取得元には現在のROSリポジトリが指定されたままになっている](https://github.com/osrf/docker_images/issues/897)ことが報告されました。

そのため、後から別のROSパッケージをインストールすると、既存のイメージに新しいバイナリが取り込まれる可能性がありました。

報告者の再現手順では、それによってABIの不一致が発生し、最終的に次のエラーが出ました。

```text
double free or corruption (out)
```

報告者は、日付を指定したROSのスナップショットを使ってイメージを再ビルドし、同じ再現手順が正常に完了することを確認しました。

問題は、単にどのバージョンのパッケージを指定したかだけではありません。イメージが参照していたリポジトリの状態そのものが変わっていたのです。

パッケージを固定すれば、APTにどのバージョンを使うか指定できます。しかし、そのバージョンが今後も取得できることや、依存関係全体が後からも同じ状態であることまでは保証できません。

## ROSにはすでにスナップショットが用意されている

ROSは、ROSパッケージリポジトリの過去の状態を保存する独自のスナップショット基盤を[snapshots.ros.org](https://snapshots.ros.org/)で提供しています。

ROSリポジトリだけを保存できればよいビルドにとっては、有効な選択肢です。

しかし、ROSのビルドは通常、ROSだけに依存しているわけではありません。

ベースとなるUbuntuパッケージに加えて、ほかのAPTリポジトリ、Pythonパッケージ、コンテナ、CUDAパッケージ、ビルド中に直接ダウンロードするファイルなどに依存している可能性があります。

それぞれの提供元には、それぞれ異なるライフサイクルがあります。

ビルドを再現可能な状態に保つには、ROSリポジトリの保存だけでは環境の一部しか保存できません。

## StableBuildはROS 1とROS 2に対応

StableBuildは、UbuntuとサードパーティのAPTリポジトリを指定した日時の状態で保存し、ROS 1とROS 2の両方に対応しています。

Ubuntu 20.04上のROS 1では、次のように設定します。

```dockerfile
FROM ubuntu:20.04

ARG SB_API_KEY=...
ARG APT_PIN_DATE=2026-07-23T10:40:01Z

COPY ./sb-apt.sh /opt/sb-apt.sh
RUN bash /opt/sb-apt.sh load-apt-sources ubuntu ros1

RUN apt update && apt install -y python3-rosdep
```

ROS 1の対応環境はUbuntu 20.04 Focalです。StableBuildでは、Ubuntu 20.04について2026年7月23日までのスナップショットを利用できます（[公式ドキュメント](https://stablebuild.gitbook.io/ja/mirrors-and-caches/os-package-registry-ubuntu-debian-alpine)を参照）。そのため、ROS 1のビルドでは同日以前の日時を指定する必要があります。

ROS 2も同じ仕組みで利用できます。たとえば、次のように設定します。

```dockerfile
FROM ubuntu:22.04

ARG SB_API_KEY=...
ARG APT_PIN_DATE=2026-09-01T08:40:01Z

COPY ./sb-apt.sh /opt/sb-apt.sh
RUN bash /opt/sb-apt.sh load-apt-sources ubuntu ros2

RUN apt update && apt install -y ros-dev-tools
```

重要なのは、日時の指定です。

後から同じビルドを実行しても、APTは現在の上流リポジトリではなく、指定した日時のリポジトリ状態を使って依存関係を解決できます。

## 古いロボットには今も古いソフトウェアが必要

ROS 2が登場してから、すでに何年も経っています。[ROS 2初の正式リリースであるArdent Apaloneは、2017年12月に公開されました](https://www.ros.org/news/2017/12/ros-2-ardent-apalone-released.html)。ROS 1からの移行も、長い間推奨されてきました。

しかし、既存のロボット内部のソフトウェアを置き換えることは、新しいプロジェクトでROS 2を選ぶこととは違います。

ロボットには、ROS 1を前提として何年もかけてテストされてきたコード、ドライバー、ハードウェア連携、運用上の前提があるかもしれません。スタック全体の移行には時間がかかり、その間も古い環境を再びビルドする必要があります。

ROS 2に移行しても、根本的な依存関係の問題がなくなるわけではありません。Autowareの再現可能なビルドへの取り組みと、最近のROS DockerイメージのIssueは、どちらもROS 2に関するものでした。

古いビルドを再現可能な状態で残すには、ソースコードを保存するだけでは不十分です。

そのビルドが依存していたパッケージも必要です。

StableBuildには[無料のCommunityプラン](/pricing)があります。ROSとUbuntuのリポジトリを特定の日時に固定して試してみてください。
