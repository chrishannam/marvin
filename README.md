# Marvin
This project is named after the android from The Hitchhikers Guide to Galaxy. https://en.wikipedia.org/wiki/Marvin_(character).

## Purpose
To track the mood of a Slack channel either in real time or historically. Using a sentiment analysis algorithm from https://algorithmia.com
each comment is rated for it's general tone or sentiment.

# Setup
```
virtualenv .
source bin/activate

```

# Usage
Marvin uses the algorithm https://algorithmia.com/algorithms/nlp/SentimentAnalysis to analyse a message in the Slack channel.
The results from the analysis are in the form of:

* Very Negative
* Negative
* Neutral
* Postitive
* Very Positive

For more detail check out the algorithm's page https://algorithmia.com/algorithms/nlp/SentimentAnalysis.

# Historical Analysis
Provided in the historical directory is ascript that will review the last 24 hours of your Slack channel.