---
title: 再現可能なビルドのために依存関係を保持する
date: 2026-11-10
category: 記事
description: 同じソースコードだけでは、同じビルド結果を再現できるとは限りません。Docker タグの参照先が変わった場合でも、StableBuild に保存したコンテナイメージを使って元のバイナリを再現できることを、GNU Hello を使って検証します。
hero: https://cdn.prod.website-files.com/6558cb02ceb72f12e74052f7/6af2679caed98dcf7eb6b9e7_frozen_gear.png
en_url: https://www.stablebuild.com/blog/preserving-build-dependencies-for-reproducible-builds
---

ビルドを再現可能にするには、同じソースコードがあるだけでは足りません。ビルド環境も重要です。[Reproducible Builds プロジェクト](https://reproducible-builds.org/docs/perimeter/)では、コンパイラ、ビルドツール、そのバージョンもビルド環境の一部として扱っています。

コンテナを使えば、OS、コンパイラ、ビルドツール、依存関係など、ビルド環境の多くをまとめてパッケージ化できます。ただし、そのコンテナイメージ自体も、同じ内容のまま利用できなければなりません。Docker タグは変更可能です。タグが同じでも、その参照先のイメージが変わることがあります。

最近の例が `traefik:v3.7.13` です。2026年9月、[タグが変わっていないにもかかわらず、Docker Hub 上のイメージダイジェストが変わったことに、あるユーザーが気づきました](https://community.traefik.io/t/sha-hash-changed-for-traefik-image-v3-7-13-in-docker-hub/30253)。Traefik は、Alpine にセキュリティ修正が入った後、Docker が公式イメージを再ビルドしたと説明しました。Traefik のバイナリ自体は変わっていませんでしたが、その周囲にある OS レイヤーは変わっていました。

つまり、再ビルドの前後で `traefik:v3.7.13` をプルすると、異なるコンテナイメージが返される可能性があります。ほとんどの利用者にとって、それは問題ではなく、むしろ望ましい場合もあります。しかし、あるマシンには以前のイメージが残っていて、別のマシンは再ビルド後のイメージをプルした場合、どちらも `traefik:v3.7.13` を指定しているのに、異なるコンテナ環境で動くことになります。その結果、あまりにもおなじみの「自分の PC では動くのに」という状況が起こり得ます。

上流のイメージが変わるのを待つ代わりに、この状況を自分たちで再現してみます。小さなサンプルプログラムとして GNU Hello を使い、自分たちで管理するタグの参照先イメージを変更します。今回は違いを分かりやすくするため、GCC 12 を GCC 13 に置き換えます。実際には、イメージ内のシステムパッケージが更新されるといった、もっと小さな変化でも再現性が損なわれる可能性があります。

**要約**

Docker タグで公開した GCC 12 を使って GNU Hello をビルドし、そのイメージを StableBuild 経由でキャッシュしました。次に、Docker Hub 上で同じタグのイメージを GCC 13 に差し替えました。その後、Docker Hub からは GCC 13 が返されましたが、StableBuild からはキャッシュ済みの GCC 12 が返され続けました。StableBuild のイメージで GNU Hello をもう一度ビルドすると、元のバイナリをバイト単位で再現できました。

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

次の4つの手順で検証します。

1. **GCC 12 で基準となるビルドを作成する**
2. **StableBuild 経由で GCC 12 をキャッシュする**
3. **`testing-v1` を GCC 13 に差し替える**
4. **もう一度 `testing-v1` をプルして、ビルド結果を比較する**

Docker タグは、最初から最後まで `testing-v1` のままです。変わるのは、Docker Hub でそのタグから配信されるイメージだけです。

## 1. GCC 12 で基準となるビルドを作成する

まず、GCC 12.5.0 を `tfryer/sb-hello-build-env:testing-v1` として公開しました。

```bash
docker pull --platform linux/amd64 gcc:12.5.0-bookworm
docker tag gcc:12.5.0-bookworm tfryer/sb-hello-build-env:testing-v1
docker push tfryer/sb-hello-build-env:testing-v1
```

次に、そのイメージを使い、新しく取得した GNU Hello 2.12.1 のソースを `./configure` と `make -j1` でコンパイルしました。

生成された `original/hello` バイナリを、比較の基準とします。

## 2. StableBuild 経由で GCC 12 をキャッシュする

次に、同じイメージを [StableBuild の Docker ミラー](https://stablebuild.gitbook.io/stablebuild-docs/docs/ja/mirrors-and-caches/docker-mirror)経由でプルしました。

```bash
docker pull --platform linux/amd64 <stablebuild-mirror>/tfryer/sb-hello-build-env:testing-v1
```

StableBuild は、その時点で Docker Hub が `testing-v1` として配信していた GCC 12 のイメージをキャッシュしました。

## 3. `testing-v1` を GCC 13 に差し替える

次に、同じ Docker Hub のタグで GCC 13.5.0 を公開しました。

```bash
docker pull --platform linux/amd64 gcc:13.5.0-bookworm
docker tag gcc:13.5.0-bookworm tfryer/sb-hello-build-env:testing-v1
docker push tfryer/sb-hello-build-env:testing-v1
```

これで、Docker Hub は `tfryer/sb-hello-build-env:testing-v1` として GCC 13 を配信するようになりました。

## 4. もう一度 `testing-v1` をプルして、ビルド結果を比較する

イメージを再びプルする前に、ローカルの Docker キャッシュを削除しました。これにより、ローカルに保存されているイメージが結果に影響するのを防ぎます。

```bash
docker system prune -af
```

次に、Docker Hub から直接、そして StableBuild 経由で、それぞれ `testing-v1` をプルしました。

```bash
docker pull --platform linux/amd64 tfryer/sb-hello-build-env:testing-v1
docker pull --platform linux/amd64 <stablebuild-mirror>/tfryer/sb-hello-build-env:testing-v1
```

それぞれのイメージに入っているコンパイラのバージョンを確認しました。

```bash
docker run --rm --platform linux/amd64 tfryer/sb-hello-build-env:testing-v1 gcc --version
docker run --rm --platform linux/amd64 <stablebuild-mirror>/tfryer/sb-hello-build-env:testing-v1 gcc --version
```

Docker Hub からは GCC 13.5.0 が返され、StableBuild からは GCC 12.5.0 が返されました。

![Docker Hub からは GCC 13.5.0、StableBuild からは GCC 12.5.0 が返された結果](https://cdn.prod.website-files.com/6558cb02ceb72f12e74052f7/6af25405ffacb8187efba776_82a84ee6.png)

次に、それぞれのイメージを使って、新しく取得した GNU Hello 2.12.1 のソースをコンパイルしました。どちらのビルドでも、基準となるビルドと同じソース、`./configure`、`make -j1` を使用しています。

これで、3つのバイナリができました。

| バイナリ | 使用した Docker イメージ |
| --- | --- |
| `original/hello` | `testing-v1` が変わる前に Docker Hub から取得した GCC 12 |
| `dockerhub/hello` | `testing-v1` が変わった後に Docker Hub から取得した GCC 13 |
| `stablebuild/hello` | `testing-v1` が変わる前に StableBuild がキャッシュした GCC 12 |

それぞれの SHA-256 ハッシュを比較しました。

```bash
sha256sum original/hello dockerhub/hello stablebuild/hello
```

![3つの GNU Hello バイナリの SHA-256 ハッシュを比較した結果](https://cdn.prod.website-files.com/6558cb02ceb72f12e74052f7/6af25405ffacb8187efba779_65fa14cd.png)

`original/hello` と `stablebuild/hello` の SHA-256 ハッシュは同じでした。GCC 13 でビルドした `dockerhub/hello` のハッシュは異なっていました。

StableBuild にキャッシュした GCC 12 のイメージを使うことで、元の GNU Hello バイナリをバイト単位で再現できました。

## StableBuild が担う部分

今回の検証では、ビルド環境の一部分を固定しました。上流の Docker タグが変わった後も、元のビルドで使ったコンパイライメージを利用できる状態に保っています。

何が変わったかをあらかじめ把握していたため、今回の検証では SHA-256 の比較だけで十分でした。GCC 12 から GCC 13 への変更は、意図的に分かりやすくしたものです。2つのビルドに違いがあり、その原因が明らかでない場合は、[diffoscope](https://diffoscope.org/)を使って成果物を調べ、どこが異なるのかを特定できます。また、ビルド中に追加される非決定的なデータによって違いが生じることもあります。[strip-nondeterminism](https://salsa.debian.org/reproducible-builds/strip-nondeterminism)を使うと、そのようなデータの一部を正規化できます。

StableBuild が扱うのは、また別の部分です。上流で外部依存関係が変更または削除された後も、それらを利用できる状態に保ちます。

今回の検証で、その依存関係にあたるのが GCC 12 の Docker イメージでした。`testing-v1` が変わる前に StableBuild がキャッシュしていたため、後から元の GNU Hello バイナリを再現できました。`traefik:v3.7.13` の再ビルドは、同じ問題が実際に起きた例です。タグは同じまま、イメージが変わりました。

外部依存関係を利用できる状態に保つだけで、再現性に関するすべての問題を解決できるわけではありません。ただし、再現に必要なビルド環境の一部が、上流の変更によって失われるのを防ぐことはできます。

同じ考え方は Docker 以外にも当てはまります。StableBuild は、[Ubuntu、Debian、Alpine の過去のリポジトリ](https://stablebuild.gitbook.io/stablebuild-docs/docs/ja/mirrors-and-caches/os-package-registry-ubuntu-debian-alpine)、[過去の状態を保持する PyPI ミラー](https://stablebuild.gitbook.io/stablebuild-docs/docs/ja/mirrors-and-caches/pypi-mirror)、[HuggingFace のミラー](https://stablebuild.gitbook.io/stablebuild-docs/docs/ja/mirrors-and-caches/huggingface-mirror)、[その他の外部ファイルを保存するキャッシュ](https://stablebuild.gitbook.io/stablebuild-docs/docs/ja/mirrors-and-caches/file-mirror)も提供しています。

[StableBuild の無料アカウントを作成](/pricing)して、ビルドが依存している外部依存関係の保存を始めてみてください。
