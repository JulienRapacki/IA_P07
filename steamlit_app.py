import streamlit as st
import requests

# URL de votre API Azure
API_URL = "https://p07-api.azurewebsites.net/predict_sentiment"

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
    else:
        st.write("Veuillez entrer une phrase à analyser.")