import requests
import json
import streamlit as st
import os
from dotenv import dotenv_values

url_ru_model = os.getenv('RU_TRANSLATE_MODEL') if os.getenv('RU_TRANSLATE_MODEL') else dotenv_values(".env")[
    'RU_TRANSLATE_MODEL']
url_uk_model = os.getenv('UK_TRANSLATE_MODEL') if os.getenv('UK_TRANSLATE_MODEL') else dotenv_values(".env")[
    'UK_TRANSLATE_MODEL']

@st.cache_data(show_spinner=False, max_entries=1)
def translate_text(text, language_code='uk'):
    url = url_ru_model if language_code == "ru" else url_uk_model
    print(url)
    payload = {"text": text}
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, data=json.dumps(payload), headers=headers)

    if response.status_code == 200:
        translated_text = response.json().get("translated_text", "Translation not available")
        return translated_text
    else:
        return f"Sorry translation request for {language_code} has not available yet "
