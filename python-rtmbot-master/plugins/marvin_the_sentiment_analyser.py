import Algorithmia
import yaml

CONFIG = yaml.load(file("rtmbot.conf", "r"))

ALGORITHMIA_CLIENT = Algorithmia.client(CONFIG["ALGORITHMIA_KEY"])
ALGORITHM = ALGORITHMIA_CLIENT.algo("nlp/SentimentAnalysis/0.1.2")

outputs = []

MAPPING = {
    0: "very negative",
    1: "negative",
    2: "neutral",
    3: "positive",
    4: "very positive"
}

sentiment_results = {
    "very negative": 0,
    "negative": 0,
    "neutral": 0,
    "positive": 0,
    "very positive": 0
}

sentiment_averages = {
    "very negative": 0,
    "negative": 0,
    "neutral": 0,
    "positive": 0,
    "very positive": 0,
    "total": 0,
}


def process_message(data):

    text = data.get("text", None)

    if not text or data.get("subtype", "") == "channel_join":
        return

    if "what's the mood?" in text:

        reply = ""

        for k, v in sentiment_averages.iteritems():
            if k == "total":
                continue
            reply += "{}: {}%\n ".format(k.capitalize(), v)

        outputs.append([data["channel"], str(reply)])

        return

    results = ALGORITHM.pipe(text)

    sentiment_results[MAPPING[results.result]] += 1

    # increment counter so we can work out averages
    sentiment_averages["total"] += 1

    for k, v in sentiment_results.iteritems():
        if k == "total":
            continue
        if v == 0:
            continue
        sentiment_averages[k] = round(
            float(v) / float(sentiment_averages["total"]) * 100, 2)

    if results.result == 0:
        outputs.append([data["channel"], "Easy there, negative Nancy!"])

    # print to the console what just happened
    print 'Comment "{}" was {}'.format(text, MAPPING[results.result])
