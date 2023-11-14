import os
import re

import streamlit as st
import whisper
import torch
import shutil

from helpers.youtube_utils import get_youtube_video_info, txt_formatter, srt_formatter, _get_audio_from_youtube_url, \
    get_auto_transcript_text, get_youtube_playlist_links

SAMPLES = {
    "DALL·E 2 Explained by OpenAI": "https://www.youtube.com/watch?v=qTgPSKKjfVg",
    "Streamlit Shorts: How to make a select box by Streamlit": "https://www.youtube.com/watch?v=8-GavXeFlEA"
}

MAX_VIDEO_LENGTH = 240 * 60

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


@st.cache_resource(show_spinner=False)
def load_whisper_model():
    model_size = "base"
    print("loading model :", model_size)
    model = whisper.load_model(model_size).to(DEVICE)
    print(model_size, "model loaded", DEVICE)
    return model


def valid_url(url):
    return re.search(r'((http(s)?:\/\/)?)(www\.)?((youtube\.com\/)|(youtu.be\/))[\S]+', url)


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

import os
import zipfile


@st.cache_data(show_spinner=True, max_entries=1)
def playlist_transcript_arc(playlist,language):
    links = get_youtube_playlist_links(playlist)

    title, author, metadata, filename = get_youtube_video_info(links[0])
    if os.path.isfile(f'zipfiles/playlist_{author + title}.zip'):
        print("exist")
        return f'zipfiles/playlist_{author + title}.zip'

    print("start playlist transcript")
    for url in links:
        if not is_translation_available(url):
            try:
                transcript = get_auto_transcript_text(url, language)
                save_transcribe_result(url, auto_transcript=transcript)
            except:
                print(f"Someting go wrong with {url}")
    path_to_dir = f'output/{author}'
    output_filename = f'zipfiles/playlist_{author + title}'

    shutil.make_archive(output_filename, 'zip', f'output/{author}')
    print("zip created")
    return output_filename


def clean_filename(filename):
    # Define a set of allowed characters (letters, numbers, underscores, and hyphens)
    allowed_characters = "АБВГДЕЄЖЗИІЇКЛМНОПРСТУФХЦЧШЩЬЮЯабвгдежзиіїйклмнопрстуфхцчшщьюяABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"

    # Replace any characters that are not in the allowed set with underscores
    cleaned_filename = ''.join(c if c in allowed_characters else '_' for c in filename)

    return cleaned_filename


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
