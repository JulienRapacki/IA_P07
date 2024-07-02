import streamlit as st
import requests

from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace.tracer import Tracer
import logging

# URL de votre API Azure
API_URL = "https://p07-api.azurewebsites.net/predict_sentiment"

# Configuration d'Application Insights
INSTRUMENTATION_KEY = '3702b2ba-5fab-46e7-8c1b-b4e13381c925'

# Configuration du logger
logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(
    connection_string=f'InstrumentationKey={INSTRUMENTATION_KEY}')
)

# Configuration du tracer
tracer = Tracer(
    exporter=AzureExporter(connection_string=f'InstrumentationKey={INSTRUMENTATION_KEY}'),
    sampler=ProbabilitySampler(1.0),
)






def get_sentiment(text):
    response = requests.post(API_URL, params={"text": text})
    if response.status_code == 200:
        return response.json()["sentiment"]
    else:
        return "Erreur lors de l'appel à l'API"

st.title("Analyse de sentiment")

user_input = st.text_area("Entrez votre phrase ici :")

if st.button("Analyser le sentiment"):
    if user_input:
        with tracer.span(name="analyze_sentiment"):
            sentiment = get_sentiment(user_input)
            st.write(f"Le sentiment de la phrase est : {sentiment}")
            
            # Suivi des prédictions non conformes
            if sentiment not in ['positif', 'négatif']:
                logger.warning(f"Prédiction non conforme: '{user_input}' -> {sentiment}")
    else:
        st.write("Veuillez entrer une phrase à analyser.")
