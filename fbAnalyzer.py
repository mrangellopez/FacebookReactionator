from sentiment import NaiveBayes as SentimentClassifier
from NaiveBayes import NaiveBayes
from PorterStemmer import PorterStemmer
from DataParser import DataParser


def main():
    ps = PorterStemmer()
    nb = NaiveBayes()
    sc = SentimentClassifier.NaiveBayes()
    dp = DataParser()
    #data = dp.parse('data/data.json')
    #firstPostNumLove = data[0]['reactions_love']['summary']['total_count']
    #print "first post recieved %s love reactions" % firstPostNumLove

    reaganData = dp.parse('data/inputs.json')
    print reaganData

if __name__ == '__main__':
   main()
