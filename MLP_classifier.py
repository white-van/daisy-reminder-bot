import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split


class NLPSpamDetector:
    def execute(self):
        df = pd.read_csv('spam.csv', sep=',', encoding='latin-1')
        stop_words = set(stopwords.words('english'))
        processed_text = []
        target = []
        for i in df.itertuples():
            processed_text.append(i[2])
            target.append(i[1])
        tf = TfidfVectorizer()
        t = tf.fit_transform(processed_text)
        x_train,x_test,y_train,y_test = train_test_split(t,target,test_size = 0.3)
        model = MLPClassifier(hidden_layer_sizes = (6,2), activation = 'tanh', learning_rate = 'adaptive', max_iter = 400)
        model.fit(x_train, y_train)
        print(model.predict(x_test))
        print(model.score(x_test, y_test))

if __name__=='__main__':
    a = NLPSpamDetector()
    a.execute()
