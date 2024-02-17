import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os #noqa

app = Flask(__name__, static_url_path='/static')
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/app')
def app_page():
    return render_template('app.html')

CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')

# Initialize Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

@app.route('/get_recommendations', methods=['GET'])
def get_recommendations():
    seed_name = request.args.get('seed_name')
    if not seed_name:
        return jsonify({'error': 'Missing seed_name parameter'}), 400
    
    try:
        seed_name_lower = seed_name.lower()

        # Search for the seed song or artist
        results = sp.search(q=seed_name_lower, type="track,artist", limit=1)

        if results and results["tracks"]["items"]:
            seed_artist = results["tracks"]["items"][0]["artists"][0]["name"]
            seed_song = results["tracks"]["items"][0]["name"]

            # Get recommendations based on the seed artist or song
            recommendations = sp.recommendations(seed_tracks=[results["tracks"]["items"][0]["id"]], limit=8)

            recommended_music_names = []
            recommended_music_posters = []
            recommended_audio_urls = []

            for track in recommendations["tracks"]:
                name = track["name"]
                poster_url = track["album"]["images"][0]["url"]
                audio_url = track["preview_url"]

                # Check if both poster_url and audio_url are available
                if poster_url and audio_url:
                    recommended_music_names.append(name)
                    recommended_music_posters.append(poster_url)
                    recommended_audio_urls.append(audio_url)

            return jsonify({
                'seed_song': seed_song,
                'seed_artist': seed_artist,
                'recommended_music_names': recommended_music_names,
                'recommended_music_posters': recommended_music_posters,
                'recommended_audio_urls': recommended_audio_urls
            })
    except Exception as e:
        return jsonify({'Error': f'Error fetching recommendations: {str(e)}'}), 500
    
if __name__=='__main__':
    app.run(debug=True, host='localhost', port='5000')