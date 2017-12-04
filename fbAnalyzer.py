from NaiveBayes import NaiveBayes
from DataParser import DataParser
import random, util, copy, math
from FeatureExtractor import FeatureExtractor
import matplotlib.pyplot as plt

featureExtractor = FeatureExtractor()



# Function: generateWeights
# -------------------------
# generates weights given a set of (feature vectors, result) pairs
def generateWeights(trainExamples, numIters, eta):
    weights = {}
    randomIndexes = [i for i in range(len(trainExamples))]

    random.shuffle(randomIndexes)
    randomIndexes = randomIndexes[:int(0.1 * len(randomIndexes))]

    #eta_original = eta
    #num_updates = 1
    for i in range(numIters):
        random.shuffle(randomIndexes)
        #num_updates += 1
        for j in randomIndexes:
            (features, y) = trainExamples[j]
            #eta = eta_original / num_updates

            #Loss_squared_gradient = 2 (w * phi(x) - y) * phi(x)
            # ==> 2 (prediction - y) * phi(x)

            # w = w - eta * gradient
            # w = w - (2 * eta * (prediction - y)) * phi(x)
            util.increment(weights, y * eta if util.dotProduct(weights, features) * y < 1 else 0 , features)

    return weights


# Functions: getFeaturesTo[Reaction, ProportionReaction, ProportionEmotional]
# ---------------------------------------------------------------------------
# From a (featureVector, set of all reactions) dict, transform the dict
# to one like (featureVector, result) where result is either an absolute number
# of reactions (num_likess, num_angrys, etc.), or a proportion of that reaction
# - (numAngry / (total_reactions + total_num_likess) ) - or a proportion of
# emotional reactions for that post (i.e. of all likes and reactions, how many
# were some emotional reaction such as a wow or a sad or an angry?)
def getFeaturesToReaction(featuresToResultsAll, reactionType):
    if not reactionType in ["num_likes", "num_reactions"]:
        raise Exception(reactionType + ' not recognized')
    return [(vec, results[reactionType]) \
        for vec, results, post_id in featuresToResultsAll]

# Functions: getAbsolutesWeights:
# ---------------------------------------------------------------------------
# returns a dict where the keys are a reaction ('like', 'love', etc.), and
# the values are weight vectors that were trained on examples whose ultimate goal
# was to predict the total number (or proportion relative to all reactions) of that reaction

def getAbsolutesWeights(featuresToResultsAll):

    likeExamples = getFeaturesToReaction(featuresToResultsAll, 'num_likes')
    allExamples = getFeaturesToReaction(featuresToResultsAll, 'num_reactions')
    numIters = 5000
    eta = 0.008

    print "Getting 'Like' weight vector... This could take a while..."
    weightsLike = generateWeights(likeExamples, numIters, eta)

    print "Getting general weight vector... This could take a while..."
    weights = generateWeights(allExamples, numIters, eta)
    #weightsLike = weights

    print "likes vector:"
    for k, v in weightsLike.iteritems():
        print "\t%s: %s" % (k, v)

    print "reactions vector:"
    for k, v in weights.iteritems():
        print "\t%s: %s" % (k, v)

    return {'like': weightsLike, 'general': weights}



def predict(weights, fv, featureExtractor):

    #fv = featureExtractor.extractFeatures(post)

    #for k, v in weights['like'].iteritems():
        #print "%s: %s" % (k, v)

    Likes = util.dotProduct(fv, weights['like'])
    Reactions = util.dotProduct(fv, weights['general'])

    results = {'like': Likes, 'general': Reactions}

    return results


def printResults(guess, post):

    numReactions = 0
    if 'num_likes' in post:
        numLikes = post['num_likes']
        numReactions += numLikes
        print "\tGuessed %s likes, real total was %s"  % (guess['like'], numLikes)

    for num_key in ['num_loves', 'num_wows', 'num_hahas', 'num_sads', 'num_angrys']:
        if num_key in post:
            numReactions += post[num_key]

    print "\tGuessed %s reactions, real total was %s" % (guess['general'], numReactions)


def getAverageAbsoluteError(dp, numTrials):
    features = dp.getFeatureResultPairs()
    testProfile = dp.parseProfile('tests/testProfile/profile.txt', False)
    testPost = dp.parsePost('tests/testProfile/10376464573_10156028999814574.txt', testProfile, False)
    guess_sum = {}
    for i in range(numTrials):
        weights = getAbsolutesWeights(features)
        iter_guess = predict(weights, testPost, dp.featureExtractor)
        if i == 0:
            guess_sum = iter_guess
        else:
            guess_sum = {k: v + iter_guess[k] for k,v in guess_sum.iteritems()}
        print guess_sum
    guess_sum = {k: v/numTrials for k,v in guess_sum.iteritems()}
    return guess_sum

def main():
    print "parsing data... this could take a while..."
    dp = DataParser('posts_news')
    featuresToResultsAll =  dp.getFeatureResultPairs()


    # calculate weights
    print "calculating weight vectors..."
    absolutesWeights = getAbsolutesWeights(featuresToResultsAll)

    # get example post to test
    testProfile = dp.parseProfile('tests/testProfile/profile.txt', False)

    for i in range(15):

        testPost, results, test_id = random.choice(featuresToResultsAll)
        # calculate results

        guess = predict(absolutesWeights, testPost, dp.featureExtractor)
        print "testPost %s:" % test_id

        printResults(guess, results)
        print "\n"

if __name__ == '__main__':
   main()
