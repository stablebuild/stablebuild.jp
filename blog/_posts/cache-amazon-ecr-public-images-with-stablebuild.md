---
title: Amazon ECR Public のイメージを StableBuild でキャッシュする
date: 2026-10-27
category: 記事
description: StableBuild の Docker ミラーが Amazon ECR Public に対応しました。ECR Public のイメージを一度キャッシュしておけば、上流でタグが差し替えられたり削除されたりしても、同じイメージでビルドできます。
hero: https://cdn.prod.website-files.com/6558cb02ceb72f12e74052f7/6ae01998666accf5390eaebc_ECR_icecube.png
en_url: https://www.stablebuild.com/blog/cache-amazon-ecr-public-images-with-stablebuild
---

StableBuild の Docker ミラーが、Docker Hub、GitHub Container Registry、NVIDIA NGC、Quay.io に加えて、新たに Amazon ECR Public（`public.ecr.aws`）にも対応しました。

ミラー経由でプルしたイメージは StableBuild に保存され、その後は内容が変わりません。一度キャッシュしたタグなら、上流で差し替えられたり削除されたりしても、以降のビルドでは StableBuild から同じイメージを取得できます。

## ECR Public から消えた Bitnami のイメージ

Dockerfile で参照しているイメージが、いつまでもレジストリに残っているとは限りません。ECR Public も例外ではありません。

2026年5月、AWS は Bitnami の317のコンテナイメージリポジトリを、6月10日以降に ECR Public から[削除すると発表しました](https://aws.amazon.com/blogs/containers/bitnami-image-removal-from-ecr-public/)。削除後は `public.ecr.aws/bitnami/` からプルできなくなるとしたうえで、引き続き必要なイメージはミラーリングし、今後の上流の変化にはプルスルーキャッシュで備えるよう勧めていました。

## ミラー経由でのプル

使い方は、イメージ名の先頭に StableBuild の Docker ミラーのドメインを付けるだけです。たとえば、ECR Public から直接プルしている次の Dockerfile は、

```dockerfile
FROM public.ecr.aws/aws-cli/aws-cli:2.31.0
```

次のように書き換えます。

```dockerfile
FROM your-domain.dockermirror.stablebuild.com/public.ecr.aws/aws-cli/aws-cli:2.31.0
```

初回のプルでは、StableBuild が ECR Public からイメージを取得して保存し、2回目以降は同じタグに対して保存済みのコピーを返します。キャッシュしたタグの内容は変わらないので、配布元が後からタグの参照先を変えても、StableBuild は最初に保存したイメージを返し続けます。

ECR Public には、プル回数の制限もあります。現在の AWS の上限は、未認証のプルが1秒あたり1回、認証済みのプルがデフォルトで1秒あたり10回です。キャッシュ済みのイメージを StableBuild からプルするときは ECR Public から取得し直さないため、この制限の影響を受けません。

なお、今回対応したのは Amazon ECR Public のみで、プライベートの ECR レジストリにはまだ対応していません。ご希望の場合は、[support@stablebuild.com](mailto:support@stablebuild.com) までお気軽にご相談ください。

## 上流から消えた後の再ビルド

一度キャッシュしたイメージは、ECR Public や配布元が提供をやめても、再ビルドに使い続けられます。ただし、StableBuild が保存できるのは、ミラー経由で一度でもプルしたイメージだけです。ミラーを通す前に上流から消えたイメージを、後から復元することはできません。ECR Public のイメージに依存しているビルドがあるなら、キャッシュするのは上流からまだ取得できる今のうちです。

StableBuild は [Community プラン](/pricing)なら無料で使えます。今のビルドで使っている ECR Public のイメージで、ぜひ試してみてください。設定方法は [Docker ミラーのドキュメント](https://stablebuild.gitbook.io/ja/mirrors-and-caches/docker-mirror)で紹介しています。
