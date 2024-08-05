import streamlit as st
import requests
from opentelemetry.trace import Tracer
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry import environment_variables, metrics, trace
import logging
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter


# URL de votre API Azure
API_URL = "https://p07.azurewebsites.net"

logger = logging.getLogger(__name__)
exporter = AzureMonitorTraceExporter(
    connection_string="InstrumentationKey=ec60a799-186d-4345-86af-c5babe81ee62")

# Configuration du tracer
#trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(exporter))

tracer = trace.get_tracer(__name__)

logger = logging.getLogger(__name__)


#----------------------------------------------------------------------------------------

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
        span.set_attribute("text", user_input)
        span.set_attribute("predicted_sentiment", st.session_state.sentiment)
    st.session_state.feedback_given = False

# Bouton pour analyser
if st.button("Analyser"):
    analyze_sentiment()

# Affichage du résultat et des boutons de feedback
if st.session_state.sentiment is not None:
    st.write(f"Sentiment prédit : {st.session_state.sentiment}")
    
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
                    feedback_span.set_attribute("feedback", "non_conforme")
                    feedback_span.set_attribute("text", user_input)
                    feedback_span.set_attribute("sentiment", st.session_state.sentiment)
                st.error("Merci pour votre retour. Nous allons améliorer notre modèle.")
                st.session_state.feedback_given = True

# Bouton pour réinitialiser
if st.session_state.feedback_given:
    if st.button("Nouvelle analyse"):
        st.session_state.sentiment = None
        st.session_state.feedback_given = False
        st.experimental_rerun()
