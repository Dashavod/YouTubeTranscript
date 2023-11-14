import os
import re
from pytube import YouTube
from pytube import extract
import streamlit as st
from youtube_transcript_api.formatters import SRTFormatter,TextFormatter
from pytube import Playlist

srt_formatter = SRTFormatter()
txt_formatter =TextFormatter()
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





def check_youtube_url(url):
    video_pattern = re.compile(r'^(https?://)?(www\.)?youtube\.(com|nl)/watch\?v=[\w-]+(&\S+)?$')
    playlist_pattern = re.compile(r'^(https?://)?(www\.)?youtube\.(com|nl)/playlist\?list=[\w-]+(&\S+)?$')

    if video_pattern.match(url):
        return "video"
    elif playlist_pattern.match(url):
        return "playlist"
    else:
        return False


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


def _get_audio_from_youtube_url(url):
    yt = YouTube(url)
    if not os.path.exists('../data'):
        os.makedirs('../data')
    yt.streams.filter(only_audio=True).first().download(filename=os.path.join('../data', 'audio.mp3'))




def get_youtube_video_info(url):
    yt = YouTube(url)
    title = yt.title
    author = yt.author
    metadata = yt.metadata
    filename = f"{title}_{metadata}"
    return title, author, metadata, filename

def get_youtube_playlist_links(url):
    p = Playlist(url)
    for url in p.video_urls:
        print(url)
    return p.video_urls