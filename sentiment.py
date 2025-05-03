import sys
import json
import time
import re
import requests
import nltk
import argparse
import logging
import string
from datetime import datetime
from random import randrange
from bs4 import BeautifulSoup
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from newspaper import Article, ArticleException
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import tweepy

from config import *  # Your Twitter credentials and Elasticsearch details

STOCKSIGHT_VERSION = '0.2'

if sys.version_info < (3, 7):
    print("Python 3.7+ is required")
    sys.exit(1)

# PART 2: Logging
logger = logging.getLogger('stocksight')
logger.setLevel(logging.INFO)

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.INFO
)

# PART 3: Helper Functions

def clean_text(text):
    text = text.replace("\n", " ")
    text = re.sub(r"https?\S+", "", text)
    text = re.sub(r"&.*?;", "", text)
    text = re.sub(r"<.*?>", "", text)
    text = text.replace("RT", "").replace(u"\u2026", "").strip()
    return text

def clean_text_sentiment(text):
    return re.sub(r"[#|@]\S+", "", text).strip()

def sentiment_analysis(text):
    blob = TextBlob(text)
    vader = SentimentIntensityAnalyzer().polarity_scores(text)
    polarity = (blob.sentiment.polarity + vader['compound']) / 2
    subjectivity = blob.sentiment.subjectivity

    if polarity > 0.05:
        sentiment = "positive"
    elif polarity < -0.05:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return polarity, subjectivity, sentiment
