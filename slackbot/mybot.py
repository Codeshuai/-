import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter
from intent_clarification.interaction.run_new import Api_Cubic

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET_'], '/slack/events', app)

client = slack.WebClient(token=os.environ['SLACK_TOKEN_'])
BOT_ID = client.api_call("auth.test")['user_id']

cache_message = {}


@ slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')
    if user_id != None and BOT_ID != user_id:
        if user_id not in list(cache_message.keys()):
            cache_message[user_id] = ""
        session_history = cache_message[user_id]
        if text == 'Start a new conversation':
            cache_message[user_id] = ""
            bot_reply = "Please input your query:"
        else:
            input_query = session_history + text
            q, d, flag = Api_Cubic().wechatbot(input_query)
            bot_reply = ""
            if flag == 'recommend':
                for _, api in enumerate(q):
                    bot_reply = str(_ + 1) + '. API method: ' + api + '\n' + 'API description: ' + d[_] + '\n\n'
                bot_reply = bot_reply.rstrip('\n\n')
                cache_message[user_id] = ""
                recommend_message = '这些API可能对您有帮助：\n'
                bot_reply = recommend_message + bot_reply
            else:
                for idd, option in enumerate(d):
                    bot_reply = bot_reply + str(idd + 1) + ". " + option + "\n"
                bot_reply = q + '\n' + bot_reply
                err1 = 'These options may help you:'
                err2 = 'Your reply seems to be outside the above options.'
                if err1 not in bot_reply and err2 not in bot_reply:
                    cache_chat = input_query + '\n' + bot_reply + '=========='
                    cache_message[user_id] = cache_chat
                # 发送我创建的文本信息
        client.chat_postMessage(channel=channel_id, text=bot_reply)


if __name__ == '__main__':
    app.run()