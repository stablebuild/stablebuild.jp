---
title: Debianがビルドの再現性を必須化
date: 2026-05-11
category: 記事
description: DebianはDebian 14「Forky」から、再現可能なパッケージの提供を必須とすることを決定しました。それでも依存性を自分でピン止めしておくことが重要な理由を解説します。
en_url: https://www.stablebuild.com/blog/debian-just-mandated-reproducible-builds
---

Debianの開発チームは、[Debianが再現可能なパッケージを提供しなければならない](https://www.phoronix.com/news/Debian-Must-Ship-Reproducible)ことを決定しました。この方針はDebian 14「Forky」から適用されます。

Debianがこの決定を下したことは素晴らしいことだと考えています。StableBuildが目指している方向とも一致しています。

とはいえ、Debianがこの方針を徹底したとしても、*すべての*パッケージが再現可能になるとは考えにくく、さまざまな理由で対応から漏れるパッケージは必ず出てくるでしょう。

また、仮にDebianのすべてのパッケージが再現可能になったとしても、StableBuildならDebianパッケージ以外のもの（たとえばサードパーティのaptリポジトリなど）もピン止めできます。さらに、ミラー自体がなくなってしまうこともあります。だからこそ、ピン止めしたコピーを手元に残しておくことが重要なのです。
