from flask import render_template, flash, redirect, request, session, make_response, jsonify
from app import app
from app.functions import createStateKey, getToken, refreshToken, checkTokenStatus, getUserInformation, getAllTopTracks, getTopTracksID, getTopArtists, getRecommendedTracks, startPlayback, startPlaybackContext, pausePlayback, shuffle, getUserPlaylists, getUserDevices, skipTrack, getTrack, createPlaylist, addTracksPlaylist, searchSpotify
import time


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

		payload = getToken(code)
		if payload != None:
			session['token'] = payload[0]
			session['refresh_token'] = payload[1]
			session['token_expiration'] = time.time() + payload[2]

	current_user = getUserInformation(session)
	session['user'] = current_user['display_name']
	session['user_id'] = current_user['id']

	return redirect(session['previous_url'])


@app.route('/tracks',  methods=['GET', 'POST'])
def tracks():
	print("**** called tracks")

	if session.get('token') == None or session.get('token_expiration') == None:
		session['previous_url'] = '/tracks'
		# authorize()
		return redirect('/authorize')

	checkTokenStatus(session)

	track_ids = getAllTopTracks(session)
		
	return render_template('tracks.html', track_ids=track_ids)


@app.route('/create',  methods=['GET', 'POST'])
def create():
	print("**** called create")

	if session.get('token') == None or session.get('token_expiration') == None:
		session['previous_url'] = '/create'
		# authorize()
		return redirect('/authorize')

	checkTokenStatus(session)

	return render_template('create.html')


@app.route('/timer',  methods=['GET', 'POST'])
def timer():
	print("**** called timer")

	if session.get('token') == None or session.get('token_expiration') == None:
		session['previous_url'] = '/timer'
		# authorize()
		return redirect('/authorize')

	checkTokenStatus(session)

	device_names = getUserDevices(session)
	device_length = len(device_names)

	playlist_names = getUserPlaylists(session)
	playlist_length = len(playlist_names)

	return render_template('timer.html', playlist_names=playlist_names, playlist_length=playlist_length, device_names=device_names, device_length=device_length)


@app.route('/createTopPlaylist',  methods=['POST'])
def createTopPlaylist():
	print("**** called create top playlist")


	if 'short_term' in request.form:
		playlist_id = createPlaylist(session, request.form['short_term_name'])
		addTracksPlaylist(session, playlist_id, 'short_term')

	if 'medium_term' in request.form:
		playlist_id = createPlaylist(session, request.form['medium_term_name'])
		addTracksPlaylist(session, playlist_id, 'medium_term')

	if 'long_term' in request.form:
		playlist_id = createPlaylist(session, request.form['long_term_name'])
		addTracksPlaylist(session, playlist_id, 'long_term')

	auto_update = False
	if 'auto_update' in request.form:
		auto_update = True

	return "success"


@app.route('/intervalStart',  methods=['POST'])
def intervalStart():
	print("**** called interval start")

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

    print(results)
    return jsonify(matching_results=results[0])

###################

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

# @app.route('/playback/get')
# def playbackGet():
# 	current_playing = getTrack(session)
# 	return current_playing








# @app.route('/playback/previous')
# def playbackPrevious():
# 	previousTrack(session)
# 	return "previous"

###################
# @app.route('/save/favorite', methods=['POST'])
# def saveFavoritePlaylist():
# 	print(request.data)
# 	time_range = 'short_term'
# 	print("Time range ", time_range)
# 	# global sp
# 	# playlist_id = createPlaylist(sp, session['user'], "Top 25 Most Played", "Created by Discover Daily")
# 	# addTracksPlaylist(sp, session['user'], playlist_id)

# 	return "playlist created and filled"


