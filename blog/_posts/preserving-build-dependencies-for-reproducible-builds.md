---
title: 依存関係を保存してビルドの再現性を守る
date: 2026-11-10
category: 記事
description: Docker タグが同じでも、その中身のイメージは変わることがあります。タグの参照先が差し替えられた後も、StableBuild に保存したイメージから元のバイナリをバイト単位で再現できるかを、GNU Hello で検証しました。
hero: https://cdn.prod.website-files.com/6558cb02ceb72f12e74052f7/6af2679caed98dcf7eb6b9e7_frozen_gear.png
en_url: https://www.stablebuild.com/blog/preserving-build-dependencies-for-reproducible-builds
---

ソースコードが同じでも、ビルド環境が変われば同じバイナリができるとは限りません。[Reproducible Builds プロジェクト](https://reproducible-builds.org/docs/perimeter/)も、コンパイラやビルドツールとそのバージョンをビルド環境の一部と位置づけています。

コンテナを使えば、OS、コンパイラ、ビルドツール、依存関係といったビルド環境の大部分をひとまとめにできます。ただし、それはコンテナイメージ自体が同じ内容のまま手に入ることが前提です。Docker のタグは書き換えられるため、タグが同じでも中身のイメージが変わることがあります。

## 同じタグ、別のイメージ

2026年9月、Docker Hub の `traefik:v3.7.13` について、[タグは変わっていないのにイメージダイジェストが変わっている、とユーザから報告がありました](https://community.traefik.io/t/sha-hash-changed-for-traefik-image-v3-7-13-in-docker-hub/30253)。Traefik の説明によると、Alpine にセキュリティ修正が入ったことを受けて、Docker が公式イメージを再ビルドしたためです。Traefik のバイナリ自体は同じでも、それを包む OS レイヤーは変わっていました。

つまり、再ビルドの前と後では、同じ `traefik:v3.7.13` をプルしても別のイメージが返ってきます。多くの利用者にとっては問題なく、セキュリティ修正が入る分、むしろ歓迎すべき変化です。しかし、古いイメージが残っているマシンと、再ビルド後のイメージをプルしたマシンが混在すると、どちらも `traefik:v3.7.13` を指定しているのに、実際には別の環境で動くことになります。おなじみの「自分の PC では動くのに」現象は、こうして起こります。

## 検証の概要

上流のイメージが変わるのを待つのではなく、この状況を自分たちで再現してみました。題材は小さなサンプルプログラムの GNU Hello で、自分たちで管理するタグの中身を差し替えます。違いが分かりやすいよう、今回は GCC 12 を GCC 13 に入れ替えました。実際には、イメージ内のシステムパッケージが更新される程度の小さな変化でも、再現性は崩れることがあります。

結論から言うと、Docker タグで公開した GCC 12 のイメージで GNU Hello をビルドし、同じイメージを StableBuild 経由でキャッシュしておけば、元のバイナリを後から再現できました。Docker Hub 上の同じタグを GCC 13 のイメージに差し替えた後、Docker Hub は GCC 13 を返すようになりましたが、StableBuild はキャッシュ済みの GCC 12 を返し続けました。StableBuild のイメージで GNU Hello をビルドし直すと、元のバイナリとバイト単位で一致しました。

<div class="sb-gcc-diagram">
  <style>
    .sb-gcc-diagram {
      font-family: system-ui, sans-serif;
      color: #20252b;
      max-width: 760px;
      margin: 24px auto;
      font-size: 14px;
      line-height: 1.5;
    }

    .sb-gcc-diagram * {
      box-sizing: border-box;
    }

    .sb-gcc-step {
      border: 1px solid #dce2e8;
      border-radius: 10px;
      padding: 20px;
      margin-bottom: 16px;
    }

    .sb-gcc-heading {
      font-weight: 700;
      font-size: 14px;
      margin-bottom: 18px;
    }

    .sb-gcc-flow {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
    }

    .sb-gcc-node {
      flex: 1;
      min-width: 0;
      text-align: center;
      background: #f3f6f8;
      border: 1px solid #e0e5ea;
      border-radius: 7px;
      padding: 12px 8px;
    }

    .sb-gcc-node strong {
      display: block;
      font-weight: 700;
    }

    .sb-gcc-node small {
      display: block;
      color: #64748b;
      margin-top: 4px;
      font-size: 12px;
    }

    .sb-gcc-node code {
      font-size: 12px;
      overflow-wrap: anywhere;
    }

    .sb-gcc-arrow {
      flex-shrink: 0;
      color: #64748b;
      font-size: 22px;
    }

    .sb-gcc-branches {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }

    .sb-gcc-branch {
      text-align: center;
      border: 1px solid #e0e5ea;
      border-radius: 8px;
      padding: 14px;
    }

    .sb-gcc-branch .sb-gcc-node {
      margin-bottom: 12px;
    }

    .sb-gcc-down {
      display: block;
      color: #64748b;
      font-size: 22px;
      margin: 6px 0;
    }

    .sb-gcc-binary {
      font-weight: 700;
      font-size: 16px;
    }

    .sb-gcc-cached {
      background: #eef8f1;
      border-color: #b8dec4;
    }

    .sb-gcc-result {
      border: 1px solid #b8dec4;
      background: #f4faf5;
      border-radius: 10px;
      padding: 20px;
      text-align: center;
    }

    .sb-gcc-result-row {
      font-size: 20px;
      font-weight: 700;
      margin: 8px 0;
    }

    .sb-gcc-result-row small {
      display: block;
      font-size: 12px;
      font-weight: 400;
      color: #526258;
    }

    @media (max-width: 520px) {
      .sb-gcc-flow {
        flex-direction: column;
      }

      .sb-gcc-flow .sb-gcc-node {
        width: 100%;
        flex: auto;
      }

      .sb-gcc-flow .sb-gcc-arrow {
        transform: rotate(90deg);
      }

      .sb-gcc-branches {
        gap: 8px;
      }

      .sb-gcc-branch {
        padding: 8px;
      }

      .sb-gcc-branch .sb-gcc-node {
        padding: 10px 4px;
      }
    }
  </style>

  <!-- Step 1 -->
  <section class="sb-gcc-step">
    <div class="sb-gcc-heading">1. 最初のビルド</div>
    <div class="sb-gcc-flow">
      <div class="sb-gcc-node">
        <strong>Docker Hub</strong>
        <code>testing-v1</code>
        <small>GCC 12</small>
      </div>
      <span class="sb-gcc-arrow">→</span>
      <div class="sb-gcc-node">
        <strong>GNU Hello をビルド</strong>
      </div>
      <span class="sb-gcc-arrow">→</span>
      <div class="sb-gcc-node">
        <strong>バイナリ A</strong>
        <small>元のバイナリ</small>
      </div>
    </div>
  </section>

  <!-- Step 2 -->
  <section class="sb-gcc-step">
    <div class="sb-gcc-heading">2. イメージをキャッシュ</div>
    <div class="sb-gcc-flow">
      <div class="sb-gcc-node">
        <strong>Docker Hub</strong>
        <code>testing-v1</code>
        <small>GCC 12</small>
      </div>
      <span class="sb-gcc-arrow">→</span>
      <div class="sb-gcc-node sb-gcc-cached">
        <strong>StableBuild</strong>
        <code>testing-v1</code>
        <small>GCC 12 · キャッシュ済み</small>
      </div>
    </div>
  </section>

  <!-- Step 3 -->
  <section class="sb-gcc-step">
    <div class="sb-gcc-heading">
      3. Docker Hub のイメージを差し替え
    </div>
    <div class="sb-gcc-branches">
      <div class="sb-gcc-branch">
        <div class="sb-gcc-node">
          <strong>Docker Hub</strong>
          <code>testing-v1</code>
          <small>GCC 13 · 変更後</small>
        </div>
        <span class="sb-gcc-down">↓</span>
        <div>GNU Hello をビルド</div>
        <span class="sb-gcc-down">↓</span>
        <div class="sb-gcc-binary">バイナリ B</div>
      </div>

      <div class="sb-gcc-branch">
        <div class="sb-gcc-node sb-gcc-cached">
          <strong>StableBuild</strong>
          <code>testing-v1</code>
          <small>GCC 12 · キャッシュ済み</small>
        </div>
        <span class="sb-gcc-down">↓</span>
        <div>GNU Hello をビルド</div>
        <span class="sb-gcc-down">↓</span>
        <div class="sb-gcc-binary">バイナリ C</div>
      </div>
    </div>
  </section>

  <!-- Step 4 -->
  <section class="sb-gcc-result">
    <div class="sb-gcc-heading">4. バイナリを比較</div>
    <div class="sb-gcc-result-row">
      A = C ✓
      <small>バイト単位で一致</small>
    </div>
    <div class="sb-gcc-result-row">
      A ≠ B
      <small>異なるバイナリ</small>
    </div>
  </section>
</div>

検証は次の4つのステップで進めます。タグは最初から最後まで `testing-v1` のままで、変わるのは Docker Hub がそのタグで配信するイメージだけです。

1. **GCC 12 による基準ビルド**
2. **StableBuild での GCC 12 のキャッシュ**
3. **`testing-v1` の GCC 13 への差し替え**
4. **再プルとビルド結果の比較**

## 1. GCC 12 による基準ビルド

まず、GCC 12.5.0 のイメージを `tfryer/sb-hello-build-env:testing-v1` として公開しました。

```bash
docker pull --platform linux/amd64 gcc:12.5.0-bookworm
docker tag gcc:12.5.0-bookworm tfryer/sb-hello-build-env:testing-v1
docker push tfryer/sb-hello-build-env:testing-v1
```

このイメージで、新たに取得した GNU Hello 2.12.1 のソースを `./configure` と `make -j1` でビルドしました。ここで生成した `original/hello` が比較の基準です。

## 2. StableBuild での GCC 12 のキャッシュ

続いて、同じイメージを [StableBuild の Docker ミラー](https://stablebuild.gitbook.io/stablebuild-docs/docs/ja/mirrors-and-caches/docker-mirror)経由でプルしました。

```bash
docker pull --platform linux/amd64 <stablebuild-mirror>/tfryer/sb-hello-build-env:testing-v1
```

この時点で StableBuild は、Docker Hub が `testing-v1` として配信していた GCC 12 のイメージをキャッシュしています。

## 3. `testing-v1` の GCC 13 への差し替え

次に、同じタグで GCC 13.5.0 のイメージを公開しました。

```bash
docker pull --platform linux/amd64 gcc:13.5.0-bookworm
docker tag gcc:13.5.0-bookworm tfryer/sb-hello-build-env:testing-v1
docker push tfryer/sb-hello-build-env:testing-v1
```

これで、Docker Hub の `tfryer/sb-hello-build-env:testing-v1` は GCC 13 のイメージを返すようになりました。

## 4. 再プルとビルド結果の比較

ローカルに残ったイメージが結果に影響しないよう、プルし直す前に Docker のキャッシュを削除しました。

```bash
docker system prune -af
```

そのうえで、Docker Hub から直接と StableBuild 経由の両方で `testing-v1` をプルしました。

```bash
docker pull --platform linux/amd64 tfryer/sb-hello-build-env:testing-v1
docker pull --platform linux/amd64 <stablebuild-mirror>/tfryer/sb-hello-build-env:testing-v1
```

それぞれのイメージに入っているコンパイラのバージョンを確認します。

```bash
docker run --rm --platform linux/amd64 tfryer/sb-hello-build-env:testing-v1 gcc --version
docker run --rm --platform linux/amd64 <stablebuild-mirror>/tfryer/sb-hello-build-env:testing-v1 gcc --version
```

Docker Hub のイメージは GCC 13.5.0、StableBuild のイメージは GCC 12.5.0 でした。

![Docker Hub のイメージは GCC 13.5.0、StableBuild のイメージは GCC 12.5.0 を返した](https://cdn.prod.website-files.com/6558cb02ceb72f12e74052f7/6af25405ffacb8187efba776_82a84ee6.png)

次に、それぞれのイメージで、新たに取得した GNU Hello 2.12.1 のソースをビルドしました。ソースも `./configure` と `make -j1` も基準ビルドと同じです。これで3つのバイナリがそろいました。

| バイナリ | 使用した Docker イメージ |
| --- | --- |
| `original/hello` | `testing-v1` の差し替え前に Docker Hub から取得した GCC 12 |
| `dockerhub/hello` | `testing-v1` の差し替え後に Docker Hub から取得した GCC 13 |
| `stablebuild/hello` | `testing-v1` の差し替え前に StableBuild がキャッシュした GCC 12 |

SHA-256 ハッシュを比較します。

```bash
sha256sum original/hello dockerhub/hello stablebuild/hello
```

![3つの GNU Hello バイナリの SHA-256 ハッシュの比較結果](https://cdn.prod.website-files.com/6558cb02ceb72f12e74052f7/6af25405ffacb8187efba779_65fa14cd.png)

`original/hello` と `stablebuild/hello` のハッシュは一致し、GCC 13 でビルドした `dockerhub/hello` だけが異なりました。StableBuild にキャッシュした GCC 12 のイメージを使えば、元の GNU Hello のバイナリをバイト単位で再現できるということです。

## StableBuild の役割

今回固定したのは、ビルド環境のうちコンパイラのイメージという一部分です。上流の Docker タグが変わった後も、元のビルドで使ったイメージを使い続けられるようにしました。

何が変わったのかは最初から分かっていたので、今回は SHA-256 の比較で十分でした。GCC 12 から GCC 13 への変更は、あえて分かりやすくしたものです。原因の分からない差分が出たときは、[diffoscope](https://diffoscope.org/) で成果物を比べると、どこが違うのかを突き止められます。ビルド中に紛れ込む非決定的なデータが差分の原因になることもあり、その一部は [strip-nondeterminism](https://salsa.debian.org/reproducible-builds/strip-nondeterminism) で正規化できます。

StableBuild が受け持つのは、これとは別の部分です。外部の依存関係が上流で変更・削除された後も、それを取得できる状態に保ちます。

今回の検証では、GCC 12 の Docker イメージがその依存関係にあたります。`testing-v1` が差し替えられる前に StableBuild がキャッシュしていたからこそ、後から元のバイナリを再現できました。`traefik:v3.7.13` の再ビルドは、タグはそのままにイメージだけが変わるという同じ問題が、実際に起きた例です。

外部の依存関係を保存しておくだけで、再現性の問題がすべて解決するわけではありません。それでも、再現に必要なビルド環境の一部が、上流の都合で失われることは防げます。

この考え方は Docker に限りません。StableBuild は、[Ubuntu、Debian、Alpine の過去のリポジトリ](https://stablebuild.gitbook.io/stablebuild-docs/docs/ja/mirrors-and-caches/os-package-registry-ubuntu-debian-alpine)、[過去の状態を保持する PyPI ミラー](https://stablebuild.gitbook.io/stablebuild-docs/docs/ja/mirrors-and-caches/pypi-mirror)、[HuggingFace のミラー](https://stablebuild.gitbook.io/stablebuild-docs/docs/ja/mirrors-and-caches/huggingface-mirror)、[その他の外部ファイル向けのキャッシュ](https://stablebuild.gitbook.io/stablebuild-docs/docs/ja/mirrors-and-caches/file-mirror)も提供しています。

StableBuild は [Community プラン](/pricing)なら無料で使えます。ビルドに必要な外部依存関係を、上流から消えてしまう前に保存しておきましょう。
