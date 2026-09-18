---
title: StableBuild の日本語版を公開しました
date: 2026-09-07
category: 記事
featured: true
hero: https://cdn.prod.website-files.com/6558cb02ceb72f12e74052f7/65ce320d5d8a5e84a9399533_launch.webp
description: ビルドの再現性を高めるためのミラーとレジストリ、StableBuild をローンチしました。Docker イメージ、OS パッケージ、Python パッケージ、そして任意のファイルをピン止め・凍結できます。
---

本日、StableBuild の日本語版を公開しました。

StableBuild は、Docker イメージ、OS パッケージ、Python パッケージ、そしてインターネットから取得する任意のファイルをピン止め・凍結して、ビルドの再現性を高めるためのミラーとレジストリの集合です。

## コードを変えていないのに、ビルドが壊れる

Dockerfile は一見すると再現性があるように思えます。同じ Dockerfile なら同じコンテナができる、と。ところが実際には、ベースイメージのレジストリ、OS のパッケージリポジトリ、PPA、PyPI、そしてファイルのダウンロード元 URL といった、自分たちの管理下にないサービスに依存しています。

そのどれかが更新されたり削除されたりすれば、コードを一行も変えていなくてもビルドの結果は変わります。ある朝 CI が赤くなっていて、原因が上流の変更だったという経験は、一度や二度ではないはずです。

この構造については「[同じ Dockerfile から同じコンテナはできない](/blog/launching-stablebuild-freeze-and-pin-all-your-dependencies)」で詳しく書きました。

## 提供している機能

**Docker ミラー** — Docker Hub、GitHub Container Registry、NVIDIA NGC のプルスルーキャッシュとして機能します。一度プルしたイメージはキャッシュに保存された後は変わらないため、常に同じコンテナを取得できます。レート制限もありません。

**OS パッケージ** — Ubuntu、Debian、Alpine のパッケージリポジトリと主要な PPA の完全な日次コピー。apt や apk のパッケージを特定の日付に固定できます。パッケージが更新・削除されても、常に同じバージョンをインストールできます。

**Python パッケージ** — PyPI レジストリの完全な日次コピー。Python 依存性を特定の日付に固定できます。pip と Poetry に対応しています。

**ファイルミラー** — 任意の URL やファイルをキャッシュし、変更や削除から保護します。

**ドキュメント** — [ドキュメント](https://stablebuild.gitbook.io/ja)では、はじめてのコンテナのピン止めから、各ミラーの使い方、シングルサインオン（SAML）やお支払い方法までを解説しています。

既存の Dockerfile やビルドインフラへの統合は5分で終わります。アーキテクチャを変える必要はありません。

## このブログについて

依存性が消えたり書き換わったりしてビルドが壊れる事例と、その具体的な対処を中心にお届けします。すでに次のような記事を公開しています。

- [Deadsnakes が Ubuntu 20.04 のサポートを終了。既存のビルドはどうなる？](/blog/deadsnakes-removed-ubuntu-20-04-support)
- [依存性が消えてもビルドを再現する - StableBuild が入力を安定させる仕組み](/blog/reproducible-builds-when-dependencies-disappear)
- [Debian がビルドの再現性を必須化](/blog/debian-just-mandated-reproducible-builds)

## ステイブルビルド合同会社

StableBuild を開発・提供しているステイブルビルド合同会社は、東京都に拠点を置いています。詳細は[会社概要](/company.html)をご覧ください。

ご要望やご質問は contact@stablebuild.jp までお気軽にお送りください。

## 無料の Community プランでお試しください

Community プランでは、StableBuild のすべてのミラー、キャッシュ、リポジトリを完全に無料でご利用いただけます。5ユーザ、トラフィック 1TB、CDN ストレージ 30GB が含まれます。

[ダッシュボード](https://dashboard.stablebuild.com/?lang=ja)で登録して「Community」プランを選択すれば、Docker コンテナ、OS パッケージ、Python パッケージ、任意のファイルのピン止めがすぐに使えるようになります。

チーム全体で使う場合は、数クリックで有料プランに切り替えられます。有料プランではユーザ数の制限がなくなり、月額199ドルから利用できます。詳細は[料金ページ](/pricing)をご覧ください。

すでに依存性の問題でビルドが壊れた経験のあるプロジェクトで試していただくのが、一番わかりやすいと思います。
