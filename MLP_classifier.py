import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split


class NLPSpamDetector:

    def train_test(self):
        df = pd.read_csv('spam.csv', sep=',', encoding='latin-1')
        self.stop_words = set(stopwords.words('english'))
        self.processed_text = []
        self.target = []
        for i in df.itertuples():
            text = i[2].strip().split(' ')
            text_processed = ' '.join([i for i in text if i not in self.stop_words])
            self.processed_text.append(text_processed)
            self.target.append(i[1])
        self.tf = TfidfVectorizer()
        t = self.tf.fit_transform(self.processed_text)
        x_train,x_test,y_train,y_test = train_test_split(t,self.target,test_size = 0.3)
        self.model = MLPClassifier(hidden_layer_sizes = (6,2), activation = 'tanh', learning_rate = 'adaptive', max_iter = 400)
        self.model.fit(x_train, y_train)
        self.model.predict(x_test)
        print(self.model.score(x_test, y_test))

    def predict(self, text):
        pre_process = text[2].strip().split(' ')
        text_processed = ' '.join([i for i in pre_process if i not in self.stop_words])
        self.processed_text.append(text)
        t = self.tf.fit_transform(self.processed_text)
        a = self.model.predict(t)
        print(a[len(a)-1])

if __name__=='__main__':
    a = NLPSpamDetector()
    a.train_test()
    a.predict("Hi this is interesting")

