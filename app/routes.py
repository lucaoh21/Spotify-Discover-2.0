from flask import render_template, flash, redirect
from app import app
from app.forms import LoginForm
import spotipy
import spotipy.util as util


@app.route('/')
@app.route('/index')
def index():
	songs = [
        {
            'artist': 'Kygo',
            'track': 'Oasis'
        },
        {
            'artist': 'Kanye West',
            'track': 'Homecoming'
        }
    ]
	return render_template('index.html', title='Welcome', songs=songs)

@app.route('/tracks')
def tracks():
	clientID = 'your_password'
	clientSecret = 'your_password'
	redirectURI = 'https://localhost:8080/'
	scope = 'user-library-read user-modify-playback-state user-read-currently-playing user-read-playback-state user-top-read'
	username = 'lucaoh21'

	token = util.prompt_for_user_token(username, scope, clientID, clientSecret, redirectURI)

	if token:
		sp = spotipy.Spotify(auth=token)

		tracks = sp.current_user_top_tracks(limit=5, time_range='medium_term')
		track_list = []
		for track in tracks['items']:
			track_list.append(track['name'])
	return render_template('tracks.html', title='Top Tracks', track_list=track_list)


@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
		return redirect(url_for('index'))
	return render_template('login.html', title='Sign In', form=form)


# @app.route('/authorize', methods=['GET', 'POST'])
# def authorize():


