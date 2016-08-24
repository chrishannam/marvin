import Algorithmia
import yaml
import traceback


CONFIG = yaml.load(file("rtmbot.conf", "r"))

ALGORITHMIA_CLIENT = Algorithmia.client(CONFIG["ALGORITHMIA_KEY"])
#ALGORITHM = ALGORITHMIA_CLIENT.algo("nlp/SentimentAnalysis/0.1.2")
ALGORITHM = ALGORITHMIA_CLIENT.algo('nlp/SocialSentimentAnalysis/0.1.3')

outputs = []

sentiment_results = {
    "negative": 0,
    "neutral": 0,
    "positive": 0,
    "total": 0,
}

sentiment_averages = {
    "negative": 0,
    "neutral": 0,
    "positive": 0
}


def display_current_mood(channel):
    reply = ""

    # something has gone wrong if we don't have a channel do nothing
    if not channel:
        return

    # loop over our stats and send them in the
    # best layout we can.
    for k, v in sentiment_averages.iteritems():
        if k == "total":
            continue
        reply += "{}: {}%\n ".format(k.capitalize(), v)

    outputs.append([channel, str(reply)])
    return

def process_message(data):

    text = data.get("text", None)

    if not text or data.get("subtype", "") == "channel_join":
        return

    # remove any odd encoding
    text = text.encode('utf-8')

    if "current mood?" in text:
        return display_current_mood(data.get("channel", None))

    # don't log the current mood reply!
    if text.startswith('Positive:'):
        return

    try:
        sentence = {
            "sentence": text
        }

        result = ALGORITHM.pipe(sentence)

        results = result.result[0]

        verdict = "neutral"
        compound_result = results.get('compound', 0)

        if compound_result == 0:
            sentiment_results["neutral"] += 1
        elif compound_result > 0:
            sentiment_results["positive"] += 1
            verdict = "positive"
        elif compound_result < 0:
            sentiment_results["negative"] += 1
            verdict = "negative"

        # increment counter so we can work out averages
        sentiment_averages["total"] += 1

        for k, v in sentiment_results.iteritems():
            if k == "total":
                continue
            if v == 0:
                continue
            sentiment_averages[k] = round(
                float(v) / float(sentiment_averages["total"]) * 100, 2)

        if compound_result < -0.75:
            outputs.append([data["channel"], "Easy there, negative Nancy!"])

        # print to the console what just happened
        print 'Comment "{}" was {}, compound result {}'.format(text, verdict, compound_result)

    except Exception as exception:
        # a few things can go wrong but the important thing is keep going
        # print the error and then move on
        print "Something went wrong processing the text: {}".format(text)
        print traceback.format_exc(exception)