import streamlit as st
import requests
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.tracer import Tracer

# URL de votre API Azure
API_URL = "https://p07-insights.azurewebsites.net"

tracer = Tracer(exporter=AzureExporter(connection_string='InstrumentationKey=7041f9ba-42f6-4ca8-9b3f-bd436fca5122'))


st.title("Analyse de sentiment")

user_input = st.text_area("Entrez votre phrase ici :")

if st.button("Analyser"):
    with tracer.span(name='API predict_sentiment'):
        response = requests.post(f"{API_URL}/predict_sentiment", params={"text":user_input})
    prediction = response.json()['sentiment']
    probability = response.json()['probability']
    st.write(f"Sentiment prédit : {prediction} pour une probabilité de {probability}")


if st.button("Prédiction correcte"):
    with tracer.span(name='API predict_sentiment'):
        response = requests.post(f"{API_URL}/predict_sentiment", params={"text":user_input})
    prediction = response.json()['sentiment']
    probability = response.json()['probability']
    requests.post(f"{API_URL}/feedback", params={"prediction": prediction, "is_correct": "True"})
    if response.status_code == 200:
        st.write("Merci pour votre feedback !")
    else:
        st.write("Erreur lors de l'envoi du feedback.")

if st.button("Prédiction incorrecte"):
    with tracer.span(name='API predict_sentiment'):
        response = requests.post(f"{API_URL}/predict_sentiment", params={"text":user_input})
    prediction = response.json()['sentiment']
    probability = response.json()['probability']
    requests.post(f"{API_URL}/feedback", params={"prediction": prediction, "is_correct": "False"})
    if response.status_code == 200:
        st.write("Merci pour votre feedback !")
    else:
        st.write("Erreur lors de l'envoi du feedback.")

