# Klein Reference Studio

FLUX.2 klein 4Bと9Bを一つの画面・APIから切り替えて使うローカル画像生成アプリです。T2I、I2I、最大8枚のRef2Iに対応します。

## 起動

リポジトリを取得し、使用するモデルを準備してから起動します。

```bash
git clone git@github.com:animede/flux2-klein-studio.git
cd flux2-klein-studio
./setup.sh 4b
CUDA_VISIBLE_DEVICES=0 ./run.sh
```

画面: http://127.0.0.1:7864/

API仕様: http://127.0.0.1:7864/docs

画面上部の「使用モデル」で切り替えます。モデル切替時は現在のモデルをGPUとRAMから解放してから次を読み込むため、両モデルを同時にVRAMへ載せません。

## モデル

| 選択値 | 用途 | 画像モデル | テキスト側 | ライセンス表示 |
|---|---|---|---|---|
| `4b` | 軽量・高速・通常利用 | GGUF Q4_K_M | Qwen3-4B NF4 | Apache-2.0 |
| `9b` | 品質比較 | GGUF Q3_K_M | Qwen3-8B NF4 | 非商用 |

既定は4Bです。9Bを選ぶと画面上に非商用表示が出ます。参照画像は4Bで最大4枚まで各768px、8枚時512px、9Bでは4枚時512px、8枚時384pxへ自動調整します。

## API

`POST /api/generate` のmultipartフォームに `model=4b` または `model=9b` を指定します。省略時は互換性のため4Bです。

```bash
curl -X POST http://127.0.0.1:7864/api/generate \
  -F 'model=9b' \
  -F 'prompt=The same character reading a book by a cafe window.' \
  -F 'image=@/absolute/path/character.png' \
  -F 'width=1024' -F 'height=768' -F 'seed=42'
```

- `GET /api/health`: 利用可能モデル、現在読み込まれているモデル、稼働状態
- `GET /api/models`: 選択値、量子化、ライセンス表示
- `GET /api/jobs/JOB_ID`: 生成状況と使用モデル
- `POST /api/jobs/JOB_ID/cancel`: 停止
- `POST /api/unload`: 現在のモデルを解放

## 省メモリ構成と実測

CPUオフロード、VAEタイル、4ステップ、guidance 1.0、PyTorch上限7GiBを使用します。大容量GPUを7GiBに制限した検証であり、実際の8GB GPUではドライバー等の使用量によって余裕が小さくなる場合があります。

統合サーバー上のモデル切替テスト:

| 切替 | 512×512生成 | 予約ピーク |
|---|---:|---:|
| 起動→4B | 3.92秒 | 3.355GiB |
| 4B→9B | 5.33秒 | 6.166GiB |
| 9B→4B | 2.39秒 | 3.355GiB |

読み込み込みの時間は順に23.98秒、25.30秒、8.81秒でした。API入力、両モデル一覧、最大8枚、同時実行拒否、停止、失敗後の復帰を含む6テストが通過しています。

## セットアップ

このPCでは既存の4B・9Bモデルを共有しており、重複コピーしていません。別PCではPython 3.12、NVIDIA CUDA対応GPU、32GB以上のRAM、モデル用に40GB以上の空きディスクを推奨します。`.venv`、`models`、`outputs`、`uploads`はコピーせず、アプリのソースだけを移してください。

### 全モデルを一度に準備

```bash
./setup.sh
```

`setup.sh`を実行すると、最初にPython依存ライブラリをインストールし、その直後に4Bと9Bを並行ダウンロードします。初回起動時や最初の生成時にモデルを取得する方式ではありません。両モデルで約31GBです。途中で停止しても、同じコマンドを再実行すればHugging Faceのキャッシュから再開します。

準備が完了してから起動します。

```bash
./run.sh
```

### 4Bだけ先に準備

まず約11GBの4Bだけを取得して使い始めることもできます。

```bash
./setup.sh 4b
./run.sh
```

後から9B（約20GB）を追加するときは、サーバーを停止する必要はありません。

```bash
.venv/bin/python download_models.py 9b
```

取得完了後に画面を再読み込みすると9Bを選べるようになります。未取得モデルは選択欄で無効表示されます。依存ライブラリだけ準備し、モデルを後で取得する場合は `./setup.sh none` を使います。個別取得は次の通りです。

```bash
.venv/bin/python download_models.py 4b
.venv/bin/python download_models.py 9b
```

モデル取得にはインターネット接続が必要です。取得後の生成はローカルファイルのみで動作し、画像・プロンプトは外部APIへ送信しません。

## ライセンス

このリポジトリで作成したアプリケーションコードは[Apache License 2.0](LICENSE)で提供します。

モデル、モデル重み、トークナイザー、および依存ライブラリには、それぞれの提供元ライセンスが適用されます。このリポジトリのApache-2.0ライセンスは、それら第三者配布物のライセンスを変更しません。特にFLUX.2 klein 9Bは非商用ライセンスです。ダウンロード時に保存される各モデルの`LICENSE.md`と配布ページを確認してください。

- [FLUX.2 klein 4B](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B)
- [FLUX.2 klein 9B](https://huggingface.co/black-forest-labs/FLUX.2-klein-9B)
- [4B GGUF](https://huggingface.co/unsloth/FLUX.2-klein-4B-GGUF)
- [9B GGUF](https://huggingface.co/unsloth/FLUX.2-klein-9B-GGUF)
