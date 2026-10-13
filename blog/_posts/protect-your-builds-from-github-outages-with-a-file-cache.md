---
title: ファイルキャッシュで GitHub の障害からビルドを守る
date: 2026-10-13
category: 記事
description: GitHub Releases からファイルを直接取得するビルドは、GitHub に障害が起きると止まってしまいます。StableBuild のファイルミラーでアーティファクトをキャッシュし、GitHub に接続できないときもビルドを続けられるようにする方法を紹介します。
hero: https://cdn.prod.website-files.com/6558cb02ceb72f12e74052f7/6ac850e452383e7e269470e8_Invertocat_icecube.png
en_url: https://www.stablebuild.com/blog/protect-your-builds-from-github-outages-with-a-file-cache
---

GitHub も常に安定しているわけではありません。2026年8月だけでも、[複数のサービスでパフォーマンスが低下したインシデントが5件報告されています](https://github.blog/news-insights/company-news/github-availability-report-august-2026/)。

そのうち最大の障害は8時間近く続き、github.com、認証、Actions、各種 API など多くのサービスに影響しました。

ビルドのたびに GitHub からリリースアーティファクトを取得していると、ビルドが成功するかどうかも GitHub の稼働状況に左右されます。

最近、あるお客様のビルドでも、こうした依存関係が問題になりました。GitHub Releases で公開されているアーティファクトのダウンロードがタイムアウトし、ビルドが止まってしまったのです。

エラーだけを見ると、npm の問題のようでした。ログには次のような内容が出ていました。

```text
npm error code 1
npm error path /app/node_modules/sharp
npm error command failed
```

ログを読み進めると、本当の原因が次のようなパターンで書かれていました。

```text
sharp: Downloading https://github.com/example/project/releases/download/v1.2.3/artifact.tar.br
sharp: Installation error: Request timed out
```

このビルドでは npm で `sharp` をインストールしていました。このプロジェクトが使っていたバージョンの sharp は、インストール時にビルド済みの libvips アーカイブを GitHub Releases からダウンロードします。

つまり、クリーンビルドのたびに、GitHub に接続できること、そしてそのリリースアーティファクトが残っていることが前提になっていたわけです。

障害であれば、ビルドが失敗するのは一時的です。しかし、リリースが削除されたり、アクセス方針が変わったり、プロジェクトが放棄されたりすれば、そのファイルはいつまでも取得できなくなるおそれがあります。

## GitHub のリリースアーティファクトもビルドの依存関係

こうした依存関係が、Dockerfile に直接書かれていることもあります。

```dockerfile
RUN curl https://github.com/example/project/releases/download/v1.2.3/tool.tar.gz -o tool.tar.gz
```

これなら、ビルドが GitHub に依存していることは明らかです。

一方で、ずっと気づきにくいケースもあります。

今回のお客様の場合、依存関係はおおよそ次のようにつながっていました。

```text
npm install
  → sharp
  → インストールスクリプト
  → GitHub Releases
  → libvips アーカイブ
```

libvips アーカイブは、お客様が `package.json` に直接追加したものではなく、インストール中に別の依存関係が取得していたものです。

だからこそ見落としやすいのです。npm の依存関係をロックしていても、その奥に別の依存関係が隠れていることがあります。

## 毎回ダウンロードせず、キャッシュを使う

幸い、sharp では libvips のダウンロード元を環境変数で変更できました。

お客様はこれを使い、ダウンロードを [StableBuild のファイルミラー](https://stablebuild.gitbook.io/ja/mirrors-and-caches/file-mirror)経由に切り替えました。設定はおおよそ次のとおりです。

```dockerfile
ENV npm_config_sharp_libvips_binary_host=https://YOUR-DOMAIN.httpcache.stablebuild.com/sharp-cache/https://github.com/example/project/releases/download
```

最初のリクエストでは、これまでどおり GitHub からアーティファクトを取得し、StableBuild がそのファイルを保存します。以降のビルドでは、GitHub から改めてダウンロードせず、キャッシュ済みのコピーを使えます。

そのため、GitHub に一時的に接続できなくなっても、必要なファイルがキャッシュ済みであれば、ビルドが失敗することはありません。

なお、上記の環境変数は sharp 固有のものです。ダウンロード元の変え方はツールによって異なりますが、目的は変わりません。上流からまだ取得できるうちに、アーティファクトをキャッシュ経由で取得しておくことです。

## GitHub 以外でも同じことが起こる

今回は GitHub でしたが、ビルド中に直接ダウンロードするファイルの取得元はさまざまです。

ビルドが依存しうるものとしては、たとえば次のようなものがあります。

- GitHub のリリースアーティファクト
- S3 バケット
- ベンダーの配布サーバー
- CDN
- URL から取得するスクリプト
- 別の依存関係がダウンロードするビルド済みバイナリ

こうしたファイルは、ロックファイルやマニフェストに載るとは限りません。そのため、npm パッケージやコンテナイメージよりも見落とされがちです。

StableBuild のファイルミラーを使えば、こうした URL から取得するファイルをキャッシュできます。以降のビルドでは、毎回元のサーバーに頼ることなく、保存済みのコピーを使えます。

ただし、上流から取得できるうちに、一度 StableBuild を経由させておく必要があります。StableBuild に保存されていないファイルは、上流から消えてしまった後では復元できません。

## 障害で発覚する前に見つける

外部からのダウンロードには、Dockerfile やビルドスクリプトを見ればすぐにわかるものもあれば、依存関係を何層もたどって初めて見つかるものもあります。

そこでおすすめなのが、ときどきネットワークを切断した状態でクリーンビルドを実行し、どこで失敗するかを確かめることです。インストールやビルドの途中で GitHub、S3、CDN などの外部サービスに接続しようとする処理があれば、それも調べておくべきビルドの依存関係です。

見つかったものへの対処としては、依存関係のバージョンを上げる、アーティファクトを自分たちで保管する、キャッシュ経由で取得する、などが考えられます。大切なのは、ビルドが止まってから気づくのではなく、事前にその存在を把握しておくことです。

今回のお客様の場合、npm の依存関係を通じて、GitHub Releases 上のアーティファクトにも依存していました。ダウンロードを StableBuild 経由に切り替えたことで、以降のビルドは GitHub に頼らず、キャッシュ済みのコピーを使えるようになりました。

GitHub などで公開されているファイルにビルドが依存している場合は、[StableBuild の無料アカウントを作成](/pricing)し、[ファイルミラー](https://stablebuild.gitbook.io/ja/mirrors-and-caches/file-mirror)経由で保存してみてください。
