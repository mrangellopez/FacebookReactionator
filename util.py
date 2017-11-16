import collections
import math

############################################################
# Problem 3a

def dotProduct(d1, d2):
    """
    @param dict d1: a feature vector represented by a mapping from a feature (string) to a weight (float).
    @param dict d2: same as d1
    @return float: the dot product between d1 and d2
    """
    if len(d1) < len(d2):
        return dotProduct(d2, d1)
    else:
        return sum(d1.get(f, 0) * v for f, v in d2.items())

def increment(d1, scale, d2):
    """
    Implements d1 += scale * d2 for sparse vectors.
    @param dict d1: the feature vector which is mutated.
    @param float scale
    @param dict d2: a feature vector.
    """
    for f, v in d2.items():
        d1[f] = d1.get(f, 0) + v * scale

def evaluatePredictor(examples, predictor):
    '''
    predictor: a function that takes an x and returns a predicted y.
    Given a list of examples (x, y), makes predictions based on |predict| and returns the fraction
    of misclassiied examples.
    '''
    error = 0
    for x, y in examples:
        if predictor(x) != y:
            error += 1
    return 1.0 * error / len(examples)

def findAlphabeticallyLastWord(text):
    """
    Given a string |text|, return the word in |text| that comes last
    alphabetically (that is, the word that would appear last in a dictionary).
    A word is defined by a maximal sequence of characters without whitespaces.
    You might find max() and list comprehensions handy here.
    """
    # BEGIN_YOUR_CODE (our solution is 1 line of code, but don't worry if you deviate from this)
    words = text.lower().split()
    words.sort()
    return words[-1]
    # END_YOUR_CODE

############################################################
# Problem 3b

def euclideanDistance(loc1, loc2):
    """
    Return the Euclidean distance between two locations, where the locations
    are pairs of numbers (e.g., (3, 5)).
    """
    # BEGIN_YOUR_CODE (our solution is 1 line of code, but don't worry if you deviate from this)
    return math.sqrt((loc2[0] - loc1[0])**2 + (loc2[1] - loc1[1])**2)
    # END_YOUR_CODE

############################################################
# Problem 3c

def mutateSentences(sentence):
    """
    Given a sentence (sequence of words), return a list of all "similar"
    sentences.
    We define a sentence to be similar to the original sentence if
      - it has the same number of words, and
      - each pair of adjacent words in the new sentence also occurs in the original sentence
        (the words within each pair should appear in the same order in the output sentence
         as they did in the orignal sentence.)
    Notes:
      - The order of the sentences you output doesn't matter.
      - You must not output duplicates.
      - Your generated sentence can use a word in the original sentence more than
        once.
    Example:
      - Input: 'the cat and the mouse'
      - Output: ['and the cat and the', 'the cat and the mouse', 'the cat and the cat', 'cat and the cat and']
                (reordered versions of this list are allowed)
    """

    # BEGIN_YOUR_CODE (our solution is 20 lines of code, but don't worry if you deviate from this)

    #concats a word
    def concatWord(s, w):
        if(s == ''):
            return w
        words = s.split()
        words.append(w)
        return ' '.join(words)

    def setupMutation():
        for i in range(0, length - 1):
            pairs[words[i]].add(words[i+1])

        for (key, value) in pairs.iteritems():
            levelSentences[0].add(key)

    def mutateSentence(n):
        if n == length:
            return
        for lastSentence in levelSentences[n-1]:

            lastWord = lastSentence.split()[-1]

            if len(pairs[lastWord]) != 0:
                for word in pairs[lastWord]:
                    levelSentences[n].add(concatWord(lastSentence, word))

        mutateSentence(n+1)

    def getMutations():
        return list(levelSentences[length - 1])

    words = sentence.split()
    length = len(words)

    levelSentences = [set([]) for i in range(length)]
    pairs = collections.defaultdict(lambda: set([]))

    setupMutation()
    mutateSentence(1)

    return getMutations()

    # END_YOUR_CODE

############################################################
# Problem 3d

def sparseVectorDotProduct(v1, v2):
    """
    Given two sparse vectors |v1| and |v2|, each represented as collection.defaultdict(float), return
    their dot product.
    You might find it useful to use sum() and a list comprehension.
    This function will be useful later for linear classifiers.
    """
    # BEGIN_YOUR_CODE (our solution is 4 lines of code, but don't worry if you deviate from this)
    smallList = v1 if len(v1) < len(v2) else v2
    return sum([v1[key] * v2[key] for (key, value) in smallList.iteritems() if v2[key] != 0.0])
    # END_YOUR_CODE

############################################################
# Problem 3e

def incrementSparseVector(v1, scale, v2):
    """
    Given two sparse vectors |v1| and |v2|, perform v1 += scale * v2.
    This function will be useful later for linear classifiers.
    """
    # BEGIN_YOUR_CODE (our solution is 2 lines of code, but don't worry if you deviate from this)
    for (key, value) in v2.iteritems():
        v1[key] += scale * v2[key]
    # END_YOUR_CODE

############################################################
# Problem 3f

def findSingletonWords(text):
    """
    Splits the string |text| by whitespace and returns the set of words that
    occur exactly once.
    You might find it useful to use collections.defaultdict(int).
    """
    # BEGIN_YOUR_CODE (our solution is 4 lines of code, but don't worry if you deviate from this)
    wordCounts = collections.defaultdict(lambda: 0)
    for word in text.split():
        wordCounts[word] += 1
    return set([word for word in wordCounts if wordCounts[word] == 1])
    # END_YOUR_CODE

############################################################
# Problem 3g

def computeLongestPalindromeLength(text):
    """
    A palindrome is a string that is equal to its reverse (e.g., 'ana').
    Compute the length of the longest palindrome that can be obtained by deleting
    letters from |text|.
    For example: the longest palindrome in 'animal' is 'ama'.
    Your algorithm should run in O(len(text)^2) time.
    You should first define a recurrence before you start coding.
    """
    L = collections.defaultdict(lambda: collections.defaultdict(lambda: 0))

    def longestPal(i, j):
        if j <= 0:
            L[i][j] = len(text)
            return L[i][j]

        if L[i][j] != 0:
            return L[i][j]

        if i == j:
            L[i][j] = 1
            return 1

        if i+1 == j:
            L[i][j] = 2 if text[i] == text[j] else 1
            return L[i][j]

        if text[i] == text[j]:
            L[i][j] = longestPal(i+1, j-1) + 2
        else:
            L[i][j] = max(longestPal(i+1, j), longestPal(i, j-1))
        return L[i][j]


    return longestPal(0, len(text)-1)
    # END_YOUR_CODE
