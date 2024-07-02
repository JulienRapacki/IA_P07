import streamlit as st
import requests
from applicationinsights import TelemetryClient



# URL de votre API Azure
API_URL = "https://p07-api.azurewebsites.net/predict_sentiment"

# Configuration d'Application Insights
tc = TelemetryClient( '3702b2ba-5fab-46e7-8c1b-b4e13381c925')


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
        sentiment = get_sentiment(user_input)
        st.write(f"Le sentiment de la phrase est : {sentiment}")
        
        # Enregistrement de l'analyse
        tc.track_event('SentimentAnalysisRequested', {'text': user_input, 'sentiment': sentiment})
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Prédiction conforme"):
                tc.track_event('PredictionConfirmed', {'text': user_input, 'sentiment': sentiment})
                st.success("Merci pour votre confirmation!")
        with col2:
            if st.button("Prédiction non conforme"):
                tc.track_event('PredictionDisputed', {'text': user_input, 'sentiment': sentiment})
                st.error("Merci pour votre signalement. Nous allons examiner cette prédiction.")
    else:
        st.write("Veuillez entrer une phrase à analyser.")

# Assurez-vous d'envoyer les télémétries à la fin
tc.flush()
