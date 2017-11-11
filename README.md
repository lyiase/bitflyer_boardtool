# bitflyer_boardtool
bitflyer_stream_captureで出力した板情報を一定秒数ごとの状況をmsgpackとして出力するツール。

## 出力されるファイルフォーマット

`board.(start_unixtime).("main"/"last").msg`

`board.xxxxx.main.msg``board.xxxxx.last.msg`は最後まで処理した時に余り

## オプション

```
-s xxxx  開始時刻(UnixTimeで指定。秒まで有効)
         デフォルトでは板情報スナップショットファイルの最初の時刻以後、処理インターバルで割り切れる時間
-i xxxx  処理インターバル(秒。デフォルト5秒)
-l xxxx  処理後`board.xxx.last.msg`
```

## 保存形式

サイズを小さくするため以下の疑似JSONの形式(JSONではキーが数値のものを扱えないため)の構造になっています。

```
{
  "middle": 1234567,
  "asks": {
    1234567: 10.07,
    1234568: 2.111
  },
  "bids": {
    1234567: 10.07,
    1234568: 2.1100023
  },
  "timestamp": "2017-11-01T09:00:00Z"
  "time": 1234567890
}
```
