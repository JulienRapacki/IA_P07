import streamlit as st
import requests

from applicationinsights import TelemetryClient
import atexit


# URL de votre API Azure
API_URL = "https://p07-api.azurewebsites.net/predict_sentiment"

# Configuration d'Application Insights
tc = TelemetryClient( '7041f9ba-42f6-4ca8-9b3f-bd436fca5122')


def get_sentiment(text):
    response = requests.post(API_URL, json={"text": text})
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
        tc.flush()
        
        # Utilisation des variables d'état pour les boutons de confirmation
        if "feedback" not in st.session_state:
            st.session_state.feedback = None
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Prédiction conforme"):
                st.session_state.feedback = "conforme"
                st.write("Prédiction conforme cliquée")
        with col2:
            if st.button("Prédiction non conforme"):
                st.session_state.feedback = "non conforme"
        
        if st.session_state.feedback == "conforme":
            tc.track_event('PredictionConfirmed', {'text': user_input, 'sentiment': sentiment})
            st.success("Merci pour votre confirmation!")
            st.session_state.feedback = None  # Reset feedback state
            tc.flush()
        
        if st.session_state.feedback == "non conforme":
            tc.track_event('PredictionDisputed', {'text': user_input, 'sentiment': sentiment})
            st.error("Merci pour votre signalement. Nous allons examiner cette prédiction.")
            st.session_state.feedback = None  # Reset feedback state
            tc.flush()
    else:
        st.write("Veuillez entrer une phrase à analyser.")
        
atexit.register(tc.flush)
