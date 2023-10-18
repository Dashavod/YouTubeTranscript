import requests
import json
import streamlit as st

@st.cache_data(show_spinner=False, max_entries=1)
def translate_text(text,language_code='uk'):
    url = f"http://127.0.0.1:3000/translate_{language_code}"
    print(url)
    payload = {"text": text}
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, data=json.dumps(payload), headers=headers)

    if response.status_code == 200:
        translated_text = response.json().get("translated_text", "Translation not available")
        return translated_text
    else:
        return f"Sorry translation request for {language_code} has not available yet "

