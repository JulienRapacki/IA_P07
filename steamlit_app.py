import streamlit as st
import requests

from opentelemetry.trace import Tracer
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace


# URL de votre API Azure
API_URL = "https://p07.azurewebsites.net"

# Configuration du tracer
instrumentation_key = "62ffb7a1-0b9f-4cb6-8e6d-6ab03636e5aa"

configure_azure_monitor(
    connection_string=f"InstrumentationKey={instrumentation_key}")

tracer = trace.get_tracer(__name__)

if 'sentiment' not in st.session_state:
    st.session_state.sentiment = None
if 'feedback_given' not in st.session_state:
    st.session_state.feedback_given = False

st.title("Analyse de sentiment")

user_input = st.text_input("Entrez une phrase :")


# Fonction pour analyser le sentiment
def analyze_sentiment():
    with tracer.start_as_current_span("analyze_sentiment") as span:
        response = requests.post(f"{API_URL}/predict_sentiment", params={"text":user_input})
        st.session_state.sentiment = response.json()['sentiment']
        st.session_state.probability = round(response.json()['probability'],2)
        span.set_attribute("text", user_input)
        span.set_attribute("predicted_sentiment", st.session_state.sentiment)
        span.set_attribute("probability", st.session_state.probability)
    st.session_state.feedback_given = False

# Bouton pour analyser
if st.button("Analyser"):
    analyze_sentiment()

# Affichage du résultat et des boutons de feedback
if st.session_state.sentiment is not None:
    st.write(f"Sentiment prédit : {st.session_state.sentiment} , Probabilité : {st.session_state.probability}")
    
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




