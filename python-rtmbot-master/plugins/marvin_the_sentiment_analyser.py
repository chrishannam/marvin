import Algorithmia
import yaml

CONFIG = yaml.load(file('rtmbot.conf', 'r'))

ALGORITHMIA_CLIENT = Algorithmia.client(CONFIG["ALGORITHMIA_KEY"])
ALGORITHM = ALGORITHMIA_CLIENT.algo('nlp/SentimentAnalysis/0.1.2')

outputs = []

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


def process_message(data):

    text = data.get('text', None)

    if not text or data.get('subtype', '') == 'channel_join':
        return

    if 'what's the mood?' in text:
        outputs.append([data['channel'], str(sentiment_results)])
        return

    results = ALGORITHM.pipe(text)

    sentiment_results[MAPPING[results.result]] += 1

    if results.result == 0:
        outputs.append([data['channel'], "Easy there, negative Nancy!"])

    print "Comment was {}".format(MAPPING[results.result])
