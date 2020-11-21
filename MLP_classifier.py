import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier

class NLPSpamDetector:
    def execute(self):
        df = pd.read_csv('spam.csv', sep=',', encoding='latin-1')
        text = df[['v2']]
        target = df[['v1']]
        stop_words = set(stopwords.words('english'))
            
if __name__=='__main__':
    a = NLPSpamDetector()
    a.execute()
