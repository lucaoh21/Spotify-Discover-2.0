from flask import render_template, flash, redirect, request, session, make_response, jsonify, abort
from app import app
from app.functions import createStateKey, getToken, refreshToken, checkTokenStatus, getUserInformation, getAllTopTracks, getTopTracksID, getTopTracksURI, getTopArtists, getRecommendedTracks, startPlayback, startPlaybackContext, pausePlayback, shuffle, getUserPlaylists, getUserDevices, skipTrack, getTrack, createPlaylist, addTracksPlaylist, searchSpotify
from app.models import addUser

import time


@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')


@app.route('/authorize')
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


@app.route('/callback')
def callback():
	if request.args.get('state') != session['state_key']:
		return render_template('index.html', error='State failed.')
	if request.args.get('error'):
		return render_template('index.html', error='Spotify error.')
	else:
		code = request.args.get('code')
		session.pop('state_key', None)

		payload = getToken(code)
		if payload != None:
			session['token'] = payload[0]
			session['refresh_token'] = payload[1]
			session['token_expiration'] = time.time() + payload[2]
		else:
			return render_template('index.html', error='Failed to access token.')

	current_user = getUserInformation(session)
	session['user_id'] = current_user['id']

	return redirect(session['previous_url'])


@app.route('/information',  methods=['GET'])
def information():
	return render_template('information.html')


@app.route('/tracks',  methods=['GET'])
def tracks():
	if session.get('token') == None or session.get('token_expiration') == None:
		session['previous_url'] = '/tracks'
		# authorize()
		return redirect('/authorize')

	if session.get('user_id') == None:
		current_user = getUserInformation(session)
		session['user_id'] = current_user['id']

	track_ids = getAllTopTracks(session)

	if track_ids == None:
		return render_template('index.html', error='Failed to gather top tracks.')
		
	return render_template('tracks.html', track_ids=track_ids)


@app.route('/create',  methods=['GET'])
def create():
	if session.get('token') == None or session.get('token_expiration') == None:
		session['previous_url'] = '/create'
		# authorize()
		return redirect('/authorize')

	if session.get('user_id') == None:
		current_user = getUserInformation(session)
		session['user_id'] = current_user['id']

	return render_template('create.html')


@app.route('/timer',  methods=['GET'])
def timer():
	if session.get('token') == None or session.get('token_expiration') == None:
		session['previous_url'] = '/timer'
		# authorize()
		return redirect('/authorize')

	if session.get('user_id') == None:
		current_user = getUserInformation(session)
		session['user_id'] = current_user['id']

	device_names = getUserDevices(session)
	playlist_names = getUserPlaylists(session)

	if device_names == None or playlist_names == None:
		return render_template('index.html', error='Failed to get device ID and playlists.')

	device_length = len(device_names)
	playlist_length = len(playlist_names)

	return render_template('timer.html', playlist_names=playlist_names, playlist_length=playlist_length, device_names=device_names, device_length=device_length)


@app.route('/tracks/topplaylist',  methods=['POST'])
def createTopPlaylist():

	playlist_id_short = None
	playlist_id_medium = None
	playlist_id_long = None
	playlist_uri = ''

	if 'short_term' in request.form:
		playlist_id_short, playlist_uri = createPlaylist(session, request.form['short_term_name'])
		uri_list = getTopTracksURI(session, 'short_term', 50)
		addTracksPlaylist(session, playlist_id_short, uri_list)

	if 'medium_term' in request.form:
		playlist_id_medium, playlist_uri =  createPlaylist(session, request.form['medium_term_name'])
		uri_list = getTopTracksURI(session, 'medium_term', 50)
		addTracksPlaylist(session, playlist_id_medium, uri_list)

	if 'long_term' in request.form:
		playlist_id_long, playlist_uri = createPlaylist(session, request.form['long_term_name'])
		uri_list = getTopTracksURI(session, 'long_term', 50)
		addTracksPlaylist(session, playlist_id_long, uri_list)

	if 'auto_update' in request.form:
		addUser(session['user_id'], session['refresh_token'], playlist_id_short=playlist_id_short, playlist_id_medium=playlist_id_medium, playlist_id_long=playlist_id_long)

	return playlist_uri


@app.route('/create/playlist',  methods=['POST'])
def createSelectedPlaylist():
	search = []
	for i in range(0, 5):
		if str(i) in request.form:
			search.append(request.form[str(i)])
		else:
			break

	tuneable_dict = {}

	acoustic = 0
	if 'acoustic_level' in request.form:
		# acoustic = request.form['slider_acoustic']
		tuneable_dict.update({'acoustic': request.form['slider_acoustic']})


	danceability = 0
	if 'danceability_level' in request.form:
		# danceability = request.form['slider_danceability']
		tuneable_dict.update({'danceability': request.form['slider_danceability']})


	energy = 0
	if 'energy_level' in request.form:
		# energy = request.form['slider_energy']
		tuneable_dict.update({'energy': request.form['slider_energy']})


	popularity = 0
	if 'popularity_level' in request.form:
		# popularity = request.form['slider_popularity']
		tuneable_dict.update({'popularity': request.form['slider_popularity']})


	valence = 0
	if 'valence_level' in request.form:
		# valence = request.form['slider_valence']
		tuneable_dict.update({'valence': request.form['slider_valence']})


	limit = 10
	playlist_id, playlist_uri = createPlaylist(session, request.form['playlist_name'])
	uri_list = getRecommendedTracks(session, search, tuneable_dict)
	addTracksPlaylist(session, playlist_id, uri_list)

	return playlist_uri


@app.route('/timer/start',  methods=['POST'])
def intervalStart():
	playlist = request.form['playlist']
	session['device'] = request.form['device']

	is_shuffle = False
	if 'shuffle' in request.form:
		is_shuffle = True

	shuffle(session, session['device'], is_shuffle)
	startPlaybackContext(session, playlist, session['device'])

	current_playing = getTrack(session)
	return jsonify(current_playing)


@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    search = request.args.get('q')
    results = searchSpotify(session, search)

    return jsonify(matching_results=results)


@app.route('/playback/skip')
def playbackSkip():
	skipTrack(session)
	current_playing = getTrack(session)
	return jsonify(current_playing)


@app.route('/playback/pause')
def playbackPause():
	pausePlayback(session)
	return "success"


@app.route('/playback/resume')
def playbackResume():
	startPlayback(session, session['device'])

	current_playing = getTrack(session)
	return jsonify(current_playing)

