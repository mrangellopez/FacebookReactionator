from sentiment import NaiveBayes as SentimentClassifier
from NaiveBayes import NaiveBayes
from PorterStemmer import PorterStemmer

def main():
    ps = PorterStemmer()
    nb = NaiveBayes()
    sc = SentimentClassifier.NaiveBayes()
    print 'ready to start coding shit up'

if __name__ == '__main__':
   main()
