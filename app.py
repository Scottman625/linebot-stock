from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage,FlexSendMessage
)

from googletrans import Translator

app = Flask(__name__)

from config import * 

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

def translate_text(text,dest='en'):
    """以google翻譯將text翻譯為目標語言

    :param text: 要翻譯的字串，接受UTF-8編碼。
    :param dest: 要翻譯的目標語言，參閱googletrans.LANGCODES語言列表。
    """
    translator = Translator()
    result = translator.translate(text, dest).text
    return result

import mplfinance as mpf
import pandas_datareader.data as web
import pyimgur
import twstock as t
import json
import lxml
IMGUR_CLIENT_ID = imgur_client_id

def plot_stcok_k_chart(IMGUR_CLIENT_ID,stock="0050" , date_from='2020-01-01' ):
    """
    進行個股K線繪製，回傳至於雲端圖床的連結。將顯示包含5MA、20MA及量價關係，起始預設自2020-01-01起迄昨日收盤價。
    :stock :個股代碼(字串)，預設0050。
    :date_from :起始日(字串)，格式為YYYY-MM-DD，預設自2020-01-01起。
    """
    stock = str(stock)+".tw"
    df = web.DataReader(stock, 'yahoo', date_from) 
    mpf.plot(df,type='candle',mav=(5,20),volume=True, ylabel=stock.upper()+' Price' ,savefig='testsave.png')
    PATH = "testsave.png"
    im = pyimgur.Imgur(IMGUR_CLIENT_ID)
    uploaded_image = im.upload_image(PATH, title=stock+" candlestick chart")
    return uploaded_image.link

@handler.add(MessageEvent,message=TextMessage)
def handle_message(event):
    
    if event.message.text[:4].lower() == "help":
        FlexMessage = json.load(open('help.json','r',encoding='utf-8'))
        line_bot_api.reply_message(event.reply_token, FlexSendMessage('help', FlexMessage))
    if event.message.text[:3] == "@翻英":
        content = translate_text(event.message.text[3:], "en")
        message = TextSendMessage(text=content)
        line_bot_api.reply_message(event.reply_token, message)
    if event.message.text[:3] == "@翻日":
        content = translate_text(event.message.text[3:] , "ja")
        message = TextSendMessage(text=content)
        line_bot_api.reply_message(event.reply_token, message)
    if event.message.text[:3] == "@翻中":
        content = translate_text(event.message.text[3:] , "zh-tw")
        message = TextSendMessage(text=content)
        line_bot_api.reply_message(event.reply_token, message)
    if event.message.text[:2].upper() == "@K":
        input_word = event.message.text.replace(" ","") #合併字串取消空白
        stock_name = input_word[2:6] #2330
        start_date = input_word[6:] #2020-01-01
        stock_price = t.realtime.get(stock_name)
        # with open("user_profile_business.txt", "a") as myfile:
        output_name=stock_price['info']['name']
        output1=stock_price['realtime']['latest_trade_price']
        output2=stock_price['realtime']['open']
        output3=stock_price['realtime']['high']
        output4=stock_price['realtime']['low']
            # myfile.write(json.dumps(vars(user_profile),sort_keys=True))
            # myfile.write('\n')
        reply_arr=[]
        reply_arr.append( TextSendMessage(text=f'現在「{output_name}」的最新成交價：{output1}\n當日開盤價：{output2}\n當日最高價：{output3}\n當日最低價：{output4}') )
            # line_bot_api.reply_message(event.reply_token,TextSendMessage(text=f'現在「{output_name}」的最新成交價：{output1}\n當日開盤價：{output2}\n當日最高價：{output3}\n當日最低價：{output4}'))
        content = plot_stcok_k_chart(IMGUR_CLIENT_ID,stock_name,start_date)
        reply_arr.append( ImageSendMessage(original_content_url=content,preview_image_url=content) )
            # message = ImageSendMessage(original_content_url=content,preview_image_url=content)

        line_bot_api.reply_message(event.reply_token, reply_arr)
    elif event.message.text[:5] == "@個股資訊":
        line_bot_api.reply_message(
          event.reply_token,
          TextSendMessage(text="請輸入'@k 股票代號'進行查詢")
          )
    elif event.message.text[:5] == "@英文翻譯":
        line_bot_api.reply_message(
          event.reply_token,
          TextSendMessage(text="請輸入'@翻英 文字'進行翻譯")
          )
    elif event.message.text[:5] == "@中文翻譯":
        line_bot_api.reply_message(
          event.reply_token,
          TextSendMessage(text="請輸入'@翻中 文字'進行翻譯")
          )
    elif event.message.text[:5] == "@日文翻譯":
        line_bot_api.reply_message(
          event.reply_token,
          TextSendMessage(text="請輸入'@翻日 文字'進行翻譯")
          )

    else: 
        pass


if __name__ == "__main__":
    app.run()