import streamlit as st
import requests


# URL de votre API Azure
API_URL = "p07-insights.azurewebsites.net"


st.title("Analyse de sentiment")

user_input = st.text_area("Entrez votre phrase ici :")

if st.button("Analyser"):
    response = requests.post(f"{API_URL}/predict_sentiment", params={"text":user_input})
    prediction = response.json()['sentiment']
    probability = response.json()['probability']
    st.write(f"Sentiment prédit : {prediction} pour une probabilité de {probability}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Prédiction correcte"):
            requests.post(f"{API_URL}/feedback", params={"prediction": prediction, "is_correct": True})
            st.success("Merci pour votre feedback !")
    with col2:
        if st.button("Prédiction incorrecte"):
            requests.post(f"{API_URL}/feedback", params={"prediction": prediction, "is_correct": False})
            st.success("Merci pour votre feedback !")

