from flask import render_template, flash, redirect, request, session, make_response
from app import app
from app.functions import createStateKey, getToken, refreshToken, getUserInformation, getTopTracks2, getRecommendedTracks, startPlayback, pausePlayback, previousTrack, skipTrack, getUserDevices, createPlaylist, addTracksPlaylist, getTopTracks, searchSpotify
from app.forms import PlaylistForm
import spotipy
import spotipy.util as util
import time

sp = None

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html', title='Welcome')

# @app.route('/authorize', methods=['GET', 'POST'])
@app.route('/authorize')
def authorize():
	print("**** called authorize")

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


@app.route('/callback')
def callback():
	print("**** called callback")
	# state = request.args.get('state')
	# code = request.args.get('code')

	if request.args.get('state') != session['state_key']:
		print("failed state")
		return
	if request.args.get('error'):
		print("ran into error")
		return request.args.get('error')
	# elif state == None or state != session['state_key']:
	# 	print("failed state")
	# 	return
	else:
		code = request.args.get('code')
		session.pop('state_key', None)

		token, refresh_token, expiration_time = getToken(code)
		session['token'] = token
		session['refresh_token'] = refresh_token
		session['token_expiration'] = time.time() + expiration_time

	return redirect('/tracks')


@app.route('/tracks',  methods=['GET', 'POST'])
def tracks():
	print("**** called tracks")

	if session.get('token') == None or session.get('token_expiration') == None:
		# authorize()
		return redirect('/authorize')

	if time.time() > session['token_expiration']:
		refreshToken(session['refresh_token'])
	else:
		print("Time okay")
		print(session['token_expiration'])

	global sp
	if sp == None:
		sp = spotipy.Spotify(auth=session['token'])


	current_user = getUserInformation(sp)
	session['user'] = current_user['display_name']
	session['user_location'] = current_user['country']

	track_ids = getTopTracks2(sp)
	rec_track_ids = getRecommendedTracks(sp)

	searchSpotify(sp)
	playlist_form = PlaylistForm()

	if playlist_form.validate_on_submit():
		time_range = ""
		if playlist_form.short_term.data:
			time_range = "short_term"
		elif playlist_form.medium_term.data:
			time_range = "medium_term"
		else:
			time_range = "long_term"
		playlist_id = createPlaylist(sp, session['user'], playlist_form.playlist_name.data, "Created by Discover Daily")
		addTracksPlaylist(sp, session['user'], playlist_id, time_range)
		return redirect('/tracks')
		
	return render_template('tracks.html', user=session['user'], track_ids=track_ids, rec_track_ids=rec_track_ids, form=playlist_form)


@app.route('/create',  methods=['GET', 'POST'])
def create():

	return render_template('create.html', user=session['user'])



###################

@app.route('/playback/start')
def playbackStart():
	global sp
	startPlayback(sp)
	return "start"

@app.route('/playback/pause')
def playbackPause():
	global sp
	pausePlayback(sp)
	return "pause"

@app.route('/playback/skip')
def playbackSkip():
	global sp
	skipTrack(sp)
	return "skip"

@app.route('/playback/previous')
def playbackPrevious():
	global sp
	previousTrack(sp)
	return "previous"

###################
@app.route('/save/favorite', methods=['POST'])
def saveFavoritePlaylist():
	print(request.data)
	time_range = 'short_term'
	print("Time range ", time_range)
	# global sp
	# playlist_id = createPlaylist(sp, session['user'], "Top 25 Most Played", "Created by Discover Daily")
	# addTracksPlaylist(sp, session['user'], playlist_id)

	return "playlist created and filled"


