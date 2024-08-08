import streamlit as st
import requests

from opentelemetry.trace import Tracer
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry import environment_variables, metrics, trace

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from azure.monitor.opentelemetry import configure_azure_monitor

# URL de votre API Azure
API_URL = "https://p07.azurewebsites.net"

# Configuration du tracer
instrumentation_key = "a76e31d9-acf0-4446-9fa2-874cbd600f90"

configure_azure_monitor(
    connection_string=f"InstrumentationKey={instrumentation_key}")
tracer = trace.get_tracer(__name__)

if 'sentiment' not in st.session_state:
    st.session_state.sentiment = None
if 'feedback_given' not in st.session_state:
    st.session_state.feedback_given = False



API_URL = "https://p07main.azurewebsites.net/predict_sentiment"

def get_sentiment(text):
    response = requests.post(API_URL, params={"text": text})
    if response.status_code == 200:
        return response.json()["sentiment"],response.json()["probability"]
    else:
        return "Erreur lors de l'appel à l'API"


def send_feedback(prediction, is_correct):
    response = requests.post(
        f'{API_BASE_URL}/feedback',
        json={'prediction': prediction, 'is_correct': is_correct})



st.title("Analyse de sentiment")

user_input = st.text_input("Entrez une phrase :")


# Fonction pour analyser le sentiment
def analyze_sentiment():
    with tracer.start_as_current_span("analyze_sentiment") as span:
        response = requests.post(f"{API_URL}/predict_sentiment", params={"text":user_input})
        st.session_state.sentiment = response.json()['sentiment']
        st.session_state.probability = response.json()['probability']
        span.set_attribute("text", user_input)
        span.set_attribute("predicted_sentiment", st.session_state.sentiment)
        span.set_attribute("probability", st.session_state.probability)
    st.session_state.feedback_given = False

# Bouton pour analyser
if st.button("Analyser"):
    analyze_sentiment()

# Affichage du résultat et des boutons de feedback
if st.session_state.sentiment is not None:
    st.write(f"Sentiment prédit : {st.session_state.sentiment} , Probabilité : {round(st.session_state.probability,2)}")
    
    if not st.session_state.feedback_given:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Prédiction conforme"):
                
                with tracer.start_as_current_span("prediction_feedback") as feedback_span:
                    feedback_span.set_attribute("feedback", "conforme")
                    feedback_span.set_attribute("text", user_input)
                    feedback_span.set_attribute("sentiment", st.session_state.sentiment)
                st.success("Merci pour votre retour !")
                st.session_state.feedback_given = True

        with col2:
            if st.button("Prédiction non conforme"):
                
                with tracer.start_as_current_span("prediction_feedback") as feedback_span:                    
                    feedback_data = {"prediction","non_conforme"}
                    response = requests.post(f"{API_URL}/feedback", params={"feedback_error":feedback_data})
                    feedback_span.set_attribute("feedback", "non_conforme")
                    feedback_span.set_attribute("text", user_input)
                    feedback_span.set_attribute("sentiment", st.session_state.sentiment)
                st.error("Merci pour votre retour. Nous allons améliorer notre modèle.")
                st.session_state.feedback_given = True

if st.button("Analyser le sentiment"):
    if user_input:
        sentiment = get_sentiment(user_input)
        st.write(f"Le sentiment de la phrase est : {sentiment},{probability}")
              
        if st.button('Feedback : Prédiction correcte'):
            send_feedback(sentiment, True)
            st.write('Merci pour votre feedback !')
        if st.button('Feedback : Prédiction incorrecte'):
            send_feedback(sentiment, False)
            st.write('Merci pour votre feedback !')
    else:
        st.write("Veuillez entrer une phrase à analyser.")


