from sentiment import NaiveBayes as SentimentClassifier
from PorterStemmer import PorterStemmer
import json, math, collections

class FeatureExtractor:
    def __init__(self):
        self.stemmer = PorterStemmer()

    def extractFeatures(self, post):
        v = {}

        #v['fan_count'] = post['fan_count']

        if 'message' in post and len(post['message']) > 0:
            message = post['message']
            v['text_length'] = len(message)
            v['num_words'] = len(message.split())
            unique_stems = set([])
            for word in message.split():
                unique_stems.add(self.stemmer.stem(word))
            v['num_unique_stems'] = len(unique_stems)
            # TODO: sentiment analysis


        #v['time'] = post['created_time']

        if post['type'] == 'photo':
            v['is_photo'] = 1
            v['original_photo'] = 1 if post['status_type'] == 'added_photos' else 0
        elif post['type'] == 'video':
            v['is_video'] = 1
            v['original_video'] = 1 if post['status_type'] == 'added_video' else 0
        else:
            if post['type'] == 'link':
                v['is_link'] = 1
            elif post['type'] == 'status':
                v['is_status'] = 1

            v['was_mobile'] = 1 if post['status_type'] == 'mobile_status_update' else 0
            v['original_post'] = 1 if post['status_type'] == 'wall_post' else 0
            v['shared'] = 1 if post['status_type'] == 'shared_story' else 0

        return v
