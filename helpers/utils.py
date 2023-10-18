import os
import re

import sys

from pytube import YouTube
from pytube import extract
import streamlit as st
import whisper
import torch
from youtube_transcript_api.formatters import SRTFormatter,TextFormatter
srt_formatter = SRTFormatter()
txt_formatter =TextFormatter()

SAMPLES = {
    "DALL·E 2 Explained by OpenAI": "https://www.youtube.com/watch?v=qTgPSKKjfVg",
    "Streamlit Shorts: How to make a select box by Streamlit": "https://www.youtube.com/watch?v=8-GavXeFlEA"
}

MAX_VIDEO_LENGTH = 240 * 60

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

from youtube_transcript_api import (
    YouTubeTranscriptApi, YouTubeRequestFailed, VideoUnavailable, InvalidVideoId, TooManyRequests,
    TranscriptsDisabled, NoTranscriptAvailable, NotTranslatable, TranslationLanguageNotAvailable,
    CookiePathInvalid, CookiesInvalid, FailedToCreateConsentCookie, NoTranscriptFound
)


def extract_video_id_from_url(url):
    try:
        return extract.video_id(url)
    except Exception:
        st.error("Please provide a valid YouTube URL.")
        st.stop()


def get_languages_auto_transcript_text(url):
    transcript_list = YouTubeTranscriptApi.list_transcripts(extract_video_id_from_url(url))
    language_codes = set()
    # iterate over all available transcripts
    for transcript in transcript_list:
        # the Transcript object provides metadata properties

        transcript.video_id,
        language_codes.add(transcript.language_code)

    return language_codes


def get_auto_transcript_text(url, language_code: str = 'en'):
    video_id = extract_video_id_from_url(url)
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language_code], preserve_formatting=True)
        return transcript
    except (
            YouTubeRequestFailed, VideoUnavailable, InvalidVideoId, TooManyRequests, NoTranscriptAvailable,
            NotTranslatable,
            TranslationLanguageNotAvailable, CookiePathInvalid, CookiesInvalid, FailedToCreateConsentCookie):
        st.error("An error occurred while fetching the transcript. Please try another video.")
        st.stop()
    except TranscriptsDisabled:
        st.error("Subtitles are disabled for this video. Please try another video.")
        st.stop()
    except NoTranscriptFound:
        st.error(
            "The video doesn't have English subtitles. Please ensure the video you're selecting is in English or has English subtitles available.")
        st.stop()
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}. Please try again.")
        st.stop()


def sample_to_url(option):
    return SAMPLES.get(option)


@st.cache_resource(show_spinner=False)
def load_whisper_model():
    model_size = "base"
    print("loading model :", model_size)
    model = whisper.load_model(model_size).to(DEVICE)
    print(model_size, "model loaded", DEVICE)
    return model


def valid_url(url):
    return re.search(r'((http(s)?:\/\/)?)(www\.)?((youtube\.com\/)|(youtu.be\/))[\S]+', url)


def get_video_duration_from_youtube_url(url):
    yt = YouTube(url)
    return yt.length


def is_subitles_available(url):
    yt = YouTube(url)
    caption = yt.captions
    # caption.xml_captions
    # srt_format = caption.xml_caption_to_srt(caption.xml_captions)
    print(caption)
    return caption


def is_translation_available(url):
    title, author, metadata, filename = get_youtube_video_info(url)

    return os.path.exists(f'output/{author}/{clean_filename(filename)}.txt') or os.path.exists(
        f'output/{author}/{clean_filename(filename)}.srt')


def get_translation_from_file(url, extension):
    title, author, metadata, filename = get_youtube_video_info(url)
    file_extension = "txt" if extension == "TXT (.txt)" else "srt"

    file_path = f'output/{author}/{clean_filename(filename)}.{file_extension}'
    print(file_path)
    try:
        with open(file_path, "r",encoding="utf-8") as file:
            data = file.read()
        return data
    except FileNotFoundError:
        # Handle the case where the file doesn't exist
        return None


def _get_audio_from_youtube_url(url):
    yt = YouTube(url)
    if not os.path.exists('../data'):
        os.makedirs('../data')
    yt.streams.filter(only_audio=True).first().download(filename=os.path.join('../data', 'audio.mp3'))


def _whisper_result_to_srt(result):
    text = []
    for i, s in enumerate(result['segments']):
        text.append(str(i + 1))

        time_start = s['start']
        hours, minutes, seconds = int(time_start / 3600), (time_start / 60) % 60, (time_start) % 60
        timestamp_start = "%02d:%02d:%06.3f" % (hours, minutes, seconds)
        timestamp_start = timestamp_start.replace('.', ',')
        time_end = s['end']
        hours, minutes, seconds = int(time_end / 3600), (time_end / 60) % 60, (time_end) % 60
        timestamp_end = "%02d:%02d:%06.3f" % (hours, minutes, seconds)
        timestamp_end = timestamp_end.replace('.', ',')
        text.append(timestamp_start + " --> " + timestamp_end)

        text.append(s['text'].strip() + "\n")

    return "\n".join(text)


def clean_filename(filename):
    # Define a set of allowed characters (letters, numbers, underscores, and hyphens)
    allowed_characters = "АБВГДЕЄЖЗИІЇКЛМНОПРСТУФХЦЧШЩЬЮЯабвгдежзиіїйклмнопрстуфхцчшщьюяABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"

    # Replace any characters that are not in the allowed set with underscores
    cleaned_filename = ''.join(c if c in allowed_characters else '_' for c in filename)

    return cleaned_filename


def get_youtube_video_info(url):
    yt = YouTube(url)
    title = yt.title
    author = yt.author
    metadata = yt.metadata
    desc = yt.description
    print('desc: ', desc)
    filename = f"{title}_{metadata}"
    return title, author, metadata, filename


def save_transcribe_result(url, result=None, auto_transcript=''):
    title, author, metadata, filename = get_youtube_video_info(url)

    if not os.path.exists(f'output/{author}'):
        os.makedirs(f'output/{author}')
    if result:
        txtFile = open(f'output/{author}/{clean_filename(filename)}.txt', mode="w", encoding="utf-8")
        txtFile.write(result['text'])
        srtFile = open(f'output/{author}/{clean_filename(filename)}.srt', mode="w", encoding="utf-8")
        srtFile.write(result['srt'])
        return "Result save in .txt and .srt format"
    txt_formatted = txt_formatter.format_transcript(auto_transcript)
    txtFile = open(f'output/{author}/{clean_filename(filename)}.txt', "w",encoding="utf-8")
    txtFile.write(txt_formatted)
    srt_formatted = srt_formatter.format_transcript(auto_transcript)
    with open(f'output/{author}/{clean_filename(filename)}.srt', 'w', encoding='utf-8') as srt_file:
        srt_file.write(srt_formatted)

    return "Result save in srt and .txt"


@st.cache_data(show_spinner=False, max_entries=1)
def transcribe_youtube_video(_model, url,language='en'):
    _get_audio_from_youtube_url(url)

    options = whisper.DecodingOptions(fp16=False, language=language)
    result = _model.transcribe(os.path.join('../data', 'audio.mp3'), **options.__dict__)
    result['srt'] = _whisper_result_to_srt(result)
    return result
