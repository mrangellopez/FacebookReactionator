import sys
import getopt
import os
import math
import operator
import collections
import time

class NaiveBayes:
  class TrainSplit:
    """Represents a set of training/testing data. self.train is a list of Examples, as is self.test.
    """
    def __init__(self):
      self.train = []
      self.test = []

  class Example:
    """Represents a document with a label. klass is 'pos' or 'neg' by convention.
       words is a list of strings.
    """
    def __init__(self):
      self.klass = ''
      self.words = []


  def __init__(self):
    """NaiveBayes initialization"""
    self.FILTER_STOP_WORDS = False
    self.BOOLEAN_NB = False
    self.BEST_MODEL = False
    self.stopList = set(self.readFile('sentiment/data/english.stop'))
    self.customStopList = self.customStopList = ['a', 'the', 'of', 'to', 'in', 'that', 'is', 'and', 'it', 'with', 'for', 'as', 'this', 'on', 'an', 'by', 'are', 'at']
    self.wordClassCount = collections.defaultdict(lambda: collections.defaultdict(lambda: 0))
    self.nPos = 0
    self.nNeg = 0
    self.nUnitsInPos = 0
    self.nUnitsInNeg = 0
    self.alpha = 1
    self.numFolds = 10
  #############################################################################
  def classify(self, words):
    V = 0
    if self.FILTER_STOP_WORDS:
        words =  self.filterStopWords(words)
    elif self.BOOLEAN_NB:
        words = self.filterRedundancies(words)
    else:
        words = self.filterRedundancies(words)
        words = self.filterStopWords(words)
        #fix

    nPosAndNeg = self.nPos + self.nNeg
    posScore = 0
    negScore = 0

    if self.nPos > 0:
        posScore = 1.0 * math.log(self.nPos)
    if self.nNeg > 0:
        negScore = 1.0 * math.log(self.nNeg)
    if nPosAndNeg > 0:
        posScore -= math.log(nPosAndNeg)
        negScore -= math.log(nPosAndNeg)

    alpha = self.alpha
    V_Alpha = 1.0
    V_Alpha = V_Alpha * self.V
    V_Alpha = V_Alpha * alpha
    for word in words:
        nk_pos = 0
        nk_neg = 0
        nk_pos = self.wordClassCount[word]['pos']
        nk_neg = self.wordClassCount[word]['neg']
        posScore += math.log(nk_pos + alpha)
        posScore -= math.log(self.nUnitsInPos + V_Alpha)
        negScore += math.log(nk_neg + alpha)
        negScore -= math.log(self.nUnitsInNeg + V_Alpha)

    # Be optimistic :-)
    if posScore >= negScore:
        return 'pos'
    return 'neg'


  def addExample(self, klass, words):
    nUnitsInEx = 0
    if self.FILTER_STOP_WORDS:
        words = self.filterStopWords(words)
    elif self.BOOLEAN_NB:
        words = self.filterRedundancies(words)
    elif self.BEST_MODEL:
        self.stopList = self.customStopList
        self.alpha = 4.6
        words = self.filterStopWords(words)
        words = self.filterRedundancies(words)

    for word in words:
        self.wordClassCount[word][klass] += 1
    nUnitsInEx += len(words)

    if klass == 'pos':
        self.nPos += 1
        self.nUnitsInPos += nUnitsInEx
    elif klass == 'neg':
        self.nNeg += 1
        self.nUnitsInNeg += nUnitsInEx

    self.V = len(self.wordClassCount)
  #############################################################################


  def readFile(self, fileName):
    """
     * Code for reading a file.  you probably don't want to modify anything here,
     * unless you don't like the way we segment files.
    """
    contents = []
    f = open(fileName)
    for line in f:
      contents.append(line)
    f.close()
    result = self.segmentWords('\n'.join(contents))
    return result


  def segmentWords(self, s):
    """
     * Splits lines on whitespace for file reading
    """
    return s.split()


  def trainSplit(self, trainDir):
    """Takes in a trainDir, returns one TrainSplit with train set."""
    split = self.TrainSplit()
    posTrainFileNames = os.listdir('%s/pos/' % trainDir)
    negTrainFileNames = os.listdir('%s/neg/' % trainDir)
    for fileName in posTrainFileNames:
      example = self.Example()
      example.words = self.readFile('%s/pos/%s' % (trainDir, fileName))
      example.klass = 'pos'
      split.train.append(example)
    for fileName in negTrainFileNames:
      example = self.Example()
      example.words = self.readFile('%s/neg/%s' % (trainDir, fileName))
      example.klass = 'neg'
      split.train.append(example)
    return split

  def train(self, split):
    for example in split.train:
        words = example.words
        if self.FILTER_STOP_WORDS:
            words =  self.filterStopWords(words)
        self.addExample(example.klass, words)


  def crossValidationSplits(self, trainDir):
    """Returns a lsit of TrainSplits corresponding to the cross validation splits."""
    splits = []
    posTrainFileNames = os.listdir('%s/pos/' % trainDir)
    negTrainFileNames = os.listdir('%s/neg/' % trainDir)
    #for fileName in trainFileNames:
    for fold in range(0, self.numFolds):
      split = self.TrainSplit()
      for fileName in posTrainFileNames:
        example = self.Example()
        example.words = self.readFile('%s/pos/%s' % (trainDir, fileName))
        example.klass = 'pos'
        if fileName[2] == str(fold):
          split.test.append(example)
        else:
          split.train.append(example)
      for fileName in negTrainFileNames:
        example = self.Example()
        example.words = self.readFile('%s/neg/%s' % (trainDir, fileName))
        example.klass = 'neg'
        if fileName[2] == str(fold):
          split.test.append(example)
        else:
          split.train.append(example)
      yield split

  def test(self, split):
    """Returns a list of labels for split.test."""
    labels = []
    for example in split.test:
      words = example.words
      if self.FILTER_STOP_WORDS:
        words =  self.filterStopWords(words)
      guess = self.classify(words)
      labels.append(guess)
    return labels

  def buildSplits(self, args):
    """Builds the splits for training/testing"""
    trainData = []
    testData = []
    splits = []
    trainDir = args[0]
    if len(args) == 1:
      print '[INFO]\tPerforming %d-fold cross-validation on data set:\t%s' % (self.numFolds, trainDir)

      posTrainFileNames = os.listdir('%s/pos/' % trainDir)
      negTrainFileNames = os.listdir('%s/neg/' % trainDir)
      for fold in range(0, self.numFolds):
        split = self.TrainSplit()
        for fileName in posTrainFileNames:
          example = self.Example()
          example.words = self.readFile('%s/pos/%s' % (trainDir, fileName))
          example.klass = 'pos'
          if fileName[2] == str(fold):
            split.test.append(example)
          else:
            split.train.append(example)
        for fileName in negTrainFileNames:
          example = self.Example()
          example.words = self.readFile('%s/neg/%s' % (trainDir, fileName))
          example.klass = 'neg'
          if fileName[2] == str(fold):
            split.test.append(example)
          else:
            split.train.append(example)
        splits.append(split)
    elif len(args) == 2:
      split = self.TrainSplit()
      testDir = args[1]
      print '[INFO]\tTraining on data set:\t%s testing on data set:\t%s' % (trainDir, testDir)
      posTrainFileNames = os.listdir('%s/pos/' % trainDir)
      negTrainFileNames = os.listdir('%s/neg/' % trainDir)
      for fileName in posTrainFileNames:
        example = self.Example()
        example.words = self.readFile('%s/pos/%s' % (trainDir, fileName))
        example.klass = 'pos'
        split.train.append(example)
      for fileName in negTrainFileNames:
        example = self.Example()
        example.words = self.readFile('%s/neg/%s' % (trainDir, fileName))
        example.klass = 'neg'
        split.train.append(example)

      posTestFileNames = os.listdir('%s/pos/' % testDir)
      negTestFileNames = os.listdir('%s/neg/' % testDir)
      for fileName in posTestFileNames:
        example = self.Example()
        example.words = self.readFile('%s/pos/%s' % (testDir, fileName))
        example.klass = 'pos'
        split.test.append(example)
      for fileName in negTestFileNames:
        example = self.Example()
        example.words = self.readFile('%s/neg/%s' % (testDir, fileName))
        example.klass = 'neg'
        split.test.append(example)
      splits.append(split)
    return splits

  def filterStopWords(self, words):
    """Filters stop words."""
    filtered = []
    for word in words:
      if not word in self.stopList and word.strip() != '':
        filtered.append(word)
    return filtered

  def getBigrams(self, words):
    bigrams = []
    for i in xrange(1, len(words)):
        if word[i-1] in self.stopList:
            continue
        bigram = (words[i-1], words[i])
        bigrams.append(bigram)
    return bigrams

  def filterRedundancies(self, words):
    """Filters redundant words."""
    filtered = set([])
    for word in words:
      if not word in filtered and word.strip() != '':
        filtered.add(word)
    return filtered

