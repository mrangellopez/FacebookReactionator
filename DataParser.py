import json
import math
import collections


# Class: DataParser
# --------------------
# Parses data to create feature vectors for every post
# Defines ways to retrieve these vectors
class DataParser:

    def __init__(self):

        # map account IDs to a map of (POST_ID, feature_vector) key-value pairs
        # e.g. data['ACCOUNT_ID']['POST_ID'] gives a feature vector for a post
        self.feature_vectors = collections.defaultdict(lambda: {})

        # map between categoryKey (maxNumberOfFollowers) to a set of
        # names associated with that group
        self.accountsByPopularity = collections.defaultdict(lambda: set([]))

        # map between account IDs and their names
        # map between account IDs and their profile objects (JSON)
        self.Names = collections.defaultdict(lambda: '')
        self.Profiles = collections.defaultdict(lambda: '')





    followerPopularityCategories = {
        10000:'upToTenThousand', 100000:'upToHundredThousand', \
        1000000: 'upToOneMillion', 10000000: 'upToTenMillion',
        100000000: 'moreThanTenMillion' \
    }

    # Function: categorizeByNumFollowers
    # ----------------------------------
    # takes a profile name and its number of followers,
    # and bookkeeps the group to which it belongs.
    def categorizeByPopularity(self, ID, nFollowers):
        n = max(nFollowers, 10000)

        if n > 10000:
            n = min(100000000, int(10 ** (math.ceil(math.log10(n)))))

        popularity = followerPopularityCategories[n]

        self.accountsByPopularity[popularity].add(ID)
        return popularity

    # Function: getAccoutsByPopularity
    # ----------------------------------
    # returns a list of account IDs that have a certain
    # range of followers defined by 'popularity'

    def getAccoutsByPopularity(self, popularity):
        if not popularity in self.accountsByPopularity:
            err = 'invalid popularity category: %s' % popularity
            raise Exception (err)
        return self.accountsByPopularity[popularity]


    # Function: parseProfile
    # ----------------------------------
    # reads a profile.json file and parses the contents,
    # then organizes the profile contents for internal use
    # TODO: implement with appropriate file format handling
    def parseProfile(self, path):
        profile = None

        try:
            with open(path) as data_file:
                profile = json.load(data_file)
        except Exception:
            err = 'error opening %s' % path
            raise Exception(err)

        ID = profile.id

        self.Names[ID] = profile.name
        self.Profiles[ID] = profile
        self.categorizeByPopularity(ID, profile.followers)

        return profile

    # TODO: implement with appropriate file format handling
    def parsePost(self, path):

        data = None

        try:
            with open(path) as data_file:
                data = json.load(data_file)
        except Exception:
            print 'error opening %s' % path
            return None

        return data

    # parses all data in the /data directory, or otherwise specified
    def parseData(self, path='/data'):
        #traverse through all subdirectories
        for (name, children, files) in os.walk(path):
            subDir = path + '/' + name

            for File in files:
                if File == 'profile.txt':
                    self.parseProfile(subDir + '/' + File)
                else:
                    self.parsePost(subDir + '/' + File)
