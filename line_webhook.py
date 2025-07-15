from flask import Flask, request, abort
import os
import json
import requests

# LINEからの署名検証のため
from hashlib import sha256
import hmac
import base64

# Flaskアプリケーション作成
app = Flask(__name__)

# 環境変数から取得（またはconfigで読み込んでOK）
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "3f8fa94864662183862e67f9737917c6")
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "YhSluRS7aLLcA94bVb4AojgjC1sP+cBzsKWYZ0vJhpv/i5eHJEcsI9ghSgIPypuPtQWQz6IxXJbnrNn0yj/KAdMoJ2pzPbUYnbqN4ocEEZSXaBJZTV//NbUm+c/58JsHNlJIjtDaXuUskjuoWz0M4AdB04t89/1O/w1cDnyilFU=")

# LINEのWebhookを受信するルート
@app.route("https://dd795d52fe10.ngrok-free.app/callback", methods=["POST"])
def callback():
    # ヘッダから署名を取得
    signature = request.headers.get("X-Line-Signature", "")

    # ボディ取得
    body = request.get_data(as_text=True)
    print("◆受信ボディ：", body)

    # 署名検証
    hash = hmac.new(CHANNEL_SECRET.encode("utf-8"), body.encode("utf-8"), sha256).digest()
    computed_signature = base64.b64encode(hash).decode("utf-8")

    if computed_signature != signature:
        print("❌ 署名不一致。処理中止")
        abort(400)

    # メッセージ処理
    events = json.loads(body)["events"]
    for event in events:
        if event["type"] == "message":
            reply_token = event["replyToken"]
            message_text = event["message"]["text"]
            reply_text = f"あなたはこう言いました：『{message_text}』"
            send_reply(reply_token, reply_text)

    return "OK"

# メッセージ返信関数
def send_reply(token, text):
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "replyToken": token,
        "messages": [{"type": "text", "text": text}]
    }
    requests.post(url, headers=headers, data=json.dumps(payload))

# サーバー起動
if __name__ == "__main__":
    app.run(port=5000)
