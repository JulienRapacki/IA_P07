import streamlit as st
import requests


API_URL = "https://p07main.azurewebsites.net/predict_sentiment"

def get_sentiment(text):
    response = requests.post(API_URL, params={"text": text})
    if response.status_code == 200:
        return response.json()["sentiment"],response.json()["probability"]
    else:
        return "Erreur lors de l'appel à l'API"

def send_feedback(prediction, is_correct):
    response = requests.post(
        f'{API_BASE_URL}/feedback',
        json={'prediction': prediction, 'is_correct': is_correct}
    )



st.title("Analyse de sentiment")

user_input = st.text_area("Entrez votre phrase ici :")

if st.button("Analyser le sentiment"):
    if user_input:
        sentiment = get_sentiment(user_input)
        st.write(f"Le sentiment de la phrase est : {sentiment},{probability}")
              
        if st.button('Feedback : Prédiction correcte'):
            send_feedback(sentiment, True)
            st.write('Merci pour votre feedback !')
        if st.button('Feedback : Prédiction incorrecte'):
            send_feedback(sentiment, False)
            st.write('Merci pour votre feedback !')
    else:
        st.write("Veuillez entrer une phrase à analyser.")

