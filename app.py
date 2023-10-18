import os
import subprocess
import glob
import shutil
import streamlit as st
import tempfile
import ffmpeg
from PIL import Image
from whisper.tokenizer import LANGUAGES

st.set_page_config(
    page_title="Youtube Transcript",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)
# main_image = Image.open('static/main_banner.png')


# st.image(main_image,use_column_width='auto')
st.title("✨ Automatic YouTube subtitle generation 🔊")
col1, col2, col3 = st.columns([0.3, 0.2, 0.3],gap="large")
with col1:
    st.markdown("#### Input data")

    url = st.text_input('YouTube URL:')
    st.markdown("#### Input data")
    uploaded_file = st.file_uploader("Завантажте відео", type=["mp4", "avi", "mov"])

    if uploaded_file:
        # Створюємо тимчасовий файл для завантаженого відео
        with tempfile.NamedTemporaryFile(delete=False) as temp_video:
            temp_video.write(uploaded_file.read())

        # Витягнути аудіо з відео та зберегти його
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            ffmpeg.input(temp_video.name).output(temp_audio.name, y='-y').run()

        # Показати завантажений відео та витягнутий аудіо
        st.video(temp_video.name, format="video/mp4")
        st.audio(temp_audio.name, format="audio/mp3")
    pass
with col2:
    st.markdown("#### Input data")
    model_type = st.radio("Please choose your model type", ('Small', 'Medium', 'Large'),horizontal=True)
    st.markdown("#### Input data")
    task_type = st.radio("Please choose your task type", ('Transcribe', 'Translate'),horizontal=True)
with col3:
    st.markdown("#### Input data")
    format_type = st.radio("Please choose your output format type", ('TXT', 'SRT'), horizontal=True)
