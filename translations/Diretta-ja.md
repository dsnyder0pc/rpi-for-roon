# Raspberry Pi上のAudioLinuxで構築する専用Direttaリンク

このガイドでは、2台のRaspberry Piデバイスを専用のDiretta HostおよびDiretta Targetとして構成するための詳細な手順を順を追って説明します。この構成では、2台のデバイス間を直接ポイント・ツー・ポイントのEthernet接続で結ぶことにより、究極のネットワークアイソレーションとオーディオパフォーマンスを実現します。

**Diretta Host**はメインネットワーク（ミュージックサーバーへのアクセス用）に接続し、Targetのゲートウェイとしても機能します。**Diretta Target**はHostおよびUSB DACまたはDDCにのみ接続します。

## バージョンの管理

このガイドは、Piero氏が提供する現在の公式AudioLinuxダウンロードリンクとの互換性を維持することを目的としています。

**現在の動作確認状況 :**
これらの手順は、**AudioLinux V5**（イメージ：`audiolinux_pi4-pi5_520`、メニューバージョン：`536`）で最後にテストされました。

**アップデートに関する注意 :**
AudioLinuxはArch Linux（ローリングリリース）ベースであるため、新規インストール時には常に最新のソフトウェアが取得されます。システムが正常に動作し始めたら、次の2つの選択肢があります。

1.  **頻繁にアップデートする :** 少なくとも月に1回はアップデートを実施し、小さな不具合が発生した段階で修正します。
2.  **システムを固定する（推奨） :** 素晴らしい音が鳴っているなら、下手に弄らないでください。バックアップイメージを作成して、音楽を楽しみましょう！

## リファレンスRoonアーキテクチャのご紹介

最先端のRoonストリーミングエンドポイントを構築するための決定版ガイドへようこそ。AudioLinuxは他のプロトコルもサポートしていますが、このビルドではRoonを例として使用します。Diretta Hostのメニューシステムを使用して、HQPlayer、Audirvana、DLNA、AirPlayなどの他のプロトコルのサポートをインストールすることも可能です。段階的な手順に進む前に、このプロジェクトの「なぜ（理由）」を理解することが重要です。この導入部では、このアーキテクチャが解決する課題、高額な市販の代替製品よりも根本的に優れている理由、そしてこのDIYプロジェクトがRoonシステムから究極の音質を引き出すための近道であり、いかにやりがいのある道であるかを説明します。

### Roonのパラドックス : 強力な体験と音質面での課題

Roonは、現時点で最も強力で魅力的な音楽管理システムとして、ほぼ例外なく称賛されています。その豊富なメタデータとシームレスなユーザー体験は群を抜いています。しかし、この機能面での優位性には、一部のオーディオマニアからの根強い批判が長年付きまとっていました。それは、他の再生プレーヤーと比較してRoonの音質が損なわれがちであり、「平坦で、退屈で、生命感がない」と表現されることがあるという点です。

この「Roonの音（Roon Sound）」は迷信ではなく、Roonのビットパーフェクト再生ソフトウェアの欠陥でもありません。これは、Roonの強力かつリソースを大量に消費する性質に伴う「症状」と言えます。「処理負荷の大きい」Roon Coreは多大な処理能力を必要とし、それが電気的ノイズ（RFI/EMI）を発生させます。Roon Coreを実行しているコンピュータが、ノイズに対して敏感なDAコンバーター（DAC）の近くにあると、このノイズがアナログ出力段に混入し、ディテールを覆い隠し、音場を狭め、音楽から活力を奪ってしまうのです。

---

### 「対症療法」を超えた根本的な解決策へ

Roon Labs自身も、この主要な問題を解決するために「2筐体」構成のアーキテクチャを推奨しています。負荷の高い**Roon Core**と、軽量なネットワーク**エンドポイント**（ストリーミングトランスポートとも呼ばれます）を分離する手法です。これは負荷の高い処理を遠隔のコンピュータに逃がし、そのノイズをオーディオラックから隔離するため、正しい第一歩と言えます。

しかし、この優れた2階層（2-tier）設計であっても、より微細な問題が残ります。Roon独自のRAATを含む標準的なネットワークプロトコルは、オーディオデータを断続的な「バースト（塊）」として送信します。これにより、エンドポイントのCPUはこれらバーストを処理するために常に活動の急上昇（スパイク）を強いられ、電流消費の急激な変動を引き起こします。この変動が、DACに最も近いコンポーネントであるエンドポイント自体で低周波の電気的ノイズを発生させてしまうのです。

ハイエンドオーディオ機器メーカーは、このバーストトラフィックの「症状」に対処するため、様々な「対症療法的な」解決策を試みています。電流スパイクをより適切に処理するための巨大なリニア電源、スパイクの強度を最小限に抑えるための超低消費電力CPU、発生したノイズをクリーンアップするための追加のフィルタリング段などです。これらの対策は一定の効果をもたらしますが、ノイズの根本原因である「バースト的な処理プロセス」そのものを解決するわけではありません。

このガイドでは、よりエレガントで劇的に効果のある解決策を提示します。ノイズをクリーンアップしようとするのではなく、そもそもノイズが発生しないアーキテクチャを構築します。

---

### 3階層（3-Tier）アーキテクチャ : Roon + Diretta

このプロジェクトは、Roonが推奨する2筐体構成を、多層的かつ複合的なアイソレーションを提供する究極の3階層（3-tier）システムへと進化させます。

1.  **Tier 1 : Roon Core** : パワフルなRoonサーバーはリスニングルームから離れた専用のコンピュータで実行されます。すべての重い処理を引き受け、その電気的ノイズはオーディオシステムから隔離されます。
2.  **Tier 2 : Diretta Host** : 構築する1台目のRaspberry Piは**Diretta Host**として機能します。メインネットワークに接続してRoon Coreからオーディオストリームを受信し、それを極めて小さく、正確にタイミング制御されたセグメントに分割して送信することで、元のストリームのバースト的な性質を排除します。
3.  **Tier 3 : Diretta Target** : 2台目のRaspberry Piである**Diretta Target**は、短いEthernetケーブルを介してHost Piに*のみ*接続し、ポイント・ツー・ポイントの電気的に隔離された（ガルバニックアイソレーション）リンクを構築します。Hostからオーディオを受信し、USB経由でDACまたはDDCに接続します。

### DirettaとAudioLinuxがもたらすメリット

この設計の優位性は、Raspberry Piデバイス上で実行される2つの主要なソフトウェアコンポーネントによるものです。

* **AudioLinux** : オーディオマニア向けに特別に設計された専用のリアルタイムオペレーティングシステムです。汎用OSとは異なり、プロセッサのレイテンシやシステムの「ジッター」を最小限に抑えるよう最適化されており、エンドポイントに安定した低ノイズの基盤を提供します。
* **Diretta** : この画期的なプロトコルこそが、根本原因を解決する秘訣です。エンドポイントにおける処理負荷の変動が低周波の電気的ノイズを生成し、それがDACの内部フィルタリング（電源電圧変動除去比、すなわちPSRRで定義されます）をかいくぐってアナログ性能を微細に低下させることをDirettaは見出しました。これに対抗するため、Direttaは「Host-Target」モデルを採用しています。Hostは、小さく均等な間隔のパケットの連続的かつ同期されたストリームとしてデータを送信します。これによりTargetデバイス上の処理負荷が「平均化」され、消費電流が安定し、この有害な電気的ノイズの発生を最小限に抑えます。

ポイント・ツー・ポイントのEthernetリンクによる物理的なガルバニックアイソレーションと、Direttaプロトコルによる処理ノイズの排除の組み合わせは、DACへの非常にクリーンな信号経路を生み出します。これは、何千ドルもする市販のソリューションを凌駕する実力を持っています。

---

### 至高の音質へ至るやりがいのある道

このプロジェクトは、単なる技術的な作業にとどまりません。ホビーとして深く関わり、システムのパフォーマンスを自ら直接コントロールする素晴らしい手段です。この「Diretta Bridge」を構築することで、単にコンポーネントを組み立てるだけでなく、デジタルオーディオの核心的な課題に真正面から取り組む最先端のアーキテクチャを実装することになります。デジタル再生において本当に重要なことは何かについて理解が深まり、Roonからこれまで不可能だと思っていたレベルの透明感、ディテール、そして音楽的なリアリズムを引き出すという見返りを得ることができるでしょう。

それでは、始めましょう。

---

米国での価格を基準にすると、評価用の44.1/48 kHz再生に限定された基本構成を構築するのに約320ドル（税・送料別）かかり、さらにハイレゾ再生を有効にするために100ユーロが必要となります（価格は変更される場合があります）。
- ハードウェア（240ドル）
- AudioLinuxの1年間サブスクリプション（79ドル）
- Diretta Targetライセンス（100ユーロ）

