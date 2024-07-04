import streamlit as st
import requests


# URL de votre API Azure
API_URL = "https://p07-insights.azurewebsites.net"


st.title("Analyse de sentiment")

user_input = st.text_area("Entrez votre phrase ici :")

if st.button("Analyser"):
    response = requests.post(f"{API_URL}/predict_sentiment", params={"text":user_input})
    prediction = response.json()['sentiment']
    probability = response.json()['probability']
    st.write(f"Sentiment prédit : {prediction} pour une probabilité de {probability}")


if st.button("Prédiction correcte"):
    requests.post(f"{API_URL}/feedback", params={"prediction": prediction, "is_correct": "True"})
    if feedback_response.status_code == 200:
        st.write("Merci pour votre feedback !")
    else:
        st.write("Erreur lors de l'envoi du feedback.")

if st.button("Prédiction incorrecte"):
    requests.post(f"{API_URL}/feedback", params={"prediction": prediction, "is_correct": "False"})
    if feedback_response.status_code == 200:
        st.write("Merci pour votre feedback !")
    else:
        st.write("Erreur lors de l'envoi du feedback.")

