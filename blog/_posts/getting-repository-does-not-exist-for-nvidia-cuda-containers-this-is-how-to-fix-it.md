---
title: NVIDIA CUDAコンテナで「Repository does not exist」が出たら？NVIDIAにビルドを壊されないための対策
date: 2024-05-17
category: 記事
description: NVIDIAはEOLを迎えたCUDAコンテナイメージをDocker HubとNGCから削除します。過去のイメージに依存したビルドを壊さずに保つ方法を解説します。
hero: https://cdn.prod.website-files.com/6558cb02ceb72f12e74052f7/6646672849647bb520bbd5c5_65775edcdc86bcc72d3a594b_docker.png
en_url: https://www.stablebuild.com/blog/getting-repository-does-not-exist-for-nvidia-cuda-containers-this-is-how-to-fix-it
---

2022年10月に発表されたNVIDIAの新しいコンテナイメージサポートポリシーは、CUDAコンテナイメージを日常の開発フローで利用している開発者にとって大きな課題となっています。イメージがEOL（サポート終了）を迎えるとDocker HubとNGCから削除され、それまで問題なく動いていたビルドがイメージレイヤーの欠落によって壊れてしまうためです。

エラーは次のような形で現れます。

```
Error response from daemon: manifest for nvidia/cuda:12.0.1 not found: manifest unknown: manifest unknown
```

古いNVIDIAコンテナイメージをプルしようとして「repository does not exist or may require 'docker login'」というエラーに遭遇し、頭を抱えた開発者は少なくありません。これは、イメージがEOLを迎えて削除されたために起こります。そのイメージに依存していたビルドは、そのまま動かなくなります。複雑なビルドパイプラインを持つプロジェクトや、古いバージョンのCUDA Toolkitに依存しているプロジェクトでは、特に深刻な影響が出ます。

さらにNVIDIAは、公開済みのタグを後から更新することもあります。これもビルドを壊す原因になります。

## なぜこうなるのか

NVIDIAは2022年10月28日に、CUDAコンテナイメージの新しいサポートポリシーを発表しました。このポリシーはNVIDIA側の運用を楽にする一方で、コンテナイメージに依存する開発者には影響を及ぼします。

### NVIDIAのサポートポリシー

NVIDIAの新しいポリシーは、次のような課題への対応を目的としています。

- **セキュリティ**: 古いイメージには未修正の脆弱性が含まれている可能性があり、セキュリティリスクとなります。
- **持続可能性**: ほとんど使われないイメージを大量に保持し続けることは、NVIDIAにとって負担が大きくなります。
- **移行の停滞**: 古いイメージが残っていると新しいバージョンへの移行が進まず、開発の妨げになります。

これらの主張には妥当な面もありますが、結果としてビルドは予期しないタイミングで壊れ、開発者が自分で制御できなくなってしまいます。

## StableBuildでイメージをキャッシュし、ビルドを止めない

StableBuildは、Dockerイメージを無期限にキャッシュするプラットフォームを提供することで、この問題を解決します。NVIDIAが公式リポジトリからイメージを削除・上書きしたあとでも、StableBuildを利用していればそのイメージにアクセスし、プルし続けられます。

**仕組みは次のとおりです。**

- **不変のDockerミラー**: StableBuildは一度プルしたイメージを常に同じ内容で提供します。バージョンが変わるのは、利用者が自分で切り替えたときだけです。
- **マルチアーキテクチャ対応**: 複数のアーキテクチャ向けに同じイメージを取得しておくため、後から別のアーキテクチャで実行しても問題なく動作します。

StableBuildを使えば、NVIDIAのEOLポリシーによって公式リポジトリからイメージが削除されても、開発フローを止めずに済みます。

## StableBuildに登録する

StableBuildにはCommunityプランがあり、イメージのキャッシュ機能を無料で利用できます。NVIDIAのイメージ削除ポリシーによる混乱から開発フローを守るうえで、有力な選択肢になります。

[今すぐ無料でStableBuildに登録](https://dashboard.stablebuild.com/?lang=ja)して、コンテナイメージの提供状況が変わってもプロジェクトが影響を受けない状態にしましょう。