## 目次
1.  [前提条件](#1-前提条件)
2.  [初期イメージの準備](#2-初期イメージの準備)
3.  [コアシステムの構成（両方のデバイスで実施）](#3-コアシステムの構成両方のデバイスで実施)
4.  [システムアップデート（両方のデバイスで実施）](#4-システムアップデート両方のデバイスで実施)
5.  [ポイント・ツー・ポイント・ネットワーク構成](#5-ポイントツーポイントネットワーク構成)
6.  [便利で安全なSSHアクセス](#6-便利で安全なsshアクセス)
7.  [一般的なシステム最適化](#7-一般的なシステム最適化)
8.  [Direttaソフトウェアのインストールと構成](#8-direttaソフトウェアのインストールと構成)
9.  [最終手順とRoonの統合](#9-最終手順とroonの統合)
10. [付録 1 : オプションのArgon ONEファン制御](#10-付録-1オプションのargon-oneファン制御)
11. [付録 2 : オプションの赤外線（IR）リモコン](#11-付録-2オプションの赤外線irリモコン)
12. [付録 3 : オプションのピュリストモード（Purist Mode）](#12-付録-3オプションのピュリストモードpurist-mode)
13. [付録 4 : オプションのシステム管理Web UI](#13-付録-4オプションのシステム管理web-ui)
14. [付録 5 : システムヘルスチェック](#14-付録-5システムヘルスチェック)
15. [付録 6 : オプションのリアルタイムパフォーマンスチューニング](#15-付録-6オプションのリアルタイムパフォーマンスチューニング)
16. [付録 7 : オプションのIRQおよびスレッド最適化](#16-付録-7オプションのirqおよびスレッド最適化)
17. [付録 8 : オプションのピュリストネットワーク速度](#17-付録-8オプションのピュリストネットワーク速度)
18. [付録 9 : オプションのジャンボフレーム最適化](#18-付録-9オプションのジャンボフレーム最適化)
19. [付録 10 : オプションのシステムアップデート](#19-付録-10オプションのシステムアップデート)

---

### **このガイドの使い方**

このガイドは、手動でのファイル編集の必要性を最小限に抑え、できるだけシンプルに進められるよう設計されています。主な作業フローは、本ドキュメントのコマンドブロックを**コピーして貼り付け（コピー＆ペースト）**、Raspberry Piデバイスに接続されたターミナルウィンドウに直接入力する形になります。

ほとんどの手順で実行するプロセスは以下の通りです。

1.  **SSH接続する** : 各セクション의指示に従い、メインのコンピュータからSSHクライアントを使用して、**Diretta Host**または**Diretta Target**にログインします。
2.  **コマンドをコピーする** : ウェブブラウザ上で、本ガイドのコマンドブロックの右上隅にカーソルを合わせると、**コピーアイコン**が表示されます。それをクリックして、ブロック全体をクリップボードにコピーします。
3.  **貼り付けて実行する** : コピーしたコマンドを適切なSSHターミナルウィンドウに貼り付け、`Enter`キーを押します。

スクリプトとコマンドは安全性を考慮して慎重に作成されており、複数回実行してもエラーが発生しないようになっています。このコピー＆ペーストの手順に従うことで、よくある入力ミスや設定エラーを防止できます。

---

### ビデオによる実演ガイド

プロセスの流れを説明する短い動画シリーズへのリンクは以下の通りです。

* [2台のRaspberry Piコンピュータを使用したDiretta構築ガイドの実演](https://youtube.com/playlist?list=PLMl09rJ6zKCk13V-IH_kRKW7FP8Q0_Fw0&si=u_E8rUEhgMiQ4NIb)

---

### 1. 前提条件

#### ハードウェア

必要な部材（BOM：部品構成表）の一覧を以下に示します。他のパーツで代用することも可能ですが、ここに挙げた特定のコンポーネントを使用することで、構築成功の確率が高まります。

**主要コンポーネント（[pishop.us](https://www.pishop.us/)または同等のサプライヤーから入手）:**
* 2 x [Raspberry Pi 5 / 1GB](https://www.pishop.us/product/raspberry-pi-5-1gb/)
* 2 x [Flirc Raspberry Pi 5ケース](https://www.pishop.us/product/flirc-raspberry-pi-5-case/)
* 2 x [64 GB A2 microSDXCカード](https://www.bhphotovideo.com/c/product/1830849-REG/lexar_lmssipl064g_bnanu_64gb_silver_plus_microsdxc.html)
* 2 x [Raspberry Pi公式 45W USB-C電源アダプター（白）](https://www.pishop.us/product/raspberry-pi-45w-usb-c-power-supply-white/)

**必須のネットワークコンポーネント:**
* 1 x [Plugable USB3 - Ethernet アダプター](https://www.amazon.com/dp/B00AQM8586) (Diretta Host用)
* 1 x [短いCAT6 Ethernetパッチケーブル](https://www.amazon.com/Cable-Matters-Snagless-Ethernet-Internet/dp/B0B57S1G2Y/?th=1) (ポイント・ツー・ポイント接続用)

**トラブルシューティングに役立つオプションの機器:**
* 1 x [Micro-HDMI - 標準HDMI (A/M) 2mケーブル（白）](https://www.pishop.us/product/micro-hdmi-to-standard-hdmi-a-m-2m-cable-white/)
* 1 x [Raspberry Pi公式キーボード（赤/白）](https://www.pishop.us/product/raspberry-pi-official-keyboard-red-white/)

**オプションのアップグレードパーツ:**
* 2 x [Argon ONE V3 Raspberry Pi 5ケース](https://www.amazon.com/Argon-ONE-V3-Raspberry-Case/dp/B0CNGSXGT2/) (Flircケースの代替品として)
* 1 x [Argon 赤外線（IR）リモコン](https://www.amazon.com/Argon-Raspberry-Infrared-Batteries-Included/dp/B091F3XSF6/) (Diretta Hostにリモコン制御機能を追加するため)
* 1 x [Flirc USB赤外線（IR）レシーバー](https://www.pishop.us/product/flirc-rpi-usb-xbmc-ir-remote-receiver/) (Flircケースに入れたDiretta HostでArgon IRリモコンを使用するため)
* 1 x [Blue Jeans Cable BJC CAT6a Belden Bonded Pairs 500 MHz](https://www.bluejeanscable.com/store/data-cables/index.htm) (HostとTarget間のポイント・ツー・ポイント接続用)
* 1 x [iFi SilentPower iPower Elite](https://www.amazon.com/gp/product/B08S622SM7/) (Diretta Targetにクリーンな電力を供給するため)
* 1 x [iFi SilentPower Pulsar USBケーブル](https://www.silentpower.tech/products/pulsar-usb) (ガルバニックアイソレーション機能付きUSB接続ケーブル)
* 1 x [DC 5.5mm x 2.1mm - USB-Cアダプター](https://www.amazon.com/5-5mm-Adapter-Female-Convert-Connector/dp/B0CRB7N4GH/) (iPower EliteのプラグをDiretta TargetのUSB-C電源入力に変換するために必要)
* 1 x [SMSL PO100 PRO DDC](https://www.amazon.com/dp/B0BLYVZCV5) (USB入力の設計が不十分なDAC向けデジタル・ツー・デジタルコンバーター)
* 1 x [USB無線LANアダプター](https://www.pishop.us/product/raspberry-pi-dual-band-5ghz-2-4ghz-usb-wifi-adapter-with-antenna/) (有線接続の方がはるかに望ましく信頼性も高いですが、オーディオシステムの近くに有線LANを引き回すのが現実的でない場合、Plugable USB - Ethernetアダプターの代わりにこのWi-Fi adapterを使用します)
* 1 x [電源用2分配ケーブル](https://www.amazon.com/dp/B01K3ADXX2?th=1) (2基の45W電源アダプターを1つのコンセントに差し込むため)

**必須のオーディオ機器:**
* 1 x USB DACまたはDDC

**構築に必要な作業ツール:**
* Linux、macOS（iTerm2、https://iterm2.com/ 推奨）、またはMicrosoft Windows（[WSL2](https://learn.microsoft.com/ja-jp/windows/wsl/install)搭載）が動作するノートPCまたはデスクトップPC
* SDまたはmicroSDカードリーダー
* HDMI対応のテレビやディスプレイ、およびUSBキーボード（トラブルシューティング用に役立ちます。オプション）

#### ソフトウェアおよびライセンス費用

* **AudioLinux** : 愛好家には「アンリミテッド（無期限）」ライセンスが推奨され、現在の価格は**158ドル**です（価格は変更される場合があります）。ただし、最初は現在の年間サブスクリプション（**79ドル**）で始めても問題ありません。どちらのオプションも、同じ場所（住宅内）にある複数のデバイスにインストール可能です。
* **Diretta Target** : Diretta Targetデバイスを介したハイレゾ再生（48 kHzを超えるPCM）にはライセンスが必要で、現在の価格は**100ユーロ**です。
    * 44.1/48 kHzのストリームを使用すれば、評価用として長期間のテストが可能です。そのため、評価期間中はRoonの「MUSE」DSP設定内にある「サンプルレート変換（Sample rate conversion）」機能を使用し、すべてのコンテンツを44.1 kHzに変換して出力することをお勧めします。動作に満足できたら、Diretta Targetライセンスを購入して制限を解除してください。ライセンス購入後、Direttaチームから「ご使用のハードウェアがデータベースでアクティベートされた」旨を通知する2通目のメールが届くまでは、サンプルレート変換設定を有効にしたままにしておいてください。
    * **重要 :** このライセンスは、購入時に使用した特定のRaspberry Piのハードウェアに「紐付け（ロック）」されます。恒久的に使用する予定のハードウェアそのものを使って、最終的なライセンス適用手続きを行うことが不可欠です。
    * Direttaは最初の2年以内のハードウェア故障に対して、1回限りの代替ライセンスを提供する場合があります（購入時に利用規約をご確認ください）。それ以外の理由でハードウェアを変更した場合は、新規にライセンスを購入する必要があります。

---

### 2. 初期イメージの準備

1.  **購入とダウンロード** : [公式ウェブサイト](https://www.audio-linux.com/)からAudioLinuxイメージを購入します。通常、購入後24時間以内に、`.img.gz`または`.img.xz`ファイルをダウンロードするためのリンクが記載されたメールが届きます。
2.  **イメージの書き込み** : [Raspberry Pi Imager](https://www.raspberrypi.com/software/)を使用して、ダウンロードしたAudioLinuxイメージを**両方**のmicroSDカードに書き込み（フラッシュ）します。

---

### 3. コアシステムの構成（両方のデバイスで実施）

イメージの書き込み完了後、ネットワーク上での競合を避けるため、各Raspberry Piを個別に構成する必要があります。

最高のパフォーマンスを得るために、本ガイドではDiretta Target（DACに接続されるデバイス）とDiretta Hostの両方にRaspberry Pi 5を使用します。まずHostから設定を行います。

> **極めて重要な警告：** 双方のデバイスは全く同じイメージから書き込まれているため、同一の`machine-id`を持ちます。同一のLANに接続した状態で2台のデバイスの電源を同時に投入すると、DHCPサーバーが両方に同じIPアドレスを割り当ててしまい、ネットワークの競合が発生する可能性が高くなります。
>
> **各デバイスの初回起動と初期設定は、必ず1台ずつ個別に行ってください。**

1.  **1台目**のRaspberry PiにmicroSDカードを挿入し、ネットワークに接続して電源を入れます。**注意** : Argon ONEケースを使用している場合、ファンからかなりの動作音が発生する場合がありますが、心配いりません。Direttaのセットアップ完了後に、ファンのノイズに対処するための手順が[付録 1](#10-付録-1オプションのargon-oneファン制御)に用意されています。
2.  この1台目のデバイスに対して、**セクション3のすべての手順**を完了させます。
3.  独自の新しい構成で1台目のデバイスが再起動したら、電源を切ります。
4.  次に、**2台目**のRaspberry Piの電源を投入し、同様に**セクション3のすべての手順**を繰り返します。

デフォルトのSSHユーザーおよびsudo/rootのパスワードについては、Audiolinux購入時のレシート（領収メール）を参照してください。このプロセス全体で何度も使用することになるため、メモを取っておくことをお勧めします。

このプロセス全体を通じて、ローカルコンピュータのSSHクライアントを使用してRPiコンピュータにログインします。これを行うには、再起動ごとに変更される可能性があるRPiのIPアドレスを確認する手段が必要です。この情報を得る最も簡単な方法は、家庭内ネットワークルーターのWeb管理画面または専用アプリを確認することですが、スマートフォンやタブレットに[fing](https://www.fing.com/app/)アプリをインストールして確認することもできます。

いずれかのRPiコンピュータのIPアドレスを確認できたら、ローカルコンピュータのSSHクライアントを使用して次のプロセスでログインします。このガイドでは全体を通じてこれに類似したコマンドを使用するため、記述されている`ssh`コマンドの例を控えておいてください。
```bash
cmd=$(cat <<'EOT'
read -rp "RPiのアドレスを入力して[enter]を押してください: " RPi_IP_Address
echo '注意：デフォルトのパスワードはPieroから届いたAudioLinuxのメールに記載されています'
echo '$' ssh "audiolinux@${RPi_IP_Address}"
ssh -o StrictHostKeyChecking=accept-new "audiolinux@${RPi_IP_Address}"
EOT
)
bash -c "$cmd"
```

#### 3.1. Machine IDの再生成

`machine-id`は、OSインストールに対する一意の識別子です。これはデバイスごとに異なる値にする必要があります。

```bash
echo ""
echo "古いマシンID: $(cat /etc/machine-id)"
sudo rm /etc/machine-id
sudo systemd-machine-id-setup
echo "新しいマシンID: $(cat /etc/machine-id)"
```

#### 3.2. 一意のホスト名（Hostname）の設定

簡単に識別できるように、各デバイスに明確なホスト名を設定します。**注意 :** もしこれが本手順を使用した初めての構築ではなく、すでにネットワーク上にDiretta Host/Targetのペアが存在する場合は、今回の新しいDiretta Hostには`diretta-host2`のような異なる名前を設定することを検討してください。そうすることで、後で両方に個別にアクセスしやすくなります。

**1台目のデバイス（将来のDiretta Host）での作業 :**
```bash
# Diretta Host上
sudo hostnamectl set-hostname diretta-host
```

**2台目のデバイス（将来のDiretta Target）での作業 :**
```bash
# Diretta Target上
sudo hostnamectl set-hostname diretta-target
```

**ここでデバイスをシャットダウンします。2台目のRaspberry Piに対して、[上記の手順](#3-コアシステムの構成両方のデバイスで実施)を繰り返します。**
```bash
sudo sync && sudo poweroff
```

---

### 4. システムアップデート（両方のデバイスで実施）

このセクションの手順を行う際、通常はDiretta Host側でセクション4のすべてを完了させてから、Diretta Target側でセクション全体を繰り返すのが最も効率的（かつ混乱が少ない）です。

各RPiはそれぞれ固有のmachine IDを持ったため、両方の電源を投入して構いません。2本のネットワークケーブルがある場合は、次の数ステップのために両方を同時にホームネットワークに接続すると便利ですが、そうでない場合は1台ずつ進めることもできます。**注意** : ルーターは最初にログインしたときとは異なるIPアドレスを割り当てる可能性が高いため、以降のSSHコマンドでは必ず新しいIPアドレスを使用してください。以下はログイン用コマンドのリマインダーです。

```bash
cmd=$(cat <<'EOT'
read -rp "RPiの(新しい)アドレスを入力して[enter]を押してください: " RPi_IP_Address
echo '$' ssh "audiolinux@${RPi_IP_Address}"
ssh -o StrictHostKeyChecking=accept-new "audiolinux@${RPi_IP_Address}"
EOT
)
bash -c "$cmd"
```

#### 4.1. システムクロック更新用「Chrony」のインストール

アップデートをインストールする前に、システムクロック（時刻）が正確である必要があります。Raspberry PiにはNVRAMバッテリーが搭載されていないため、起動するたびに時刻を設定する必要があります。これは通常、ネットワークサービスに接続して行われます。このスクリプトは、起動時に時刻を設定し、コンピュータの稼働中に正確な状態を維持するようにします。

```bash
sudo id
curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_chrony.sh | sudo bash
sleep 5
chronyc sources
```

#### 4.2. タイムゾーンの設定

```bash
cmd=$(cat <<'EOT'
clear
echo "対話型タイムゾーン設定へようこそ。"
echo "最初に地域を選択し、次に特定のタイムゾーンを選択します。"

# ユーザーが地域を選択できるようにする
PS3="地域に対応する番号を選択してください: "

select region in $(timedatectl list-timezones | grep -F / | cut -d/ -f1 | sort -u); do
  if [[ -n "$region" ]]; then
    echo "次の地域が選択されました: $region"
    break
  else
    echo "無効な選択です。もう一度お試しください。"
  fi
done

echo ""

# その地域内のタイムゾーンをユーザーが選択できるようにする
PS3="タイムゾーンに対応する番号を選択してください: "

select timezone in $(timedatectl list-timezones | grep "^$region/"); do
  if [[ -n "$timezone" ]]; then
    echo "次のタイムゾーンが選択されました: $timezone"
    break
  else
    echo "無効な選択です。もう一度お試しください。"
  fi
done

# 選択されたタイムゾーンを設定する
echo
echo "タイムゾーンを${timezone}に設定しています..."
sudo timedatectl set-timezone "$timezone"
echo "✅ タイムゾーンが設定されました。"

# 変更を確認する
echo
echo "現在のシステム時刻とタイムゾーン:"
timedatectl status
EOT
)
bash -c "$cmd"
```

#### 4.3. DNSユーティリティのインストール
`dnsutils`パッケージをインストールして、**menu**アップデートが`dig`コマンドにアクセスできるようにします。
```bash
sudo pacman -S --noconfirm --needed dnsutils
```

#### 4.4. システムおよびメニューのアップデートの実行

すべてのアップデートを行うには、AudioLinuxのメニューシステムを使用します。Piero氏から届いたメールに記載されている、イメージダウンロード用のユーザー名とパスワードを手元に用意してください。これらはメニューのアップデートで必要になります。途中で「**your menu update user（メニューアップデート用ユーザー）**」を求められますが、これは少し紛らわしいです。ここでは、AudioLinuxのインストールイメージをダウンロードする際に使用したユーザー名とパスワードを入力します。

1.  ターミナルで`menu`を実行します。
2.  **INSTALL/UPDATE menu**を選択します。
    ```text
    Verifying license...
    Please enter the email address used at the time of purchase
    (You will only be asked once)
    ?
    <email address used to purchase AudioLinux support>
    OK
    OK

    Please type your menu update user
    ?
    <AUDIOLINUX RASPBERRY "user:" from your license email)>
    Please type your menu update password
    ?
    <AUDIOLINUX RASPBERRY "password:" from your license email)>
    ```
3.  次の画面で**UPDATE system**を選択し、処理を完了させます。
4.  システムアップデートの完了後、同じ画面で**Update menu**を選択して最新バージョンのAudioLinuxスクリプトを取得します。*注意 :* AudioLinuxの購入時に使用したメールアドレス、およびダウンロード用のユーザー名とパスワードが必要になります。
5.  メニューシステムを終了し、ターミナルに戻ります。

#### 4.5. 再起動
カーネルおよびその他のアップデートをロードするために再起動します。
```bash
sudo sync && sudo reboot
```

---

### 5. ポイント・ツー・ポイント・ネットワーク構成

このセクションでは、専用のプライベートリンクを有効にするためのネットワーク設定ファイルを作成します。物理キーボードやディスプレイ（コンソールアクセス）を必要としないようにするため、双方のデバイスがメインLANに接続され、SSH経由でアクセスできる状態のまま、これらの手順を実施します。

Diretta Targetのアップデートを終えたばかりの場合は、[こちら](https://github.com/dsnyder0pc/rpi-for-roon/blob/main/Diretta.md#52-pre-configure-the-diretta-target)をクリックして、Target用のポイント・ツー・ポイント・ネットワーク構成手順にジャンプしてください。

---
> #### **ネットワーク構成に関する注意：なぜシンプルなブリッジにしないのか？**
>
> AudioLinuxに慣れているユーザーは、`menu`システムで提供されているよりシンプルなネットワークブリッジオプションを使用せず、なぜこのガイドがあえて特定のスクリプトを使用してNATを伴うルーティング接続によるポイント・ツー・ポイント・リンクを構築するのか疑問に思うかもしれません。これは、可能な限り高いレベルのネットワーク隔離（アイソレーション）を実現するために選択された、意図的なアーキテクチャ上の設計です。
>
> * **ネットワークブリッジ**を採用した場合、Diretta TargetがメインのLAN上に直接配置され、オーディオ再生とは無関係なネットワーク全体のブロードキャストやマルチキャストトラフィックにさらされることになります。
> * 今回の**ルーティング設定**では、ファイアウォールで保護された完全に別のサブネットが構築されます。Diretta Hostが不要なすべてのネットワークの「雑音」からTargetを保護し、Targetのプロセッサがオーディオストリームのみを処理するようにします。これによりシステム全体の活動と電気的ノイズの発生リスクが最小限に抑えられます。これが、このピュリスト的（純粋主義的）アーキテクチャの究極の目標です。
>
> 機能的なセットアップはブリッジの方が簡単ですが、ルーティング方式はアイソレーションを最大化することで、オーディオパフォーマンスにおいて理論的により優れた基盤を提供します。
---

#### 5.1. Diretta Hostの事前設定

1.  **ネットワークファイルの作成 :**
    **Diretta Host**で以下の2つのファイルを作成します。`end0.network`ファイルは将来のポイント・ツー・ポイント接続のための静的IPを設定します。`usb-uplink.network`ファイルは、USB EthernetアダプターがメインのLANから継続してIPアドレスを取得できるようにします。

    *ファイル : `/etc/systemd/network/end0.network`*
    ```bash
    cat <<'EOT' | sudo tee /etc/systemd/network/end0.network
    [Match]
    Name=end0

    [Link]
    MTUBytes=1500

    [Network]
    Address=172.20.0.1/24
    EOT
    ```

    *ファイル : `/etc/systemd/network/usb-uplink.network`*
    ```bash
    cat <<'EOT' | sudo tee /etc/systemd/network/usb-uplink.network
    [Match]
    Name=en[pu]*

    [Link]
    MTUBytes=1500

    [Network]
    DHCP=yes
    DNSSEC=no
    EOT
    ```

    **重要 :** 古いen.networkファイルが存在する場合は削除してください。
    ```bash
    # 競合を避けるため、古い汎用ネットワークファイルを削除する。
    sudo rm -fv /etc/systemd/network/{en,enp,auto,eth}.network
    ```

    `/etc/hosts`にDiretta Targetのエントリを追加します：
    ```bash
    HOSTS_FILE="/etc/hosts"
    TARGET_IP="172.20.0.2"
    TARGET_HOST="diretta-target"

    # エントリが存在しない場合にのみ、Diretta Targetのエントリを追加する
    if ! grep -q "$TARGET_IP\s\+$TARGET_HOST" "$HOSTS_FILE"; then
      printf "%s\t%s target\n" "$TARGET_IP" "$TARGET_HOST" | sudo tee -a "$HOSTS_FILE"
    fi
    ```

2.  **IPフォワーディングの有効化 :**
    ```bash
    # 現在のセッションで有効にする
    sudo sysctl -w net.ipv4.ip_forward=1

    # 再起動後も永続的に有効にする
    echo "net.ipv4.ip_forward=1" | sudo tee /etc/sysctl.d/99-ip-forwarding.conf
    ```

3.  **ネットワークアドレス変換（NAT）の構成 :**
    ```bash
    # nftがインストールされていることを確認する
    sudo pacman -S --noconfirm --needed nftables

    # ファイアウォールおよびNATルールをインストールする
    cat <<'EOT' | sudo tee /etc/nftables.conf
    #!/usr/sbin/nft -f

    # メモリからすべての古いルールをフラッシュ（消去）する
    flush ruleset

    # 'my_table'という名前の'ip'（IPv4）テーブルを作成する
    table ip my_table {

        # === ルール 2 : ポートフォワーディング（DNAT） ===
        # このチェーンはNATの'prerouting'パスにフックする
        chain prerouting {
            type nat hook prerouting priority dstnat;

            # Hostのポート5101をTargetのポート172.20.0.2:5001に転送する
            tcp dport 5101 dnat to 172.20.0.2:5001
        }

        # === ルール 3 : 転送トラフィックの許可（FILTER） ===
        # このチェーンはパケットフィルタリングの'forward'パスにフックする
        chain forward {
            type filter hook forward priority 0;

            # デフォルトで、すべての転送トラフィックをドロップ（破棄）する
            policy drop;

            # 確立済み、または関連する接続を許可する
            ct state established,related accept

            # ポート転送ルールに一致する新規（NEW）トラフィックを許可する
            ip daddr 172.20.0.2 tcp dport 5001 ct state new accept

            # Targetサブネットからのその他の新規（NEW）トラフィックをすべて許可する
            ip saddr 172.20.0.0/24 accept
        }

        # === ルール 1 : インターネットアクセス（マスカレード） ===
        # このチェーンはNATの'postrouting'パスにフックする
        chain postrouting {
            type nat hook postrouting priority 100;

            # 送信元サブネットから発信されるトラフィックをマスカレード（NAT）する
            # 'enp'、'enu'、または'wlp'で始まるインターフェースを介して送信されるトラフィック
            ip saddr 172.20.0.0/24 oifname "enp*" masquerade
            ip saddr 172.20.0.0/24 oifname "enu*" masquerade
            ip saddr 172.20.0.0/24 oifname "wlp*" masquerade
        }
    }
    EOT

    # 古いiptablesサービスが存在する場合は停止し、無効化する（2>/dev/nullにより存在しない場合のエラーを抑制）
    sudo systemctl disable --now iptables.service 2>/dev/null
    sudo rm /etc/iptables/iptables.rules 2>/dev/null

    # nft経由でルールを有効化し、適用する
    sudo systemctl enable --now nftables.service
    ```

4.  **Plugable USB - Ethernet アダプターの構成**

    デフォルトのUSBドライバーは、Plugable製Ethernetアダプターのすべての機能をサポートしていません。信頼性の高いパフォーマンスを得るために、デバイスが接続されたときの処理方法をカーネルのデバイスマネージャーに通知する必要があります。
    ```bash
    cat <<'EOT' | sudo tee /etc/udev/rules.d/99-ax88179a.rules
    ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="0b95", ATTR{idProduct}=="1790", ATTR{bConfigurationValue}!="1", ATTR{bConfigurationValue}="1"
    EOT
    sudo udevadm control --reload-rules
    ```

5.  **`update_motd.sh`スクリプトの修正**

    ログインバナー（`/etc/motd`）を更新するスクリプトが、2つのネットワークインターフェースが存在する場合を正しく処理できません。この不具合により、再起動後に誤ったIPアドレス情報でログイン画面が乱雑になるのを防止します。以下の新しいスクリプトでこの問題を解決します。
    ```bash
    [ -f /opt/scripts/update/update_motd.sh.dist ] || \
    sudo mv /opt/scripts/update/update_motd.sh /opt/scripts/update/update_motd.sh.dist
    curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/update_motd.sh
    sudo install -m 0755 update_motd.sh /opt/scripts/update/
    rm update_motd.sh
    ```

    最後に、Host the power-offします：
    ```bash
    sudo sync && sudo poweroff
    ```

#### 5.2. Diretta Targetの事前設定

**注意 :** もしDiretta Targetで[ステップ 4](#4-システムアップデート両方のデバイスで実施)を実行していない場合は、[今すぐ](#4-システムアップデート両方のデバイスで実施)実行し、その後ここに戻ってきてください。

**Diretta Target**で、`end0.network`ファイルを作成します。これにより静的IPが構成され、すべてのインターネットトラフィックのゲートウェイとしてDiretta Hostを使用するよう設定されます。

*ファイル : `/etc/systemd/network/end0.network`*
```bash
cat <<'EOT' | sudo tee /etc/systemd/network/end0.network
[Match]
Name=end0

[Link]
MTUBytes=1500

[Network]
Address=172.20.0.2/24
Gateway=172.20.0.1
DNS=1.1.1.1
EOT
```

**重要 :** 古いen.networkファイルが存在する場合は削除してください。
```bash
# 競合を避けるため、古い汎用ネットワークファイルを削除する。
sudo rm -fv /etc/systemd/network/{en,auto,eth}.network
```

Diretta Host用の`/etc/hosts`エントリを追加します。**注意 :** Diretta Hostに別のネットワーク名を選択した場合でも、Diretta TargetがHostを`diretta-host`として認識するように設定するのが最善です。
```bash
HOSTS_FILE="/etc/hosts"
HOST_IP="172.20.0.1"
HOST_NAME="diretta-host"

# エントリが存在しない場合にのみ、Diretta Hostのエントリを追加する
if ! grep -q "$HOST_IP\s\+$HOST_NAME" "$HOSTS_FILE"; then
  printf "%s\t%s host\n" "$HOST_IP" "$HOST_NAME" | sudo tee -a "$HOSTS_FILE"
fi
```

> ---
> ### ⚠️ トポロジーに関する重要な警告 : フィルターは必ず上流に配置すること
>
> LANリジェネレーター、ガルバニックアイソレーター、またはフィルター（StackAudio SmoothLAN、iFi SilentPower LAN iSilencer、LAN iPurifier Proなど）を導入して本システムをアップグレードする場合は、**それらを必ずDiretta Hostの上流**（メインのネットワークスイッチ/ルーターと、HostのUSB-Ethernetアダプターの間）に配置してください。
>
> **HostとTarget間のポイント・ツー・ポイント接続の線上には、ネットワークフィルターやアクティブなリクロックデバイスを決して配置しないでください。** 配置すると、ほぼ例外なくオーディオパフォーマンスが低下し、接続の深刻な不安定化（レグレッション）を引き起こす原因になります。
>
> * **メインLANはノイズの主要な発生源です :** 家庭用ルーターやメインスイッチからの接続ラインは、電磁干渉（EMI）、高周波干渉（RFI）、ブロードキャストの「ジャンク」トラフィックで溢れかえっています。Hostの「手前」にリジェネレーターを配置することで、このデジタル的な汚染を境界線上で遮断できます。これによりHostは極めてクリーンなストリームを処理可能になり、CPU負荷、電力変動、熱ノイズを最小限に抑えることができます。
> * **レイヤー2タイミングの維持 :** 直接のポイント・ツー・ポイントのブリッジ上にアクティブデバイスを介入させると、Direttaの非常に厳しいタイミング制約（`CycleTime`および`syncBufferCount`）に干渉します。これはレイヤー2フレームの精密な伝送を阻害し、音質改善効果を損なったり、レイテンシアーティファクトを発生させたり、あるいはTargetがネットワーク速度の変更を正常にネゴシエートできなくなる原因となります。
> * **カスケードアイソレーションの原則 :** 真の隔離は、デリケートなDACを家庭内ネットワークから完全に切り離すために、何重もの階層構造で構築されます：
>   * **メインネットワーク** → `[ LANフィルター/リジェネレーター ]` → **Diretta Host** *(Hostを家庭内ネットワークから隔離)*
>   * **Diretta Host** → `[ 専用Ethernetケーブル ]` → **Diretta Target** *(ポイント・ツー・ポイント接続およびプロトコルスタックによる隔離)*
> ---

#### 5.3. 物理的接続の変更

> **警告 :** 作成したファイルの内容を念入りにダブルチェックしてください。タイポ（誤字）があると、再起動後にデバイスにアクセスできなくなる可能性があり、復旧にコンソール作業やSDカードの再書き込みが必要になります。

1.  ファイルの内容を確認したら、**両方**のデバイスをクリーンシャットダウンします：
    ```bash
    sudo sync && sudo poweroff
    ```
2.  メインのLANスイッチ/ルーターから両方のデバイスを取り外します。
3.  Diretta Hostの**オンボードEthernetポート**と、Diretta Targetの**オンボードEthernetポート**を1本のEthernetケーブルで直接接続します。
4.  Diretta Hostコンピュータの青いUSB 3.0ポートのいずれかに**USB-Ethernetアダプター**を差し込みます。
5.  Diretta Host上の**USB-Ethernetアダプター**をメインのLANスイッチ/ルーターに接続します。
6.  両方のデバイスの電源を入れます。

起動すると、自動的に新しいネットワーク構成が適用されます。**注意** : Diretta HostはUSB-Ethernetアダプター経由で家庭内ネットワークに接続されるようになるため、IPアドレスが変更されている可能性が高いです。ルーターのWeb管理画面やFingアプリを使用して新しいアドレスを確認してください。この時点でIPアドレスは安定するはずです。

```bash
cmd=$(cat <<'EOT'
read -rp "Direttaホストの最終アドレスを入力して[enter]を押してください: " RPi_IP_Address
echo '$' ssh "audiolinux@${RPi_IP_Address}"
ssh -o StrictHostKeyChecking=accept-new "audiolinux@${RPi_IP_Address}"
EOT
)
bash -c "$cmd"
```

HostからTargetへpingが通ることを確認できるはずです：
```bash
echo ""
echo "\$ ping -c 3 172.20.0.2"
ping -c 3 172.20.0.2
```

また、HostからTargetにログインできるはずです：
```bash
echo ""
echo "\$ ssh target"
ssh -o StrictHostKeyChecking=accept-new target
```

Targetからインターネット上のホストへpingを送信し、インターネット接続が機能していることを確認します：
```bash
echo ""
echo "\$ ping -c 3 one.one.one.one"
ping -c 3 one.one.one.one
```

---

### 6. 便利で安全なSSHアクセス

#### 6.1. `ProxyJump`設定の必要性

ネットワークの構成が完了したため、**Diretta Target**は隔離されたネットワーク（`172.20.0.0/24`）上にあり、メインLANから直接アクセスすることはできません。Targetにアクセスする唯一の方法は、**Diretta Host**を経由して「ジャンプ」することです。

ローカルのSSH設定で`ProxyJump`ディレクティブを使用するのが、これを実現するための標準的かつ必須の方法です。

1.  ローカルコンピュータ（Raspberry Pi上ではありません）でこのコマンドを実行します。Diretta HostのIPアドレスを入力するよう求められ、その後、必要な正確な設定ブロックが出力されます。
```bash
cmd=$(cat <<'EOT'
clear
# --- インタラクティブなSSHエイリアス設定スクリプト ---

SSH_CONFIG_FILE="$HOME/.ssh/config"
SSH_DIR="$HOME/.ssh"

# --- .sshディレクトリとconfigファイルが存在し、正しい権限が設定されていることを確認する ---
mkdir -p "$SSH_DIR"
chmod 0700 "$SSH_DIR"
touch "$SSH_CONFIG_FILE"
chmod 0600 "$SSH_CONFIG_FILE"

# --- 推奨されるグローバル設定ブロックを定義する ---
GLOBAL_SETTINGS=$(cat <<'EOF'
# --- 推奨されるグローバルSSH設定 ---
Host *
    AddKeysToAgent yes
    IdentityFile ~/.ssh/id_ed25519

EOF
)

# --- グローバル設定が存在しない場合は、ファイルの先頭に挿入する ---
if ! grep -q "AddKeysToAgent yes" "$SSH_CONFIG_FILE"; then
  echo "✅ 推奨されるグローバルSSH設定を追加しています..."
  # 設定を先頭に挿入するために一時ファイルを使用する
  echo "$GLOBAL_SETTINGS" | cat - "$SSH_CONFIG_FILE" > temp_ssh_config && mv temp_ssh_config "$SSH_CONFIG_FILE"
else
  echo "✅ 推奨されるグローバルSSH設定は既に存在します。変更は行われませんでした。"
fi

# --- Diretta固有のホスト設定を追加する ---
if grep -q "Host diretta-host" "$SSH_CONFIG_FILE"; then
  echo "✅ 'diretta-host'のSSH設定は既に存在します。変更は行われませんでした。"
else
  read -rp "DirettaホストのLAN IPアドレスを入力して[Enter]を押してください: " Diretta_Host_IP

  # 分かりやすくするためにヒアドキュメントを使用して新しい設定を追加する
  cat <<EOT_HOSTS >> "$SSH_CONFIG_FILE"

# --- Diretta設定（スクリプトにより追加） ---
Host diretta-host host
    HostName ${Diretta_Host_IP}
    User audiolinux

Host diretta-target target
    HostName 172.20.0.2
    User audiolinux
    ProxyJump diretta-host
EOT_HOSTS

  echo "✅ 'diretta-host'および'diretta-target'のSSH設定が追加されました。"
fi

# --- 本ガイドの古いバージョンに含まれていたStrictHostKeyCheckingの設定をクリーンアップする ---
# 推奨されるSSH鍵のセットアップでは、これは不要になります
if command -v sed >/dev/null; then
    sed -i.bak -e '/StrictHostKeyChecking/d' "$SSH_CONFIG_FILE"
    # 残っている可能性のある空行を削除する
    sed -i.bak -e '/^$/N;/^\n$/D' "$SSH_CONFIG_FILE"
    rm -f "${SSH_CONFIG_FILE}.bak"
fi

echo ""
echo "--- 現在の~/.ssh/configファイルの内容は次のとおりです: ---"
cat "$SSH_CONFIG_FILE"
EOT
)
bash -c "$cmd"
```

2.  **接続の確認 :**

これで、新しいエイリアスを使用して両方のデバイスに接続できるようになりました。以下のコマンドで接続をテストしてください：

**Diretta Hostにログインする場合：**
```bash
ssh -o StrictHostKeyChecking=accept-new diretta-host
```

「`exit`」と入力してログアウトします。

**Diretta Targetにログインする場合：** _（パスワードの入力が2回求められます）_
```bash
ssh -o StrictHostKeyChecking=accept-new diretta-target
```
**注意 :** パスワードの入力は、1回目が接続経路となるdiretta-host（踏み台サーバー / jump box）に対して、2回目がdiretta-target自体に対して求められます。次のセクションで、これをシームレスな鍵認証（パスワードなし）に変更します。

**注意 :** 省略形として`ssh host`および`ssh target`を使用することも可能です。

#### 6.2. 推奨 : SSH鍵を使用した安全な認証

パスワード認証も可能ですが、最も安全かつ便利な方法は公開鍵認証です。このSSH設定によりプロセスの大部分が自動化されます。一度設定してしまえば、以降はパスワードを入力することなく、HostとTargetの両方に安全にログインできるようになります。

**ローカルコンピュータ上での作業：**

1.  **SSH鍵の作成（まだ作成していない場合）：**
    `ed25519`のような現代的なアルゴリズムを使用するのがベストプラクティスです。入力を求められたら、強固で覚えやすい**パスフレーズ**を設定してください。これはログイン用のパスワードではなく、秘密鍵ファイル自体を保護するためのパスワードです。

    ```bash
    ssh-keygen -t ed25519 -C "audiolinux"
    ```

2.  **公開鍵のデバイスへのコピー：**
    これらのコマンドにより、作成した鍵のアクセス権限を各デバイスに安全に付与します。最初のコマンドでDiretta Hostのパスワードが求められます。これによりHostへの接続がパスワード不要（パスワードレス）になるため、2番目のコマンドではDiretta Targetのパスワードのみが求められます。

    ```bash
    echo ""
    ssh-copy-id diretta-host
    echo ""
    ssh-copy-id diretta-target
    ```

3.  **安全なログイン：**
    これで、各デバイスにSSH接続できるようになります。それぞれ初めて接続する際に、ステップ1で作成した**パスフレーズ**の入力が求められます。

    ```bash
    ssh diretta-host
    ```

      * **Linuxの場合：** `AddKeysToAgent yes`設定により、現在のターミナルセッションのSSHエージェントに鍵が登録されます。そのため、コンピュータを再起動するか新しいログインセッションを開始するまでは、パスフレーズの再入力を求められることはありません。

---

### （オプション）Linux環境での使い勝手の向上

Linuxユーザーで、macOSと同様に再起動後もSSH鍵のパスフレーズを維持させたい場合は、`keychain`のインストールを強くお勧めします。

  * **keychainのインストール（Ubuntu/Debianの場合）：**

    ```bash
    sudo apt update && sudo apt install keychain
    ```

  * **シェルの設定：** ターミナルを開いたときに`keychain`が起動するよう、`~/.bashrc`（または`~/.zshrc`、`~/.profile`など）に以下の行を追加します。再起動後に初めてターミナルを開いたときにのみ、パスフレーズの入力を求められます。

    ```bash
    eval "$(keychain --eval --quiet id_ed25519)"
    ```

  * 新しいターミナルを開くか、`source ~/.bashrc`を実行してシェルをリロードします。

これで、SSH鍵による安全な認証により、パスワードの入力を求められることなく、両方のデバイスにSSH接続（`ssh diretta-host`、`ssh diretta-target`）できるようになります。

---

### 7. 一般的なシステム最適化

これらの手順は、Diretta HostとTargetの**両方**のコンピュータで実施してください。後で`menu`を使用してアップデートを実行した場合は、`sudoers`の修正を再実行する必要があります。

#### 7.1. systemdの「劣化（degraded）」状態の修正

AudioLinuxを新規インストールした状態では、システムのステータスが`degraded`（劣化）と報告されることがよくあります。これは通常、システムのグループファイル（`/etc/group`と`/etc/gshadow`）間における無害な不整合が原因です。以下のコマンドでこれらのファイルを安全に同期させることで、失敗していた`shadow.service`を解決し、健全なシステム状態を確保します。

```bash
sudo grpconv
```

#### 7.2. `sudoers`ルールの優先順位の補正

メインの`/etc/sudoers`ファイルにあるデフォルトのルールが、Web UIや他の機能に必要なより具体的なルールを上書きしてしまうことがあります。その結果、パスワード入力なしで実行できるはずのコマンドに対して、誤ってパスワードの入力が求められる問題が発生します。

以下のスクリプトは、`/etc/sudoers`ファイルのルールの順序を安全に補正し、例外設定が正しく処理されるようにします。このスクリプトは、不適切な順序が検出された場合にのみ変更を加えます。

```bash
SUDOERS_FILE="/etc/sudoers"
TEMP_SUDOERS=$(mktemp)

# Perlフィルターを使用して、補正されたバージョンのsudoersファイルを作成する。
# このスクリプトはべき等であり、すでに正しい状態のファイルは変更しません。
sudo cat "$SUDOERS_FILE" | perl -e '
while (<>) {
  if (m{/etc/sudoers.d} and not $found_audiolinux_all) {
    pop @lines if $#lines > -1 and $lines[$#lines] =~ /^$/;
    push @drop_in, $_;
  } else {
    push @lines, $_;
  }
  if (/^audiolinux ALL=\(ALL\) ALL$/) {
    $found_audiolinux_all++;
    push @lines, ("\n", @drop_in) if @drop_in;
  }
}
print @lines;
' > "$TEMP_SUDOERS"

# インストール前に、visudoを使用して新しいファイルを検証する
if [ -s "$TEMP_SUDOERS" ] && sudo visudo -c -f "$TEMP_SUDOERS"; then
    echo "Sudoersファイルの検証に合格しました。修正されたバージョンをインストールしています..."
    # installを使用して正しい所有者/権限を設定し、オリジナルのファイルと置き換える
    sudo install -m 0440 -o root -g root "$TEMP_SUDOERS" "$SUDOERS_FILE"
else
    echo "エラー: 変更されたsudoersファイルの検証に失敗しました。変更は行われませんでした。" >&2
fi
rm -f "$TEMP_SUDOERS"
```

#### 7.3. 起動時間の最適化
システムがネットワーク接続を待つ間、起動処理が長く遅延するのを防ぐため、「wait-online」サービスを無効化します。
```bash
# 起動の大幅な遅延を防ぐため、ネットワーク待機サービスを無効にする
sudo systemctl disable systemd-networkd-wait-online.service

# MOTDスクリプトがデフォルトルートの確立を待つようにオーバーライド（制御設定）を作成する
sudo mkdir -p /etc/systemd/system/update_motd.service.d
cat <<'EOT' | sudo tee /etc/systemd/system/update_motd.service.d/wait-for-ip.conf
[Service]
ExecStartPre=/bin/sh -c "while [ -z \"$(ip route show default)\" ]; do sleep 0.5; done"
EOT
```

#### 7.4. 修復スクリプトの作成
Arch Linuxのデフォルトの挙動では、コンピュータが正常にシャットダウンされなかった場合、`/boot`ファイルシステムがアンクリーン（不整合）な状態のまま残されます。通常は安全ですが、今回のプライベートネットワークの立ち上げ時に競合状態（レースコンディション）を招く原因になり得ることが分かりました。また、ユーザーがシャットダウン手続きを経ずにデバイスの電源をぶつ切りすることもよくあります。これらの問題を防止するため、ソフトウェアアップデート時にのみ変更される`/boot`ファイルシステムをクリーンな状態に保つ、回避策用スクリプトを追加します。

このスクリプトは、起動時の自動実行および稼働中のシステムでの手動実行のいずれも安全に行うことができます。
```bash
curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/check-and-repair-boot.sh
sudo install -m 0755 check-and-repair-boot.sh /usr/local/sbin/
rm check-and-repair-boot.sh
```

#### 7.5. `systemd`サービスファイルの作成とサービスの有効化
```bash
cat <<'EOT' | sudo tee /etc/systemd/system/boot-repair.service
[Unit]
Description=Check and repair /boot filesystem before other services
DefaultDependencies=no
Conflicts=shutdown.target
Before=local-fs.target network-pre.target shutdown.target

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/check-and-repair-boot.sh
RemainAfterExit=yes

[Install]
WantedBy=local-fs.target
EOT
sudo systemctl daemon-reload
sudo systemctl --now enable boot-repair.service
sleep 5
journalctl -b -u boot-repair.service
```

#### 7.6. ディスクI/Oの最小化
`/etc/systemd/journald.conf`内の`#Storage=auto`を`Storage=volatile`に変更します。
```bash
sudo sed -i 's/^#Storage=auto/Storage=volatile/' /etc/systemd/journald.conf
```

---

### 8. Direttaソフトウェアのインストールと構成

#### 8.1. Diretta Target上での作業

1.  USB DACを**Diretta Target**の黒いUSB 2.0ポートのいずれかに接続し、DACの電源が入っていることを確認します。
2.  TargetにSSH接続します：`ssh diretta-target`。
3.  互換性のあるコンパイラツールチェーンの構成
    ```bash
    curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_diretta_compiler.sh | sudo bash
    ```
4.  `menu`を実行します。
5.  **AUDIO extra menu**を選択します。
6.  **DIRETTA target installation/configuration**を選択します。以下のメニューが表示されます：
    ```text
    What do you want to do?

    1) Install/update last version
    2) Enable/Disable Diretta Target
    3) Configure Audio card
    4) Edit configuration
    5) Copy and edit new default configuration
    6) License
    7) Diretta Target log
    8) Exit

    ?
    ```
7.  以下の手順を順番に実行してください：
    * **1) Install/update**を選択してソフトウェアをインストールします（すべての確認プロンプトに対して「Y」と答えてください）。
    * **2) Enable/Disable Diretta Target**を選択し、有効（enable）にします。
    * **3) Configure Audio card**を選択します。利用可能なオーディオデバイスが一覧表示されます。ご使用のUSB DACに対応するカード番号を入力します。
        ```text
        ?3
        This option will set DIRETTA target to use a specific card
        Your available cards are:

        card 0: AUDIO [SMSL USB AUDIO], device 0: USB Audio [USB Audio]

        Please type the card number (0,1,2...) you want to use:
        ?0
        ```
    * **4) Edit configuration**を選択します。Raspberry Pi 5がTargetの場合は`AlsaLatency=20`を、RPi4の場合は`AlsaLatency=40`を設定します。
    * **6) License**を選択します。システムは体験モードとして、ハイレゾ（44.1 kHzを超えるPCMオーディオ）を6分間再生します。画面に表示されるリンクと指示に従って、ハイレゾ対応のためのフルライセンスを購入し、適用してください。これには、ステップ5で構成したインターネット接続が必要になります。
        ```text
        The price of this third party license is 100$
        Without license DIRETTA Target will work for 6 min.
        If you see a link, you can use it to purchase a license
        If you see instead the word 'valid' the license has been correctly applied
        Please wait a few seconds...

        https://www.diretta.link/cgi-bin/target_app_regist.cgi?hash=1fd430fe950936867b31cc084a9dac031ffa7c57c8ba1d5034a1a5219444f441&vender=Audlinux


        The license will be applied at the next DIRETTA target start
        Press any key to continue
        ```
    * **8) Exit**を選択します。プロンプトに従ってターミナルに戻ります。

#### 8.2. Diretta Host上での作業

1.  HostにSSH接続します：`ssh diretta-host`。

2.  互換性のあるコンパイラツールチェーンの構成
    ```bash
    curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_diretta_compiler.sh | sudo bash
    ```

3.  `menu`を実行します。

4.  **AUDIO extra menu**を選択します。

5.  **DIRETTA host installation/configuration**を選択します。以下のメニューが表示されます：
    ```text
    What do you want to do?

    1) Install/update last version
    2) Enable/Disable Diretta daemon
    3) Set Ethernet interface
    4) Edit configuration
    5) Copy and edit new default configuration
    6) Diretta log
    7) Exit

    ?
    ```

6.  以下の手順を順番に実行してください：
    * **1) Install/update**を選択してソフトウェアをインストールします（すべてのプロンプトに対して「Y」と答えてください）。*(注意：インストール中に `error: package 'lld' was not found` と表示される場合がありますが、心配いりません。インストール処理によって自動的に修正されます)*
    * **2) Enable/Disable Diretta daemon**を選択し、有効（enable）にします。
    * **3) Set Ethernet interface**を選択します。ポイント・ツー・ポイント接続用のインターフェースである`end0`を必ず選択してください。
        ```text
        ?3
        Your available Ethernet interfaces are: end0  enu1
        Please type the name of your preferred interface:
        end0
        ```
    * **4) Edit configuration**を選択します。高度な変更が必要な場合にのみ、これを使用してください。通常はこれまでの手順で十分ですが、以下に示す調整済みの設定をお試しいただくことも可能です：
        ```text
        ScanOnlineStop=enable
        InfoCycle=80000
        FlexCycle=disable
        CycleTime=800
        periodMin=16
        periodSizeMin=2048
        ```

    * 上記の調整済みパラメータをそのまま適用したい場合は、以下のコマンドブロックを使用できます：
        ```bash
        cat <<'EOT' | sudo tee /opt/diretta-alsa/setting.inf
        [global]
        Interface=end0
        Broadcast=disable
        ScanOnlineStop=enable
        ScanInterval=
        TargetProfileLimitTime=200
        ThredMode=1
        InfoCycle=80000
        FlexCycle=disable
        CycleTime=800
        CycleMinTime=
        Debug=stdout
        periodMax=32
        periodMin=16
        periodSizeMax=38400
        periodSizeMin=2048
        syncBufferCount=8
        alsaUnderrun=enable
        alsaUnderrunSleep=0
        alsaUnderrunClear=disable
        unInitMemDet=disable
        CpuSend=
        CpuOther=
        LatencyBuffer=0
        disConnectDelay=enable
        singleMode=
        EOT
        ```
    * **7) Exit**を選択します。プロンプトに従ってターミナルに戻ります。

7.  Direttaサービスが失敗したときに自動的に再起動するよう、オーバーライド設定を作成する
    ```bash
    sudo mkdir -p /etc/systemd/system/diretta_alsa.service.d
    cat <<'EOT' | sudo tee /etc/systemd/system/diretta_alsa.service.d/restart.conf
    [Service]
    Restart=on-failure
    RestartSec=5
    EOT
    ```

---

### 9. 最終手順とRoonの統合

1.  前ステップの後にターミナルに戻っている場合は`menu`を実行し、そうでない場合は**Main menu**に移動します。

2.  **Roon Bridgeのインストール（Host側）：** Roonを使用する場合は、**Diretta Host**で以下の手順を実行します：
    * Run `menu`.
    * **INSTALL/UPDATE menu**を選択します。
    * **INSTALL/UPDATE Roonbridge**を選択します。
    * インストールが進行します。これには1〜2分かかる場合があります。

3.  **Roon Bridgeの有効化（Host側）：**
    * Main menuから**Audio menu**を選択します
    * **SHOW audio service**を選択します
    * 有効なサービス（enabled services）の一覧に**roonbridge**が表示されていない場合は、**ROONBRIDGE enable/disable**を選択して有効にします。

4.  **両方のデバイスの再起動：** システムをクリーンな状態で起動するため、Target、Hostの順で両デバイスを再起動します：
    ```bash
    sudo sync && sudo reboot
    ```

5.  **Roonの構成：**
    * 操作用デバイス（PCやスマホなど）でRoonを開きます。
    * 「`Settings`（設定）」→「`Audio`（オーディオ）」に移動します。
    * `diretta-host`の項目内に、デバイスが表示されているはずです。デバイス名はご使用のDACに基づいて決まります。
    * 「`Enable`（有効にする）」をクリックし、任意の名前を設定すれば、音楽を再生する準備は完了です！

これで、最もクリーンで隔離されたオーディオ再生のための専用Direttaリンクの構成が完了しました。
**注意：** ハイレゾオーディオの再生開始から6分が経過すると、Roon上の体験用「Limited」ゾーンが消えます。これは仕様通りの挙動です。この制限をなくすためには、Diretta Targetのライセンスを購入する必要があります。ライセンス料は現在100ユーロで、アクティベーションが完了するまでに最大48時間かかる場合があります。購入後、Direttaチームから2通のメールが届きます。1通目は領収書で、2通目がアクティベーション完了の通知です。アクティベーション通知メールを受け取ったら、Targetのコンピュータを再起動して設定を適用してください。

> ---
> ### ✅ Checkpoint: コアシステムの動作確認
>
> これで、基本的なDirettaおよびRoonシステムが完全に機能する状態になったはずです。すべてのサービスと接続を確認するために、[**付録 5**](#14-付録-5システムヘルスチェック)に進み、HostとTargetの両方で共通の**System Health Check（システムヘルスチェック）**コマンドを実行してください。
>
> ---

---

## 10. 付録 1：オプションのArgon ONEファン制御
Raspberry Pi用のケースとしてArgon ONEを使用することを選択した場合、公式のデフォルトインストーラスクリプトはDebian系OSを前提として動作します。しかし、AudiolinuxはArch Linuxベースであるため、代わりに以下の手順を実行する必要があります。

Diretta HostとTargetの両方でArgon ONEケースを使用している場合は、両方のコンピュータでこれらの手順を実行する必要があります。

### ステップ 1：マニュアル記載の`argon1.sh`スクリプトの実行をスキップする
メーカーのマニュアルには、download.argon40.comからargon1.shスクリプトをダウンロードして`bash`に渡すよう記載されています。これはDebian系OSを前提としているため、Audiolinux上では動作しません。この手順はスキップし、代わりに以下のステップを実行してください。

### ステップ 2：システムの構成：
これらのコマンドによりI2Cインターフェースが有効化され、Argon ONEケース専用の`dtoverlay`設定が追加されます。このスクリプトは、まずコメントアウトされている場合は`i2c_arm`パラメータを有効化し、その後、設定がない場合は`argonone`オーバーレイを追加することで、エラーや二重書き込みを防止します。
```bash
BOOT_CONFIG="/boot/config.txt"
I2C_PARAM="dtparam=i2c_arm=on"

# --- 設定が存在する場合にコメントアウトを解除してI2Cを有効化する ---
if grep -q -F "#$I2C_PARAM" "$BOOT_CONFIG"; then
  echo "Enabling I2C parameter..."
  sudo sed -i -e "s/^#\($I2C_PARAM\)/\1/" "$BOOT_CONFIG"
fi
```

### ステップ 3 : `udev`権限の設定
```bash
cat <<'EOT' | sudo tee /etc/udev/rules.d/99-i2c.rules
KERNEL=="i2c-[0-9]*", MODE="0666"
EOT
```

### ステップ 4 : Argon Oneパッケージのインストール
```bash
yay -S argonone-c-git
```

**Note :** 上記のコマンドがコンパイルエラーで失敗した場合は、以下の手動手順を試してパッケージを修正およびインストールできます：
```bash
# パッケージのリポジトリをクローンする
git clone https://aur.archlinux.org/argonone-c-git.git
cd argonone-c-git

# ビルド（コンパイル）を行わずにソースコードのみをダウンロードする
makepkg -o

# GCC 14以降でのコンパイルエラーを修正するためのパッチを適用する
sed -i 's/_timer_thread()/_timer_thread(void *args)/g' src/argonone-c-git/src/event_timer.c

# パッチ適用済みのソースを使用してコンパイルおよびインストールを行う
makepkg -e -i --noconfirm

# クリーンアップを行う
cd ..
rm -rf argonone-c-git
```

### ステップ 5 : Argon ONEケースの制御をハードウェアからソフトウェア制御に切り替える
```bash
sudo pacman -S --noconfirm --needed i2c-tools libgpiod
```

```bash
# 起動時にケースをソフトウェアモードに切り替えるためのsystemdオーバーライド設定を作成する
sudo mkdir -pv /etc/systemd/system/argononed.service.d
cat <<'EOT'| sudo tee /etc/systemd/system/argononed.service.d/software-mode.conf
[Service]
ExecStartPre=/bin/sh -c "while [ ! -e /dev/i2c-1 ]; do sleep 0.1; done && /usr/bin/i2cset -y 1 0x1a 0"
EOT

cat <<'EOT'| sudo tee /etc/systemd/system/argononed.service.d/override.conf
[Unit]
After=multi-user.target
EOT
```

### ステップ 6 : サービスの有効化
```bash
# 新しい設定を読み込むためにsystemdマネージャーをリロードする
sudo systemctl daemon-reload

# 起動時にサービスが自動開始されるよう有効化する
sudo systemctl enable argononed.service
```

### ステップ 7 : 再起動
最後に、すべての変更を反映させるためにRaspberry Piを再起動します（Targetを先に行い、その後にHostを再起動します）：
```bash
sudo sync && sudo reboot
```

これで、ファンはデーモンによって制御されるようになり、電源ボタンも完全に機能するようになります。

### ステップ 8 : サービスの確認
```bash
systemctl status argononed.service
journalctl -u argononed.service -b
```

### ステップ 9 : ファン動作モードと設定の確認：
現在の設定値を確認するには、以下のコマンドを実行します：
```bash
sudo argonone-cli --decode
```

これらの値を調整するには、設定ファイルを作成する必要があります。まずは以下の開始設定値を使用してください：
```bash
cat <<'EOT' | sudo tee /etc/argononed.conf
temp0=55
fan0=0
temp1=60
fan1=50
temp2=65
fan2=100
hysteresis=3
EOT
```

新しい設定値を反映するためにサービスを再起動します：
```bash
sudo systemctl restart argononed.service
echo ""
echo "更新されたファン値:"
sleep 5
sudo argonone-cli --decode
```

以降は、上記の手順に従って必要に応じて値を自由に調整してください。

---

## 11. 付録 2：オプションの赤外線（IR）リモコン

このガイドでは、Roonを操作するための赤外線（IR）リモコンをインストールおよび構成する手順を説明します。セットアップは2つのパートに分かれています。

  * **Part 1**では、ハードウェア固有のセットアップについて説明します。Flirc USBレシーバーを使用するか、Argon Oneケース内蔵のレシーバーを使用するかに応じて、2つの付録のいずれか**一方**を選択します。
  * **Part 2**では、両方のハードウェアオプションで共通となる`roon-ir-remote`制御スクリプトのソフトウェアセットアップについて説明します。

**Note :** これらの手順はDiretta Hostでのみ実施してください。Targetは、IRリモコンの操作コマンドをRoon Serverへリレー（中継）する目的には使用しないでください。

---

### **パート1：IRレシーバーのハードウェアセットアップ**

*使用しているハードウェアに対応する付録の手順に従ってください。*

#### **オプション1：Flirc USB IRレシーバーのセットアップ**

1.  **Flircデバイスの購入とプログラミング :**
    Flirc USB IRレシーバーが必要です。同社のウェブサイトから購入できます：[https://flirc.tv/products/flirc-usb-receiver](https://flirc.tv/products/flirc-usb-receiver)

    Flircデバイスは、Flirc GUIソフトウェアを使用してデスクトップコンピュータ上でキーの割り当て（プログラミング）を行う必要があります。

      * Flircをデスクトップコンピュータに接続し、Flirc GUIを開きます。
      * 「`Controllers`（コントローラー）」に進み、「`Full Keyboard`（フルキーボード）」を選択します。
      * GUI上のキーをクリックした後に物理リモコンの対応するボタンを押すことで、スクリプトに必要なキー（`KEY_UP`、`KEY_DOWN`、`KEY_ENTER`など）をプログラミングします。
      * プログラミング完了後、Flircを**Diretta Host**に接続します。

2.  **Flircデバイスのテスト :**
    Raspberry PiがFlircをキーボードとして認識していることを確認します。

    ```bash
    sudo pacman -S --noconfirm evtest
    sudo evtest
    ```

    メニューから「Flirc」デバイスを選択します。リモコンのボタンを押したときに、キーボードイベントが画面に出力されることを確認します。

3.  [パート2：制御スクリプトのソフトウェアセットアップ](#part-2-control-script-software-setup)に進みます。

---

#### **オプション2：Argon One IRリモコンのセットアップ**

1.  **IRレシーバーハードウェアの有効化 :**
    Argon Oneケースの内蔵IRレシーバー用のハードウェアオーバーレイを有効にする必要があります。

      * このコマンドは、設定が重複して追加されないように事前に確認を行った上で、必要なハードウェアオーバーレイを`/boot/config.txt`ファイルに安全に追加します。
        ```bash
        BOOT_CONFIG="/boot/config.txt"
        IR_CONFIG="dtoverlay=gpio-ir,gpio_pin=23"

        # すでに設定が存在する場合を除き、IRリモコンのオーバーレイ設定を追加する
        if ! sed 's/#.*//' $BOOT_CONFIG | grep -q -F "$IR_CONFIG"; then
          echo "Argon One IRレシーバーを有効にしています..."
          sudo sed -i "/# Uncomment this to enable infrared communication./a $IR_CONFIG" /boot/config.txt
        else
          echo "Argon One IRレシーバーは既に有効になっています。"
        fi
        ```
      * ハードウェア変更を反映させるために再起動が必要です。
        ```bash
        sudo sync && sudo reboot
        ```

2.  **IRツールのインストールとプロトコルの有効化 :**
    `ir-keytable`をインストールします。
    ```bash
    sudo pacman -S --noconfirm v4l-utils
    ```

3.  **ボタンのスキャンコード（Scancode）のキャプチャ :**
     リモコンからの信号をデコードできるように、すべてのカーネルプロトコルを有効にします。テストツールを実行して、リモコンの各ボタンに割り当てられた一意のスキャンコードを確認します。
    ```bash
    sudo ir-keytable -p all
    sudo ir-keytable -t
    ```

    使用したい各ボタンを押し、`MSC_SCAN`イベント出力からそのスキャンコード（例：`value ca`）をメモします。完了したら`Ctrl+C`を押します。

4.  **キーマップ（Keymap）ファイルの作成 :**
    このファイルは、スキャンコードを標準的なキー名にマッピング（関連付け）します。

      * 新しいキーマップファイルを作成します：
        ```bash
        cat <<'EOT' | sudo tee /etc/rc_keymaps/argon.toml
        # /etc/rc_keymaps/argon.toml
        [[protocols]]
        name = "argon_remote"
        protocol = "nec"
        [protocols.scancodes]
        0xca = "KEY_UP"
        0xd2 = "KEY_DOWN"
        0x99 = "KEY_LEFT"
        0xc1 = "KEY_RIGHT"
        0xce = "KEY_ENTER"
        0x90 = "KEY_ESC"
        0x80 = "KEY_VOLUMEUP"
        0x81 = "KEY_VOLUMEDOWN"
        0xcb = "KEY_MUTE"
        EOT
        ```
      * 上記のサンプルファイル内のスキャンコードがメモしたものと一致しない場合は、ファイルを編集（`sudo nano /etc/rc_keymaps/argon.toml`）し、実際のコードに書き換えてください。

5.  **キーマップをロードするための`systemd`サービスの作成 :**
    このサービスは、起動時にキーマップを自動的にロードします。

    新しいサービスファイルを作成し、サービスを有効にします：
    ```bash
    cat <<'EOT' | sudo tee /etc/systemd/system/ir-keymap.service
    [Unit]
    Description=Load custom IR keymap
    After=multi-user.target

    [Service]
    Type=oneshot
    RemainAfterExit=yes
    ExecStart=/usr/bin/ir-keytable -c -p nec -w /etc/rc_keymaps/argon.toml

    [Install]
    WantedBy=multi-user.target
    EOT
    sudo systemctl enable --now ir-keymap.service
    ```

6.  **入力デバイスのテスト :**
    システムがIRリモコンからキーボードイベントを受信していることを確認します。

    ```bash
    sudo pacman -S --noconfirm evtest
    sudo evtest
    ```

    `gpio_ir_recv`デバイスを選択します。リモコンのボタンを押したときに、対応するキーイベントが表示されることを確認します。
    テストが完了したら`Ctrl+C`を入力します。

---

### **パート2：制御スクリプトのソフトウェアセットアップ**

*パート1でハードウェアを設定した後、以下の手順に従ってPython制御スクリプトをインストールおよび構成します。*

### **ステップ 1：`input`グループへの`audiolinux`ユーザーの追加**
これは、`audiolinux`アカウントがリモコンレシーバーからのイベントにアクセスできるようにするために必要です。
```bash
sudo usermod --append --groups input audiolinux
```
この変更を反映させるため、一度ログアウトして再度ログインしてください。以下のコマンドで確認できます：
```bash
echo ""
echo ""
echo "グループの所属状況を確認しています:"
echo "\$ groups"
groups
echo ""
echo "上記に以下が表示されている必要があります:"
echo "audiolinux realtime video input audio wheel"
```

---

### **ステップ 2：`pyenv`によるPythonのインストール**

`pyenv`および最新の安定版Pythonをインストールします。

```bash
# ビルド用の依存関係をインストールする
sudo pacman -Syu --noconfirm
sudo pacman -S --noconfirm --needed base-devel git zlib bzip2 xz expat libffi openssl ncurses readline util-linux db gdbm sqlite vim jq

# すでにインストールされている場合を除き、pyenvをインストールする
if [ ! -d "$HOME/.pyenv" ]; then
  echo "--- pyenvをインストールしています ---"
  curl -fsSL https://pyenv.run | bash
else
  echo "--- pyenvは既にインストールされています。インストールをスキップします。 ---"
fi

# シェルにおけるpyenvのパス等の設定を行う
if grep -q 'pyenv init' ~/.bashrc; then
  :
else
  cat <<'EOT'>> ~/.bashrc

export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - bash)"
eval "$(pyenv virtualenv-init -)"
EOT
fi

# 設定ファイルをロードして、現在のシェルでpyenvを使用可能にする
. ~/.bashrc

# まだインストールされていない場合にのみ、最新バージョンのPythonをインストールして設定する
PYVER=$(pyenv install --list | grep -E '^\s{2}3\.[0-9]+\.[0-9]+$' | tail -n 1 | tr -d ' ')

if ! pyenv versions --bare | grep -q "^${PYVER}$"; then
    # メモリの総量をMB単位で取得する
    TOTAL_MEM=$(awk '/^MemTotal:/ {print int($2/1024)}' /proc/meminfo)

    if [ "$TOTAL_MEM" -lt 1900 ]; then
        echo "--- 物理RAMは${TOTAL_MEM}MBです。フリーズを防ぐため、1コアに制限しています。 ---"
        export MAKE_OPTS="-j1"
        export MAKEFLAGS="-j1"
        mkdir -p "$HOME/pyenv_build_scratch"
        export TMPDIR="$HOME/pyenv_build_scratch"
    else
        echo "--- 物理RAMは${TOTAL_MEM}MBです。並列ビルドを実行します。 ---"
    fi

    echo "--- Python ${PYVER}をインストールしています。これには数分かかります... ---"
    pyenv install "$PYVER"
    [ -n "$TMPDIR" ] && [ -d "$TMPDIR" ] && rm -rf "$TMPDIR"
else
    echo "--- Python ${PYVER}は既にインストールされています。 ---"
fi

pyenv global "$PYVER"
```

**Note :** ソースからPythonをコンパイルするため、`Installing Python-3.14.5...`のステップには通常10分程度かかります。途中で止めないでください！待ち時間の間は、Roonの新しいDirettaゾーンから流れる素晴らしい音楽を聴いてリラックスしましょう。Host側でPythonのインストールが実行されている間も、音楽の再生は可能です。

---

### **ステップ 3：`roon-ir-remote`ソフトウェアリポジトリのダウンロード**

スクリプトのリポジトリをクローンし、キーコードを数値ではなく名前で正しく処理するためのパッチを取得します。

```bash
cd
# リポジトリが存在しない場合はクローンし、存在する場合はアップデートする
if [ ! -d "roon-ir-remote" ]; then
  git clone https://github.com/dsnyder0pc/roon-ir-remote.git
else
  (cd roon-ir-remote && git pull)
fi
```

---

### **ステップ 4：Roon環境設定ファイルの作成**

スクリプトにRoonの接続情報を設定します。**Note :** `event_mapping`のコードは、ハードウェアセットアップで定義したキー名（`KEY_ENTER`、`KEY_VOLUMEUP`など）と完全に一致する必要があります。

```bash
bash <<'EOF'
# --- スクリプトの開始 ---

# Roon Zone名を取得して変数に格納する
echo "Roonゾーンの名前を入力してください。"
echo "重要: これはRoonアプリ内のゾーン名と完全に（大文字と小文字を区別して）一致している必要があります。"
# この行が修正箇所： < /dev/tty は read コマンドにターミナルを使用するよう指示する
read -rp "Roonゾーン名を入力してください: " MY_ROON_ZONE < /dev/tty

# Flirc/キーボードのマッピングが必要かどうかを検出する
if [ -f "/etc/systemd/system/ir-keymap.service" ]; then
    VOL_UP_CODE="KEY_VOLUMEUP"
    VOL_DOWN_CODE="KEY_VOLUMEDOWN"
    echo "--- 標準IRレシーバーが検出されました。KEY_VOLUMEUP/DOWNを使用します。 ---"
else
    VOL_UP_CODE="KEY_UP"
    VOL_DOWN_CODE="KEY_DOWN"
    echo "--- Flirc/HIDアダプターが検出されました。音量調整にKEY_UP/DOWNを使用します。 ---"
fi

# 対象ディレクトリが存在することを確認する
mkdir -p roon-ir-remote

# ヒアドキュメント（Here Document）を使用して設定ファイルを作成する
# 変数は正しく展開されて値が書き込まれる
cat <<EOD > roon-ir-remote/app_info.json
{
  "roon": {
    "app_info": {
      "extension_id": "com.smangels.roon-ir-remote",
      "display_name": "Roon IR Remote",
      "display_version": "1.1.0",
      "publisher": "dsnyder",
      "email": "dsnyder0cnn@gmail.com",
      "website": "https://github.com/dsnyder0pc/roon-ir-remote"
    },
    "zone": {
      "name": "${MY_ROON_ZONE}"
    },
    "event_mapping": {
      "codes": {
        "play_pause": "KEY_ENTER",
        "stop": "KEY_ESC",
        "skip": "KEY_RIGHT",
        "prev": "KEY_LEFT",
        "vol_up": "${VOL_UP_CODE}",
        "vol_down": "${VOL_DOWN_CODE}",
        "mute": "KEY_MUTE"
      }
    }
  }
}
EOD

echo ""
echo "✅ 設定ファイル 'roon-ir-remote/app_info.json' が正常に作成されました。"

# --- スクリプトの終了 ---
EOF
```

---

### **ステップ 5：`roon-ir-remote`の準備とテスト**

スクリプトの依存関係を仮想環境にインストールし、初めて実行します。

```bash
cd ~/roon-ir-remote
# まだ存在しない場合にのみ仮想環境を作成する
if ! pyenv versions --bare | grep -q "^roon-ir-remote$"; then
  echo "--- 'roon-ir-remote' 仮想環境を作成しています ---"
  pyenv virtualenv roon-ir-remote
else
  echo "--- 'roon-ir-remote' 仮想環境は既に存在します ---"
fi
pyenv activate roon-ir-remote
pip3 install --upgrade pip
pip3 install -r requirements.txt

python roon_remote.py
```

スクリプトを初めて起動した際には、Roonの「`Settings`（設定）」→「`Extensions`（拡張機能）」画面に移動し、**拡張機能の承認（許可）**を行ってください。

Roonの新しいDirettaゾーンで音楽が再生されている状態で、赤外線リモコンを直接Diretta Hostコンピュータに向け、再生/一時停止ボタン（5方向コントローラーの中央ボタンなど）を押します。曲送りや曲戻し（Next / Previous）もお試しください。これらが機能しない場合は、ターミナルウィンドウにエラーメッセージが表示されていないか確認します。テストが完了したら、`Ctrl+C`を入力して終了します。

---

### **ステップ 6：`systemd`サービスの作成**

スクリプトをバックグラウンドで自動的に実行するためのサービスを作成します。

```bash
cat <<EOT | sudo tee /etc/systemd/system/roon-ir-remote.service
[Unit]
Description=Roon IR Remote Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${LOGNAME}
Group=${LOGNAME}
WorkingDirectory=/home/${LOGNAME}/roon-ir-remote
ExecStart=/home/${LOGNAME}/.pyenv/versions/roon-ir-remote/bin/python /home/${LOGNAME}/roon-ir-remote/roon_remote.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOT

# サービスを有効化し、起動する
sudo systemctl daemon-reload
sudo systemctl enable --now roon-ir-remote.service

# ステータスを確認する
sudo systemctl status roon-ir-remote.service
```

---

### **ステップ 7：ログの監視：**
```bash
journalctl -b -u roon-ir-remote.service -f
```

正常に動作していることが確認できたら、`Ctrl+C`を入力して終了します。

---

### **ステップ 8：`set-roon-zone`スクリプトのインストール**
後で必要に応じてRoonのゾーン名を更新できるように、スクリプトを用意しておくと便利です。以下にインストール方法を示します：
```bash
curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/set-roon-zone
sudo install -m 0755 set-roon-zone /usr/local/bin/
rm set-roon-zone
```

使用する際は、Diretta Hostコンピュータにログインし、次のように入力します：
```bash
set-roon-zone
```
プロンプトに従って、Roonゾーンの新しい名前を入力します。変更を反映させるために、rootパスワードの入力が必要になる場合があります。

**Note : ゾーンを設定するより良い方法**
このスクリプトは問題なく機能しますが、Roonゾーンを変更する推奨方法は、[付録 4](#13-付録-4オプションのシステム管理web-ui)に記載されているWebアプリケーション「AnCaolas Link System Control」を使用することです。Web UIを使用すると、スマートフォンやブラウザからゾーン名を確認・編集するための専用ページが利用できます。

### **ステップ 9：これで完了です！ 📈**

> ---
> ### ✅ Checkpoint: 赤外線リモコン設定の動作確認
>
> これで、赤外線リモコンのハードウェアおよびソフトウェアの設定が完了したはずです。設定を確認するには、[**付録 5**](#14-付録-5システムヘルスチェック)に進み、Diretta Hostで共通の**System Health Check（システムヘルスチェック）**コマンドを実行してください。
>
> ---

これで赤外線リモコンでRoonを操作できるようになります。お楽しみください！

---

## 12. 付録 3：オプションのピュリストモード（Purist Mode）
Diretta Targetコンピュータ上では、Direttaプロトコルを使用した音楽再生に関係のない、不要なネットワーク活動やバックグラウンド処理は最小限に抑えられています。しかし、ノイズ混入の可能性をさらに下げるために、追加の対策を講じることを好むユーザーもいます。すでに究極のオーディオパフォーマンスの領域に達していますが、さらに上を目指してみませんか？

---
> 重要かつ重大な警告：Diretta Target専用手順
>
> `purist-mode`スクリプトおよび本付録のすべての指示は、Diretta Target専用に作成されています。
>
> このスクリプトをDiretta Hostにはインストールまたは実行しないでください。実行すると、Hostのメインネットワークへの接続が切断され、アクセス不能になり、Roon Coreやストリーミングサービスとの通信ができなくなります。その結果、物理キーボードとディスプレイを使用したコンソールアクセスにより設定を元に戻すまで、システム全体が動作不能になります。
---

### Step 1: Install the `purist-mode` script **(only on the Diretta Target computer)**
```bash
curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/purist-mode
sudo install -m 0755 purist-mode /usr/local/bin
rm purist-mode

# ログイン時にPurist Modeのステータスを表示するスクリプト
cat <<'EOT' | sudo tee /etc/profile.d/purist-status.sh
#!/bin/sh
BACKUP_FILE="/etc/nsswitch.conf.purist-bak"

if [ -f "$BACKUP_FILE" ]; then
    echo -e '\n\e[1;32m✅ Purist Mode is ACTIVE.\e[0m System optimized for the highest sound quality.'
else
    echo -e '\n\e[1;33m⚠️ CAUTION: Purist Mode is DISABLED.\e[0m Background activity may impact sound quality.'
fi
EOT
```

To run it, simply login to the Diretta Target and type `purist-mode`：
```bash
purist-mode
```

For example：
```text
[audiolinux@diretta-target ~]$ purist-mode
This script requires sudo privileges. You may be prompted for a password.
🚀 Activating Purist Mode...
  -> Stopping time synchronization service (chronyd)...
  -> Disabling DNS lookups...
  -> Overriding gateway with high-priority blackhole route...

✅ Purist Mode is ACTIVE.
```

しばらく音楽を聴いてみて、音質（あるいは精神的な安心感）が好みに合うか確認してください。

---

### Step 2: Enable Purist Mode by Default

ピュリストモードを有効にした音の方が好みに合う場合は、毎回の再起動後にデフォルトで有効化されるように設定します。

```bash
echo ""
echo "- クリーンな状態を確保するためにPurist Modeを無効化しています"
purist-mode --revert

echo ""
echo "- 起動時に毎回Standard Modeに戻すためのサービスを作成しています"
cat <<'EOT' | sudo tee /etc/systemd/system/purist-mode-revert-on-boot.service
[Unit]
Description=Revert Purist Mode on Boot to Ensure Standard Operation
After=network-online.target
Wants=network-online.target
Before=purist-mode-auto.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/purist-mode --revert

[Install]
WantedBy=multi-user.target
EOT

echo ""
echo "- 遅延自動有効化サービスを作成しています"
cat <<'EOT' | sudo tee /etc/systemd/system/purist-mode-auto.service
[Unit]
Description=Activate Purist Mode 60 seconds after boot
After=diretta-cache.service

[Service]
Type=oneshot
TimeoutStartSec=infinity
ExecStart=/bin/bash -c "until ping -c 1 -q 172.20.0.1 &>/dev/null; do sleep 2; done && sleep 60 && /usr/local/bin/purist-mode"

[Install]
WantedBy=multi-user.target
EOT

echo ""
echo "- 新しいサービスを有効化しています"
sudo systemctl daemon-reload
sudo systemctl enable purist-mode-revert-on-boot.service
sudo systemctl enable purist-mode-auto.service
```

---

### Step 3: Install a wrapper around the `menu` command
AudioLinuxの多くの機能はインターネット接続を必要とします。通常通りに機能を利用できるようにするため、`menu`コマンドにラッパーを適用します。これにより、メニューを開いている間はピュリストモードが一時的に無効化され、メニューを終了してターミナルに戻った際に自動的に再有効化されます。

```bash
if grep -q menu_wrapper ~/.bashrc; then
  :
else
  echo ""
  echo "menuコマンドのラッパーを追加します"
  cat <<'EOT' | tee -a ~/.bashrc

# Purist Modeを管理するためのAudioLinuxメニュー用カスタムラッパー
menu_wrapper() {
  local was_active=false
  # バックアップファイルの存在を確認して、ピュリストモードの初期状態を確認する。
  if [ -f "/etc/nsswitch.conf.purist-bak" ]; then
    was_active=true
  fi

  # Purist Modeが有効な場合、メニュー表示のために一時的に解除します。
  if [ "$was_active" = true ]; then
    echo "Purist Modeを管理するための認証情報を確認しています..."
    sudo -v

    echo "メニューを実行するためにPurist Modeを一時的に無効化しています..."
    purist-mode --revert > /dev/null 2>&1 # Revert quietly
  fi

  # オリジナルのmenuコマンドを呼び出す
  /usr/bin/menu

  # 以前にPurist Modeが有効だった場合は、ここで再有効化します。
  if [ "$was_active" = true ]; then
    echo "Purist Modeを再有効化しています..."
    purist-mode > /dev/null 2>&1 # Activate quietly
    echo "Purist Modeが再び有効になりました。"
  fi
}

# 'menu'コマンドを新しいラッパー関数にエイリアスします
alias menu='menu_wrapper'
# 自動Purist Modeサービスを管理するためのエイリアス
alias purist-mode-auto-enable='echo "起動時にPurist Modeを有効にしています..."; purist-mode; sudo systemctl enable purist-mode-auto.service'
alias purist-mode-auto-disable='echo "起動時にPurist Modeを無効にしています..."; purist-mode --revert; sudo systemctl disable --now purist-mode-auto.service'
EOT
fi

source ~/.bashrc
```

---

### ピュリストモードのステータスについて

ピュリストモードのシステムは柔軟に設計されており、手動での制御も、システム起動後の自動有効化も可能です。主に以下の2つの状態（ステータス）で動作します：

  * **Disabled (Standard Mode) ：**
    Diretta Targetの通常かつ全機能が利用可能な状態です。ネットワークゲートウェイが有効で、すべてのサービス（`chronyd`、`argononed`）が動作し、デバイスは制限なく動作します。

  * **Active (Purist Mode) ：**
    集中してリスニングを行うための最適化された状態です。インターネットトラフィックを遮断するためにネットワークゲートウェイが切断され、システム干渉を最小限に抑えるために不要なバックグラウンドサービス（Argon ONEのファン制御を含む）が停止されます。

これらの状態は、起動時の**自動管理**と、コマンドライン経由の**手動管理**の2つの方法で管理できます。

#### 自動制御（起動時）

起動プロセスは安全で予測可能であるよう設計されており、オプションとして起動後にピュリストモードへ自動切り替えすることができます。

1.  **起動時の強制復元：** シャットダウン時の状態にかかわらず、Diretta Targetは起動時には**必ず**最初に**スタンダードモード**で立ち上がります。これは、ネットワーク時刻同期などの必須サービスを正常に実行させるための重要な仕様です。

2.  **オプションの自動有効化：** 自動起動機能を有効にした場合、システムは起動後60秒間待機した後に、自動的に**ピュリストモード**に切り替わります。これにより、常に最適化された状態でリスニングを楽しみたいユーザーに「設定したら後は任せるだけ」の使い勝手を提供します。

#### 手動制御（対話式の利用）

いつでもシステムを手動で完全に制御できます。

  * リスニングセッションのためにピュリストモードを**手動で有効化**するには、Diretta Targetコンピュータにログインして以下を実行します：

    ```bash
    purist-mode
    ```

  * ピュリストモードを**手動で無効化**して通常動作に戻すには、以下を実行します：

    ```bash
    purist-mode --revert
    ```

  * **起動時の自動有効化挙動**を制御するには、Diretta Target上の便利なエイリアスを使用します：

    ```bash
    # 次回起動時に60秒後の自動有効化を有効にする
    purist-mode-auto-enable

    # 次回起動時の自動有効化を無効にする
    purist-mode-auto-disable
    ```

---

## 13. 付録 4：オプションのシステム管理Web UI

この付録では、Diretta HostにシンプルなWebベースのアプリケーションをインストールする手順について説明します。このアプリケーションは、スマートフォンやタブレットからアクセスできる使いやすいインターフェースを提供し、Target上のピュリストモードやHost上のRoon IRリモコン統合設定など、Direttaシステムの主要機能を管理できるようにします。

> **重要かつ重大な警告：これらの手順は注意深く実行してください。**
> このセットアップでは、新しいユーザーの作成とセキュリティ設定の変更が行われます。システムの安全性と正常動作を維持するために、指示に正確に従ってください。

セットアップは2つのパートに分かれています。まず**Diretta Target**を設定して安全にコマンドを受け入れられるようにし、次に**Diretta Host**にWebアプリケーションをインストールします。ただし、ホスト間の切り替えが頻繁に行われるため、操作対象に注意してください。

---

### **パート1：Diretta Targetの構成**

**Diretta Target**で、権限が非常に限定された新しいユーザーを作成します。このユーザーは、ピュリストモードの管理に必要な特定のコマンドの実行のみが許可されます。

1.  **Diretta TargetにSSH接続します：**
    ```bash
    ssh diretta-target
    ```

2.  **アプリケーション用新規ユーザーの作成：**
    このコマンドは、`purist-app`という名前の新しいユーザーとそのホームディレクトリを作成します。非対話式のSSHコマンドを機能させるために、有効なシェルが必要となります。
    ```bash
    sudo useradd --create-home --shell /bin/bash purist-app
    ```

3.  **安全なコマンドスクリプトの作成：**
    Webアプリの実行が許可される*唯一の*アクションとなる、4つの小さく専用のスクリプトを作成します。これは重要なセキュリティ対策のステップです。
    ```bash
    # ライセンス状態を含む現在のステータスを取得するスクリプト
    cat <<'EOT' | sudo tee /usr/local/bin/pm-get-status
    #!/bin/bash
    IS_ACTIVE="false"
    IS_AUTO_ENABLED="false"
    LICENSE_LIMITED="false"

    # ピュリストモード（Purist Mode）の状態を確認する
    if [ -f "/etc/nsswitch.conf.purist-bak" ]; then
      IS_ACTIVE="true"
    fi

    # 自動起動（auto-start）が有効になっているか確認する
    if systemctl is-enabled --quiet purist-mode-auto.service; then
      IS_AUTO_ENABLED="true"
    fi

    # アクティブな評価用リンクがないか、検証済みの起動キャッシュを確認する
    if [ ! -f /tmp/diretta_license_url.cache ] || grep -q "http" /tmp/diretta_license_url.cache; then
      LICENSE_LIMITED="true"
    fi

    # すべてのステータスフラグを単一のJSONオブジェクトとして出力する
    echo "{\"purist_mode_active\": $IS_ACTIVE, \"auto_start_enabled\": $IS_AUTO_ENABLED, \"license_needs_activation\": $LICENSE_LIMITED}"
    EOT

    # ピュリストモードを切り替えるスクリプト
    cat <<'EOT' | sudo tee /usr/local/bin/pm-toggle-mode
    #!/bin/bash
    if [[ "$1" == "--enforce" ]]; then
        # 強制実行：有効であるべき状態の場合は再実行して
        # 復活したデフォルトルート等をベースラインスクリプトでクリーンアップする。
        if [ -f "/etc/nsswitch.conf.purist-bak" ]; then
            /usr/local/bin/purist-mode
        fi
    elif [ -f "/etc/nsswitch.conf.purist-bak" ]; then
        /usr/local/bin/purist-mode --revert
    else
        /usr/local/bin/purist-mode
    fi
    EOT

    # 自動起動（auto-start）サービスの状態を切り替えるスクリプト
    cat <<'EOT' | sudo tee /usr/local/bin/pm-toggle-auto
    #!/bin/bash
    if systemctl is-enabled --quiet purist-mode-auto.service; then
      systemctl disable --now purist-mode-auto.service
    else
      systemctl enable purist-mode-auto.service
    fi
    EOT

    # Direttaサービスを再起動するスクリプトの作成
    cat <<'EOT' | sudo tee /usr/local/bin/pm-restart-target
    #!/bin/bash
    # Diretta ALSA Targetサービスを再起動します。
    # このスクリプトは、purist-appユーザーによってsudo経由で呼び出されることを想定しています。
    /usr/bin/systemctl restart diretta_alsa_target.service
    EOT

    # DirettaライセンスURLを取得するスクリプトの作成
    cat <<'EOT' | sudo tee /usr/local/bin/pm-get-license-url
    #!/bin/bash

    # このスクリプトの唯一の役割は、起動時に作成されたキャッシュファイルを読み取ることです。
    readonly CACHE_FILE="/tmp/diretta_license_url.cache"

    if [ -s "$CACHE_FILE" ]; then
        # キャッシュが存在し内容がある場合はそれを表示する。
        cat "$CACHE_FILE"
    else
        # 存在しない場合は、標準エラー出力（stderr）にエラーを出力して終了する。
        echo "エラー: ライセンスキャッシュが見つからないか、空です。" >&2
        exit 1
    fi
    EOT

    # リンク速度（link speed）を設定するスクリプトを作成する
    cat <<'EOT' | sudo tee /usr/local/bin/pm-set-link
    #!/bin/bash
    # Targetの物理リンク境界を強制するためのプロファイルスクリプト
    # ハードウェアデッドロックを防止するために明示的なアドバタイズマスクを用いてリファクタリング

    SPEED="$1"

    if [ "$SPEED" = "10" ]; then
        echo "10Mbps制限をスケジュールしています (Super Purist)..."
        /usr/bin/sh -c "sleep 1 && sudo /usr/bin/ethtool -s end0 advertise 0x002" >/dev/null 2>&1 < /dev/null &
    elif [ "$SPEED" = "100" ]; then
        echo "100Mbps制限をスケジュールしています (Purist)..."
        /usr/bin/sh -c "sleep 1 && sudo /usr/bin/ethtool -s end0 advertise 0x008" >/dev/null 2>&1 < /dev/null &
    elif [ "$SPEED" = "1000" ]; then
        echo "制限を解除しています。すべての10/100/1000ポートフォリオを復元しています (Standard)..."
        /usr/bin/sh -c "sleep 1 && sudo /usr/bin/ethtool -s end0 advertise 0x03f" >/dev/null 2>&1 < /dev/null &
    else
        echo "Usage: $0 [10|100|1000]"
        exit 1
    fi
    EOT

    # 作成した新しいスクリプトを実行可能にする
    sudo chmod -v +x /usr/local/bin/pm-*
    ```

4.  **Sudo権限の付与：**
    このステップにより、`purist-app`ユーザーが対話式ターミナルを使用せず、root権限で作成した4つの新しいスクリプトを実行できるようになります。
    ```bash
    cat <<'EOT' | sudo tee /etc/sudoers.d/purist-app
    # purist-appユーザーに対してTTY要件をsudoで不要に設定する
    Defaults:purist-app !requiretty

    # パスワードなしで特定の制御スクリプトを実行することをpurist-appユーザーに許可する
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-get-status
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-toggle-mode
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-toggle-auto
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-restart-target
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-get-license-url
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-set-link
    EOT
    ```

5.  **起動時のDirettaライセンスキャッシュファイルへの書き込み**
    DirettaライセンスURLの取得にはインターネット接続が必要です。デフォルトでピュリストモードが有効になっている場合、Targetはインターネットと通信できないためURLを取得できません。しかし、起動時には時刻設定とDirettaライセンスのアクティベーションチェックを行うため、60秒間ピュリストモードが無効化されています。この時間枠（タイムウィンドウ）を利用して、同時にURLを取得することができます。
    ```bash
    # スクリプトをダウンロードして適切な権限を設定し、システムパスに配置する
    curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/create-diretta-cache.sh
    sudo install -m 0755 create-diretta-cache.sh /usr/local/bin/
    rm create-diretta-cache.sh

    # ライセンス状態キャッシュを書き込むためのサービスを作成する
    cat <<'EOT' | sudo tee /etc/systemd/system/diretta-cache.service
    [Unit]
    Description=Asynchronous Diretta License Cache Collector
    After=network.target purist-mode-revert-on-boot.service
    Before=purist-mode-auto.service

    [Service]
    Type=oneshot
    RemainAfterExit=yes
    # Hostがpingに応答するまで、ここでクリーンに実行をブロック（待機）する
    TimeoutStartSec=infinity
    ExecStartPre=/bin/bash -c "until ping -c 1 -q 172.20.0.1 &>/dev/null; do sleep 2; done"
    ExecStart=/usr/local/bin/create-diretta-cache.sh
    Restart=no

    [Install]
    WantedBy=multi-user.target
    EOT

    # 更新されたカスタマイズ設定を読み込むためにsystemdをリロードする
    sudo rm -rf /etc/systemd/system/purist-mode-revert-on-boot.service.d
    sudo systemctl daemon-reload
    sudo systemctl enable diretta-cache.service

    # スクリプトを手動で一度実行する
    sudo /usr/local/bin/create-diretta-cache.sh
    ls -l /tmp/diretta_license_url.cache
    ```

---

### **パート2：Diretta Hostの構成**

次に**Diretta Host**にWebアプリケーションをインストールし、構成するためのすべてのステップを行います。このセクション全体を通じて、`audiolinux`ユーザーでログインしている必要があります。

1.  **Diretta HostにSSH接続します：**
    ```bash
    ssh diretta-host
    ```

2.  **専用SSH鍵の生成：**
    Webアプリ専用の新しいSSH鍵ペアを作成します。これにはパスフレーズを設定しないでください。
    ```bash
    ssh-keygen -t ed25519 -f ~/.ssh/purist_app_key -N "" -C "purist-app-key"
    ```

3.  **SSHの構成とTargetへの鍵のコピー：**
    このステップでSSH設定を作成し、Targetへ公開鍵を安全にコピーします。
    ```bash
    mkdir -p ~/.ssh
    chmod go-rwx ~/.ssh
    cat <<'EOT' > ~/.ssh/config
    Host diretta-target target
        StrictHostKeyChecking no
        UserKnownHostsFile /dev/null
        GlobalKnownHostsFile /dev/null
        LogLevel ERROR
        ConnectTimeout 5
    EOT

    # 公開鍵をTargetのホームディレクトリにコピーする
    echo "--> ターゲットに公開鍵をコピーしています..."
    scp -o StrictHostKeyChecking=accept-new ~/.ssh/purist_app_key.pub diretta-target:
    ```

4.  **Targetでの鍵の認証登録：**
    ```bash
    ssh diretta-target

    ```

    Targetにログイン後、このスクリプトを実行して'purist-app'ユーザーに鍵を登録します。
    ```bash
    echo "--> ターゲットでセットアップスクリプトを実行しています..."
    set -e
    # コピーしたファイルから公開鍵を読み取る
    PUB_KEY=$(cat purist_app_key.pub)

    # .sshディレクトリが存在し、正しい権限が設定されていることを確認する
    sudo mkdir -p /home/purist-app/.ssh
    sudo chmod 0700 /home/purist-app/.ssh

    # 必要なセキュリティ制限を設定したauthorized_keysファイルを作成する
    echo "command=\"sudo \$SSH_ORIGINAL_COMMAND\",from=\"172.20.0.1\",no-port-forwarding,no-x11-forwarding,no-agent-forwarding,no-pty ${PUB_KEY}" | sudo tee /home/purist-app/.ssh/authorized_keys > /dev/null

    # 最終的な所有者および権限を設定する
    sudo chown -R purist-app:purist-app /home/purist-app/.ssh
    sudo chmod 0600 /home/purist-app/.ssh/authorized_keys

    # コピーした公開鍵ファイルをクリーンアップ（削除）する
    rm purist_app_key.pub

    echo "✅ SSH鍵がターゲットで正常に承認されました。"
    ```

5.  **リモートコマンドの手動テスト（推奨）：**
    Webアプリを起動する前に、**Diretta Host**のターミナルから読み取り専用のリモートコマンドをテストし、バックエンドが正常に機能していることを確認します。
    ```bash
    # ステータスコマンドをテストする（JSON文字列が返されるはずです）
    ssh -i ~/.ssh/purist_app_key purist-app@diretta-target '/usr/local/bin/pm-get-status'

    # ライセンス状態取得コマンドをテストする
    ssh -i ~/.ssh/purist_app_key purist-app@diretta-target '/usr/local/bin/pm-get-license-url'
    ```

6.  **Diretta Hostにpyenv経由でPythonをインストールする** （赤外線リモコン設定時にすでに実施している場合は、このステップをスキップしてください）
    `pyenv`および最新の安定版Pythonをインストールします。
    ```bash
    # ビルド用の依存関係をインストールする
    sudo pacman -Syu --noconfirm
    sudo pacman -S --noconfirm --needed base-devel git zlib bzip2 xz expat libffi openssl ncurses readline util-linux db gdbm sqlite vim jq

    # すでにインストールされている場合を除き、pyenvをインストールする
    if [ ! -d "$HOME/.pyenv" ]; then
      echo "--- pyenvをインストールしています ---"
      curl -fsSL https://pyenv.run | bash
    else
      echo "--- pyenvは既にインストールされています。インストールをスキップします。 ---"
    fi

    # シェルにおけるpyenvの設定を行う
    if grep -q 'pyenv init' ~/.bashrc; then
      :
    else
      cat <<'EOT'>> ~/.bashrc

    export PYENV_ROOT="$HOME/.pyenv"
    [[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init - bash)"
    eval "$(pyenv virtualenv-init -)"
    EOT
    fi

    # 設定ファイルをロードして、現在のシェルでpyenvを使用可能にする
    . ~/.bashrc

    # まだインストールされていない場合にのみ、最新バージョンのPythonをインストールして設定する
    PYVER=$(pyenv install --list | grep -E '^\s{2}3\.[0-9]+\.[0-9]+$' | tail -n 1 | tr -d ' ')
    if ! pyenv versions --bare | grep -q "^${PYVER}$"; then
      # メモリの総量をMB単位で取得する
      TOTAL_MEM=$(awk '/^MemTotal:/ {print int($2/1024)}' /proc/meminfo)

      if [ "$TOTAL_MEM" -lt 1900 ]; then
        echo "--- 物理RAMは${TOTAL_MEM}MBです。フリーズを防ぐため、1コアに制限しています。 ---"
        export MAKE_OPTS="-j1"
        export MAKEFLAGS="-j1"
        mkdir -p "$HOME/pyenv_build_scratch"
        export TMPDIR="$HOME/pyenv_build_scratch"
      else
        echo "--- 物理RAMは${TOTAL_MEM}MBです。並列ビルドを実行します。 ---"
      fi

      echo "--- Python ${PYVER}をインストールしています。これには数分かかります... ---"
      pyenv install $PYVER
      [ -n "$TMPDIR" ] && [ -d "$TMPDIR" ] && rm -rf "$TMPDIR"
    else
      echo "--- Python ${PYVER}は既にインストールされています。 ---"
    fi

    pyenv global $PYVER
    ```

    **Note :** ソースからPythonをコンパイルするため、`Installing Python-3.14.5...`のステップには通常10分程度かかります。途中で止めないでください！待ち時間の間は、Roon의新しいDirettaゾーンから流れる素晴らしい音楽を聴いてリラックスしましょう。Host側でPythonのインストールが実行されている間も、音楽の再生は可能です。

7.  **Diretta HostへのAvahiおよびPython依存関係のインストール：**

    **注意：** オプション - ネットワーク上に複数のDiretta Hostが存在する場合は、それぞれが一意の名前を持っていることを確認してください。進める前に、次のコマンドを使用してこのマシンの名前を変更できます：

    ```bash
    # 同じネットワーク上での2回目のビルドである場合、必要に応じてDiretta Hostの名前を変更する
    sudo hostnamectl set-hostname diretta-host2
    ```

    このステップは**Diretta Host**で実行します。Avahiデーモンをインストールし、`requirements.txt`ファイルを使用して専用の仮想環境にFlaskをインストールします。
    ```bash
    # .localの名前解決のためにAvahiをインストールする
    sudo pacman -Syu --noconfirm
    sudo pacman -S --noconfirm avahi

    # USB Ethernetインターフェース名（例：enp...やenu1...）を動的に検出する
    USB_INTERFACE=$(ip -o link show | awk -F': ' '/en[pu]/{print $2}')

    # AvahiをUSBインターフェースのみに隔離するための設定オーバーライドを作成する
    echo "--- インターフェース $USB_INTERFACE を使用するようにAvahiを設定しています ---"
    sudo mkdir -p /etc/avahi/avahi-daemon.conf.d
    cat <<EOT | sudo tee /etc/avahi/avahi-daemon.conf.d/interface-scoping.conf
    [server]
    allow-interfaces=$USB_INTERFACE
    deny-interfaces=end0
    EOT

    # Avahiデーモンを有効化して起動する
    sudo systemctl enable --now avahi-daemon.service

    # アプリケーション用ディレクトリとrequirementsファイルを作成する
    mkdir -p ~/purist-mode-webui
    echo "Flask" > ~/purist-mode-webui/requirements.txt

    # 仮想環境を作成し、依存関係をインストールする
    echo "--- Web UI用にPython環境をセットアップしています ---"
    # まだ存在しない場合にのみ仮想環境を作成する
    if ! pyenv versions --bare | grep -q "^purist-webui$"; then
      echo "--- 'purist-webui' 仮想環境を作成しています ---"
      pyenv virtualenv purist-webui
    else
      echo "--- 'purist-webui' 仮想環境は既に存在します ---"
    fi
    pyenv activate purist-webui
    pip install -r ~/purist-mode-webui/requirements.txt
    pyenv deactivate
    ```

8.  **Flaskアプリのインストール：**
    GitHubから直接、**Diretta Host**のアプリケーション用ディレクトリにPythonスクリプトをダウンロードします。
    ```bash
    curl -L https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/purist-mode-webui.py -o ~/purist-mode-webui/app.py
    ```

9. **ポートバインディング（Port-Binding）権限の付与**
    Webアプリを起動するために、Python実行バイナリに対してDiretta Hostのポート80にバインド（占有接続）する権限を与える必要があります。
    ```bash
    # 'setcap'コマンドを提供するパッケージをインストールする
    sudo pacman -S --noconfirm --needed libcap

    # すべてのシンボリックリンクを解決して、Python実行ファイルの実際のパス（実体）を見つける
    PYTHON_EXEC=$(readlink -f /home/audiolinux/.pyenv/versions/purist-webui/bin/python)

    # 最終的なPython実行バイナリに対して、ポートバインド権限を直接付与する
    echo "実際のファイル ${PYTHON_EXEC} にケーパビリティを適用しています"
    sudo setcap 'cap_net_bind_service=+ep' "$PYTHON_EXEC"
    ```

10. **Host上でのSudo権限の付与：**
    このステップは、Webアプリケーションがパスワードなしで必要なRoon関連サービスを再起動できるようにするために重要です。
    ```bash
    cat <<'EOT' | sudo tee /etc/sudoers.d/webui-restarts
    # webui（audiolinuxとして実行）がホストプロファイルを強制し、サービスを再起動できるように許可する
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/systemctl daemon-reload
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart roon-ir-remote.service
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart roonbridge.service
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart diretta_alsa.service
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/ethtool -s end0 *
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/mv /tmp/setting.inf.tmp /opt/diretta-alsa/setting.inf
    EOT
    sudo chmod 0440 /etc/sudoers.d/webui-restarts
    ```

11. **Flaskアプリの対話テスト：**
    Webアプリが正しく起動することを確認するために、**Diretta Host**のコマンドラインから対話的にアプリを実行します。
    ```bash
    cd ~/purist-mode-webui
    pyenv activate purist-webui
    python app.py
    ```
    Flaskサーバーがポート**8080**で起動したことを示す出力が表示されるはずです。他のデバイス（PCやスマホなど）から [http://diretta-host.local:8080](http://diretta-host.local:8080) にアクセスします。正常に動作したら、SSHターミナルに戻り、`Ctrl+C`を押してサーバーを停止します。

12. **`systemd`サービスの作成：**
    このサービスにより、`pyenv`仮想環境の適切なPython実行ファイルを使用して、**Diretta Host**上でWebアプリが自動実行されるようになります。
    ```bash
    cat <<EOT | sudo tee /etc/systemd/system/purist-webui.service
    [Unit]
    Description=Purist Mode Web UI
    After=network-online.target
    Wants=network-online.target

    [Service]
    Type=simple
    User=${LOGNAME}
    Group=${LOGNAME}
    WorkingDirectory=/home/${LOGNAME}/purist-mode-webui
    ExecStart=/home/${LOGNAME}/.pyenv/versions/purist-webui/bin/python app.py
    Restart=on-failure
    RestartSec=5

    [Install]
    WantedBy=multi-user.target
    EOT
    ```

13. **Webアプリの有効化と起動：**
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl stop purist-webui.service
    sudo systemctl enable --now purist-webui.service
    ```

14. **ログを少し監視する：**
    ```bash
    journalctl -b -u purist-webui.service -f
    ```

15. **最終的なURLでのWeb UIのテスト：**
    ブラウザで [http://diretta-host.local](http://diretta-host.local) を開き、エラーがログに出力されていないか監視します。

期待通りに動作していることを確認できたら、`Ctrl+C`を入力して終了します。

---

### **Web UIへのアクセス**

これで準備完了です！Diretta Hostと同じネットワークに接続されたスマートフォン、タブレット、またはコンピュータでWebブラウザを開き、メインのトップページにアクセスします：

[http://diretta-host.local](http://diretta-host.local)

---
> **ブラウザのセキュリティ警告に関する注意**
> 初めて http://diretta-host.local にアクセスした際、ブラウザに「接続が安全ではありません」というセキュリティ警告が表示される可能性が高いです。これは想定された挙動であり、無視して安全に進めることができます。この警告は、オーディオデバイスの処理負荷（オーバーヘッド）を最小限に抑えることを意図して、暗号化された`HTTPS`ではなく標準の`HTTP`接続を選択しているために発生します。このアプリは信頼できるご自宅のプライベートネットワーク内でのみ動作し、いかなる機密データも扱わないため、安心して警告をバイパス（サイトへ進む）してください。
---

トップページの上部にあるナビゲーションバーから、各コントロールパネルに移動できます：

* **Home（ホーム）：** 各アプリケーションへのリンクが掲載されたメインのトップページ。

* **Purist Mode App：** Diretta Target上のピュリストモードおよびその自動起動挙動を切り替えるためのコントロールです。現在のステータスを表示するために30秒ごとに自動更新されます。Direttaライセンスのアクティベーション完了後に使用する「Restart Services（サービスの再起動）」ボタンもこのページにあります。

* **IR Remote App：** 赤外線リモコンのセットアップ（付録2）を完了している場合、このリンクが表示されます。リモコンが制御するRoonのゾーン名（Zone Name）を確認・更新するためのシンプルなフォームが提供されます。このページは自動更新されないため、時間をかけて編集を行えます。

### 🔗 Web UIの全機能利用に関する注意

システム管理Web UIのすべての機能（具体的にはネットワークの接続速度（**Link Speed**）の調整や**Super Purist**モードの切り替え）を解放するには、[**付録 8：オプションのピュリストネットワーク速度**](#17-付録-8オプションのピュリストネットワーク速度)で詳しく説明されているハードウェアおよびサービスの構成も完了する必要があります[cite: 1]。Webインターフェースは、そのセクションで構築されるスクリプト、フラグ、およびサービスに直接依存して、ポイント・ツー・ポイント接続の物理リンク速度の制限を適用および制御します[cite: 1]。

> ---
> ### ✅ Checkpoint：Web UI設定の動作確認
>
> ピュリストモードのWeb UIが動作可能な状態になったはずです。この複雑な機能のすべてのコンポーネントを確認するために、[**付録 5**](#14-付録-5システムヘルスチェック)に進み、HostとTargetの両方で共通の**System Health Check（システムヘルスチェック）**コマンドを実行してください。
>
> ---

## 14. 付録 5：システムヘルスチェック

本ガイドの主要なセクションを完了した後は、品質保証（QA）チェックを実行し、すべてが正しく構成されているか確認することをお勧めします。

実行している環境が**Diretta Host**であるか**Diretta Target**であるかを自動的に検出し、適切なチェック項目を実行するスマートなスクリプトを作成しました。

### **チェックの実行方法**

HostまたはTargetのいずれかで、以下の単一のコマンドを実行します。QAスクリプトをダウンロードして実行し、システムの詳細なステータスレポートを出力します。

```bash
curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/main/scripts/qa.sh | sudo bash
```

---

## 15. 付録 6：オプションのリアルタイムパフォーマンスチューニング

以下の手順はオプションですが、Direttaの構成から絶対的な最大パフォーマンスを引き出したいユーザーには推奨されます。AudioLinuxの作成者であるPiero氏のアドバイスに基づく戦略は、HostとTargetの両デバイスにおいて、可能な限り安定し、電気的に最も静かな動作環境を作り出すことです。

これは、特定のプロセッサコアをオーディオ処理専用に割り当ててOS全体のタスクから隔離する**CPU隔離（CPU isolation）**を使用し、オーディオデータパスが一切妨げられないように**リアルタイム優先度（realtime priorities）**を慎重に調整することによって達成されます。

> **注意：** これは高度なチューニングプロセスです。進める前に、本ガイドのセクション1〜9を完了し、Direttaの基本システムが完全に機能していることを確認してください。また、両方のRaspberry Piデバイスの冷却が適切に行われている必要があります。

---

### **パート1：Diretta Targetの最適化**

Targetにおける目標は、純粋で低レイテンシのオーディオエンドポイントにすることです。Direttaアプリケーションを単一の専用CPUコアに隔離し、過度にならない範囲で高いリアルタイム優先度を割り当てます。

#### **ステップ 6.1：オーディオアプリケーション専用のCPUコアの隔離**

このステップにより、1基のCPUコアがDiretta Targetアプリケーション専用として割り当てられます。

1.  Diretta TargetにSSH接続します：
    ```bash
    ssh diretta-target
    ```
2.  AudioLinuxのメニューシステムに入ります：
    ```bash
    menu
    ```
3.  **ISOLATED CPU CORES configuration**メニュー（**SYSTEM menu**内）に移動します。

4.  CPU隔離（isolated cores）が無効になっていることを確認します。有効になっている場合は、オプション3を使用して無効にします：
    ```text
    ISOLATED CORES CONFIGURATION
    This option will divide CPU cores in 2 or more sets: one for audio services, one for system processes
    After you can specify the CPU core set used by each audio service
    You can also assign Audio or Network IRQ to specific cores

    Isolated cores is disabled

    Please chose your option:
    1) Configure and enable
    2) Edit configuration (for experts)
    3) Enable/disable (keep configuration)
    4) Exit
    ?
    ```

5.  再び**ISOLATED CPU CORES configuration**メニュー（**SYSTEM menu**内）に移動します。以下の指示通りに従い、**コア 2 および 3**を隔離し、そこにDirettaアプリケーションを割り当てます。
    ```text
    Please chose your option:
    1) Configure and enable
    2) Edit configuration (for experts)
    3) Enable/disable (keep configuration)
    4) Exit
    ?
    1

    How many groups do you want to create? (1 or more)
    ?1
    Please type the cores of the group 1:
    ?2,3

    Type the service that should be confined to group 1...
    ?diretta_alsa_target

    Please type the Address (iSerial) number of your card(s)...
    ?end0
    ```

6.  処理が完了したら、ターミナルに戻ります。

> **自動IRQアフィニティ（割り当て）に関する注意：** スクリプトが`end0`ネットワークのIRQも同じコアに隔離したと報告することに気づくかもしれません。これは不具合ではなく、合理的な最適化動作です。スクリプトは、ネットワーク割り込みをそのネットワークを使用するアプリケーションと同じコアに自動的に固定（ピン留め）し、最も効率的なデータパスを形成します。

#### **ステップ 6.2：従来の`rtapp`タイマーの無効化**
```bash
sudo systemctl stop rtapp.timer
sudo systemctl disable rtapp.timer
```

#### **ステップ 6.3：再起動して変更を反映する**
```bash
sudo sync && sudo reboot
```

---

### **パート2：Diretta Hostの最適化**

Hostにおける目標は、高いリアルタイム優先度を使用するのではなく、Direttaサービスの各スレッドに対して専用の処理リソースを割り当てることです。CPU隔離は、そもそもプロセスが他のタスクに邪魔されるのを防止するため、ここにおいてより強力な手段となります。

#### **ステップ 6.4：オーディオアプリケーション専用のCPUコアの隔離**

このステップにより、Diretta Hostのサービススレッドを処理するために2基のCPUコアが専用として割り当てられます。

1.  Diretta HostにSSH接続します：
    ```bash
    ssh diretta-host
    ```
2.  AudioLinuxのメニューシステムに入ります：
    ```bash
    menu
    ```
3.  **ISOLATED CPU CORES configuration**メニュー（**SYSTEM menu**内）に移動します。

4.  CPU隔離（isolated cores）が無効になっていることを確認します。有効になっている場合は、オプション3を使用して無効にします：
    ```text
    ISOLATED CORES CONFIGURATION
    This option will divide CPU cores in 2 or more sets: one for audio services, one for system processes
    After you can specify the CPU core set used by each audio service
    You can also assign Audio or Network IRQ to specific cores

    Isolated cores is disabled

    Please chose your option:
    1) Configure and enable
    2) Edit configuration (for experts)
    3) Enable/disable (keep configuration)
    4) Exit
    ?
    ```

5.  再び**ISOLATED CPU CORES configuration**メニュー（**SYSTEM menu**内）に移動します。指示に従い、**コア 2 および 3**を隔離し、それらをDiretta ALSAに割り当てます。
    ```text
    Please chose your option:
    1) Configure and enable
    2) Edit configuration (for experts)
    3) Enable/disable (keep configuration)
    4) Exit
    ?
    1

    How many groups do you want to create? (1 or more)
    ?1
    Please type the cores of the group 1:
    ?2,3

    Type the service that should be confined to group 1...
    ?diretta_alsa

    Please type the Address (iSerial) number of your card(s)...
    ?end0
    ```

6.  処理が完了したら、ターミナルに戻ります。

---

#### **ステップ 6.5：従来の`rtapp`タイマーの無効化**
```bash
sudo systemctl stop rtapp.timer
sudo systemctl disable rtapp.timer
```

#### **ステップ 6.6：再起動して変更を反映する**
```bash
sudo sync && sudo reboot
```

## 16. 付録 7：オプションのIRQおよびスレッド最適化

### パート1：Diretta TargetのUSBパス隔離
デフォルトでは、CPUコアを隔離していても、USB割り込みが他の活動で「ノイズの多い」システムコア（0および1）で処理されてしまい、リソースの競合が発生することがあります。このスクリプトは、DACが接続されている特定のUSBコントローラーを動的に識別し、そのハードウェア割り込みを隔離されたオーディオ処理用コア（2および3）に固定（ピン留め）します。Raspberry Pi 5では、USBコントローラーはRP1チップによって管理されており、ハードウェア割り込みを特定のコアにルーティングさせることが可能です。

**注意：** この最適化は、ハードウェアレベルで割り込みが固定されているため、Raspberry Pi 4には適用できません。

1.  DACの電源が入っており、Targetに接続されていることを確認します。
2.  Diretta Targetへの音楽再生を開始します。これにより、スクリプトがアクティブな割り込みトラフィックを検出できるようになります。
3.  Diretta Targetで以下のコマンドを実行します：
    ```bash
    curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/usb-isolation.sh | sudo bash
    ```
4.  再起動して変更を反映します：
    ```bash
    sudo sync && sudo reboot
    ```

**動作内容：** スクリプトはアクティブなDACのパス（例：`xhci-hcd:usb1`または`xhci-hcd:usb3`）を検出します。次に、その特定識別子をAudioLinuxの隔離グループに追加し、ネットワーク入力からUSB出力までの完全に隔離されたデータパスを作成します。

---

### パート2：Diretta Hostのスレッド最適化

リアルタイムカーネル最適化を適用したことで、Diretta Hostはより高密度なパケット間隔を処理できるようになり、これが音質の向上につながります。この最後のステップでは、`CycleTime`パラメータを800から514マイクロ秒に削減します。パケット間のこの短いタイムラグにより、DSD256およびDXD（32ビット、352.8 kHz）までのすべてのコンテンツにおいて、1サイクルあたり1パケットの転送で済むようになります。また、Direttaのスレッドを特定のコアにスケジュールすることも可能です。

1.  まだログインしていない場合は、**Diretta Host**にSSH接続します。
2.  以下のコマンドを実行して最適化設定を適用します：
    ```bash
    cat <<'EOT' | sudo tee /opt/diretta-alsa/setting.inf
    [global]
    Interface=end0
    Broadcast=disable
    ScanOnlineStop=enable
    ScanInterval=
    TargetProfileLimitTime=200
    ThredMode=17
    InfoCycle=51400
    FlexCycle=disable
    CycleTime=514
    CycleMinTime=
    Debug=disable
    periodMax=32
    periodMin=16
    periodSizeMax=38400
    periodSizeMin=2048
    syncBufferCount=8
    alsaUnderrun=enable
    alsaUnderrunSleep=0
    alsaUnderrunClear=disable
    unInitMemDet=disable
    CpuSend=2
    CpuOther=3
    CPUFLOW=3
    LatencyBuffer=0
    disConnectDelay=enable
    singleMode=
    EOT
    ```
3.  変更を有効にするためにDirettaサービスを再起動します：
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl restart diretta_alsa.service
    ```

> ---
> ### ✅ Checkpoint：リアルタイムチューニングの動作確認
>
> これで高度なリアルタイムチューニングが完了したはずです。この新しい構成のすべてのコンポーネントを検証するために、[**付録 5**](#14-付録-5システムヘルスチェック)に戻り、HostとTargetの両方で共通の**System Health Check（システムヘルスチェック）**コマンドを実行してください。
>
> ---

## 17. 付録 8：オプションのピュリストネットワーク速度

**目的：** 専用ネットワークのリンク速度を制限し、Energy Efficient Ethernet（EEE）を明示的に無効化することにより、電気的ノイズを低減し、OSスケジューラの精度を向上させます。

直感に反するかもしれませんが、専用リンク（`end0`）のリンク速度を1 Gbpsから100 Mbps（あるいは10 Mbps）に下げることで、音質が向上する場合があります。100BASE-TXの動作周波数は低く（62.5 MHzに対して31.25 MHz）、発生する高周波ノイズ（RFI）が少なくなります。極端な話、10 Mbpsに下げると搬送波周波数はわずか10 MHzに低下します。さらに、EEEが無効化されていることを確認することで、リンクが休止状態に入るのを防止し、潜在的なレイテンシの急増（フラッピング）を排除し、Raspberry Pi 5ハードウェアにおける盤石な安定性を確保します。

> ---
> ### 🎧 Deep Dive：10 Mbpsの制限が音の「静けさ」を取り戻す理由
>
> 専用オーディオリンクを10 Mbpsに制限すると、再生可能なフォーマットが**Native DSD64**および**32ビット / 96 kHz PCM**までに制限されるという厳しい制約が生じます。しかし、CD品質（レッドブック規格）や一般的なハイレゾファイルを中心に再生するオーディオ愛好家にとっては、デジタル特有の硬さやギラつきの根本原因を取り除くことで、トレードオフとして非常に大きな音質上の恩恵が得られます。
>
> * **キャリア周波数の劇的な低下：** 通常のギガビットEthernetは、62.5 MHzという高周波のキャリア信号で動作します（複雑な多値符号化を使用）。100 Mbpsに下げると、これが31.25 MHzに低下します。さらに10 Mbpsのリンク（10BASE-T)まで下げると、マンチェスター符号化という非常にシンプルな方式が用いられ、ネイティブのキャリア周波数はわずか**10 MHz**になります。この動作周波数の劇的な低下により、機器の筐体内やケーブル沿いに発生する電磁妨害（RFI）放射が大幅に減少します。
> * **Targetの処理負荷の低減：** 広帯域のネットワーク環境では、ネットワークインターフェースカード（NIC）とCPUがパケットデータを非常に高速かつ攻撃的なピッチで処理することを強いられます。リンク速度の上限をオーディオデータの実際の需要に合わせることで、TargetのOSが処理しなければならないネットワーク割り込みの総量を大幅に削減できます。
> * **Direttaの基本理念とのシナジー：** Direttaプロトコルのすべての目的は、バースト的な処理を排除し、消費電流を安定させることです。10 Mbpsのパイプはデータフローに対する物理的なイコライザーとして機能し、電源電圧の変動を引き起こす高速なデータスパイクの発生を根本から防止します。
>
> この「Super Purist」による帯域制限の結果、デジタルノイズフロアが劇的に低下することが即座に感じ取れるはずです。音場が広がり、よりリラックスして音楽を聴けるようになったこと、高域のトランジェント追従性がクリアになったこと、そしてAudioLinuxやDirettaが目指すアナログ的な聴きやすさと静寂感が得られたことが、多くの愛好家から報告されています。
> ---

> **注意：** Targetのログに「buffer low」の警告が表示される（`LatencyBuffer`が1に低下する）場合があります。これは、リンク速度低下に伴うシリアライズレイテンシの上昇による正常な動作であり、音切れ（音飛び）の原因にはなりません。

### Step 1: Configure Host and Target (Disable EEE)

Energy Efficient Ethernet（EEE：省電力イーサネット）は、特定のハードウェアの組み合わせにおいてリンクの不安定性を引き起こす原因となります。一貫した動作を確保するために、HostとTargetの**両方**で明示的にEEEを無効化するサービスを作成します。

**無効化サービスの作成：** *（HostとTargetの両方で実施）*

```bash
cat <<'EOT' | sudo tee /etc/systemd/system/disable-eee.service
[Unit]
Description=Disable EEE on end0 for Link Stability
After=network.target
BindsTo=sys-subsystem-net-devices-end0.device
After=sys-subsystem-net-devices-end0.device

[Service]
Type=oneshot
# インターフェースが実際にUP（アクティブ）と表示されるまで最大5秒間待機する
ExecStartPre=/usr/bin/bash -c 'for i in {1..5}; do if ip link show end0 | grep -q "UP"; then exit 0; fi; sleep 1; done; exit 1'
# ハードウェアの最適化を設定する
ExecStart=-/usr/bin/ethtool -s end0 advertise 0x03f
ExecStart=-/usr/bin/ethtool --set-eee end0 eee off
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOT

sudo systemctl daemon-reload
sudo systemctl enable --now disable-eee.service
```

### ステップ 2：Targetにフラグを設定する（QA用）

**Target QAスクリプト**がこの特定の構成を検証できるようにするために、Target上にマーカーファイルを作成します：

```bash
sudo touch /etc/diretta-100m
```

### ステップ 3：Hostの構成（速度制限）
「Super Purist」モードが有効になっているかどうかに応じて、10 Mbpsまたは100 Mbpsの全二重（Full Duplex）を強制的にアドバタイズするサービスを**Host**上に作成します。Targetは速度の変更を自動的に検出し、それに合わせます。

**制限スクリプトとサービスの作成：** *（Hostでのみ実行）*
```bash
cat <<'EOT' | sudo tee /usr/local/bin/set-link-speed.sh
#!/bin/bash
# 安全なアドバタイズマスクを使用して、Super Purist Web UIフラグに基づきリンク速度を設定する
FLAG_FILE="/home/audiolinux/purist-mode-webui/super_purist.flag"
INTERFACE="end0"

# 重要：物理インターフェースがキャリアリンクレイヤーを初期化するまで最大60秒間待機する
echo "物理リンクレイヤーと同期しています..."
for i in {1..60}; do
    if [ -f /sys/class/net/$INTERFACE/carrier ] && [ "$(cat /sys/class/net/$INTERFACE/carrier 2>/dev/null)" "==" "1" ]; then
        echo "物理リンクレイヤーが $i 秒後に検出されました。"
        break
    fi
    sleep 1
done

# フラグの状態に基づいてアドバタイズマスクを適用する
if [ -f "$FLAG_FILE" ]; then
    echo "Super Puristフラグが検出されました。10 Mbps Full Duplexをアドバタイズしています..."
    /usr/bin/ethtool -s $INTERFACE advertise 0x002
else
    echo "Standard/Puristモードです。最大100 Mbps Full Duplexをアドバタイズしています..."
    /usr/bin/ethtool -s $INTERFACE advertise 0x00a
fi

# プラットフォーム固有のネゴシエーション処理
if grep -q "Raspberry Pi 4" /proc/device-tree/model 2>/dev/null; then
    echo "Raspberry Pi 4が検出されました。強制ハードウェア再ネゴシエーションパルスをトリガーしています..."
    /usr/bin/ethtool -r $INTERFACE
elif grep -q "Raspberry Pi 5" /proc/device-tree/model 2>/dev/null; then
    echo "Raspberry Pi 5が検出されました。内蔵phylib自動パルスに依存するため、手動リセットをスキップします。"
else
    /usr/bin/ethtool -r $INTERFACE || true
fi

echo "リンク速度ポリシーが正常に確定しました。"
EOT
sudo chmod +x /usr/local/bin/set-link-speed.sh

cat <<'EOT' | sudo tee /etc/systemd/system/limit-speed-100m.service
[Unit]
Description=Set end0 link speed for Audio Purity
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecCondition=/usr/bin/ip link show end0
ExecStart=/usr/local/bin/set-link-speed.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOT

echo "サービスを有効化して起動します:"
sudo systemctl daemon-reload
sudo systemctl enable --now limit-speed-100m.service
```

***
> **再生レイテンシに関する注意：**
> 「再生」ボタンを押してから音楽が聴こえるまでの遅延がわずかに増加する（最大で1秒程度）ことに気づくかもしれません。これは想定された挙動です。リンクを10または100 Mbpsに制限することにより、意図的に初期のデータバーストを抑制し、接続がより低く、より静かな周波数で動作するようにしています。システムは、再生中のより安定しノイズの少ない定常状態を確保するために、瞬間的な起動時間をトレードオフにしています。
***

>
>
> ---
>
> ### ✅ Checkpoint：ネットワーク構成の検証
>
> これで、専用ネットワークリンクが「Purist」の100Mbps動作に構成されました。Hostのサービスがアクティブであり、Targetが速度を正しくネゴシエートしたこと（マーカーファイルを介して検出）を検証するには、[**付録 5**](#14-付録-5システムヘルスチェック)に戻り、HostとTargetの両方で共通の**System Health Check（システムヘルスチェック）**コマンドを実行してください。
>
> ---

## 18. 付録 9：オプションのジャンボフレーム最適化
このセクションでは、広帯域幅の効率性を高めるためにトランスポートを最適化します。

#### **ステップ 1：** インターフェースの準備

カーネルのサポート状況を検証し、リンクテストを準備するために、一時的にネットワークインターフェースのMTUを強制的に9000にする必要があります。

**最初にTargetで実行し、次にHostで実行します：**

```bash
sudo sh -c 'ip link set end0 down; sleep 2; ip link set end0 mtu 9000; ip link set end0 up'
end0_mtu=$(ip link show dev end0 | awk '/mtu/ {print $5}')
if [[ "9000" == "$end0_mtu" ]]; then
  echo "成功: カーネルはジャンボフレームをサポートしています。ステップ2に進んでください。"
else
  echo "停止: カーネルがジャンボフレームをサポートしていないようです。"
fi
```

*HostまたはTargetの**いずれか**で「STOP」と表示された場合は、先に進まないでください。お使いのカーネルに必要なパッチが適用されていません。*

---

#### **ステップ 2：** 自動化されたTargetの構成

Target（`diretta-target`）にSSH接続し、以下のブロックを貼り付けます。

```bash
# 1. リンク制限の検出（Full vs Baby）
echo "リンクの性能をテストしています..."
if ping -c 1 -w 1 -M "do" -s 8972 host &>/dev/null; then
  NEW_MTU=9000
  echo "成功: 完全なジャンボフレーム (9000 MTU) がサポートされています。"
elif ping -c 1 -w 1 -M "do" -s 2004 host &>/dev/null; then
  NEW_MTU=2032
  echo "成功: ベビージャンボフレーム (2032 MTU) がサポートされています。"
else
  echo "失敗: リンクはジャンボフレームをサポートできません。安全なデフォルト値に戻します。"
  sudo ip link set end0 mtu 1500
  false
fi && {
  # 2. システムネットワーク構成の適用
  echo "Configuring /etc/systemd/network/end0.network..."
  cat <<EOF | sudo tee /etc/systemd/network/end0.network
[Match]
Name=end0

[Link]
MTUBytes=$NEW_MTU

[Network]
Address=172.20.0.2/24
Gateway=172.20.0.1
DNS=1.1.1.1
EOF
  sudo systemctl daemon-reload
  sudo networkctl reload

  # 3. 構成の適用 (Diretta Config)
  echo "Diretta Targetを設定しています..."
  CONF="/opt/diretta-alsa-target/diretta_app_target_setting.inf"
  sudo sed -i '/^ExtEtherMTU=/d' $CONF
  sudo sed -i '/^EtherMTU=/d' $CONF

  if [ "$NEW_MTU" -eq 9000 ]; then
    echo "ExtEtherMTU=9014" | sudo tee -a $CONF
    echo "EtherMTU=9000" | sudo tee -a $CONF
  else
    echo "ExtEtherMTU=2046" | sudo tee -a $CONF
    echo "EtherMTU=2032" | sudo tee -a $CONF
  fi
  sudo systemctl restart diretta_alsa_target
  echo "完了: ターゲットの最適化が完了しました。"
}

```

---

#### **ステップ 3：** 自動化されたHostの構成

Host（`diretta-host`）にSSH接続し、以下のブロックを貼り付けます。これにより、リンクの調査、永続的なネットワーク設定の構成、およびDirettaのアップデートが行われます。

```bash
# 1. リンク制限の検出（Full vs Baby）
echo "リンクの性能をテストしています..."
# 手動によるMTU変更後、リンクが落ち着くまで少し時間を与える
sleep 2

if ping -c 1 -w 1 -M "do" -s 8972 target &>/dev/null; then
  NEW_MTU=9000
  echo "成功: 完全なジャンボフレーム (9000 MTU) がサポートされています。"
elif ping -c 1 -w 1 -M "do" -s 2004 target &>/dev/null; then
  NEW_MTU=2032
  echo "成功: ベビージャンボフレーム (2032 MTU) がサポートされています。"
else
  echo "失敗: リンクはジャンボフレームをサポートできません。安全なデフォルト値に戻します。"
  sudo ip link set end0 mtu 1500
  false
fi && {
  # 2. システムネットワーク構成の適用
  echo "Configuring /etc/systemd/network/end0.network..."
  cat <<EOF | sudo tee /etc/systemd/network/end0.network
[Match]
Name=end0

[Link]
MTUBytes=$NEW_MTU

[Network]
Address=172.20.0.1/24
EOF
  sudo systemctl daemon-reload
  sudo networkctl reload

  # 3. 構成の適用 (Diretta Config)
  echo "Diretta Hostを設定しています..."

  # 安定性を確保するため、ジャンボフレームでは常にFlexCycleを有効にする
  sudo sed -i 's/^FlexCycle=.*/FlexCycle=enable/' /opt/diretta-alsa/setting.inf

  # 条件付きのCycleTimeおよびInfoCycleの最適化
  if [ "$NEW_MTU" -eq 9000 ]; then
    echo "最適化: 完全なジャンボフレームが検出されました。CycleTimeを1000usに緩和します。"
    sudo sed -i 's/^CycleTime=.*/CycleTime=1000/' /opt/diretta-alsa/setting.inf
    sudo sed -i 's/^InfoCycle=.*/InfoCycle=100000/' /opt/diretta-alsa/setting.inf
  else
    echo "最適化: ベビージャンボフレームが検出されました。CycleTimeを700usに設定します。"
    sudo sed -i 's/^CycleTime=.*/CycleTime=700/' /opt/diretta-alsa/setting.inf
    sudo sed -i 's/^InfoCycle=.*/InfoCycle=70000/' /opt/diretta-alsa/setting.inf
  fi

  sudo systemctl restart diretta_alsa
  echo "完了: ホストの最適化が完了しました。"
}
```

#### **ステップ 4：** MTUの変更を反映するための再起動
最初にTargetを再起動し、次にHostを再起動します：
```bash
sudo sync && sudo reboot
```

>
>
> ---
>
> ### ✅ Checkpoint：ネットワーク構成の検証
>
> お使いの環境でジャンボフレームのサポートを有効にできた場合は、ここで[**付録 5**](#14-付録-5システムヘルスチェック)に戻り、HostとTargetの両方で共通の**System Health Check（システムヘルスチェック）**コマンドを実行するのが良いタイミングです。
>
> ---

## 19. 付録 10：オプションのシステムアップデート
このセクションでは、Raspberry Piハードウェア、AudioLinuxオペレーティングシステム、およびDirettaソフトウェアスタックへのアップデートの適用に関するガイドラインを提供します。

#### **パート 1：** Raspberry Piブートローダーのアップデート（オプション）

Raspberry Piブートローダー（EEPROM）のアップデートは必須ではなく、固有のリスクを伴います。しかし、Raspberry Pi財団が提供する継続的なバグ修正により、動作温度の低下やよりスムーズな起動シーケンスなどのメリットが得られる場合があります。

*警告：必ず対応するボードに適した正しいファームウェア書き込みイメージを適用してください。Raspberry Pi 4にRaspberry Pi 5のブートローダーを書き込んだり、その逆を行ったりすると、ボードが永続的に起動しなくなる（ブリックする）などの深刻な悪影響が生じる可能性があります。*

**現在のブートローダーバージョンの確認**
開始する前に、HostとTargetの両方にSSH接続し、以下のコマンドを実行して現在のブートローダーのリリース日を確認します。後でアップデートが成功したことを確認できるように、これらの日付を控えておいてください。

```bash
vcgencmd bootloader_version
```

*（出力の最初の行にある日付を探してください）。*

**アップデートメディアの準備**
空のmicroSDカード、SDカードリーダー、およびお使いのPC/ワークステーションにインストールされた公式のRaspberry Pi Imagerソフトウェアが必要です。

1. Raspberry Pi Imagerを開きます。**デバイスを選ぶ（CHOOSE DEVICE）**をクリックし、アップデート対象の特定のRaspberry Piボードを選択します。

   ![Select Raspberry Pi 5 Device](images/01-rpi-dev.png)

2. **OSを選ぶ（CHOOSE OS）**をクリックし、リストを下へスクロールして**実用的なその他のイメージ（Misc utility images）**を選択します。

   ![Select Misc Utility Images](images/02-rpi-misc.png)

3. **ブートローダー（Bootloader）**を選択します。*（注意：メニューには、ステップ1で選択したPiファミリーが表示されます）。*

   ![Select Bootloader for Pi 5 Family](images/03-rpi-bl.png)

4. **SDカード起動（SD Card Boot）**を選択します。

   ![Select SD Card Boot](images/04-rpi-sd.png)

5. **ストレージを選ぶ（CHOOSE STORAGE）**をクリックし、空のmicroSDカードを選択し、**次へ（NEXT）**をクリックしてイメージを書き込みます。

*重要：TargetがRaspberry Pi 5でHostがRaspberry Pi 4である場合（またはその逆の混在構成の場合）、同じアップデート用カードを使い回すことはできません。先に進む前に、PCに戻り、2台目のボードタイプ専用の新しいアップデート用microSDカードを書き込む必要があります。*

**ハードウェアアップデートの実行**

1. 両方のマシンを安全にシャットダウンします。最初にTargetをシャットダウンし、次にHostをシャットダウンします（`sudo poweroff`）。
2. 両方のユニットから物理的な電源ケーブルを取り外します。
3. 各ユニットからメインの起動用microSDカードを取り外し、安全な場所に保管します。
4. 作成したばかりのアップデート用microSDカードをボードに慎重に挿入します（金色の端子がRaspberry Piボードの裏面を向くようにしてください）。
5. ボードに電源を再接続します。
6. ボード上のアクティビティインジケータ（LED）を観察します。緑色のLEDが一定の速度で素早く点滅し始めるまで待ちます（通常は約10秒かかります）。この規則正しい点滅は、EEPROMの書き込みが完了したことを示しています。
7. ボードから電源を取り外します。
8. アップデート用microSDカードを取り外し、元の起動用microSDカードを再度挿入します。
9. システムに電源を再接続します。**最初にHostの電源を入れ、次にTargetの電源を入れます。**

システムが完全に起動しアクセス可能になったら、各コンピュータでブートローダーのバージョン確認をもう一度実行し、ブートローダーの日付がImagerによって書き込まれたリリース日に進んでいることを確認します。HostとTargetで異なるボードタイプ（例：RPi4とRPi5）を使用している場合、バージョンはおそらく異なりますが、問題ありません。

```bash
vcgencmd bootloader_version
```

---

#### **パート 2：** AudioLinuxおよびDirettaソフトウェアのアップデート

システムアップデートのプロセスでは、カスタムカーネル、コンパイルツールチェーン、およびALSAデーモンが完全に同期した状態を維持するために、厳格な順序が必要です。

#### それでは、アップデートを進めます
1. コマンドプロンプトで`menu`と入力し、AudioLinux構成ツールを起動します。
2. **Install/Update menu**に移動し、**UPDATE System**を選択します。
3. 引き続き**Install/Update menu**のままで、**UPDATE menu**を選択します。
   *（注意：AudioLinuxの購入時に使用したメールアドレスと、AudioLinuxイメージのダウンロード用にPiero氏から提供された特定のユーザー名とパスワードを入力する必要があります）。*
4. **SELECT/UPDATE kernel**を選択します。前述の[**ステップ 4**](#44-run-system-and-menu-updates)で推奨された正確なカーネルバージョンを選択します。
5. **Host**において、[**セクション 5.1**](#51-pre-configure-the-diretta-host)の`motd`の修正を再適用します。
6. TargetとHostの**両方**において、[**セクション 7.2**](#72-correct-sudoers-rule-precedence)の`sudoers`パッチを再適用します。
7. 最初にTargetを再起動し、次にHostを再起動します。
8. オンラインに戻ったら、TargetとHostの**両方**において、[**ステップ 8**](#8-direttaソフトウェアのインストールと構成)の「互換性のあるコンパイラツールチェーンの構成」スクリプトを再実行します。
9. **Target**において、[**セクション 8.1**](#81-on-the-diretta-target)に詳しく説明されているDirettaのインストール/アップデート手順を実行します。
10. **Host**において、[**セクション 8.2**](#82-on-the-diretta-host)に詳しく説明されているDirettaのインストール/アップデート手順を実行します。
11. 最初にTargetを再起動し、次にHostを再起動します。
>
>
> ---
>
> ### ✅ Checkpoint：システムヘルス＆回帰テスト
>
> アップデート手順の完了後、アップグレード中にソフトウェアや構成の回帰（機能低下）が発生していないことを確認するため、オーディオパイプラインの安定性を検証する必要があります。
>
> 1. Roonを開き、ネットワークゾーンが戻るのを待ってから、トランスポートレイヤーのリンクを確認し、ハードウェアカウンターを動かすために、少なくとも数秒間音楽を再生します。
> 2. **Target**にSSH接続し、一時的にStandardモードに戻すことで、診断スクリプトが回線上でトラフィックをクリーンに通過できるようにします：
>    ```bash
>    purist-mode --revert
>    ```
> 3. HostとTargetの**両方**で、[**付録 5**](#14-付録-5システムヘルスチェック)の共通**System Health Check（システムヘルスチェック）**QAスクリプトを実行します。
> 4. 出力を慎重に確認し、スクリプトによって検出されたスレッドアフィニティ（割り当て）や優先度（priority）の問題があれば解決します。
>
> ---

---

#### **パート 3：** USB電流制限のオーバーライド（Raspberry Pi 5のみ）

Raspberry Pi 5を使用していて、公式のRaspberry Pi 27W USB-C電源の代わりにプレミアムなサードパーティ製電源（例：iFi SilentPower Elite 5Vや5A出力対応の安定化リニア電源）を使用している場合、Piはデフォルトで安全な5V/3Aネゴシエーションを行います。これにより、4つのUSBポートすべての合計電流ドローは600mAに制限されます。

純粋なオーディオトランスポート用としては通常問題ありませんが、ご使用の電源が5Vで少なくとも5Aを継続して供給できることがわかっている場合は、この制限を安全にバイパスできます。

**ブート構成にオーバーライド設定を追加するために、以下のコマンドを実行します：**

```bash
if ! grep -q "^usb_max_current_enable=" /boot/config.txt; then
  echo "usb_max_current_enable=1" | sudo tee -a /boot/config.txt
else
  echo "/boot/config.txtに最適化は既に存在します。設定をスキップします。"
fi
sudo sync && sudo reboot
```

---
