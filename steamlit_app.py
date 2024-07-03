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

if st.button("Analyser"):
    response = requests.post(f"{API_URL}/predict", json={"text": text})
    prediction = response.json()['sentiment']
    st.write(f"Sentiment prédit : {prediction}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Prédiction correcte"):
            requests.post(f"{API_URL}/feedback", json={"prediction": prediction, "is_correct": True})
            st.success("Merci pour votre feedback !")
    with col2:
        if st.button("Prédiction incorrecte"):
            requests.post(f"{API_URL}/feedback", json={"prediction": prediction, "is_correct": False})
            st.success("Merci pour votre feedback !")
        
atexit.register(tc.flush)
