
import numpy as np



import re

import pickle

# pre-traitement du text
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer


# Deep learning
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer


from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences


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
                                    maxlen = MAX_SEQUENCE_LENGTH)

        probability_score = clf_model.predict(index_sequence)[0][0]

        # Compte-tenu  du résultat de la courbe ROC-AUC, on préfèrera mettre un seuil à 0.6
        # pour la proba afin de limiter les faux positifs
        if probability_score < 0.6:
            sentiment = "negative"
        else:
            sentiment = "positive"

        return sentiment, probability_score


clf_model = load_model('./model_lstm_glove.h5')

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, welcome on the sentiment classification API project 07!"


@app.route('/predict_sentiment', methods=['POST'])

def predict():
    data = request.json

    #insertion du modèle
    text = request.args['text']

    results = predict_sentiment(text)

    return jsonify(text=text, sentiment=results[0], probability=str(results[1]))
# from threading import Thread

# def run_flask():
#     app.run(port=5000)

# flask_thread = Thread(target=run_flask)
# flask_thread.start()
