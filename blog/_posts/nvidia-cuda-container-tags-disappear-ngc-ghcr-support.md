---
title: NVIDIA CUDAコンテナタグは利用できなくなることがある - StableBuildがNVIDIA NGCとGitHub Container Registryに対応
date: 2026-09-16
category: 記事
description: NVIDIA CUDAのコンテナタグは、細かく指定して固定していても消えることがあります。StableBuildがNVIDIA NGCとGitHub Container Registryに対応し、ビルドが依存するコンテナイメージを保持できるようになりました。
hero: https://cdn.prod.website-files.com/6558cb02ceb72f12e74052f7/6aa3ac167d409ae304759273_NVIDIA%20CUDA%20Container%20Tags%20Can%20Disappear.jpeg
en_url: https://www.stablebuild.com/blog/nvidia-cuda-container-tags-disappear-ngc-ghcr-support
---

**NVIDIA CUDA**イメージを、パッチリリース、イメージの種類、OSまで細かく指定して固定したとします。

```
nvidia/cuda:11.2.1-base-ubuntu20.04
```

これなら安全に見えます。

latestを指定しているわけでも、単にCUDA 11を指定しているわけでもありません。必要なCUDAのリリース、イメージの種類、ベースとなるUbuntuのリリースまで、すべて明示されています。

ところが、ある日、同じpullを再度実行すると、次のエラーが返ってきます。

```
$ docker pull nvidia/cuda:11.2.1-base-ubuntu20.04

Error response from daemon: manifest for nvidia/cuda:11.2.1-base-ubuntu20.04 not found:
manifest unknown: manifest unknown
```

Dockerfileに問題はありません。

**イメージタグそのものがなくなったのです。**

