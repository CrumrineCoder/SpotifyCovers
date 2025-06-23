from flask import Flask, redirect, request, session, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth

import os
from dotenv import load_dotenv
load_dotenv()
SPOTIPY_CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.environ.get('SPOTIPY_REDIRECT_URI')

app = Flask(__name__)
app.secret_key = os.urandom(24)

SCOPE = 'user-library-read'

@app.route('/')
def index():
    return redirect("/login")

@app.route('/login')
def login():
    sp_oauth = SpotifyOAuth(
        SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope=SCOPE
    )
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    sp_oauth = SpotifyOAuth(
        SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope=SCOPE
    )
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('liked_songs'))

# http://127.0.0.1:5000/liked-songs?page=2
@app.route('/liked-songs')
def liked_songs():
    token_info = session.get('token_info', None)
    if not token_info:
        return redirect(url_for('login'))
    sp = spotipy.Spotify(auth=token_info['access_token'])
    page = int(request.args.get('page', 0))
    limit = 10
    offset = page * limit
    results = sp.current_user_saved_tracks(limit=limit, offset=offset)
    songs = [
        {
            'name': item['track']['name'],
            'artist': item['track']['artists'][0]['name']
        }
        for item in results['items']
    ]
    return {
        'liked_songs': songs,
        'page': page,
        'total': results['total'],
        'has_next': offset + limit < results['total'],
        'has_prev': page > 0
    }