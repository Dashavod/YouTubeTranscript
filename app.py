import os
import subprocess
import glob
import shutil
import streamlit as st
import tempfile
import ffmpeg
from PIL import Image
from whisper.tokenizer import LANGUAGES
from streamlit_extras.switch_page_button import switch_page
from helpers.utils import load_whisper_model, save_transcribe_result, transcribe_youtube_video, playlist_transcript_arc, \
    transcribe_upload_video
from helpers.youtube_utils import *

st.set_page_config(
    page_title="Youtube Transcript",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)
# main_image = Image.open('static/main_banner.png')


# st.image(main_image,use_column_width='auto')
# Header
st.title("✨ Automatic Video subtitle generation 🔊")
st.markdown("#### some description")

AUDIO = False
# Input and check url
url = st.text_input('YouTube video or playlist URL:')
right_url = check_youtube_url(url)
if right_url == "video":
    st.video(url)
    st.session_state.video_url = url
    st.session_state.playlist_url = None
elif right_url == "playlist":

    st.session_state.playlist_url = url
    st.session_state.video_url = None
    links = get_youtube_playlist_links(url)
    st.session_state.playlist_links = links
    if len(links)>3:
        st.markdown(f"Found {len(links)} videos in this playlist, under first 3")
        for link in links[:3]:
            st.video(link)
    else:
        st.markdown(f"Found {len(links)} videos in this playlist")
        for link in links:
            st.video(link)

else:
    st.error('Incorrect url, paste a new one', icon="🚨")
print('url:', url)

uploaded_file = st.file_uploader("Upload Video or audio", type=["mp4", "avi", "mov", "mp3"], accept_multiple_files=False)

if uploaded_file:

    # Створюємо тимчасовий файл для завантаженого відео
    with tempfile.NamedTemporaryFile(delete=False) as temp_video:
        temp_video.write(uploaded_file.read())

    # Витягнути аудіо з відео та зберегти його
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        ffmpeg.input(temp_video.name).output(temp_audio.name, y='-y').run()
    print(temp_audio.name)

    st.session_state.upload_resourse = temp_audio.name
    # Показати завантажений відео та витягнутий аудіо
    st.video(temp_video.name, format="video/mp4")
    st.audio(temp_audio.name, format="audio/mp3")


## Check if files already translated



# Whisper or Auto
st.markdown("#### Options")
transcribe_method = st.radio("Please choose your type", ('Whisper', 'Automatic Subtitles'), horizontal=True)
st.session_state.transcribe_method = transcribe_method
print(st.session_state.transcribe_method)

# Languages
if transcribe_method == 'Whisper':
    language = st.selectbox('Please select the language', tuple(LANGUAGES.values()))
    language = list(LANGUAGES.keys())[list(LANGUAGES.values()).index(language)]
    st.session_state.language = language
    with st.spinner("Loading Whisper model..."):
        model = load_whisper_model()
else:
    url = st.session_state.playlist_links[0] if st.session_state.playlist_url else url
    st.session_state.language = st.selectbox('Please select the language', get_languages_auto_transcript_text(url))

print("language", st.session_state.language)

result = None
# Transcribe
transcribe_cb = st.checkbox("Transcribe", value=False)
if transcribe_cb:

    if transcribe_method == 'Automatic Subtitles':
        st.info(f"This Youtube {'video'if st.session_state.video_url else 'playlist'} have auto subtitles from author")
        file_extension = "txt"
        if st.session_state.video_url:
            transcript = get_auto_transcript_text(url, st.session_state.language)

            result = " ".join([item["text"] for item in transcript])
            save_transcribe_result(url, auto_transcript=transcript)
        elif st.session_state.playlist_url:

            st.markdown(f"Playlist consist of {len(st.session_state.playlist_links)}")
            with st.spinner("Transcribing playlist..."):
                try:
                    filename = playlist_transcript_arc(st.session_state.playlist_url,st.session_state.language)
                except:
                    filename = None
                    st.warning(
                        """
                        Oops! Someone else is using the model right now to transcribe another video. 
                        Please try again in a few seconds.
                        """
                    )


            st.markdown(f"Transcribed videos {filename}")
            with open(filename, "rb") as file:
                btn = st.download_button(
                    label="Download zip",
                    data=file,
                    file_name="playlist.zip"
                )



    elif transcribe_method == 'Whisper':
        if st.session_state.get("playlist_url"):
            st.error('Sorry currenty service doen`t work with playlist with playlist, please choose Autosubtitles', icon="🚨")
        else:
            with st.spinner("Transcribing audio..."):

                try:
                    if  st.session_state.get("upload_resourse"):
                        result = transcribe_upload_video(model, st.session_state.get("upload_resourse"),language)
                        save_transcribe_result(st.session_state.get("upload_resourse"), result, isUpload=True)
                    elif st.session_state.get("video_url"):
                        result = transcribe_youtube_video(model, url, language)
                        save_transcribe_result(url, result)
                    st.success("Detected language: {}".format(result['language']))


                except RuntimeError:
                    result = None
                    st.warning(
                        """
                        Oops! Someone else is using the model right now to transcribe another video. 
                        Please try again in a few seconds.
                        """
                    )
# st.text("Language")
# task_type = st.radio("Please choose your task type", ('Transcribe', 'Translate'), horizontal=True)


if result:

    if transcribe_method == 'Whisper':

        file_extension = st.selectbox("File extension:", options=["TXT (.txt)", "SubRip (.srt)"])
        if file_extension == "TXT (.txt)":
            file_extension = "txt"
            data = result['text'].strip()
        elif file_extension == "SubRip (.srt)":
            file_extension = "srt"
            data = result['srt']
        data = st.text_area("Text:", value=data, height=350)


    if transcribe_method == 'Automatic Subtitles':
        data = st.text_area("Text:", value=result, height=350)

    _, button1, button2 = st.columns([2, 1, 1], gap='small')
    button1.download_button("Download", data=data, use_container_width=True,
                            file_name="captions.{}".format(file_extension))

    if button2.button("Analyse", type='primary', use_container_width=True):
        switch_page("analyse")

    # Download data
