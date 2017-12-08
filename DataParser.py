import json, math, os, time, copy, re
import collections
import csv
import dateutil.parser as dp
from PorterStemmer import PorterStemmer
from FeatureExtractor import FeatureExtractor
from nltk.corpus import stopwords
import heapq


SECONDS_IN_HOUR = 3600.0

# Class: DataParser
# --------------------
# Parses data to create feature vectors for every post
# Defines ways to retrieve these vectors
class DataParser:

    def __init__(self, path):

        # total posts
        self.postCount = 0

        # maps a POST_ID to its feature_vector
        # e.g. feature_vectors['POST_ID'] gives a feature vector for a post
        self.feature_vectors = collections.defaultdict(lambda: {})

        # map from post_IDs to reactions mapping; example::
        #   POST_ID : {num_like: 300, num_love: 12, num_wow: 0, num_sad: 0, num_angry: 0}
        self.post_results = {}

        # map between account IDs and their names
        # map between account IDs and their profile objects (JSON)
        self.Names = collections.defaultdict(lambda: '')
        self.Profiles = collections.defaultdict(lambda: '')

        # map between post IDs and their Post objects
        self.Posts = {}

        # Porter Stemmer, Feature Extractor, Stop Words
        self.stemmer = PorterStemmer()
        self.featureExtractor = FeatureExtractor()
        self.stopwords = set(stopwords.words('english'))

        # uni/bi/tri-gram frequencies across posts
        self.wordFrequency = collections.defaultdict(lambda: 0.0)
        self.bigramFrequency = collections.defaultdict(lambda: collections.defaultdict(lambda: 0))
        self.trigramFrequency = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(lambda: 0)))

        #uni/bi/tri-gram scores
        self.wordScores = collections.defaultdict(lambda: 0.0)
        self.bigramScores = collections.defaultdict(lambda: collections.defaultdict(lambda: 0.0))
        self.trigramScores = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(lambda: 0.0)))

        #total uni/bi/tri-gram counts processed
        self.wordCount = 0
        self.bigramCount = 0
        self.trigramCount = 0

        # Heaps used to determine most popular uni/bi/tri-grams
        self.wordsHeap = None
        self.bigramsHeap = None
        self.trigramsHeap = None
        self.heapified = False


        # internal fields, shouldn't need to be called by other classes
        self.relevant_fields = ["id", "created_time", "type", "message" ]
        self.num_reaction_keys = ['num_likes', 'num_loves', 'num_wows', 'num_sads', 'num_hahas', 'num_angrys']

        # parses train data
        self.parseTrainData(path)
        self.processParsedData()

    ############################ PARSING FUNCTIONS ############################



    def recordUnigrams(self, words, num_reactions):
        seen = set([])
        for word in words:
            if word in self.stopwords:
                continue

            word = self.stemmer.stem(word)

            if word in seen:
                continue

            seen.add(word)
            self.wordFrequency[word] += 1
            self.wordScores[word] += num_reactions
            self.wordCount += 1

    def recordBigrams(self, words, num_reactions):
        i = 0
        seen = set([])
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

            self.bigramFrequency[a][b] += 1
            self.bigramScores[a][b] += num_reactions
            self.bigramCount += 1
            i += 1

    def recordTrigrams(self, words, num_reactions):
        i = 0
        seen = set([])
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

            self.trigramFrequency[a][b][c] += 1
            self.trigramScores[a][b][c] += num_reactions
            self.trigramCount += 1
            i += 1

    def getNumReactions(self, post):
        return sum([int(post[reaction_key]) for reaction_key in self.num_reaction_keys])

    # Function: parseProfile
    # ----------------------------------
    # reads a profile.txt file and parses the contents,
    # then organizes the profile contents for internal use
    def parseProfile(self, path):
        profile = None

        try:
            with open(path) as data_file:
                profile = json.load(data_file)
        except Exception:
            err = 'error opening %s' % path
            raise Exception(err)

        ID = profile['id']

        self.Names[ID] = profile['name']
        self.Profiles[ID] = profile

        return profile


    # parsePostsCSV
    def parsePostsCSV(self, path, profile):

        with open(path, 'rb') as csvFile:
            reader = csv.DictReader(csvFile)
            lastPost = None

            for post in reader:
                if post['status_type'] == 'photo' or post['status_type'] == 'video': continue

                for num_reaction in self.num_reaction_keys:
                        post[num_reaction] = int(post[num_reaction])

                post['num_comments'] = int(post['num_comments'])

                post['original_message_len'] = len(post['status_message'].decode('utf-8').encode('ascii', 'ignore').strip().lower().split())

                post['message'] = post['status_message'] + ' ' + post['link_name']
                del post['status_message']

                words = post['message'].decode('utf-8').encode('ascii', 'ignore').strip().lower().split()

                if len(words) < 2:
                    continue

                post['id'] = post['status_id']
                del post['status_id']

                post['created_time'] = post['status_published']
                del post['status_published']

                post['type'] = post['status_type']
                del post['status_type']

                post['hour_created'] = int(str(dp.parse(post['created_time'])).split(':')[0].split(' ')[1])
                created = int(dp.parse(post['created_time']).strftime('%s'))

                if lastPost != None:
                    lastPostCreated = int(dp.parse(lastPost['created_time']).strftime('%s'))
                    post['hours_since_last_post'] = (created - lastPostCreated) / SECONDS_IN_HOUR

                post['elapsed_hours'] = (os.stat(path).st_birthtime - created) / SECONDS_IN_HOUR

                num_reactions = self.getNumReactions(post)
                results = {'num_reactions': num_reactions}
                self.post_results[post['id']] = results

                self.recordUnigrams(words, num_reactions)
                self.recordBigrams(words, num_reactions)
                self.recordTrigrams(words, num_reactions)

                if profile != None:
                    post['poster'] = profile['id']
                    post['fan_count'] = profile['fan_count']

                self.Posts[post['id']] = post
                self.postCount += 1

                if self.postCount % 20000 == 0:
                    print "parsed %s posts so far..." % self.postCount
                lastPost = post


    def normalizeNGramScores(self):
        for word, score in self.wordScores.iteritems():
            self.wordScores[word] = score / self.wordFrequency[word]

        for a, Dict in self.bigramScores.iteritems():
            for b, score in Dict.iteritems():
                self.bigramScores[a][b] = score / self.bigramFrequency[a][b]

        for a, Dict1 in self.trigramScores.iteritems():
            for b, Dict2 in Dict1.iteritems():
                for c, score in Dict2.iteritems():
                    self.trigramScores[a][b][c] = score / self.trigramFrequency[a][b][c]

    # Function: parseTrianData
    # ----------------------------------
    # parses all train/test data
    def parseTrainData(self, path):
        #traverse through all subdirectories
        for (name, children, files) in os.walk(path):
            if '/' not in name: continue
            if not os.path.isfile(name + '/profile.txt'): continue
            profile = self.parseProfile(name + '/profile.txt')
            for File in files:
                if File != 'profile.txt' and File[0] != '.':
                    self.parsePostsCSV(name + '/' + File, profile)

        print "Parsed %s posts total" % self.postCount

    def processParsedData(self):

        self.normalizeNGramScores()

        # Give FeatureExtractor class relevant n-gram info to score posts
        self.featureExtractor.giveWordScores(self.wordScores)
        self.featureExtractor.giveBigramScores(self.bigramScores)
        self.featureExtractor.giveTrigramScores(self.trigramScores)

        print "Extracting post features... this may take a while..."
        processed = 0
        for postID, post in self.Posts.iteritems():
            self.feature_vectors[post['id']] = self.featureExtractor.extractFeatures(post)
            processed += 1
            if processed % 20000 == 0:
                print "\tProcessed %s posts so far..." % processed
        print "Extracted features from %s posts total" % processed

    ########################## END PARSING FUNCTIONS ##########################


    # Function: getFeatureResultPairs
    # ----------------------------------
    # returns a mapping of ALL posts' feature vectors
    # to the resulting # of likes/reactions
    def getFeatureResultPairs(self):
        featureResults = []
        for post_id, vector in self.feature_vectors.iteritems():
            featureResults.append((vector, self.post_results[post_id], post_id))
        return featureResults



    # Heapifies Unigrams/Bigrams/Trigrams to find more 'popular' ones
    def Heapify(self):

        if self.wordsHeap == None:
            self.wordsHeap = []
            for k, v in self.wordScores.iteritems():
                self.wordsHeap.append((-v, k))
            heapq.heapify(self.wordsHeap)

        if self.bigramsHeap == None:
            self.bigramsHeap = []
            for a, Dict in self.bigramScores.iteritems():
                for b, v in Dict.iteritems():
                    self.bigramsHeap.append((-v, (a, b)))
            heapq.heapify(self.bigramsHeap)

        if self.trigramsHeap == None:
            self.trigramsHeap = []
            for a, Dict1 in self.trigramScores.iteritems():
                for b, Dict2 in Dict1.iteritems():
                    for c, v in Dict2.iteritems():
                        self.trigramsHeap.append((-v, (a, b, c)))
            heapq.heapify(self.trigramsHeap)

    # Functions that print the most Provocative n-grams across posts
    def printMostProvocativeWords(self, numWords):
        if not self.heapified:
            self.Heapify()
        print "Most Provacative Words: "
        for i in range(numWords):
            print "\t%s" % heapq.heappop(self.wordsHeap)[1]
        self.wordsHeap = None


    def printMostProvocativeBigrams(self, numGrams):
        if not self.heapified:
            self.Heapify()
        print "Most Provacative Bigrams: "
        for i in range(numGrams):
            bigram = heapq.heappop(self.bigramsHeap)
            print "\t%s %s" % (bigram[1][0], bigram[1][1])
        self.bigramsHeap = None

    def printMostProvocativeTrigrams(self, numGrams):
        if not self.heapified:
            self.Heapify()
        print "Most Provacative Trigrams: "
        for i in range(numGrams):
            trigram = heapq.heappop(self.trigramsHeap)
            print "\t%s %s %s" % (trigram[1][0], trigram[1][1], trigram[1][2])
        self.trigramsHeap = None
