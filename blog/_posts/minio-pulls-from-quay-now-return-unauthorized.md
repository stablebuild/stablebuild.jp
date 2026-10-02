---
title: Quay から MinIO イメージをプルすると unauthorized が返されるようになりました
date: 2026-10-02
category: 記事
description: Docker Hub に続き、Quay でも MinIO イメージを認証なしでプルできなくなりました。同じリリースを StableBuild から引き続き取得できた理由と、ビルドが失敗した場合の対処法を紹介します。
hero: https://cdn.prod.website-files.com/6558cb02ceb72f12e74052f7/6abf6e22e872ec9d01ae081a_Quay%20padlock%20with%20recessed%20MinIO%20bird-p-1080.png
en_url: https://www.stablebuild.com/blog/minio-pulls-from-quay-now-return-unauthorized
---

9月17日、[MinIO のイメージが Docker Hub から消えたこと](/blog/minio-images-disappeared-from-docker-hub)について記事を書きました。

当時、私たちが必要としていた過去の MinIO イメージは、まだ Quay から取得できました。Docker Hub から Quay へ切り替えることで、失敗していたプルを再び動かすことができました。

10月2日、同じイメージをもう一度プルしてみました。

```text
docker pull quay.io/minio/minio:RELEASE.2025-09-07T16-13-09Z
```

Quay から返ってきたのは、次のエラーです。

```text
Error response from daemon: unauthorized: access to the requested resource is not authorized
```

認証なしでのプルは、`unauthorized` で失敗しました。このエラーだけでは、イメージが削除されたのかどうかはわかりません。確かなのは、認証なしでは取得できなくなったということです。

Docker Hub から MinIO イメージが消えた後、私たちは Quay を代わりの取得元として紹介しました。しかし今度は、同じリリースを Quay から認証なしでプルできなくなりました。

## 同じリリースを StableBuild から取得できました

StableBuild の Docker ミラーに Quay 対応を追加した際、テストのためにこの MinIO リリースを StableBuild 経由でプルしていました。MinIO はテストに使っているだけではありません。StableBuild の内部でも利用しています。

そのリリースはすでにキャッシュされていたため、10月2日にも同じコピーを再びプルできました。

ダイジェストは、イメージを最初にキャッシュした際に記録したものと一致しました。

```text
sha256:14cea493d9a34af32f524e538b8346cf79f3321eff8e708c1e2960462bd8936e
```

9月に使用したものと同じ MinIO リリースです。プルを成功させるために、古いバージョンへ切り替える必要はありませんでした。

## キャッシュされたコピーを取得できた理由

StableBuild の Docker ミラーは、プルスルーキャッシュとして動作します。

初めてミラー経由でイメージをプルすると、StableBuild が上流のレジストリからイメージを取得し、そのコピーを保存します。その後、同じタグをプルすると、保存済みのコピーが返されます。

MinIO イメージが一度キャッシュされた後は、そのイメージを再びプルする際に、Quay が認証なしで提供し続けているかどうかに依存しなくなります。

ただし、上流から取得できなくなる前にイメージをキャッシュしておく必要があります。StableBuild は、一度も保存していないイメージを復元することはできません。

MinIO イメージが Docker Hub から消えたとき、Quay は別の取得元として利用できました。しかし、それでも別のレジストリが同じイメージを提供し続けることに依存していました。

今回は、すでに自分たちのコピーを保存していました。

## MinIO を使ったビルドが失敗している場合

これらの MinIO イメージに依存するビルドが失敗し始めた場合は、まず自分たちで管理している場所に同じイメージが残っていないか確認してください。

たとえば、次のような場所です。

- 自社のコンテナレジストリ
- プルスルーキャッシュ
- CI ランナー
- 以前そのイメージをプルした開発マシン

コピーが見つかった場合は、ビルドが想定しているリリースとアーキテクチャであることを確認してください。記録してある場合は、ダイジェストも比較します。

取得できなくなったイメージを別の MinIO リリースに置き換えれば、ビルドを動かせるかもしれません。しかし、それはソフトウェアの変更であり、変更としてテストする必要があります。

キャッシュされたコピーがあれば時間を確保できますが、それだけでは一時的な対処にすぎません。今後も MinIO に依存し続けるのであれば、そのイメージを恒久的な解決策として扱うのではなく、現在もメンテナンスされている代替ソフトウェアの検討を始める価値があります。

Docker Hub からプルできなくなったとき、Quay は実用的な代替手段になりました。その後、Quay からの認証なしのプルも失敗するようになりましたが、StableBuild にコピーを保存していたため、同じイメージを再び取得できました。

上流からまだ取得できる依存関係については、[StableBuild の無料アカウントを作成](/pricing)して、[Docker ミラー](https://stablebuild.gitbook.io/ja/mirrors-and-caches/docker-mirror)からイメージを保存してみてください。
