import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/predict"

st.title("Titanic Survival Prediction")

st.write("Enter passenger details:")

# Inputs
pclass = st.selectbox("Passenger Class", [1, 2, 3])
age = st.number_input("Age", min_value=0.0, max_value=100.0, value=22.0)
sibsp = st.number_input("Siblings/Spouses", min_value=0, value=1)
parch = st.number_input("Parents/Children", min_value=0, value=0)
fare = st.number_input("Fare", min_value=0.0, value=7.25)

sex = st.selectbox("Sex", ["male", "female"])
embarked = st.selectbox("Embarked", ["S", "C", "Q"])

name = st.text_input("Name", "Braund")
ticket = st.text_input("Ticket", "A/5 21171")

# Button
if st.button("Predict"):

    payload = {
        "Pclass": pclass,
        "Age": age,
        "SibSp": sibsp,
        "Parch": parch,
        "Fare": fare,
        "Sex": sex,
        "Embarked": embarked,
        "Name": name,
        "Ticket": ticket
    }

    try:
        response = requests.post(API_URL, json=payload)

        if response.status_code == 200:
            result = response.json()

            prediction = result["prediction"]

            if prediction == 1:
                st.success(f"Survived")
            else:
                st.error(f"Did Not Survive")

            st.write("Request ID:", result["request_id"])

        else:
            st.error(f"API Error: {response.text}")

    except Exception as e:
        st.error(f"Connection Error: {e}")