import streamlit as st
import tempfile
import ffmpeg

# Створюємо Streamlit додаток
st.title("Витягнення аудіо з відео")

# Завантаження відеофайлу
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
