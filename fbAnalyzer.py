from NaiveBayes import NaiveBayes
from DataParser import DataParser
import random, util, copy, math
from FeatureExtractor import FeatureExtractor
import matplotlib.pyplot as plt
import numpy as np

featureExtractor = FeatureExtractor()


keys = ['fan_count_log',\
    'questions', 'exclamation',\
    'pos', 'neg', 'neu', \
    #'compound',\
    #'original_message_len_sqrt',\
    'unigrams_score', \
    'bigrams_score', \
    'trigrams_score', \
    'reading_ease_log', \
    'smog_index_inverse', \
    #'neg_and_reading_ease',\
    'neu_and_smog_inverse',\
    #'not_neg_and_smog_inverse',\
    #'not_pos_and_reading_ease',\
    #'num_unique_stems_log_inverse', \
    'elapsed_hours_log',\
    # 'hours_since_last_post', 'early_morning',\
    'morning','midday', \
    #'afternoon',\
    'evening', 'night', 'late_night_or_early_early_morning']
# Function: generateWeights
# -------------------------
# generates weights given a set of (feature vectors, result) pairs
def generateWeightsAndTestData(trainExamples, numIters, eta):
    weights = [0 for i in range(len(trainExamples[0][0]))]
    weights = np.array(weights)
    randomIndexes = [i for i in range(len(trainExamples))]

    random.shuffle(randomIndexes)
    dividerIndex = int(0.9 * len(randomIndexes))
    randomIndexes = randomIndexes[:dividerIndex]
    testData = trainExamples[dividerIndex:]

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
            f = (eta * 2 * (np.dot(weights, features) - y)) * features
            weights = np.subtract(weights, f)

    return (weights, testData)


# Functions: getFeaturesTo[Reaction, ProportionReaction, ProportionEmotional]
# ---------------------------------------------------------------------------
# From a (featureVector, set of all reactions) dict, transform the dict
# to one like (featureVector, result) where result is either an absolute number
# of reactions (num_likess, num_angrys, etc.), or a proportion of that reaction
# - (numAngry / (total_reactions + total_num_likess) ) - or a proportion of
# emotional reactions for that post (i.e. of all likes and reactions, how many
# were some emotional reaction such as a wow or a sad or an angry?)
def getFeaturesToReaction(featuresToResultsAll, reactionType):
    if not reactionType in ["num_reactions"]:
        raise Exception(reactionType + ' not recognized')
    return [(vec, results[reactionType]) \
        for vec, results, post_id in featuresToResultsAll]

# Functions: getWeightsAndTestData:
# ---------------------------------------------------------------------------
# returns a dict where the keys are a reaction ('like', 'love', etc.), and
# the values are weight vectors that were trained on examples whose ultimate goal
# was to predict the total number (or proportion relative to all reactions) of that reaction

def getWeightsAndTestData(featuresToResultsAll):
    allExamples = getFeaturesToReaction(featuresToResultsAll, 'num_reactions')
    numIters = 10000
    eta = 0.00008

    print "Getting weight vector... This could take a while..."
    weights, testData = generateWeightsAndTestData(allExamples, numIters, eta * 0.1)

    #print "Printing weights:"
    #for i in range(len(weights)):
    #    print '\t%s: %s' % (keys[i], weights[i])

    return (weights, testData)



def predict(weights, fv):
    guess = int(np.dot(fv, weights))
    return guess if guess > 0 else 0


def printResults(prediction, target):
    print "\tPrediction: %s, target: %s" % (prediction, target)


def main():
    print "parsing data... this could take a while..."
    dp = DataParser('posts_news')
    featuresToResultsAll =  dp.getFeatureResultPairs()


    # calculate weights
    weights, testData = getWeightsAndTestData(featuresToResultsAll)

    i = 0

    totalError = 0.0
    print "\nPrinting Example Results:"
    for fv, target in testData:
        i += 1
        prediction = predict(weights, fv)

        if i % 20 == 0:
            printResults(prediction, target)


        #error = abs(len(str(prediction)) - len(str(target)))
        error = abs(prediction - target)
        totalError += error

    totalError /= i
    print "total Error as average difference between prediction and target: %s" % totalError

    dp.printMostProvocativeWords(50)
    dp.printMostProvocativeBigrams(50)
    dp.printMostProvocativeTrigrams(50)

if __name__ == '__main__':
   main()
