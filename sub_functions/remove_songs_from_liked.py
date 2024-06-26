from flask import Flask, redirect, request, session, render_template, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
import os

app = Flask(__name__)
app.secret_key = '123456789'  # Needed to keep the session secure
# Setup Spotipy with SpotifyOAuth integrated in routes
def create_spotify_oauth(): 
    return SpotifyOAuth(
        client_id= 'df2f85dcc82f4325959feb7814b59941',
        client_secret="fd825135281e4c71a4a695b6012e1bb0",
        redirect_uri='http://localhost:5000/callback',
        scope='playlist-read-private user-library-read user-library-modify',
        cache_handler=FlaskSessionCacheHandler(session),
        show_dialog=True,
        )

def get_all_liked_songs(sp):
    liked_tracks = {}
    results = sp.current_user_saved_tracks()
    while results:
        liked_tracks.update({item['track']['id']: item['track']['name'] for item in results['items']})
        if results['next']:
            results = sp.next(results)
        else:
            break
    return liked_tracks

def get_user_playlists(sp, user_id):
    user_playlists = {}
    all_tracks = {}
    playlists = sp.current_user_playlists()
    
    # Fetch all user playlists
    while playlists:
        for playlist in playlists['items']:
            if playlist['owner']['id'] == user_id:
                playlist_name = playlist['name']
                user_playlists[playlist_name] = []
                results = sp.playlist_tracks(playlist['id'])
                
                # Fetch all tracks for the current playlist
                while results:
                    for item in results['items']:
                        track_id = item['track']['id']
                        track_name = item['track']['name']
                        user_playlists[playlist_name].append(track_id)
                        all_tracks[track_id] = track_name
                    
                    if results['next']:
                        results = sp.next(results)
                    else:
                        break
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            break
    return all_tracks

@app.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('manage_tracks'))

@app.route('/manage_tracks')
def manage_tracks():
    try:
        sp = spotipy.Spotify(auth=session['token_info']['access_token'])
        user_id = sp.me()['id']
        liked_tracks = get_all_liked_songs(sp)
        playlist_tracks= get_user_playlists(sp, user_id)
        intersecting_tracks = {k: liked_tracks[k] for k in liked_tracks if k in playlist_tracks}
        return render_template('review_songs.html', intersecting_songs=intersecting_tracks, 
                               liked_songs=len(liked_tracks), 
                               total_intersections=len(intersecting_tracks), 
                               total_liked_playlist=len(playlist_tracks))
    except spotipy.exceptions.SpotifyException as e:
        return str(e)

@app.route('/confirm_deletion', methods=['POST'])
def confirm_deletion():
    try:
        sp = spotipy.Spotify(auth=session['token_info']['access_token'])
        tracks_to_remove = request.form.getlist('tracks_to_remove')
        removed_tracks = []

        if tracks_to_remove:
            removed_tracks = remove_tracks_individually(sp, tracks_to_remove)
            message = f"Successfully removed {len(removed_tracks)} songs."
        else:
            message = "No songs were selected for removal."

        return render_template('success.html', message=message, total_removed=len(removed_tracks))
    except spotipy.exceptions.SpotifyException as e:
        return str(e)

def remove_tracks_individually(sp, track_ids):
    successfully_removed = []
    for track_id in track_ids:
        try:
            sp.current_user_saved_tracks_delete([track_id])
            successfully_removed.append(track_id)
        except spotipy.exceptions.SpotifyException:
            continue
    return successfully_removed

if __name__ == '__main__':
    app.run(debug=True)
