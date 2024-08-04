import streamlit as st
import requests
from opentelemetry.trace import Tracer
import logging
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter


# URL de votre API Azure
API_URL = "https://p07.azurewebsites.net"

logger = logging.getLogger(__name__)
# exporter = AzureMonitorTraceExporter(
#     connection_string="InstrumentationKey=ec60a799-186d-4345-86af-c5babe81ee62")
# span_processor = BatchSpanProcessor(exporter)

tracer = trace.get_tracer(__name__)


st.title("Analyse de sentiment - Projet 7")

user_input = st.text_area("Entrez votre phrase ici :")



if st.button("Analyser"):
    with tracer.start_as_current_span("analyze_sentiment") as span:
        logger.info('analyse ok')
        response = requests.post(f"{API_URL}/predict_sentiment", params={"text":user_input})
        prediction = response.json()['sentiment']
        probability = response.json()['probability']
        st.write(f"Sentiment prédit : {prediction} pour une probabilité de {probability}")
        span.set_attribute("text", user_input)
        span.set_attribute("predicted_sentiment", prediction)

        if st.button("Prédiction conforme"):
            with tracer.start_as_current_span("prediction_feedback") as feedback_span:
                feedback_span.set_attribute("feedback", "conforme")
                feedback_span.set_attribute("text", user_input)
                feedback_span.set_attribute("sentiment", prediction)
                st.success("Merci pour votre retour !")

        if st.button("Prédiction non conforme"):
            with tracer.start_as_current_span("prediction_feedback") as feedback_span:
                feedback_span.set_attribute("feedback", "non_conforme")
                logger.warning("pred not ok")
                feedback_span.set_attribute("text", user_input)
                feedback_span.set_attribute("sentiment", prediction)
                st.error("Merci pour votre retour. Nous allons améliorer notre modèle.")
