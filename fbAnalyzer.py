from NaiveBayes import NaiveBayes
from DataParser import DataParser
import random, util
from FeatureExtractor import FeatureExtractor

featureExtractor = FeatureExtractor()


# Function: generateWeights
# -------------------------
# generates weights given a set of (feature vectors, result) pairs
def generateWeights(trainExamples, numIters, eta):
    weights = {}
    randomIndexes = [i for i in range(len(trainExamples))]
    for i in range(numIters):
        random.shuffle(randomIndexes)
        for j in randomIndexes:
            (features, y) = trainExamples[j]
            util.increment(weights, y * eta if util.dotProduct(weights, features) * y < 1 else 0 , features)
    return weights



# Functions: getFeaturesTo[Reaction, ProportionReaction, ProportionEmotional]
# ---------------------------------------------------------------------------
# From a (featureVector, set of all reactions) dict, transform the dict
# to one like (featureVector, result) where result is either an absolute number
# of reactions (num_likes, num_angry, etc.), or a proportion of that reaction
# - (numAngry / (total_reactions + total_num_likes) ) - or a proportion of
# emotional reactions for that post (i.e. of all likes and reactions, how many
# were some emotional reaction such as a wow or a sad or an angry?)
def getFeaturesToReaction(featuresToResultsAll, reactionType):
    if not reactionType in ["like", "love", "wow", "sad", "haha", 'angry']:
        raise Exception(reactionType + ' not recognized')
    return [(vec, results['num_' + reactionType]) \
        for vec, results in featuresToResultsAll]

def getFeaturesToProportionReaction(featuresToResultsAll, reactionType):
    if not reactionType in ["like", "love", "wow", "sad", "haha", 'angry']:
        raise Exception(reactionType + ' not recognized')

    return [(vec, results['num_' + reactionType] * 1.0/ \
        (results['total_reactions'] + results['num_like'])) \
        for vec, results in featuresToResultsAll]

def getFeaturesToProportionEmotional(featuresToResultsAll):
    return [(vec, results['total_reactions'] * 1.0/ \
        (results['total_reactions'] + results['num_like'])) \
        for vec, results in featuresToResultsAll]

# Functions: get[Proportions/Absolutes]Weights:
# ---------------------------------------------------------------------------
# returns a dict where the keys are a reaction ('like', 'love', etc.), and
# the values are weight vectors that were trained on examples whose ultimate goal
# was to predict the total number (or proportion relative to all reactions) of that reaction
def getProportionsWeights(featuresToResultsAll):
    proportionLikeExamples = getFeaturesToProportionReaction(featuresToResultsAll, 'like')
    proportionLoveExamples = getFeaturesToProportionReaction(featuresToResultsAll, 'love')
    proportionHahaExamples = getFeaturesToProportionReaction(featuresToResultsAll, 'haha')
    proportionWowExamples = getFeaturesToProportionReaction(featuresToResultsAll, 'wow')
    proportionSadExamples = getFeaturesToProportionReaction(featuresToResultsAll, 'sad')
    proportionAngryExamples = getFeaturesToProportionReaction(featuresToResultsAll, 'angry')
    proportionEmotionalExamples = getFeaturesToProportionEmotional(featuresToResultsAll)

    weightsLike = generateWeights(proportionLikeExamples, 5000, 0.1)
    weightsLove = generateWeights(proportionLoveExamples, 5000, 0.1)
    weightsHaha = generateWeights(proportionHahaExamples, 5000, 0.1)
    weightsWow = generateWeights(proportionWowExamples, 5000, 0.1)
    weightsSad = generateWeights(proportionSadExamples, 5000, 0.1)
    weightsAngry = generateWeights(proportionAngryExamples, 5000, 0.1)
    weightsEmotional = generateWeights(proportionEmotionalExamples, 5000, 0.1)

    return {'like': weightsLike, 'love': weightsLove, 'haha': weightsHaha, \
    'wow': weightsWow, 'sad': weightsSad, 'angry': weightsAngry, 'emotional': weightsEmotional}

