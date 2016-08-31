#!/usr/bin/python

""" A small program that accesses the history of provided Slack channels
and sends the text to Algorithmia to perform sentiment analysis.

This analysis is the displayed giving the average number of the following:

Negative
Neutral
Positive
"""


import Algorithmia
import yaml
import json
import os
import argparse
from tabulate import tabulate
from slackclient import SlackClient
from datetime import datetime, date, time, timedelta

CONFIG = yaml.load(file('python-rtmbot-master/rtmbot.conf', 'r'))


def list_channels(slack_client):
    channel_list_raw = slack_client.api_call("channels.list", exclude_archived=1)

    channel_list = json.loads(channel_list_raw)
    channels = {}

    for channel in channel_list['channels']:

        channel_id = channel.get("id", "ID not found")
        channel_name = channel.get("name", "Name not found")

        channels[channel_name] = channel_id

    return channels


def run(slack_client, channel, algorithm):

    midnight = datetime.combine(date.today(), time.min)
    yesterday_midnight = midnight - timedelta(days=1)

    # fetch the history and convert to JSON
    history = slack_client.api_call("channels.history", channel=channel, inclusive=1,count=50)
    history = json.loads(history)

    sentiment_averages = {
        'negative': 0,
        'neutral': 0,
        'positive': 0
    }

    sentiment_results = {
        "negative": 0,
        "neutral": 0,
        "positive": 0,
        'total': 0,
    }

    for message in history['messages']:

        text = message.get("text")

        # exclude empty or server generated messages
        if not text or\
           message.get("subtype", "") == "channel_join":
            continue

        results = algorithm.pipe(text)

        if not results.result:
            continue

        results = results.result[0]

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
        sentiment_results["total"] += 1

        for k, v in sentiment_results.iteritems():
            if k == "total":
                continue
            if v == 0:
                continue
            sentiment_averages[k] = round(
                float(v) / float(sentiment_results["total"]) * 100, 2)

    headings = ["%" + x for x in sentiment_averages.keys()]
    values = sentiment_averages.values()

    print tabulate([values], headers=headings)

    return sentiment_averages


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('-l',
        '--list-channels', help='List available Slack channels.', action="store_true")
    parser.add_argument('-c',
        '--channel-name', help='Channel to evaluate sentiment from.')
    args = parser.parse_args()

    slack_token = os.environ.get("SLACK_TOKEN", None)

    if not slack_token:
        slack_token = CONFIG['SLACK_TOKEN']

    slack_client = SlackClient(slack_token)

    algorithmia_token = os.environ.get("ALGORITHMIA_TOKEN", None)

    if not algorithmia_token:
        algorithmia_token = CONFIG['ALGORITHMIA_KEY']

    algorithmia_client = Algorithmia.client(algorithmia_token)
    #algorithm = algorithmia_client.algo('nlp/SentimentAnalysis/0.1.2')
    algorithm = algorithmia_client.algo('nlp/SocialSentimentAnalysis/0.1.3')

    if args.list_channels:
        channels = list_channels(slack_client)

        display = []

        for channel_name, channel_id in channels.iteritems():
            display.append([channel_name, channel_id])

        print tabulate(display, headers=["Channel Name", "Slack ID"])
        exit()

    run(slack_client, args.channel_name, algorithm)
