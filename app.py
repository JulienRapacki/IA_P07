import pickle
import numpy
import re
# pre-traitement du text
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer

from applicationinsights import TelemetryClient
from applicationinsights.logging import LoggingHandler
import logging




# Deep learning
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model

from flask import Flask, request, jsonify, send_file

# téléchargement des bases de caractères
nltk.download("stopwords")
nltk.download('punkt')
nltk.download('wordnet')
stop = set(stopwords.words('english'))


# regex permettant d'ignorer les caractères spéciaux ainsi que les nombres et les mots contenant des underscores

def preprocess(text) :

    def tokenize(text):
        tokenizer = nltk.RegexpTokenizer(r'\b(?![\w_]*_)[^\d\W]+\b')
        # Tokenisation de la description et suppression des majuscules
        tokens = tokenizer.tokenize(text.lower())
        return tokens

    def lemmatize_word(text):

        lemmatizer = WordNetLemmatizer()
        lemma = [lemmatizer.lemmatize(token) for token in text]
        return lemma

    def combine_text(list_of_text):

        combined_text = ' '.join(list_of_text)
        return combined_text

    token = tokenize(text)
    stop_removed = [token for token in token if token not in stop]
    lemma = lemmatize_word(stop_removed)
    combined = combine_text(lemma)

    return  combined

MAX_SEQUENCE_LENGTH =30

# Chargement du tokenizer préalablement entraîné
with open("./tokenizer_lstm.pickle", "rb") as file:
    tokenizer = pickle.load(file)



def predict_sentiment(text):

        # First let's preprocess the text in the same way than for the training
        text = preprocess(text)

        # Let's get the index sequences from the tokenizer
        index_sequence = pad_sequences(tokenizer.texts_to_sequences([text]),
                                    maxlen = MAX_SEQUENCE_LENGTH,padding='post')

        probability_score = clf_model.predict(index_sequence)[0][0]

        if probability_score < 0.5:
            sentiment = "negative"
        else:
            sentiment = "positive"

        return sentiment, probability_score


clf_model = load_model('./model_lstm_glove.h5')



app = Flask(__name__)

tc = TelemetryClient( '3702b2ba-5fab-46e7-8c1b-b4e13381c925')

# Configuration du logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(LoggingHandler(tc))

clf_model = None

@app.before_first_request
def load_model():
    global clf_model
    clf_model = load_model('./model_lstm_glove.h5')



# This is the route to the API
@app.route("/predict_sentiment", methods=["POST"])
def predict():

    # Get the text included in the request
    text = request.args['text']

    # Process the text in order to get the sentiment
    results = predict_sentiment(text)
    logger.info(f"Sentiment analysis: '{text}' -> {sentiment}")
    
    # Suivi des événements personnalisés
    tc.track_event('SentimentAnalysis', {'text': text, 'sentiment': sentiment})
    
    return jsonify(text=text, sentiment=results[0], probability=str(results[1]))

# This is the reoute to the welcome page
@app.route("/")
def home():
    return "Hello, welcome to the sentiment classification API for project 07 !"

