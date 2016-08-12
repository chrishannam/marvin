#!/usr/bin/python

""" A small program that accesses the history of provided Slack channels
and sends the text to Algorithmia to perform sentiment analysis.

This analysis is the displayed giving the average number of the following:

Very negative
Negative
Neutral
Positive
Very positive
"""


import Algorithmia
import yaml
import json
import argparse
from tabulate import tabulate
from slackclient import SlackClient
from datetime import datetime, date, time, timedelta

CONFIG = yaml.load(file('python-rtmbot-master/rtmbot.conf', 'r'))

ALGORITHMIA_CLIENT = Algorithmia.client(CONFIG["ALGORITHMIA_KEY"])
ALGORITHM = ALGORITHMIA_CLIENT.algo('nlp/SentimentAnalysis/0.1.2')


def list_channels(slack_client):
    channel_list_raw = slack_client.api_call("channels.list", exclude_archived=1)

    channel_list = json.loads(channel_list_raw)
    channels = {}

    for channel in channel_list['channels']:

        channel_id = channel.get("id", "ID not found")
        channel_name = channel.get("name", "Name not found")

        channels[channel_name] = channel_id

    return channels


def run(slack_client, channel):

    midnight = datetime.combine(date.today(), time.min)
    yesterday_midnight = midnight - timedelta(days=1)

    # fetch the history and convert to JSON
    history = slack_client.api_call("channels.history", channel=channel, inclusive=1,count=50)
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

        text = message.get("text")

        # exclude empty or server generated messages
        if not text or\
           message.get("subtype", "") == "channel_join":
            continue

        results = ALGORITHM.pipe(message['text'])

        if not results.result:
            continue
        sentiment_results[MAPPING[results.result]] += 1

    print sentiment_results


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

    token = CONFIG['SLACK_TOKEN']
    slack_client = SlackClient(token)

    if args.list_channels:
        channels = list_channels(slack_client)

        display = []

        for channel_name, channel_id in channels.iteritems():
            display.append([channel_name, channel_id])

        print tabulate(display, headers=["Channel Name", "Slack ID"])
        exit()

    run(slack_client, args.channel_name)
