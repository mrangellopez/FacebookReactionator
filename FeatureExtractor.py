from sentiment import NaiveBayes as SentimentClassifier
from PorterStemmer import PorterStemmer
import json, math, collections, re
#from textblob.en.sentiments import NaiveBayesAnalyzer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class FeatureExtractor:
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.analyzer = SentimentIntensityAnalyzer()
        self.num_reaction_keys = ['num_likes', 'num_loves', 'num_wows', 'num_sads', 'num_hahas', 'num_angrys']

    def giveWordsToReactions(self, wordsToReactions):
        self.wordsToReactions = wordsToReactions

    def giveWordsToLikes(self, wordsToLikes):
        self.wordsToLikes = wordsToLikes

    def getMessageScore(self, words):
        score_likes = 0.0
        score_reactions = 0.0
        for i in range(0, len(words) - 2):
            a = self.stemmer.stem(words[i])
            b = self.stemmer.stem(words[i+1])
            c = self.stemmer.stem(words[i+2])
            score_likes += self.wordsToLikes[a][b][c]
            score_reactions += self.wordsToReactions[a][b][c]
        #for word in words:
        #    word = self.stemmer.stem(word)
        #    score_likes += self.wordsToLikes[word]
        #    score_reactions += self.wordsToReactions[word]
        if len(words) > 2:
            score_likes /= (len(words) - 2)
            score_reactions /= (len(words) - 2)
        else:
            scores_likes = 0
            scores_reactions = 0
        return (score_likes, score_reactions)


    def extractFeatures(self, post):
        v = {}

        v['fan_count_log'] = math.log(post['fan_count'])
        #v['fan_count_squared'] = post['fan_count'] ** 2

        if 'days_since_last_post' in post:
            v['days_since_last_post'] = post['days_since_last_post']


        if 'message' in post and len(post['message']) > 0:
            message = post['message'].strip().lower()

            #sentiment analysis
            scores = self.analyzer.polarity_scores(message)
            v['p_pos'] = scores['pos']
            v['p_neg'] = scores['neg']
            v['p_neu'] = scores['neu']
            v['p_compound'] = scores['compound']

            # text length by word count
            v['num_words_log'] = math.log(len(message.split()))

            unique_stems = collections.defaultdict(lambda: 0)

            words = message.split()

            message_score_likes, message_score_reactions = self.getMessageScore(words)

            v['message_score_likes'] = message_score_likes
            v['message_score_reactions'] = message_score_reactions

            v ['fan_count_log_times_message_score_likes'] = message_score_likes * v['fan_count_log']
            v ['fan_count_log_times_message_score_reactions'] = message_score_reactions * v['fan_count_log']

            for word in words:
                unique_stems[self.stemmer.stem(word)] += 1

            total = 0.0

            # text length by number of unique word stems
            if len(unique_stems) > 0:
                v['num_unique_stems_log'] = math.log(len(unique_stems))
            #v['num_unique_stems_squared'] = len(unique_stems) ** 2

        v['elapsed_days_log'] = math.log(post['elapsed_days'])

        if post['type'] == 'photo':
            v['is_photo'] = 1
        elif post['type'] == 'video':
            v['is_video'] = 1
        elif post['type'] == 'link':
            v['is_link'] = 1
        elif post['type'] == 'status':
            v['is_status'] = 1

        #if 'num_comments' in post:
            #v['num_comments'] = post['num_comments']

        return v
