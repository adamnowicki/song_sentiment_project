import streamlit as st
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pickle

import sklearn
import time

import os
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


def main():
    st.title(':dog2: Parkies Recommendations :dog2:')
  
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(CLIENT_ID, CLIENT_SECRET))
    st.sidebar.header("Search for your favorite song")
    
    track_search = st.sidebar.text_input("Enter the title of your song", value="", max_chars=None, key=None, type="default", help=None, autocomplete=None, on_change=None, args=None, kwargs=None, placeholder=None, disabled=False, label_visibility="visible")
    artist_search = st.sidebar.text_input("Enter the name of the artist (optional)", value="", max_chars=None, key=None, type="default", help=None, autocomplete=None, on_change=None, args=None, kwargs=None, placeholder=None, disabled=False, label_visibility="visible")

    if artist_search and track_search:
        query = f'artist:{artist_search} track:{track_search}'
    elif track_search:
        query = track_search
    else:
        print("Error: Please provide at least a song name.")
        return []
    results = sp.search(q=query, limit=3)


if __name__ == '__main__':
    main()