def getAbsolutesWeights(featuresToResultsAll):
    absoluteLikesExamples = getFeaturesToReaction(featuresToResultsAll, 'like')
    absoluteLovesExamples = getFeaturesToReaction(featuresToResultsAll, 'love')
    absoluteHahasExamples = getFeaturesToReaction(featuresToResultsAll, 'haha')
    absoluteWowsExamples = getFeaturesToReaction(featuresToResultsAll, 'wow')
    absoluteSadsExamples = getFeaturesToReaction(featuresToResultsAll, 'sad')
    absoluteAngrysExamples = getFeaturesToReaction(featuresToResultsAll, 'angry')

    weightsLike = generateWeights(absoluteLikesExamples, 5000, 0.1)
    weightsLove = generateWeights(absoluteLovesExamples, 5000, 0.1)
    weightsHaha = generateWeights(absoluteHahasExamples, 5000, 0.1)
    weightsWow = generateWeights(absoluteWowsExamples, 5000, 0.1)
    weightsSad = generateWeights(absoluteSadsExamples, 5000, 0.1)
    weightsAngry = generateWeights(absoluteAngrysExamples, 5000, 0.1)

    return {'like': weightsLike, 'love': weightsLove, 'haha': weightsHaha, \
    'wow': weightsWow, 'sad': weightsSad, 'angry': weightsAngry}



def predict(weights, post, proportional):
    fv = featureExtractor.extractFeatures(post)

    Likes = util.dotProduct(fv, weights['like'])
    Loves = util.dotProduct(fv, weights['love'])
    Hahas = util.dotProduct(fv, weights['haha'])
    Wows = util.dotProduct(fv, weights['wow'])
    Sads = util.dotProduct(fv, weights['sad'])
    Angrys = util.dotProduct(fv, weights['angry'])
    Emotionals = None

    if proportional:
        Emotionals = util.dotProduct(fv, weights['emotional'])

    results = {'like': Likes, 'love': Loves, 'haha': Hahas, \
        'wow': Wows, 'sad': Sads, 'angry': Angrys}

    if proportional:
        results['emotional'] = Emotionals
    return results

def printResults(guess, post):


    if 'num_like' in post:
        nLikes = post['num_like']
        print "\tGuessed %s likes, real total was %s"  % (guess['like'], nLikes)

    if "num_love" in post:
        nLoves = post['num_love']
        print "\tGuessed %s loves, real total was %s" % (guess['love'], nLoves)

    if "num_wow" in post:
        nWows = post['num_wow']
        print "\tGuessed %s wows, real total was %s" % (guess['wow'], nWows)

    if "num_haha" in post:
        nHahas = post['num_haha']
        print "\tGuessed %s hahas, real total was %s" % (guess['haha'], nHahas)

    if "num_sad" in post:
        nSads = post['num_sad']
        print "\tGuessed %s sads, real total was %s" % (guess['sad'], nSads)

    if "num_angry" in post:
        nAngrys = post['num_angry']
        print "\tGuessed %s angrys, real total was %s" % (guess['angry'], nAngrys)


def main():

    print "parsing data..."
    dp = DataParser('posts')
    featuresToResultsAll =  dp.getFeatureResultPairs()

    # calculate weights
    print "calculating weights for proportional queries..."
    proportionsWeights = getProportionsWeights(featuresToResultsAll)

    print "calculating weights for absolute queries..."
    absolutesWeights = getAbsolutesWeights(featuresToResultsAll)

    # get example post to test
    print "testing on test profile and test post"
    testProfile = dp.parseProfile('tests/testProfile/profile.txt', False)
    testPost = dp.parsePost('tests/testProfile/10376464573_10156028999814574.txt', testProfile, False)

    # calculate results
    proportionGuess = predict(proportionsWeights, testPost, True)

    #absoluteGuess = predict(absolutesWeights, testPost, False)

    # print results
    printResults(proportionGuess, testPost)
    #printResults(absoluteGuess, post)




if __name__ == '__main__':
   main()
