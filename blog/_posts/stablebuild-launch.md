---
title: StableBuildの日本語版を公開しました
date: 2026-09-07
category: 記事
featured: true
hero: https://cdn.prod.website-files.com/6558cb02ceb72f12e74052f7/65ce320d5d8a5e84a9399533_launch.webp
description: ビルドの再現性を高めるためのミラーとレジストリ、StableBuildをローンチしました。Dockerイメージ、OSパッケージ、Pythonパッケージ、そして任意のファイルをピン止め・凍結できます。
---

本日、StableBuildの日本語版を公開しました。

StableBuildは、Dockerイメージ、OSパッケージ、Pythonパッケージ、そしてインターネットから取得する任意のファイルをピン止め・凍結して、ビルドの再現性を高めるためのミラーとレジストリの集合です。

## コードを変えていないのに、ビルドが壊れる

Dockerfileは一見すると再現性があるように思えます。同じDockerfileなら同じコンテナができる、と。ところが実際には、ベースイメージのレジストリ、OSのパッケージリポジトリ、PPA、PyPI、そしてファイルのダウンロード元URLといった、自分たちの管理下にないサービスに依存しています。

そのどれかが更新されたり削除されたりすれば、コードを一行も変えていなくてもビルドの結果は変わります。ある朝CIが赤くなっていて、原因が上流の変更だったという経験は、一度や二度ではないはずです。

この構造については「[同じDockerfileから同じコンテナはできない](/blog/launching-stablebuild-freeze-and-pin-all-your-dependencies)」で詳しく書きました。

## 提供している機能

**Dockerミラー** — Docker Hub、GitHub Container Registry、NVIDIA NGCのプルスルーキャッシュとして機能します。一度プルしたイメージはキャッシュに保存された後は変わらないため、常に同じコンテナを取得できます。レート制限もありません。

**OSパッケージ** — Ubuntu、Debian、Alpineのパッケージリポジトリと主要なPPAの完全な日次コピー。aptやapkのパッケージを特定の日付に固定できます。パッケージが更新・削除されても、常に同じバージョンをインストールできます。

**Pythonパッケージ** — PyPIレジストリの完全な日次コピー。Python依存性を特定の日付に固定できます。pipとPoetryに対応しています。

**ファイルミラー** — 任意のURLやファイルをキャッシュし、変更や削除から保護します。

**ドキュメント** — [ドキュメント](https://stablebuild.gitbook.io/ja)では、はじめてのコンテナのピン止めから、各ミラーの使い方、シングルサインオン（SAML）やお支払い方法までを解説しています。

既存のDockerfileやビルドインフラへの統合は5分で終わります。アーキテクチャを変える必要はありません。

## このブログについて

依存性が消えたり書き換わったりしてビルドが壊れる事例と、その具体的な対処を中心にお届けします。すでに次のような記事を公開しています。

- [DeadsnakesがUbuntu 20.04のサポートを終了。既存のビルドはどうなる？](/blog/deadsnakes-removed-ubuntu-20-04-support)
- [依存性が消えてもビルドを再現する - StableBuildが入力を安定させる仕組み](/blog/reproducible-builds-when-dependencies-disappear)
- [Debianがビルドの再現性を必須化](/blog/debian-just-mandated-reproducible-builds)

## ステイブルビルド合同会社

StableBuildを開発・提供しているステイブルビルド合同会社は、東京都に拠点を置いています。詳細は[会社概要](/company.html)をご覧ください。

ご要望やご質問は contact@stablebuild.jp までお気軽にお送りください。

## 無料のCommunityプランでお試しください

Communityプランでは、StableBuildのすべてのミラー、キャッシュ、リポジトリを完全に無料でご利用いただけます。5ユーザ、トラフィック1TB、CDNストレージ30GBが含まれます。

[ダッシュボード](https://dashboard.stablebuild.com/?lang=ja)で登録して「Community」プランを選択すれば、Dockerコンテナ、OSパッケージ、Pythonパッケージ、任意のファイルのピン止めがすぐに使えるようになります。

チーム全体で使う場合は、数クリックで有料プランに切り替えられます。有料プランではユーザ数の制限がなくなり、月額199ドルから利用できます。詳細は[料金ページ](/pricing)をご覧ください。

すでに依存性の問題でビルドが壊れた経験のあるプロジェクトで試していただくのが、一番わかりやすいと思います。
