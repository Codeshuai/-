import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter
import openai

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET_'], '/slack/events', app)

client = slack.WebClient(token=os.environ['SLACK_TOKEN_'])
BOT_ID = client.api_call("auth.test")['user_id']


@ slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')
    if user_id != None and BOT_ID != user_id:
        openai.api_key = "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"
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=text,
            max_tokens=7,
            temperature=0
        )
        reply = response['choices'][0]['text']
        client.chat_postMessage(channel=channel_id, text=reply)


if __name__ == '__main__':
    app.run()