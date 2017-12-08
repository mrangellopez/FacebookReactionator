from sentiment import NaiveBayes as SentimentClassifier
from PorterStemmer import PorterStemmer
import json, math, collections, re
#from textblob.en.sentiments import NaiveBayesAnalyzer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textstat.textstat import textstat
from nltk.corpus import stopwords
import numpy as np
import pandas as pd

class FeatureExtractor:
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.analyzer = SentimentIntensityAnalyzer()
        self.stopwords = set(stopwords.words('english'))
        self.featuresList = None

    def giveTrigramScores(self, trigramScores):
        self.trigramScores = trigramScores

    def giveBigramScores(self, bigramScores):
        self.bigramScores = bigramScores

    def giveWordScores(self, wordScores):
        self.wordScores = wordScores

    def getScoreByUnigrams(self, words):
        score = 0.0
        seen = set([])
        for word in words:
            if word in self.stopwords:
                continue

            word = self.stemmer.stem(word)
            if word in seen:
                continue
            seen.add(word)
            score += self.wordScores[word]
        if len(seen) == 0 or score == 0.0:
            return 0.0
        return score * 0.001 / len(seen)

    def getScoreByBigrams(self, words):
        score = 0.0
        seen = set([])
        i = 0
        while i < len(words) - 1:
            a = words[i]
            b = words[i+1]
            if a in self.stopwords:
                i += 1
                continue

            a = self.stemmer.stem(a)
            b = self.stemmer.stem(b)

            if (a, b) in seen:
                i += 1
                continue

            seen.add((a, b))
            score += self.bigramScores[a][b]

        if len(seen) == 0 or score == 0.0:
            return 0.0
        return score * 0.0001 / len(seen)

    def getScoreByTrigrams(self, words):
        score = 0.0
        seen = set([])
        i = 0
        while i < len(words) - 2:
            a = words[i]
            b = words[i+1]
            c = words[i+2]
            if a in self.stopwords:
                i += 1
                continue

            a = self.stemmer.stem(a)
            b = self.stemmer.stem(b)
            c = self.stemmer.stem(c)

            if (a, b, c) in seen:
                i += 1
                continue

            seen.add((a, b, c))
            score += self.trigramScores[a][b][c]

        if len(seen) == 0 or score == 0.0:
            return 0.0
        return score * 0.0001 / len(seen)


    def extractFeatures(self, post):
        v = {}

        v['fan_count_log'] = math.log(post['fan_count'])

        message = post['message'].decode('utf-8').encode('ascii', 'ignore').strip().lower()

        v['questions'] = 1 if '?' in post['message'] else 0
        v['exclamation'] = 1 if '!' in post['message'] else 0

        #sentiment analysis
        scores = self.analyzer.polarity_scores(message)
        allSentimentScores = scores['pos'] + scores['neg'] + scores['neu']
        scores['pos'] = scores['pos'] / allSentimentScores
        scores['neg'] = scores['neg'] / allSentimentScores
        scores['neu'] = scores['neu'] / allSentimentScores

        v['pos'] = scores['pos']
        v['neg'] = scores['neg']
        v['neu'] = scores['neu']
        #v['compound'] = scores['compound']

        # text length by word count

        words = message.split()

        v['unigrams_score'] = self.getScoreByUnigrams(words)
        v['bigrams_score'] = self.getScoreByBigrams(words)
        v['trigrams_score'] = self.getScoreByTrigrams(words)

        readease = textstat.flesch_reading_ease(message)
        smog = textstat.smog_index(message)
        flesh_kin = textstat.flesch_kincaid_grade(message)

        v['reading_ease'] = math.log(readease) if readease > 1 else 0
        v['smog_index_inverse'] = 1 / math.log(smog) if smog > 0 else 1
        #v['grade_inverse'] = 1 / math.log(flesh_kin) if flesh_kin > 1 else 1

        v['neg_and_smog_inverse'] = scores['neg'] * v['smog_index_inverse']
        v['neg_and_reading_ease'] = scores['neg']  * v['reading_ease']
        #v['neg_and_grade_inverse'] = scores['neg'] * v['grade_inverse']

        v['pos_and_smog_inverse'] = scores['pos'] * v['smog_index_inverse']
        v['pos_and_reading_ease'] = scores['pos']  * v['reading_ease']
        #v['pos_and_grade_inverse'] = scores['pos'] * v['grade_inverse']

        v['neu_and_smog_inverse'] = scores['neu'] * v['smog_index_inverse']
        v['neu_and_reading_ease'] = scores['neu']  * v['reading_ease']
        #v['neu_and_grade_inverse'] = scores['neu'] * v['grade_inverse']

        unique_stems = collections.defaultdict(lambda: 0)

        for word in words:
            unique_stems[self.stemmer.stem(word)] += 1

        #v['num_unique_stems_log_inverse'] = 1 / math.log(len(unique_stems)) if len(unique_stems) > 1 else 1

        v['elapsed_hours_log'] = math.log10(post['elapsed_hours']) if post['elapsed_hours'] > 1 else post['elapsed_hours']

        #if 'hours_since_last_post' in post:
        #    v['hours_since_last_post_log'] = math.log(post['hours_since_last_post']) if post['hours_since_last_post'] > 1 else 0
        #else:
        #    v['hours_since_last_post_log'] = 0.0

        hr = post['hour_created']

        v['early_morning'] = 1 if hr >= 4 and hr < 8 else 0
        v['morning'] = 1 if hr >= 8 and hr < 11 else 0
        v['midday'] = 1 if hr >= 11 and hr < 13 else 0
        v['afternoon'] = 1 if hr >= 13 and hr < 16 else 0
        v['evening'] = 1 if hr >=16 and hr < 20 else 0
        v['night'] = 1 if hr >=20 else 0
        v['late_night_or_early_early_morning'] = 1 if hr < 4 else 0

        if self.featuresList == None:
            self.featuresList = [k for k, val in v.iteritems()]

        return pd.Series(v).values
