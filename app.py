import pickle
import numpy
import re

# pre-traitement du text
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer

#Analyses dans Azure
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
import logging


# Deep learning
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model

from flask import Flask, request, jsonify, send_file

# téléchargement des bases de caractères
nltk.download("stopwords")
nltk.download('punkt')
nltk.download('wordnet')
stop = set(stopwords.words('english'))


def preprocess(text) :

    def tokenize(text):
        # regex permettant d'ignorer les caractères spéciaux ainsi que les nombres et les mots contenant des underscores
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

# Chargement du modèle
clf_model = load_model('./model_lstm_glove.h5')


def predict_sentiment(text):
     
    # First let's preprocess the text in the same way than for the training
    text = preprocess(text)

    # Let's get the index sequences from the tokenizer
    index_sequence = pad_sequences(tokenizer.texts_to_sequences([text]),
                                maxlen = MAX_SEQUENCE_LENGTH,padding='post')

    probability_score = clf_model.predict(index_sequence)[0][0]

    if probability_score < 0.5:
        sentiment = "negatif"
    else:
        sentiment = "positif"

    return sentiment, probability_score


# Configuration analyses Azure
instrumentation_key = "62ffb7a1-0b9f-4cb6-8e6d-6ab03636e5aa"
configure_azure_monitor(
    connection_string=f"InstrumentationKey={instrumentation_key}")

# Configuration du tracer
tracer = trace.get_tracer(__name__)

logger = logging.getLogger(__name__)



# partie dédiée à l'API
app = Flask(__name__)


with tracer.start_as_current_span("app_start") as span:
    span.set_attribute("start", "ok")
    print("Hello world!")
 

# Page d'accueil
@app.route("/")
def home():
    return "Hello, welcome to the sentiment classification API for project 07 !"

@app.route("/predict_sentiment", methods=["POST"])
def predict():
    logger.info("running prediction")
    with tracer.start_as_current_span(name="prediction_request_received") as span:
        text = request.args['text']
        results = predict_sentiment(text)
        span.set_attribute("predicted_sentiment", str(results))
    
    
    return jsonify(text=text, sentiment=results[0], probability=str(results[1]))


@app.route('/feedback', methods=['POST'])
def feedback():
    with tracer.start_as_current_span(name="feedback_request_received") as span:
        prediction = request.args['sentiment']
        is_correct = request.args['is_correct'] 
        logger.info("correct_prediction")
        span.set_attribute('prediction', prediction)
        span.set_attribute('is_correct', str(is_correct))
        
    return jsonify({'status': 'feedback_received'})


