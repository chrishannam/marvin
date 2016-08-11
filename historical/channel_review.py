import Algorithmia
import yaml
import json

from slackclient import SlackClient
from datetime import datetime, date, time, timedelta

CONFIG = yaml.load(file('../python-rtmbot-master/rtmbot.conf', 'r'))

ALGORITHMIA_CLIENT = Algorithmia.client(CONFIG["ALGORITHMIA_KEY"])
ALGORITHM = ALGORITHMIA_CLIENT.algo('nlp/SentimentAnalysis/0.1.2')

print CONFIG

token = CONFIG['SLACK_TOKEN'] # found at https://api.slack.com/web#authentication
sc = SlackClient(token)

midnight = datetime.combine(date.today(), time.min)
yesterday_midnight = midnight - timedelta(days=1)

channel = 'C03T49SPB'

history = sc.api_call("channels.history", channel='C03T49SPB', inclusive=1,count=50)

history = json.loads(history)

MAPPING = {
    0: 'very negative',
    1: 'negative',
    2: 'neutral',
    3: 'positive',
    4: 'very positive'
}

sentiment_results = {
    'very negative': 0,
    'negative': 0,
    'neutral': 0,
    'positive': 0,
    'very positive': 0,
}

for message in history['messages']:
    results = ALGORITHM.pipe(message['text'])

    if not results.result:
        continue
    sentiment_results[MAPPING[results.result]] += 1

print sentiment_results