def test10Fold(args, FILTER_STOP_WORDS, BOOLEAN_NB, BEST_MODEL):
  nb = NaiveBayes()
  splits = nb.buildSplits(args)
  avgAccuracy = 0.0
  fold = 0
  for split in splits:
    classifier = NaiveBayes()
    classifier.FILTER_STOP_WORDS = FILTER_STOP_WORDS
    classifier.BOOLEAN_NB = BOOLEAN_NB
    classifier.BEST_MODEL = BEST_MODEL
    accuracy = 0.0
    for example in split.train:
      words = example.words
      classifier.addExample(example.klass, words)

    for example in split.test:
      words = example.words
      guess = classifier.classify(words)
      if example.klass == guess:
        accuracy += 1.0

    accuracy = accuracy / len(split.test)
    avgAccuracy += accuracy
    print '[INFO]\tFold %d Accuracy: %f' % (fold, accuracy)
    fold += 1
  avgAccuracy = avgAccuracy / fold
  print '[INFO]\tAccuracy: %f' % avgAccuracy


def classifyFile(FILTER_STOP_WORDS, BOOLEAN_NB, BEST_MODEL, trainDir, testFilePath):
  classifier = NaiveBayes()
  classifier.FILTER_STOP_WORDS = FILTER_STOP_WORDS
  classifier.BOOLEAN_NB = BOOLEAN_NB
  classifier.BEST_MODEL = BEST_MODEL
  trainSplit = classifier.trainSplit(trainDir)
  classifier.train(trainSplit)
  testFile = classifier.readFile(testFilePath)
  print classifier.classify(testFile)

def main():
  start_time = time.time()
  FILTER_STOP_WORDS = False
  BOOLEAN_NB = False
  BEST_MODEL = False
  (options, args) = getopt.getopt(sys.argv[1:], 'fbm')
  if ('-f','') in options:
    FILTER_STOP_WORDS = True
  elif ('-b','') in options:
    BOOLEAN_NB = True
  elif ('-m','') in options:
    BEST_MODEL = True

  if len(args) == 2 and os.path.isfile(args[1]):
    classifyFile(FILTER_STOP_WORDS, BOOLEAN_NB, BEST_MODEL, args[0], args[1])
  else:
    test10Fold(args, FILTER_STOP_WORDS, BOOLEAN_NB, BEST_MODEL)
  end_time = time.time()
  print end_time - start_time

if __name__ == "__main__":
    main()
