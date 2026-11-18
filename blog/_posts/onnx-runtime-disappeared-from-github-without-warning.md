---
title: ONNX Runtime のリポジトリが GitHub から突然消えました
date: 2026-11-18
category: 記事
description: 11月18日、Microsoft の ONNX Runtime のリポジトリが GitHub から突然消えました。PyPI からインストールしている環境には影響がなかった一方、GitHub からファイルを直接取得していたビルドは失敗するようになりました。バージョンを固定していても防げない理由と、その備え方を紹介します。
hero: https://cdn.prod.website-files.com/6558cb02ceb72f12e74052f7/6afd5cfb81a584aee1b2b72d_ONNX%20Runtime%20in%20a%20frosty%20ice%20cube.png
en_url: https://www.stablebuild.com/blog/onnx-runtime-disappeared-from-github-without-warning
---

11月18日、Microsoft の ONNX Runtime のリポジトリが、予告なく GitHub から消えました。バージョンをきちんと固定していたビルドでも、取得先がなくなれば失敗します。何が起きたのかと、こうした事態への備え方をまとめました。

## 影響を受けたビルド

Python から ONNX Runtime を使う場合は、`pip install onnxruntime` で PyPI からインストールするのが一般的です。PyPI のパッケージはそのまま残っていたため、こうした環境には影響はありませんでした。

影響を受けたのは、GitHub から直接ファイルを取得していたビルドです。ソースからビルドするためにリポジトリをクローンしていた場合や、C/C++ のアプリケーションに組み込むビルド済みライブラリをリリースページからダウンロードしていた場合は、取得先そのものがなくなりました。

GitHub への依存は、気づきにくいところに潜んでいることもあります。[以前の記事](/blog/protect-your-builds-from-github-outages-with-a-file-cache)では、npm で `sharp` をインストールすると、その途中で GitHub Releases から libvips のアーカイブがダウンロードされていた例を紹介しました。

## バージョン固定の限界

バージョンを固定しておけば、どのバージョンを使うかは決まります。ただし、そのファイルを今後も取得できるかどうかは配布元次第です。今回のように配布元からファイルが消えてしまえば、バージョンを正しく指定していてもビルドは通りません。

## 依存関係を手元に残す方法

こうした事態に備えるには、ビルドに必要なものを自分たちで持っておく必要があります。方法としては、主に次の3つがあります。

- 依存関係のソースコードを自分たちのリポジトリに取り込む
- ビルド済みのアーティファクトを自社のストレージに保存する
- ビルドと上流の取得元の間にキャッシュを置く

StableBuild を使えば、こうしたキャッシュを自前で構築・運用する必要はありません。URL から取得するファイルのほか、Docker イメージ、PyPI や Ubuntu、Debian、Alpine のパッケージ、Hugging Face のファイルなど、ビルドで使う依存関係を保存しておけるので、上流から消えたあとも同じものを取得できます。

今回はたまたま ONNX Runtime でしたが、同じことはどの依存関係にも起こりえます。ビルドに必要なファイルは、まだ取得できるうちに手元に残しておきましょう。

StableBuild は [Community プラン](/pricing)なら無料で使えます。いまのビルドが依存しているファイルやパッケージの保存から、ぜひ試してみてください。
