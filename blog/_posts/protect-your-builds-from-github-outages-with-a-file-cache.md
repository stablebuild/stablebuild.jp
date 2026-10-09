---
title: ファイルキャッシュで GitHub の障害からビルドを守る
date: 2026-10-09
category: 記事
description: GitHub Releases から直接ファイルを取得するビルドは、GitHub の障害にも影響されます。StableBuild のファイルミラーを使ってアーティファクトをキャッシュし、同じファイルを繰り返し取得できるようにする方法を紹介します。
hero: https://cdn.prod.website-files.com/6558cb02ceb72f12e74052f7/6ac850e452383e7e269470e8_Invertocat_icecube.png
en_url: https://www.stablebuild.com/blog/protect-your-builds-from-github-outages-with-a-file-cache
---

GitHub にも調子の悪いときがあります。2026年8月だけでも、[GitHub は複数のサービスでパフォーマンス低下を引き起こしたインシデントを5件報告しました](https://github.blog/news-insights/company-news/github-availability-report-august-2026/)。

その月で最大の障害は約8時間にわたり、github.com、認証、Actions、各種 API など複数のサービスに影響しました。

ビルドを実行するたびに GitHub からリリースアーティファクトを取得している場合、ビルドの可用性も GitHub の可用性に左右されます。

最近、StableBuild のお客様のビルドでも同じような依存関係を見つけました。そのビルドは GitHub Releases に置かれたアーティファクトに依存しており、ダウンロードがタイムアウトするとビルドも停止していました。

一見すると、npm の問題のように見えました。エラーは次のような内容でした。

```text
npm error code 1
npm error path /app/node_modules/sharp
npm error command failed
```

さらに下を見ると、重要な部分がありました。

```text
sharp: Downloading https://github.com/example/project/releases/download/v1.2.3/artifact.tar.br
sharp: Installation error: Request timed out
```

このビルドでは、npm 経由で `sharp` をインストールしていました。このプロジェクトで使われていたバージョンでは、インストール処理中にビルド済みの libvips アーカイブも GitHub Releases からダウンロードしていました。

つまり、クリーンビルドを実行するたびに、GitHub に接続でき、そのリリースアーティファクトが引き続き存在している必要がありました。

障害によるビルド失敗は一時的なものかもしれません。一方、リリースの削除、アクセス方針の変更、プロジェクトの放棄などによって、その依存関係を利用できない状態が無期限に続く可能性もあります。

## GitHub のリリースアーティファクトもビルド依存関係です

こうした依存関係が明らかな場合もあります。

たとえば、Dockerfile に次のような記述があるかもしれません。

```dockerfile
RUN curl https://github.com/example/project/releases/download/v1.2.3/tool.tar.gz -o tool.tar.gz
```

これを見れば、ビルドが GitHub に依存していることはすぐにわかります。

一方で、はるかに見つけにくい場合もあります。

今回のお客様のビルドでは、依存関係がおおよそ次のようにつながっていました。

```text
npm install
  → sharp
  → install script
  → GitHub Releases
  → libvips archive
```

libvips アーカイブは、お客様が `package.json` に直接追加したものではありません。インストール中に別の依存関係が取得していました。

そのため、簡単に見落としてしまいます。npm の依存関係をロックしていても、その背後に別の依存関係が隠れていることがあります。

## 毎回ダウンロードする代わりにアーティファクトをキャッシュする

今回のケースでは、環境変数を使って sharp が libvips をダウンロードする場所を変更できました。

お客様はこの仕組みを利用して、[StableBuild のファイルミラー](https://stablebuild.gitbook.io/ja/mirrors-and-caches/file-mirror)経由でダウンロードするように設定しました。基本的な設定は次のようになります。

```dockerfile
ENV npm_config_sharp_libvips_binary_host=https://YOUR-DOMAIN.httpcache.stablebuild.com/sharp-cache/https://github.com/example/project/releases/download
```

最初のリクエストでは、引き続き GitHub からアーティファクトを取得します。StableBuild は、その際にファイルを保存します。

その後のビルドでは、同じアーティファクトを再び GitHub からダウンロードする代わりに、キャッシュされたコピーを利用できます。

GitHub に一時的に接続できなくても、すでにキャッシュされているファイルが必要というだけでビルドが失敗することはなくなります。

上記の環境変数は、今回の sharp の構成に固有のものです。外部ファイルのダウンロード方法はツールによって異なりますが、目的は同じです。上流から取得できるうちに、そのアーティファクトをキャッシュ経由で取得しておきます。

## 同じ問題は GitHub 以外にもあります

今回の上流サービスは GitHub でしたが、ビルド中に直接ダウンロードするファイルの取得元は、ほぼどこにでもあり得ます。

たとえば、ビルドは次のようなものに依存しているかもしれません。

- GitHub のリリースアーティファクト
- S3 バケット
- ベンダーのダウンロードサーバー
- CDN
- URL から取得するスクリプト
- 別の依存関係によってダウンロードされるビルド済みバイナリ

こうした依存関係は、必ずしもロックファイルやマニフェストに現れるとは限らないため、npm パッケージやコンテナレジストリのイメージよりも見落としやすい場合があります。

StableBuild のファイルミラーは、このような URL ベースのビルド入力をキャッシュできます。その後のビルドでは、毎回元のホストに依存する代わりに、保存済みのコピーを利用できます。

ただし、上流から取得できる間に、そのファイルを StableBuild 経由で取得しておく必要があります。すでに消えてしまったファイルを、StableBuild が保存していない状態から復元することはできません。

## 障害が起きる前に見つける

Dockerfile やビルドスクリプトを見ればすぐにわかる外部ダウンロードもあります。一方で、依存関係を何層もたどった先で初めて現れるものもあります。

ときどきネットワークに接続しない状態でクリーンビルドを実行し、予想外に壊れる箇所を確認するのも有効です。インストールやビルドの途中で GitHub、S3、CDN などの外部サービスに接続しようとした場合、調査すべき別のビルド入力が見つかったということです。

依存関係を更新する、アーティファクトを自分たちで保持する、キャッシュ経由で取得するなど、対応方法はいくつかあります。重要なのは、その依存関係がビルドを止める原因になる前に、存在を把握しておくことです。

今回のお客様の場合、npm の依存関係を使うことが、GitHub Releases に置かれたアーティファクトへの依存にもつながっていました。ダウンロードを StableBuild 経由に変更したことで、その後のビルドでは、GitHub が毎回同じファイルを配信しなくてもキャッシュ済みのコピーを利用できるようになりました。

GitHub などに置かれたファイルにビルドが依存している場合は、[StableBuild の無料アカウントを作成](/pricing)して、[ファイルミラー](https://stablebuild.gitbook.io/ja/mirrors-and-caches/file-mirror)経由で保存してみてください。
