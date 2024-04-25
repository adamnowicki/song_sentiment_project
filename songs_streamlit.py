import streamlit as st
import pandas as pd
import lyricsgenius as lg
import re
from transformers import AutoTokenizer, AutoConfig
from scipy.special import softmax
import numpy as np
from transformers import AutoModelForSequenceClassification
from transformers import AutoTokenizer
import csv
import urllib.request
from gensim.parsing.preprocessing import remove_stopwords
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

CLIENT_ID = ""
CLIENT_SECRET = ""
client_access_token = ''


def main():

    LyricsGenius = lg.Genius(client_access_token)
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(CLIENT_ID, CLIENT_SECRET))
    
    st.title('Song Sentiment Analysis')
    st.sidebar.image('images/soundwave.png', use_column_width="always")
    st.sidebar.header("Search for your favorite song")
    url = "https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest#twitter-roberta-base-for-sentiment-analysis---updated-2022" 
    track_search = st.sidebar.text_input("Enter the title of your song", value="", max_chars=None, key=None, type="default", help=None, autocomplete=None, on_change=None, args=None, kwargs=None, placeholder=None, disabled=False, label_visibility="visible")
    artist_search = st.sidebar.text_input("Enter the name of the artist ", value="", max_chars=None, key=None, type="default", help=None, autocomplete=None, on_change=None, args=None, kwargs=None, placeholder=None, disabled=False, label_visibility="visible")
    st.sidebar.caption("Analyzer is using Twitter [RoBerta Base for Sentiment Analysis](%s) developed by CardiffNLP available on HuggingFace. This model is suitable for English language." %url)

    if track_search and artist_search:
        
        song = LyricsGenius.search_song(f"{artist_search},{track_search}")

        lyrics = song.lyrics   
    else:
        st.text("Error: Please provide song title and artist.")
        return[]
    def clean_text(text):

        text = text.replace('\n', ' ')
        text = re.sub(r'[,\.!?]', '', text)
        text = re.sub(r'\[.*?\]', ' ', text)
        text = re.sub(r'\w*\d\w*',' ', text)
        text = re.sub(r'[()]', ' ', text)
        text = text.lower()
        text = re.sub(r'\b(chorus|verse|intro)\b', '', text)
        return text
    
    lyrics_clean = clean_text(lyrics)
    lyrics_clean = remove_stopwords(lyrics_clean)
    

    MODEL = f"cardiffnlp/twitter-roberta-base-sentiment-latest"
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    config = AutoConfig.from_pretrained(MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL)

    encoded_input = tokenizer(lyrics_clean, return_tensors='pt', max_length=512, truncation=True, padding=True)
    output = model(**encoded_input)
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)

    ranking = np.argsort(scores)
    ranking = ranking[::-1]
    results = []
  
    for i in range(scores.shape[0]):
        l = config.id2label[ranking[i]]
        s = scores[ranking[i]]
        result=(f"{i+1}) {l} {np.round(float(s), 4)}")
        results.append(result)
    if artist_search and track_search:
        query = f'artist:{artist_search} track:{track_search}'
    elif track_search:
        query = track_search
    else:
        print("Error: Please provide at least a song name.")
        return []
    
    results2 = sp.search(q=query, limit=3)


    if results2['tracks']['items']:
        track = results2['tracks']['items'][0]  # Selecting the first track
        artists = ', '.join(artist['name'] for artist in track['artists'])
        song_name = track['name']
        track_id = track['id']
        st.subheader(f"Selected song: {artists} - {song_name}")
        st.write(f'<iframe src="https://open.spotify.com/embed/track/{track_id}?utm_source=generator" width="700" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>', unsafe_allow_html=True)
    else:
        st.sidebar.write("No results found for the given query.")

    st.subheader("Analysis Results:")
    
    for result in results:
        st.text(result)
    
    st.subheader("Lyrics")
    
    st.text(lyrics) 
if __name__ == '__main__':
    main()

