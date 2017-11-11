import json
import io
import dateutil.parser
import datetime
import time
import msgpack
import math

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("snapshot", type=str, help="board snaphot file")	# スナップショット
parser.add_argument("board", type=str, help="board diff file")	# 差分情報
parser.add_argument("-l","--last", type=str, help="last board file")	# 差分情報
parser.add_argument("-i","--interval", type=int, help="interval (default: 5)", default=5)	# 差分情報
parser.add_argument("-s","--start", type=int, help="start unixtime (default: diving interval time by first board time)")	# 差分情報
args = parser.parse_args()

# 初期
interval = args.interval
startTime = args.start
outfile = 'output/board.{}.{}.msg'

data = {
	"midde": None,
	"asks": {},
	"bids": {},
	"timestamp": None,
}

# last読込
if args.last:
	data = None
	with open(args.last,'rb') as fh:
		data = msgpack.unpackb(fh.read())

	

# boardデータ読込
f_board = open(args.board)
f_snapshot =open(args.snapshot)

def getBoard(f):
	"""
	1行ボードを取得して返却する関数
	@param f ファイルオブジェクト(stream_captureのデータ)
	"""
	
	raw = f.readline()
	if not raw:
		return None
	
	# 1行分のjsonデコード
	board = json.load(io.StringIO(raw))
	board['unixtime'] = dateutil.parser.parse(board['timestamp']).timestamp()
	
	return board

def setBoard(board,checkTime):
	"""
	boardデータを入力し更新する関数
	@param board boardのdictオブジェクト(stream_captureの1行分のデータ)
	@param checkTime 時刻が過ぎてたら書き込み
	"""
	
	is_write = False
	
	# 時刻が過ぎてたら書き込み
	if board['unixtime'] > checkTime:
		writeMessage(checkTime)
		is_write = True
	
	# middle_priceの更新
	data['midde'] = board['mid_price']
	
	# asksの更新
	for ask in board['asks']:
		if ask['size'] == 0:
			if ask['price'] in data['asks']:
				del data['asks'][ ask['price'] ]
		else:
			data['asks'][ ask['price'] ] = ask['size']
	
	# bidsの更新
	for bid in board['bids']:
		if bid['size'] == 0:
			if bid['price'] in data['bids']:
				del data['bids'][ bid['price'] ]
		else:
			data['bids'][ bid['price'] ] = bid['size']
	
	# timestampの更新
	data['timestamp'] = board['timestamp']
	
	return is_write

stack = {}
def writeMessage(time = None):
	if time is None:
		status = "last"
	else:
		status = "main"
		d = data.copy()
		d['time'] = time
	
		with open(outfile.format(startTime,time),'a') as fh:
			fh.write(json.dumps(d) + '\n')	# JSON出力、デバック用
			#fh.write(msgpack.packb(d))
		return
	
	with open(outfile.format(startTime,status),'w') as fh:
		fh.write(json.dumps(data))	# JSON出力、デバック用
		#fh.write(msgpack.packb(data))

# 更新された変数はNoneにする

d_board = None
d_snapshot = None

# startTimeを計算
if startTime is None:
	t_snapshot = getBoard(f_snapshot)['unixtime']
	t_board = getBoard(f_board)['unixtime']
	if t_snapshot <= t_board:
		startTime = math.ceil(t_snapshot/interval) * interval
	if t_snapshot > t_board:
		startTime = math.ceil(t_board/interval) * interval
	
	# ポインタリセット
	f_snapshot.seek(0)
	f_board.seek(0)

# nextTimeをstartTimeで初期化
nextTime = startTime

# 処理が終わるまでループ
while True:
	
	# データを取得
	if d_snapshot is None:
		d_snapshot = getBoard(f_snapshot)
	if d_board is None:
		d_board = getBoard(f_board)
	
	# snapshotもboardも取れなくなったら終了
	if d_board is None and d_snapshot is None:
		writeMessage()
		break
	
	# Noneでなくより小さい方をsetBoardを使って更新する
	if d_board is None or (d_snapshot is not None and d_snapshot['unixtime'] <= d_board['unixtime']):
		if setBoard(d_snapshot,nextTime):
			nextTime = nextTime + interval
		d_snapshot = None
		
	if d_snapshot is None or (d_board is not None and d_snapshot['unixtime'] > d_board['unixtime']):
		if setBoard(d_board,nextTime):
			nextTime = nextTime + interval
		d_board = None
