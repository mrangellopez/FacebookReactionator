import json
import math
import collections
import os
from FeatureExtractor import FeatureExtractor


# Class: DataParser
# --------------------
# Parses data to create feature vectors for every post
# Defines ways to retrieve these vectors
class DataParser:

    def __init__(self, path):

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
        # map between account IDs and their Post objects (JSON)
        self.Names = collections.defaultdict(lambda: '')
        self.Profiles = collections.defaultdict(lambda: '')
        self.Posts = collections.defaultdict(lambda: [])


        # internal fields, shouldn't need to be called by other classes
        self.relevant_fields = ["id", "created_time", "type", \
            "status_type","object_id", "name", "message" ]
        self.possible_reactions = ["love", "wow", "sad", "haha", 'angry']

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

    # Function: parsePost
    # ----------------------------------
    # reads a profile-id_post-id.txt file and parses the contents,
    # then organizes the posts contents for internal use
    def parsePost(self, path, profile, saveData):
        try:
            with open(path) as data_file:
                post = json.load(data_file)
        except Exception:
            err = 'error opening %s' % path
            raise Exception(err)

        results = {}

        newPost = {field: post[field] for field in self.relevant_fields if field in post}

        newPost["num_like"] = post["likes"]["summary"]["total_count"]
        results['num_like'] = newPost["num_like"]

        total_reactions = 0
        for reaction in self.possible_reactions:
            k = "num_" + reaction
            v = 0
            if "reactions_" + reaction in post:
                v = post["reactions_" + reaction]["summary"]["total_count"]
            newPost[k] = v
            results[k] = v
            total_reactions += v

        results['total_reactions'] = total_reactions
        if profile != None:
            newPost['poster'] = profile['id']
            newPost['fan_count'] = profile['fan_count']

        if saveData:
            self.Posts[profile['id']].append(newPost)
            self.post_results[newPost['id']] = results
        return newPost

    # Function: parsePost
    # ----------------------------------
    # parses all data in the /posts directory
    def parseTrainData(self, path):
        #traverse through all subdirectories
        for (name, children, files) in os.walk(path):
            if '/' not in name: continue
            profile = self.parseProfile(name + '/profile.txt', True)
            for File in files:
                if File != 'profile.txt' and File[0] != '.':
                    post = self.parsePost(name + '/' + File, profile, True)
                    self.recordFeatures(post)

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
            featureResults.append((vector, self.post_results[post_id]))
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