これは仮定の話ではありません。このタグは、以前公開されていたGPU関連のワークフローやドキュメントで使用されていましたが、2026年8月にpullを試みたところ、上記のエラーが返されました。[NVIDIAの公式サポートポリシー](https://gitlab.com/nvidia/container-images/cuda/-/blob/master/doc/support-policy.md)には、なぜこのようなことが起こるのかが説明されています。

AI、機械学習、科学技術計算をはじめ、GPUを多用するソフトウェアを保守するチームにとって、通常の再ビルドが突然、緊急の依存関係移行へと変わります。

コードは変更していません。

**変わったのは、NVIDIA側のコンテナライフサイクルです。**

## NVIDIA CUDAコンテナタグには有効期間がある

[NVIDIAのCUDAコンテナに関するドキュメント](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/cuda)には、『CUDAイメージのコンテナタグには有効期間がある』と明記されています。

NVIDIAのサポートポリシーでは、同梱されているドライバーがEOL（サポート終了）に達すると、CUDAイメージ一式もEOLになる場合があります。また、CUDA Toolkitの各バージョンでサポートされるのは最新のポイントリリースのみです。CUDAイメージ一式がEOLに達すると、その6か月後に該当するタグがDocker HubとNVIDIA NGCから削除されます。

同ポリシーでは、NVIDIAが同時にサポートするCUDAのメジャーバージョンは2つとされています。公式の例では、CUDA 13のリリース後にCUDA 11がEOLになると説明されています。すべてのCUDA 11タグに共通する公開削除日が定められているわけではありませんが、理由は明確です。古いCUDAイメージが永続的に提供されることを前提としていません。

NVIDIA側にも正当な理由があります。古いイメージには未修正の脆弱性が含まれる可能性があり、ほとんど利用されない大容量のコンテナレイヤーを何年も維持するには、実際にインフラコストがかかります。

しかし、ビルドする側にとって、直近の結果は変わりません。

**削除されたイメージに依存しているビルドは失敗します。**

StableBuildは以前の記事[『NVIDIA CUDAコンテナで「Repository does not exist」と表示される場合の対処法』](/blog/getting-repository-does-not-exist-for-nvidia-cuda-containers-this-is-how-to-fix-it)でも、この問題を取り上げました。今回のリリースではさらに対応範囲を広げ、StableBuildのDockerミラーがDocker Hubに加え、**NVIDIA NGC**とGitHub Container Registryをサポートするようになりました。

## 細かく指定したタグでも消える可能性がある

`11.2.1-base-ubuntu20.04`の例が示唆的なのは、指定方法に問題があるようには見えない点です。

- 11.2.1はCUDAのリリースを指定しています。
- baseはイメージの種類を指定しています。
- ubuntu20.04はベースとなるOSを指定しています。

これは、latestを基にビルドするよりもはるかに適切です。

**しかし、指定が具体的であることと、永続的に利用できることは別問題です。**

タグが存在している間は、必要なイメージを正確に特定できます。しかし、そのアーティファクトをレジストリの運営者が永久に提供し続けることまで保証するものではありません。

そのため、独自にコピーを作成する開発者もいます。Docker Hub上のあるコミュニティCUDAミラーは、存在理由を[『Just to make sure nvidia does not remove the image needed for QLoRA finetuning（QLoRAのファインチューニングに必要なイメージをNVIDIAに削除されないようにするため）』](https://hub.docker.com/r/pervonrosen/cuda)と一文で説明しています。

思わず笑ってしまう表現ですが、同時に、実際に採用されている継続性対策でもあります。上流側で整理される前に、必要なイメージを確保しておくという方法です。

災害復旧計画が『誰かがミラーしてくれていることを願う』というものなら、より計画的な対策が必要でしょう。

## CUDA、NGC、NVCR、NVIDIA Container Toolkitの基本用語

この領域で使われるNVIDIAの名称は、GPUビルドの不具合を調査する段階になるまで、どれも同じものに見えることがあります。

CUDAは、GPUを汎用計算に利用するためのNVIDIAの並列コンピューティングプラットフォームです。[NVIDIA CUDA Toolkit](https://gitlab.com/nvidia/container-images/cuda/-/blob/master/doc/README.md)には、GPUアクセラレーション対応アプリケーションの開発に必要なランタイム、ライブラリ、コンパイラ、開発ツールが含まれます。

**NVIDIAコンテナ**は、その環境の一部をコンテナイメージとしてまとめたものです。これにより、毎回CUDAスタック全体を一から構築する必要がなくなります。NVIDIAは、CUDAとOSの各バージョンに応じて、base、runtime、developmentのイメージを公開しています。

[NVIDIA NGC](https://docs.nvidia.com/ngc/latest/ngc-catalog-user-guide.html)は、GPUおよびAIソフトウェアを提供するNVIDIAのカタログ兼レジストリエコシステムです。コンテナレジストリのホスト名は`nvcr.io`です。

[NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/)は、これとは異なるものです。ホスト側で動作するランタイムツールであり、Dockerやcontainerdなどのコンテナランタイムを通じてコンテナ内からNVIDIA GPUを利用できるようにします。つまり、コンテナからGPUを使えるようにするためのツールであり、コンテナイメージをレジストリに保存しておくためのものではありません。

この違いは重要です。StableBuildが解決するのはイメージの可用性に関する問題であり、NVIDIAのGPUランタイムスタックを置き換えるものではありません。

## NVCRとGHCRは二者択一ではない

一見すると、『nvcr.ioとghcr.ioのどちらを選ぶか』という比較に思えます。しかし、多くのエンジニアリングチームにとって、これは二者択一の問題ではありません。

`nvcr.io`は**NVIDIA NGC**のレジストリエンドポイントです。`ghcr.io`で提供される[GitHub Container Registry](https://docs.github.com/ja/packages/working-with-a-github-packages-registry/working-with-the-container-registry)は、GitHubの汎用OCIコンテナレジストリです。

1つのAIビルドが両方に依存し、さらにDocker Hub、PyPI、Ubuntuリポジトリ、URLから直接取得する複数のファイルも利用することは珍しくありません。

**実運用上の問題は、1つのビルドが複数の異なる上流ライフサイクルを引き継ぐことです。**

| レジストリ | 概要 | ビルドが依存する条件 |
| :---- | :---- | :---- |
| NVIDIA NGC / nvcr.io | NVIDIAのGPU・AI向けコンテナレジストリ | NVIDIAがイメージを保持し、提供し続けること |
| GitHub Container Registry / ghcr.io | GitHubが提供するDocker・OCIイメージのレジストリ | 公開者がイメージを保持し、GitHubが提供を継続すること |
| Docker Hub | 汎用の公開コンテナレジストリ。nvidia/cudaもホストする | 公開者のライフサイクル、レジストリの可用性、レート制限 |

レジストリが増えるたびに、ビルドが依存する上流側のライフサイクルも1つ増えます。

タグの参照先が変わる、イメージが消える、認証情報が失効する、あるいはCIが必要とするタイミングでサービスが利用できなくなる可能性があります。

目標は、公開レジストリの利用をやめることではありません。公開レジストリは優れた配布システムです。必要なのは、それらを永続的な履歴アーカイブとして扱わないことです。

## タグを固定することとイメージを保持することは同じではない

ここでは、関連する3つの考え方が同じものとして捉えられがちです。

### 1. タグは人が読める参照名を提供する

`11.2.1-base-ubuntu20.04`のようなタグは具体的で理解しやすいものです。しかし、レジストリが管理する参照名であることに変わりはなく、レジストリ側で削除できます。

### 2. ダイジェストはイメージを正確に識別する

[GitHubのContainer Registryドキュメント](https://docs.github.com/ja/packages/working-with-a-github-packages-registry/working-with-the-container-registry)では、同一内容のイメージを確実に指定する必要がある場合、SHAダイジェストでpullすることを推奨しています。

これは適切な方法です。

**ただし、ダイジェストが答えるのは『どのイメージか』という問いです。それだけでは、『3年後もレジストリがそのイメージを提供しているか』という問いには答えられません。**

[StableBuildのDockerミラーに関するドキュメント](https://stablebuild.gitbook.io/ja/mirrors-and-caches/docker-mirror)でも、同じ違いを説明しています。ハッシュで固定すれば同一性は守れますが、イメージ自体が上流側から削除されれば、ビルドが失敗する可能性は残ります。

### 3. 保持によって継続的な可用性を確保する

長期間維持するビルドには、同一性と保持の両方が必要です。つまり、正確なイメージを特定できることと、必要なときにそのコピーが残っていることです。

この隔たりを埋めるために設計されたのが、不変のプルスルーキャッシュです。

## StableBuildがNVIDIA NGCとGitHub Container Registryに対応

[StableBuildのDockerミラー](/)は、Docker Hub、GitHub Container Registry、**NVIDIA NGC**に対応する不変のプルスルーキャッシュとして機能します。

StableBuildがイメージを初めてpullすると、上流レジストリからイメージを取得して保存します。その後、同じキャッシュ済みタグをpullすると、公開レジストリに過去のビルド環境の再現を委ねるのではなく、保存済みのイメージが返されます。

実際には、次のように機能します。

- NVIDIAが後からEOLのCUDAタグを削除しても、StableBuildがすでに取得していれば、保存されたイメージをビルドで引き続き利用できます。
- 上流側の可変タグが後から別のイメージを指すようになっても、StableBuildにキャッシュされたタグが自動的に追従することはありません。
- NGCとGHCRの両方から公開イメージを取得するビルドでも、レジストリごとに場当たり的なキャッシュを用意せず、同じ不変ミラーの仕組みを適用できます。

StableBuildは、NGCやGHCRを置き換えるものではありません。ビルドと上流レジストリの間に入り、実際にビルドで使用したイメージを保持します。

**重要なのはタイミングです。上流のコピーがなくなってからではなく、その前にイメージを保持してください。**

## Dockerfileで変更する内容

基本的な変更は、意図的にシンプルです。上流レジストリから直接イメージを取得する代わりに、元のイメージパスの先頭へStableBuildのDockerミラードメインを追加します。

たとえば、**NVIDIA NGC**から直接取得する場合は次のようになります。

```
FROM nvcr.io/nvidia/cuda:12.3.1-runtime-ubuntu22.04
```

StableBuildを経由する場合は、次のように変更します。

```
FROM your-domain.dockermirror.stablebuild.com/nvcr.io/nvidia/cuda:12.3.1-runtime-ubuntu22.04
```

GitHub Container Registryでも同じパターンを使用します。

```
# GHCRから直接取得
FROM ghcr.io/astral-sh/uv:0.5.11

# StableBuild経由で取得
FROM your-domain.dockermirror.stablebuild.com/ghcr.io/astral-sh/uv:0.5.11
```

つまり、元のレジストリパスはそのままにして、その前にStableBuildのDockerミラードメインを追加します。

your-domainという文字列をそのまま使用せず、アカウントに割り当てられた正確なStableBuildミラードメインを指定してください。

**新しいビルドシステムを導入するわけではありません。Dockerfileは引き続き必要なイメージを指定します。StableBuildが、そのイメージを保持する役割を担います。**

## AIと機械学習のビルドで特に重要な理由

GPU環境では、特定のバージョンへの依存が長く残りやすく、一般的なアプリケーションコンテナほど簡単には更新できません。

モデルの学習や推論を行うプロジェクトは、特定のCUDAリリース、cuDNNバージョン、PyTorchビルド、ドライバーの互換期間、Python環境、OSベースに依存している場合があります。1つを更新すると、ほかの要素も更新しなければならないことがあります。

そのため、『最新のCUDAイメージへ移行すればよい』という対応は、言葉ほど簡単ではありません。

過去の研究環境を再構築したい場合もあれば、学習結果を再現する必要がある場合もあります。本番環境のモデルが2年間変わっておらず、無関係なデプロイのためにGPUスタック全体を移行する合理的な理由がない場合もあります。

モデル自体は残っていても、

**そのモデルのビルドや実行に必要な環境は残っていない可能性があります。**

開発者がQLoRAなどの古いワークフロー向けに個人用のCUDAミラーを作るのも、このためです。古いソフトウェアを永久に使い続けたいとは限りません。計画的に更新できるようになるまで、既知の環境を再構築可能な状態に保ちたいのです。

コンテナの保持は、完全な再現性を確保するための要素の1つにすぎません。モデルの重み、Python wheel、aptパッケージ、外部ダウンロード、ビルドツール、データ、非決定的な学習動作なども影響します。StableBuildは、こうした依存関係の複数の領域をカバーしています。より広いアプローチについては、[『依存関係が消えても再現可能なビルドを維持する』](/blog/reproducible-builds-when-dependencies-disappear)で解説しています。

## 古いCUDAイメージを保持しても永続的な運用を推奨するわけではない

ここには、セキュリティ上の重要な注意点があります。

NVIDIAが古いイメージをEOLにするのには正当な理由があります。サポートが終了したコンテナには、既知の脆弱性や古いコンポーネントが含まれている可能性があります。

StableBuildがイメージを保持することは、脆弱性のあるソフトウェアを本番環境で無期限に使い続けることを推奨するものではありません。

**保持することで、移行のタイミングを自ら管理できるようになります。**

過去の環境を再構築して本番環境の問題を調査する、以前の結果を再現する、新しいCUDAスタックをテストする、といった対応が可能になります。上流側の削除に急かされるのではなく、アプリケーションの準備が整った時点で移行できます。

再現性の確保とパッチ適用は、相反するものではありません。成熟したワークフローには、既知の過去環境と、サポート対象の環境へ管理された形で移行する経路の両方が必要です。

## 開発者から想定される質問

### NVIDIAは本当にCUDAコンテナタグを削除するのか

はい。NVIDIAが公開しているCUDA Container Support Policyには、EOLタグがサポート期間の終了後にDocker Hubと**NVIDIA NGC**から削除されると明記されています。また、タグが削除されると基盤となるイメージレイヤーも利用できなくなるため、通常のコンテナpullが失敗する可能性があるとNVIDIAは警告しています。

### CUDA 11は利用できなくなるのか

NVIDIAのポリシーでは、同時にサポートするCUDAのメジャーバージョンは2つとされ、公式例としてCUDA 13のリリース後にCUDA 11がEOLになることが示されています。削除時期はイメージ一式やタグによって異なるため、『この日にすべてのCUDA 11が消える』という単一の公開期限はありません。しかし、古いCUDA 11タグが利用できなくなるリスクはすでに現実のものです。`11.2.1-base-ubuntu20.04`の例が、その理由を示しています。

### ダイジェストでpullすれば十分か

ダイジェストは、必要なイメージ内容をレジストリに正確に指定するという問題を解決します。

しかし、その内容をレジストリが永久に保持し、提供し続けることまでは保証しません。同一性と可用性は別のものです。

### nvcr.ioとghcr.ioの違いは何か

`nvcr.io`は**NVIDIA NGC**のコンテナレジストリエンドポイントです。`ghcr.io`はGitHub Container Registryです。それぞれ異なるイメージエコシステムをホストしており、同じビルドが両方に依存することもあります。StableBuildは現在、どちらについても不変のプルスルーキャッシュに対応しています。

### NVIDIA Container Toolkitは引き続き必要か

はい。ホストからNVIDIA GPUをDockerなどの対応ランタイムに公開する必要がある場合は、引き続き必要です。StableBuildが変更するのは、コンテナイメージの取得元と保持方法です。コンテナ内でGPUを利用可能にするNVIDIAのランタイムコンポーネントを置き換えるものではありません。

### すでに消えたイメージをStableBuildで復元できるか

StableBuildは、すでに取得したイメージであれば継続して提供できます。ただし、StableBuildが一度も取得しないまま上流側から消えたアーティファクトを、必ず復元できるとは限りません。そのため、依存関係を固定する最適なタイミングは、それがまだ利用可能なときです。

## 必要になる前に固定する

現在の実際のビルドが**NVIDIA CUDA**、NGC、GHCRのイメージに依存しているなら、本番環境の再ビルド時に上流タグがまだ存在するかを初めて確認するような状況は避けてください。

**利用できるうちに、StableBuild経由でpullしてください。**

そうすれば、NVIDIAが古いCUDAイメージを廃止した場合、GitHubパッケージが削除された場合、あるいはほかの上流レジストリが依存対象を変更した場合でも、相手側の都合に合わせて環境を再構築する必要はありません。

**AIビルドを変更するのは、上流側でイメージが削除されたときではなく、自分たちが必要だと判断したときであるべきです。**

StableBuildの[Communityプランは無料](/pricing)です。まずは、実際のビルドが依存しているコンテナを1つ保持し、自社のワークフローに適しているかを確認できます。
