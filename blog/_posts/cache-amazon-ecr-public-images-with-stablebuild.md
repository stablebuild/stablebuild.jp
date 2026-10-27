---
title: Amazon ECR Public のイメージを StableBuild でキャッシュする
date: 2026-10-27
category: 記事
description: StableBuild の Docker ミラーが Amazon ECR Public に対応しました。ECR Public のイメージをキャッシュし、上流のタグが変更または削除されても同じイメージを取得できるようにする方法を紹介します。
hero: https://cdn.prod.website-files.com/6558cb02ceb72f12e74052f7/6ae01998666accf5390eaebc_ECR_icecube.png
en_url: https://www.stablebuild.com/blog/cache-amazon-ecr-public-images-with-stablebuild
---

StableBuild の Docker ミラーが Amazon ECR Public（`public.ecr.aws`）に対応しました。

ミラー経由でプルしたイメージは保存され、以後は内容が変わりません。ECR Public のタグを一度キャッシュすると、上流のタグが変更または削除されても、その後のビルドでは StableBuild から同じイメージを取得できます。

## ECR Public のイメージも消えることがある

2026年5月、AWS は Bitnami の317個のコンテナイメージリポジトリを[6月10日以降に ECR Public から削除すると発表しました](https://aws.amazon.com/blogs/containers/bitnami-image-removal-from-ecr-public/)。削除後は、`public.ecr.aws/bitnami/` からイメージをプルできなくなると説明しています。

AWS は、引き続き必要なイメージをミラーリングし、今後の上流の変更に備えてプルスルーキャッシュを利用することを推奨しました。

イメージを参照するソースコードやビルド設定が変わらないまま、そのイメージ自体がレジストリから消えてしまうことがあります。

## StableBuild 経由で ECR Public を利用する

現在、Dockerfile で ECR Public からイメージを直接プルしている場合は、

```dockerfile
FROM public.ecr.aws/aws-cli/aws-cli:2.31.0
```

先頭に StableBuild の Docker ミラードメインを追加します。

```dockerfile
FROM your-domain.dockermirror.stablebuild.com/public.ecr.aws/aws-cli/aws-cli:2.31.0
```

最初のプルでは、ECR Public からイメージを取得して StableBuild に保存します。その後、同じタグをプルすると、保存済みのコピーが返されます。

キャッシュされたタグは変更されません。配布元が後から上流のタグの参照先を変更しても、StableBuild は最初に保存したイメージを引き続き提供します。

ECR Public にはプル回数の制限もあります。現在、AWS では未認証のイメージプルは1秒あたり1回、認証済みの場合はデフォルトで1秒あたり10回までです。一度イメージをキャッシュすれば、その後 StableBuild からプルするときに、ECR Public から再度取得する必要はありません。

現在対応しているのは Amazon ECR Public で、プライベート ECR レジストリにはまだ対応していません。対応が必要な場合は、[support@stablebuild.com](mailto:support@stablebuild.com) までお気軽にご相談ください。

## 上流からイメージが消えた後も再ビルドする

一度イメージをキャッシュすれば、その後の再ビルドは、ECR Public や配布元がそのイメージを提供し続けることに依存しなくなります。

ただし、まずイメージを StableBuild 経由で取得しておく必要があります。ミラー経由でプルする前に上流から消えてしまったイメージを、StableBuild が後から復元することはできません。

ビルドが ECR Public のイメージに依存しているなら、上流からまだ取得できるうちにキャッシュしておく必要があります。

StableBuild の [Community プランは無料](/pricing)です。すでにビルドで利用している ECR Public のイメージで試してみてください。設定方法は、[Docker ミラーのドキュメント](https://stablebuild.gitbook.io/ja/mirrors-and-caches/docker-mirror)をご覧ください。
