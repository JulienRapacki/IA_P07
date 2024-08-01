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
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace import config_integration
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.trace.tracer import Tracer
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


# partie dédiée à l'API
app = Flask(__name__)

# Configuration du middleware OpenCensus pour Flask
# middleware = FlaskMiddleware(
#     app,
#     exporter=AzureExporter(connection_string='InstrumentationKey=7041f9ba-42f6-4ca8-9b3f-bd436fca5122'),
#     sampler=ProbabilitySampler(rate=1.0)
# )

# Configuration du tracer
# tracer = Tracer(exporter=AzureExporter(connection_string='InstrumentationKey=43bf7273-a937-47a7-a8e6-ba3cd01a3a30')) 

# Configurer l'exporter pour envoyer les traces à Azure Log Analytics
logger = logging.getLogger(__name__)
azure_handler = AzureLogHandler(connection_string='InstrumentationKey=43bf7273-a937-47a7-a8e6-ba3cd01a3a30')
logger.addHandler(azure_handler)


# Page d'accueil
@app.route("/")
def home():
    return "Hello, welcome to the sentiment classification API for project 07 !"

@app.route("/predict_sentiment", methods=["POST"])
def predict():

    # Get the text included in the request
    text = request.args['text']
    
    # Process the text in order to get the sentiment
    results = predict_sentiment(text)
    return jsonify(text=text, sentiment=results[0], probability=str(results[1]))


@app.route('/feedback', methods=['POST'])
def feedback():
    prediction = request.args['sentiment']
    is_correct = request.args['is_correct'] == 'True'
    
    if is_correct:
        logger.warning('Prediction correcte ok',extra={'custom_dimensions': {'prediction': sentiment}})
    else:
        logger.error('Prediction incorrecte warning',extra={'custom_dimensions': {'prediction': sentiment}})
    
    return jsonify({'status': 'success'})



