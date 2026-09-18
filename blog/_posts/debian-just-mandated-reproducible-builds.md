---
title: Debian がビルドの再現性を必須化
date: 2026-05-11
category: 記事
description: Debian は Debian 14「Forky」から、再現可能なパッケージの提供を必須とすることを決定しました。それでも依存性を自分でピン止めしておくことが重要な理由を解説します。
en_url: https://www.stablebuild.com/blog/debian-just-mandated-reproducible-builds
---

Debian の開発チームは、[すべてのパッケージを再現可能な形で提供する](https://www.phoronix.com/news/Debian-Must-Ship-Reproducible)ことを決定しました。この方針は Debian 14「Forky」から適用されます。

Debian がこの決定を下したのは素晴らしいことだと考えています。StableBuild が目指している方向とも一致しています。

とはいえ、Debian がこの方針を徹底したとしても、*すべての*パッケージが再現可能になるとは考えにくく、さまざまな理由で対応から漏れるパッケージは必ず出てくるでしょう。

また、仮に Debian のすべてのパッケージが再現可能になったとしても、StableBuild なら Debian パッケージ以外のもの（たとえばサードパーティの apt リポジトリなど）もピン止めできます。さらに、ミラー自体がなくなってしまうこともあります。だからこそ、ピン止めしたコピーを手元に残しておくことが重要なのです。
