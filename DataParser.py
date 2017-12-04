import json, math, os, time, copy, re
import collections
import csv
import dateutil.parser as dp
from PorterStemmer import PorterStemmer
from FeatureExtractor import FeatureExtractor


SECONDS_IN_DAY = 86400.0

# Class: DataParser
# --------------------
# Parses data to create feature vectors for every post
# Defines ways to retrieve these vectors
class DataParser:

    def __init__(self, path):

        self.postCount = 0

        # maps a POST_ID to its feature_vector
        # e.g. feature_vectors['POST_ID'] gives a feature vector for a post
        self.feature_vectors = collections.defaultdict(lambda: {})

        # map from post_IDs to reactions mapping; example::
        #   POST_ID : {num_like: 300, num_love: 12, num_wow: 0, num_sad: 0, num_angry: 0}
        self.post_results = {}

        # map between categoryKey (maxNumberOfFollowers) to a set of
        # names associated with that group
        self.accountsByPopularity = collections.defaultdict(lambda: set([]))

        # map between account IDs and their names
        # map between account IDs and their profile objects (JSON)
        self.Names = collections.defaultdict(lambda: '')
        self.Profiles = collections.defaultdict(lambda: '')

        # map between post IDs and their Post objects
        self.Posts = {}

        self.stemmer = PorterStemmer()

        self.wordsToLikes = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(lambda: 0)))
        self.wordsToReactions = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(lambda: 0)))

        # 2D array between word stems and emotions, where the value is the number of
        # times a stem and reaction are associated
        # When parsing a training post, we go through all the stems in the post.
        # Every time we encounter stem in the post, we add num_reaction to
        # stemReactions[stem][reaction] counter
        self.stemReactions = collections.defaultdict(lambda: collections.defaultdict(lambda: \
            {'num_likes': 0, 'num_loves': 0, 'num_wows': 0, 'num_sads': 0, 'num_hahas': 0, 'num_angrys': 0}))


        # internal fields, shouldn't need to be called by other classes
        self.relevant_fields = ["id", "created_time", "type", "message" ]
        self.possible_reactions = ["like", "love", "wow", "sad", "haha", 'angry']
        self.num_reaction_keys = ['num_likes', 'num_loves', 'num_wows', 'num_sads', 'num_hahas', 'num_angrys']

        self.followerPopularityCategories = {
            10000:'upToTenThousand', 100000:'upToHundredThousand', \
            1000000: 'upToOneMillion', 10000000: 'upToTenMillion', \
            100000000: 'moreThanTenMillion' \
        }
        self.featureExtractor = FeatureExtractor()

        self.parseTrainData(path)

    ############################ PARSING FUNCTIONS ############################

    # Function: categorizeByNumFollowers
    # ----------------------------------
    # takes a profile name and its number of followers,
    # and bookkeeps the group to which it belongs.
    def categorizeByPopularity(self, ID, nFollowers):
        n = max(nFollowers, 10000)

        if n > 10000:
            n = min(100000000, int(10 ** (math.ceil(math.log10(n)))))

        popularity = self.followerPopularityCategories[n]

        self.accountsByPopularity[popularity].add(ID)
        return popularity


    def recordWords(self, words, num_likes, num_reactions):
        for i in range(0, len(words) - 2):
            a = self.stemmer.stem(words[i])
            b = self.stemmer.stem(words[i+1])
            c = self.stemmer.stem(words[i+2])

            self.wordsToLikes[a][b][c] += 0.001 * num_likes
            self.wordsToReactions[a][b][c] += 0.001 * num_reactions
        #for word in words:
        #    word = self.stemmer.stem(word)
        #    self.wordsToLikes[word] += 0.001 * num_likes
        #    self.wordsToReactions[word] += 0.001 * num_reactions

    def recordFeatures(self, post):
        featureVector = self.featureExtractor.extractFeatures(post)
        self.feature_vectors[post['id']] = featureVector

    # Function: parseProfile
    # ----------------------------------
    # reads a profile.txt file and parses the contents,
    # then organizes the profile contents for internal use
    def parseProfile(self, path, saveData):
        profile = None

        try:
            with open(path) as data_file:
                profile = json.load(data_file)
        except Exception:
            err = 'error opening %s' % path
            raise Exception(err)

        ID = profile['id']

        if saveData:
            #profiles contain name, id, fan_count, category, and about
            self.Names[ID] = profile['name']
            self.Profiles[ID] = profile
            self.categorizeByPopularity(ID, profile['fan_count'])

        return profile


    def parsePostsCSV(self, path, profile, saveData):
        try:
            with open(path, 'rb') as csvFile:
                reader = csv.DictReader(csvFile)
                lastPost = None
                for post in reader:
                    if post['status_type'] == 'photo' or post['status_type'] == 'video':continue

                    for num_reaction in self.num_reaction_keys:
                        post[num_reaction] = int(post[num_reaction])

                    post['num_comments'] = int(post['num_comments'])

                    post['message'] = post['status_message'] + '|' + post['link_name']
                    del post['status_message']

                    words = post['message'].split()
                    if len(words) < 3:
                        continue

                    post['id'] = post['status_id']
                    del post['status_id']

                    post['created_time'] = post['status_published']
                    del post['status_published']

                    post['type'] = post['status_type']
                    del post['status_type']

                    created = int(dp.parse(post['created_time']).strftime('%s'))

                    if lastPost != None:
                        lastPostCreated = int(dp.parse(lastPost['created_time']).strftime('%s'))
                        lastPost['days_since_last_post'] = (lastPostCreated - created) / SECONDS_IN_DAY

                    post['elapsed_days'] = (time.time() - created) / SECONDS_IN_DAY

                    results = {}
                    num_reactions = 0

                    for reaction in self.possible_reactions:
                        k = "num_" + reaction + 's'
                        v = 0

                        if k in post:
                            v = post[k]

                        results[k] = v
                        num_reactions += int(v)


                    self.recordWords(post['message'].split(), post['num_likes'], num_reactions)

                    results['num_reactions'] = num_reactions# - post['num_likes']

                    results['num_likes'] = post['num_likes']

                    self.post_results[post['id']] = results

                    strongestEmotionKey = None
                    maxEmotionCount = 0


                    for num_emotion_key in self.num_reaction_keys:
                        count = post[num_emotion_key]

                        if count > maxEmotionCount:
                            strongestEmotionKey = num_emotion_key
                            maxEmotionCount = count

                    if profile != None:
                        post['poster'] = profile['id']
                        post['fan_count'] = profile['fan_count']

                    self.post_results[post['id']] = results

                    self.Posts[post['id']] = post
                    self.postCount += 1

                    if self.postCount % 20000 == 0:
                        print "parsed %s posts so far..." % self.postCount
                    lastPost = post
        except Exception:
            err = 'error opening %s' % path
            raise Exception(err)

    # Function: parsePost
    # ----------------------------------
    # parses all data in the /posts directory
    def parseTrainData(self, path):
        #traverse through all subdirectories
        for (name, children, files) in os.walk(path):
            if '/' not in name: continue
            if not os.path.isfile(name + '/profile.txt'): continue
            profile = self.parseProfile(name + '/profile.txt', True)
            for File in files:
                if File != 'profile.txt' and File[0] != '.':
                    self.parsePostsCSV(name + '/' + File, profile, True)

                    #post = self.parsePost(name + '/' + File, profile, True)
                    #self.recordFeatures(post)

        print "Parsed %s posts total" % self.postCount

        self.featureExtractor.giveWordsToLikes(self.wordsToLikes)
        self.featureExtractor.giveWordsToReactions(self.wordsToReactions)
        print "Processing posts... this may take a while..."
        processed = 0
        for postID, post in self.Posts.iteritems():
            self.recordFeatures(post)
            processed += 1
            if processed % 20000 == 0:
                print "Processed %s posts so far..." % processed
        print "Processed %s posts total" % processed

    ########################## END PARSING FUNCTIONS ##########################

    # Function: getAccoutsByPopularity
    # ----------------------------------
    # returns a list of account IDs that have a certain
    # range of followers defined by 'popularity'

    def getAccoutsByPopularity(self, popularity):
        if not popularity in self.accountsByPopularity:
            err = 'invalid popularity category: %s' % popularity
            raise Exception (err)
        return self.accountsByPopularity[popularity]


    # Function: getFeatureResultPairs
    # ----------------------------------
    # returns a mapping of ALL posts' feature vectors
    # to the resulting # of likes/reactions
    def getFeatureResultPairs(self):
        featureResults = []
        for post_id, vector in self.feature_vectors.iteritems():
            featureResults.append((vector, self.post_results[post_id], post_id))
        return featureResults




    # Function: getFeatureResultPair
    # ----------------------------------
    # returns a mapping of a particular posts' feature vector
    # to its resulting # of likes/reactions
    def getFeatureResultPair(self, post_id):
        vector = self.feature_vectors[post_id]
        results = self.post_results[post_id]
        return (vector, results)

    def getPostResults(self, post_id):
        return self.post_results[post_id]
