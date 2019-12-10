import os

from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextMessage, TextSendMessage


channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)


def send_text_message(reply_token, text, follow_text = ''):
    line_bot_api = LineBotApi(channel_access_token)

    if (follow_text = ''):
        line_bot_api.reply_message(reply_token, TextSendMessage(text=text))
    else:
        line_bot_api.reply_message(reply_token, [TextSendMessage(text=text), TextSendMessage(text=follow_text)])

    return "OK"

"""
def send_image_url(id, img_url):
    pass

def send_button_message(id, text, buttons):
    pass
"""
