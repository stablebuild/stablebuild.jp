---
title: ONNX Runtime が予告なく GitHub から消えました
date: 2026-11-18
category: 記事
description: Microsoft の ONNX Runtime リポジトリが予告なく GitHub から消えました。PyPI からのインストールには影響がなくても、GitHub 上のソースコードやリリースファイルに直接依存するビルドには、依存関係を手元に残しておく必要があります。
hero: https://cdn.prod.website-files.com/6558cb02ceb72f12e74052f7/6afd5cfb81a584aee1b2b72d_ONNX%20Runtime%20in%20a%20frosty%20ice%20cube.png
en_url: https://www.stablebuild.com/blog/onnx-runtime-disappeared-from-github-without-warning
---

今日、Microsoft の ONNX Runtime リポジトリが、予告なく GitHub から消えました。

ほとんどのユーザーには、おそらく影響はありませんでした。Python では通常、`pip install onnxruntime` でインストールしますが、PyPI のパッケージは引き続き利用できました。

しかし、GitHub 上のソースコード、リリースファイル、C/C++ 向けのアーティファクトに直接依存しているビルドもあります。そうしたビルドでは、依存関係が突然なくなりました。

今回の件で改めて分かるのは、依存関係を固定するだけでは足りないということです。

依存関係を固定すれば、ビルドで使用するバージョンを指定できます。しかし、そのバージョンが後からも取得できるとは限りません。

これを防ぐ方法として、依存関係を自分たちのリポジトリに含める、自社でアーティファクトを保存する、あるいはビルドと上流の取得元の間にキャッシュを置く、といった選択肢があります。重要なのは、ソフトウェアのビルドに必要な入力を、自分たちで保持しておくことです。

以前にも、npm で `sharp` をインストールするときに、GitHub Releases 上の libvips アーカイブにも依存していた事例を紹介しました。

[GitHub のファイルキャッシュに関する以前の記事を読む](/blog/protect-your-builds-from-github-outages-with-a-file-cache)

StableBuild を使えば、キャッシュを自分たちで管理せずに、同じことができます。外部ファイル、Docker イメージ、PyPI、Ubuntu、Debian、Alpine のパッケージ、Hugging Face のファイルなど、ビルドで使う依存関係を保存できます。

今回は ONNX Runtime が消えました。次は、あなたのビルドが依存しているものかもしれません。

依存関係を自分たちで保持する場合でも、StableBuild のようなサービスを使う場合でも、ソフトウェアを再びビルドするために必要な入力は残しておきましょう。

[StableBuild の無料アカウントを作成](/pricing)して、ビルドが依存している外部依存関係の保存を始めてみてください。
