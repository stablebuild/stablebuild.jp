---
title: CircleCI のウェビナーで、依存関係を日付で固定する方法を紹介しました
date: 2026-11-25
category: 記事
description: CircleCI のオンラインセミナー「詳解CircleCI #03」に登壇し、Docker イメージ、OS パッケージ、Python パッケージ、ダウンロードするファイルを日付で固定し、ビルドが壊れるのを防ぎ、悪意のある版を取り込まないようにする方法を、CircleCI でのデモとあわせて紹介しました。録画は YouTube で公開されています。
hero: /blog/images/circleci-webinar-pin-dependencies-by-date.png
---

11月24日に CircleCI が開催したオンラインセミナー「詳解CircleCI」の第3回「CIでやるべきセキュリティ対策 ― 固定する・検査する・止める・絞る」に、StableBuild CEO の木本真理究が登壇しました。StableBuild のパートでは「固定する」を取り上げ、Dockerfile の依存関係を日付で固定して、ビルドが壊れるのを防ぎ、悪意のある版を取り込まないようにする方法を、CircleCI でのデモとあわせて紹介しました。録画は CircleCI の YouTube チャンネルで公開されています。

<div style="position: relative; padding-top: 56.25%; margin-bottom: 24px"><iframe src="https://www.youtube-nocookie.com/embed/EAHvy3oEY7c" title="CIでやるべきセキュリティ対策 固定する・検査する・止める・絞る ＜詳解CircleCI #03＞" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0; border-radius: 16px" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" loading="lazy" allowfullscreen></iframe></div>

## コードを変えていないのに壊れるビルド

セミナーでは、まずアプリケーションのコードを変えていないのにビルドが壊れる例を取り上げました。Dockerfile の中で取得するものは、ビルドした日によって中身が変わります。

- **Docker イメージ**：`python:3.14` のようなタグは新しいパッチ版が出るたびに上書きされ、[古いイメージが削除される](/blog/getting-repository-does-not-exist-for-nvidia-cuda-containers-this-is-how-to-fix-it)こともあります
- **OS パッケージ**：apt でインストールされる版はその日のリポジトリ次第で、古い版は削除されます
- **Python パッケージ**：`requirements.txt` で直接の依存関係を固定しても、間接的な依存関係は範囲指定のままです
- **ファイル**：GitHub Releases などから取得するファイルは、11月の [ONNX Runtime](/blog/onnx-runtime-disappeared-from-github-without-warning) のように、リポジトリごと消えることがあります

## 固定に加えて保持する

lockfile や digest で固定すれば、毎回同じものを指すようになります。ただ、指している先が上流から消えれば、ビルドは止まります。ONNX Runtime の件でも、URL と SHA-256 をきちんと書いていたビルドが失敗しました。さらに、固定しきれていない依存関係が改ざんされた場合は、止まるだけでは済みません。改ざんされた中身がそのままビルドに入り、脆弱性を抱えた製品を出荷することになりかねません。

StableBuild は、上流のレジストリと CI の間に入るミラーとして、固定と保持をまとめて受け持ちます。OS パッケージと PyPI は日付を指定すればその日の状態で解決され、Docker イメージやファイルは初回に取得した内容が返り続けます。日付を変えない限り、CircleCI のジョブをいつ実行しても同じ依存関係が入ります。セミナーでは、これを「サプライチェーンのスナップショット」と呼びました。

PyPI から削除された版も保持しているので、日付を戻せば、消える前の版をそのままインストールできます。最近削除された版は、[削除済みパッケージの一覧](https://dashboard.stablebuild.com/pypi-deleted-packages/)で誰でも確認できます。

## サプライチェーン攻撃への備え

10月には[改ざんされた LiteLLM 1.107.0 が PyPI に公開され](/blog/php2shell-vs-litellm-when-to-update-dependencies)、2024年には裏口を仕込んだ xz-utils が一部の Linux ディストリビューションのパッケージとして配布されました。範囲指定で最新の版を取得するビルドは、こうした版をそのまま取り込んでしまいます。

日付で固定していれば、その日より後に公開された版は、日付を進めるまで入ってきません。`requirements.txt` に書いていない間接的な依存関係も同じです。Docker イメージやファイルは初回に取得した内容が返り続けるので、後からタグやファイルを差し替えられても影響を受けません。

ただし、StableBuild は上流で削除された版も保持しているため、悪意のある版が公開されていた期間の日付を選ぶと、その版も入ります。日付を進めるときは直近すぎない日付を選び、その間に報告が出ていないかを確認してください。悪意のある版が見つかって削除されるまでの時間を稼げます。

## 脆弱性が見つかったときの更新

固定すると脆弱性への対応が遅れるのでは、という質問もよくいただきます。実際は逆です。すべての依存関係を固定しているので、更新したいものだけを選んで、安全に更新できます。たとえば Python パッケージに修正版が出たら、PyPI の日付や lockfile の版を修正版まで進めるプルリクエストを出します。OS パッケージやベースイメージはそのままなので、ほかの部分が一緒に変わる心配はありません。ベースイメージに含まれるパッケージは、`FROM` のタグを新しいものに変えて更新します。

あとはいつもの CircleCI のパイプラインで検証し、ビルドのログを前回と比べれば、どの版が上がったかが分かります。差分は日付や版の数行だけなのでレビューしやすく、問題が出れば元に戻すだけで以前と同じ依存関係に戻せます。

固定しておけば、検査した依存関係と同じものをいつでもビルドできるので、脆弱性スキャンの結果と出荷するものがずれることもありません。

## デモの Dockerfile

デモで使った[サンプルリポジトリ](https://github.com/stablebuild/circle-ci-stablebuild-example)の Dockerfile です（一部を省略しています）。取得先を StableBuild に向けるだけで、`apt-get install` や `pip install` の書き方は変わりません。

```dockerfile
ARG SB_API_KEY
FROM ${SB_API_KEY}.dockermirror.stablebuild.com/python:3.14.10-slim-trixie

ARG SB_API_KEY
ARG APT_PIN_DATE=2026-11-12T16:37:01Z
ARG PYPI_PIN_DATE=2026-11-12

COPY ./sb-apt.sh /opt/sb-apt.sh
RUN bash /opt/sb-apt.sh load-apt-sources debian
RUN apt-get update && apt-get install -y --no-install-recommends curl

RUN curl -fsSL -o /usr/local/bin/tini \
        "https://${SB_API_KEY}.httpcache.stablebuild.com/circleci-stablebuild-example/https://github.com/krallin/tini/releases/download/v0.19.0/tini-$(dpkg --print-architecture)"

RUN pip install -r requirements.txt \
        -i "https://${SB_API_KEY}.pypimirror.stablebuild.com/${PYPI_PIN_DATE}/"
```

CircleCI 側は、`--build-arg` で API キーを `docker build` に渡すだけです。日付は Dockerfile にだけ書くので、依存関係の更新は Dockerfile の差分としてレビューできます。

サンプルリポジトリは、フォークして CircleCI の環境変数に `SB_API_KEY` を設定すれば、そのまま動きます。API キーは [Community プラン](/pricing)なら無料で発行できます。

## 次回のテーマは SBOM

11月30日（月）14:00 からの第4回「[CIのセキュリティを仕組みにする ― 配る・絞る・外せなくする・後から追う](https://www2.circleci.com/wbn_shokai_circleci_04_security_mechanisms)」にも登壇します。固定しても、すでに取り込んだ版に脆弱性やマルウェアが見つかることはあります。そのときに、どのビルドがその版を取得していたかを、ビルドごとに残した SBOM から確かめる方法を紹介します。
