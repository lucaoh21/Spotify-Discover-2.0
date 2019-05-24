from flask import render_template, flash, redirect, request, session, make_response
from app import app
from app.forms import LoginForm
from app.functions import createStateKey, getToken, getUserInformation, getTopTracks, getRecommendedTracks
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

	sp = spotipy.Spotify(auth=session['token'])

	current_user = getUserInformation(sp)
	session['user'] = current_user['display_name']
	session['user_location'] = current_user['country']

	track_ids = getTopTracks(sp)
	rec_track_ids = getRecommendedTracks(sp)
		
	return render_template('tracks.html', user=session['user'], track_ids=track_ids, rec_track_ids=rec_track_ids)

@app.route('/callback')
def callback():
	
	state = request.args.get('state')
	code = request.args.get('code')

	if request.args.get('error'):
		print("ran into error")
		return request.args.get('error')
	elif state == None or state != session['state_key']:
		print("failed state")
		return
	else:
		session.pop('state_key', None)

		token = getToken(code)
		session['token'] = token

	return redirect('/tracks')

@app.route('/authorize', methods=['GET', 'POST'])
def authorize():
	client_id = app.config['CLIENT_ID']
	client_secret = app.config['CLIENT_SECRET']
	redirect_uri = app.config['REDIRECT_URI']
	scope = app.config['SCOPE']

	state_key = createStateKey(15)
	session['state_key'] = state_key

	authorize_url = 'https://accounts.spotify.com/en/authorize?'
	parameters = 'response_type=code&client_id=' + client_id + '&redirect_uri=' + redirect_uri + '&scope=' + scope + '&state=' + state_key

	response = make_response(redirect(authorize_url + parameters))
	return response




