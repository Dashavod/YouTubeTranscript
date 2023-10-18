from helpers.translate_utils import translate_text
from helpers.utils import *
from whisper.tokenizer import LANGUAGES
import tempfile
import ffmpeg


def main():
    # Streamlit config

    st.set_page_config(
        page_title="Youtube Transcript",
        page_icon="✨",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    # Initialization

    # Title
    st.title("✨ Automatic YouTube subtitle generation 🔊")
    st.subheader("#Transcription with Whisper 🤫")

    # Intro text
    st.markdown(
        """
        This app lets you transcribe YouTube videos using 
        [Whisper](https://github.com/openai/whisper), 
        a general-purpose speech recognition model developed by 
        [OpenAI](https://openai.com/).
        """
    )
    col1, col2, col3 = st.columns([0.3, 0.2, 0.3], gap="large")
    # Title: Input data
    col1.markdown("## Input data")

    url = col1.text_input('YouTube URL:')
    uploaded_file = col1.file_uploader("Завантажте відео", type=["mp4", "avi", "mov"])

    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False) as temp_video:
            temp_video.write(uploaded_file.read())

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            ffmpeg.input(temp_video.name).output(temp_audio.name, y='-y').run()

        col1.video(temp_video.name, format="video/mp4")
        col1.audio(temp_audio.name, format="audio/mp3")

    # Load Whisper model

    if url:
        # Check if the input url is a valid YouTube url
        right_url = valid_url(url)
        col1.video(url)
        if right_url:
            if get_video_duration_from_youtube_url(url) <= MAX_VIDEO_LENGTH:
                st.session_state.url = url
                # Display YouTube video
                transcribe_method = col2.radio("Please choose your preference", ('Whisper', 'Automatic Subtitles'),
                                               horizontal=True)
                if transcribe_method == 'Whisper':
                    language = col2.selectbox('Please select the language', tuple(LANGUAGES.values()))
                    language = list(LANGUAGES.keys())[list(LANGUAGES.values()).index(language)]
                    with st.spinner("Loading Whisper model..."):
                        model = load_whisper_model()
                else:

                    language = col2.selectbox('Please select the language', get_languages_auto_transcript_text(url))

                originate_language = col2.selectbox('Original language', ['uk', 'ru'])
                translate_cb = col2.checkbox("Translate text")

                # Transcribe checkbox
                transcribe_cb = col2.checkbox("Transcribe")

                if transcribe_cb:

                    if transcribe_method == 'Automatic Subtitles' and get_languages_auto_transcript_text(url):
                        col3.info("This Youtube video have auto subtitles from author")
                        file_extension = "txt"
                        transcript = get_auto_transcript_text(url, language)
                        data = " ".join([item["text"] for item in transcript])
                        data = col3.text_area("Text:", value=data, height=350)
                        save_transcribe_result(url, auto_transcript=transcript)
                    else:
                        if is_translation_available(url):
                            col3.info("This video have been already translated")
                            file_extension = col3.selectbox("File extension:", options=["TXT (.txt)", "SubRip (.srt)"])
                            if translate_cb:
                                with st.spinner("Translating text🤓"):
                                    data = translated_text = translate_text(
                                        get_translation_from_file(url, file_extension), originate_language)
                                    data = st.text_area("Text:", value=translated_text, height=350)
                            else:
                                data = col3.text_area("Text:", value=get_translation_from_file(url, file_extension),
                                                      height=350)
                        else:
                            # Transcribe checkbox
                            col3.info(
                                """
                                If the transcription process takes just a few seconds, this means that the output was cached.
                                You can try again with another sample or a custom YouTube URL!
                                """
                            )

                            col3.markdown("## Output")

                            # Transcribe
                            with st.spinner("Transcribing audio..."):
                                result = None
                                try:
                                    result = transcribe_youtube_video(model, url, language)
                                except RuntimeError:
                                    result = None
                                    col3.warning(
                                        """
                                        Oops! Someone else is using the model right now to transcribe another video. 
                                        Please try again in a few seconds.
                                        """
                                    )

                            if result:
                                # Print detected language
                                col3.success("Detected language: {}".format(result['language']))
                                save_transcribe_result(url, result)

                                # Select output file extension and get data
                                file_extension = col3.selectbox("File extension:",
                                                                options=["TXT (.txt)", "SubRip (.srt)"])
                                if file_extension == "TXT (.txt)":
                                    file_extension = "txt"
                                    data = result['text'].strip()
                                elif file_extension == "SubRip (.srt)":
                                    file_extension = "srt"
                                    data = result['srt']

                                    # Print output
                                if translate_cb:
                                    with st.spinner("Translating text🤓"):
                                        data = translated_text = translate_text(data, originate_language)
                                        data = st.text_area("Text:", value=translated_text, height=350)
                                else:
                                    data = col3.text_area("Text:", value=data, height=350)

                                # Download data
                    _, button1, button2 = col3.columns([2, 1, 1], gap='small')
                    button1.download_button("Download", data=data, use_container_width=True,
                                            file_name="captions.{}".format(file_extension))
                    from streamlit_extras.switch_page_button import switch_page

                    if button2.button("Analyse", type='primary', use_container_width=True):
                        switch_page("analyse")
            else:
                st.warning("Sorry, the video has to be shorter than or equal to four hours.")

        else:
            st.warning("Invalid YouTube URL.")


if __name__ == "__main__":
    main()
