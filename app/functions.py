from flask import render_template, redirect, request
from app import app
import config
import base64
import os
import random as rand
import string as string
import requests
import spotipy
import spotipy.util as util
import time

# AUTHENTICATION

def createStateKey(size):
	#https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits
	return ''.join(rand.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(size))


def getToken(code):
	print("**** called get token")
	token_url = 'https://accounts.spotify.com/api/token'
	authorization = app.config['AUTHORIZATION']
	redirect_uri = app.config['REDIRECT_URI']

	headers = {'Authorization': authorization, 'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
	body = {'code': code, 'redirect_uri': redirect_uri, 'grant_type': 'authorization_code'}
	post_response = requests.post(token_url, headers=headers, data=body)

	try:
		return post_response.json()['access_token'], post_response.json()['refresh_token'], post_response.json()['expires_in']
	except ValueError:
		print('JSON decoding failed')
		return None


def refreshToken(refresh_token):
	print("**** called refresh token")
	token_url = 'https://accounts.spotify.com/api/token'
	authorization = app.config['AUTHORIZATION']

	headers = {'Authorization': authorization, 'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
	body = {'refresh_token': refresh_token, 'grant_type': 'refresh_token'}
	post_response = requests.post(token_url, headers=headers, data=body)

	try:
		print("refresh expires: ", post_response.json()['expires_in'])
		return post_response.json()['access_token'], post_response.json()['expires_in']
	except ValueError:
		print('***********************************')
		print('JSON decoding failed')
		print('***********************************')
		return None


def checkTokenStatus(session):

	if time.time() > session['token_expiration']:
		print("getting new token with refresh")
		payload = refreshToken(session['refresh_token'])
		if payload != None:
			session['token'] = payload[0]
			session['token_expiration'] = time.time() + payload[1]
		else:
			print("******Problem 45********")

	# else:
	# 	print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
	# 	print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(session['token_expiration'])))
	# 	print("token up to date")
	return None


# MAKE REQUESTS

def makeGetRequest(session, url, params={}):
	headers = {"Authorization": "Bearer {}".format(session['token'])}
	response = requests.get(url, headers=headers, params=params)

	if response.status_code == 200:
		return response.json()
	elif response.status_code == 401:
		checkTokenStatus(session)
		return makeGetRequest(session, url, params)
	else:
		print('ERROR:', response)
    
	return None


def makePutRequest(session, url, params={}, data={}):
	headers = {"Authorization": "Bearer {}".format(session['token']), 'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
	response = requests.put(url, headers=headers, params=params, data=data)

	if response.status_code == 204:
		return response
	elif response.status_code == 401:
		checkTokenStatus(session)
		return makePutRequest(session, url, data)
	else:
		print('ERROR:', response)

	return None

def makePostRequest(session, url, data):

	headers = {"Authorization": "Bearer {}".format(session['token']), 'Accept': 'application/json', 'Content-Type': 'application/json'}
	response = requests.post(url, headers=headers, data=data)

	if response.status_code == 204:
		return response
	if response.status_code == 201:
		return response.json()
	elif response.status_code == 401:
		checkTokenStatus(session)
		return makePostRequest(session, url, data)
	else:
		print('ERROR:', response)

	return None

# PERSONAL USER INFORMATION

def getUserInformation(session):
	url = 'https://api.spotify.com/v1/me'
	payload = makeGetRequest(session, url)

	return payload


def getAllTopTracks(session):
	url = 'https://api.spotify.com/v1/me/top/tracks'
	track_ids = []
	time_range = ['short_term', 'medium_term', 'long_term']

	for time in time_range:
		track_range_ids = []

		params = {'limit': 5, 'time_range': time}
		payload = makeGetRequest(session, url, params)

		for track in payload['items']:
			track_range_ids.append(track['id'])
		track_ids.append(track_range_ids)

	return track_ids


def getTopTracksID(session, time, limit=25):
	url = 'https://api.spotify.com/v1/me/top/tracks'
	params = {'limit': limit, 'time_range': time}
	payload = makeGetRequest(session, url, params)

	track_ids = []
	for track in payload['items']:
		track_ids.append(track['id'])

	return track_ids

def getTopTracksURI(session, time, limit=25):
	url = 'https://api.spotify.com/v1/me/top/tracks'
	params = {'limit': limit, 'time_range': time}
	payload = makeGetRequest(session, url, params)

	track_uri = []
	for track in payload['items']:
		track_uri.append(track['uri'])

	return track_uri


def getTopArtists(session, time, limit=10):
	url = 'https://api.spotify.com/v1/me/top/artists'
	params = {'limit': limit, 'time_range': time}
	payload = makeGetRequest(session, url, params)

	artist_ids = []
	for artist in payload['items']:
		artist_ids.append(artist['id'])

	return artist_ids


def getRecommendedTracks(session, time='short_term', limit=10):
	track_ids = getTopTracksID(session, time, 2)
	artist_ids = getTopArtists(session, time, 3)

	url = 'https://api.spotify.com/v1/recommendations'
	params = {'limit': limit, 'seed_tracks': track_ids, 'seed_artists': artist_ids}
	payload = makeGetRequest(session, url, params)

	rec_track_ids = []
	
	for track in payload['tracks']:
		rec_track_ids.append(track['id'])

	return rec_track_ids


def getUserPlaylists(session, limit=20):
	url = 'https://api.spotify.com/v1/me/playlists'
	offset = 0
	playlist = []

	total = 1
	while total > offset:
		params = {'limit': limit, 'offset': offset}
		payload = makeGetRequest(session, url, params)
		
		for item in payload['items']:
			playlist.append([item['name'], item['uri']])

		total = payload['total']
		offset += limit

	return playlist


# PLAYBACK

def getUserDevices(session):
	url = 'https://api.spotify.com/v1/me/player/devices'
	payload = makeGetRequest(session, url)

	device_list = []
	for device in payload['devices']:
		if device['is_restricted'] != True:
			device_list.append([device['name'], device['id']])
	return device_list


def startPlayback(session, device):
	url = 'https://api.spotify.com/v1/me/player/play'
	params = {'device_id': device}
	makePutRequest(session, url, params)


def startPlaybackContext(session, playlist, device):
	url = 'https://api.spotify.com/v1/me/player/play'
	params = {'device_id': device}
	data = "{\"context_uri\":\"" + playlist + "\",\"offset\":{\"position\":0},\"position_ms\":0}"
	makePutRequest(session, url, params, data)


def pausePlayback(session):
	url = 'https://api.spotify.com/v1/me/player/pause'
	makePutRequest(session, url)


def shuffle(session, device, is_shuffle=True):
	url = 'https://api.spotify.com/v1/me/player/shuffle'
	params = {'state': is_shuffle, 'device_id': device}
	makePutRequest(session, url, params)


def skipTrack(session):
	url = 'https://api.spotify.com/v1/me/player/next'

	data = {}
	makePostRequest(session, url, data)


def getTrack(session):
	url = 'https://api.spotify.com/v1/me/player/currently-playing'
	payload = makeGetRequest(session, url)

	name = payload['item']['name']
	img = payload['item']['album']['images'][0]['url']

	return {'name': name, 'img': img}


def createPlaylist(session, playlist_name):
	url = 'https://api.spotify.com/v1/users/' + session['user_id'] + '/playlists'
	data = "{\"name\":\"" + playlist_name + "\",\"description\":\"Created by Discover Daily\"}"

	payload = makePostRequest(session, url, data)
	return payload['id']


def addTracksPlaylist(session, playlist_id, time_range):
	url = 'https://api.spotify.com/v1/playlists/' + playlist_id + '/tracks'

	uri_list = getTopTracksURI(session, time_range, 50)
	uri_str = ""
	for uri in uri_list:
		uri_str += "\"" + uri + "\","

	data = "{\"uris\": [" + uri_str[0:-1] + "]}"
	makePostRequest(session, url, data)


def searchSpotify(session, search, limit=1):
	url = 'https://api.spotify.com/v1/search'

	params = {'limit': limit, 'q': search + "*", 'type': 'artist,track'}
	payload = makeGetRequest(session, url, params)

	results = []
	for item in payload['artists']['items']:
		results.append([item['name'], item['id']])

	for item in payload['tracks']['items']:
		full_name = item['name'] + " - "
		for artist in item['artists']:
			full_name += artist['name'] + ", "

		results.append([full_name[0:-2], item['id']])

	return results

	# artists = sp.search('Kany*', limit=5, offset=0, type='artist', market=None)
	# for item in artists['artists']['items']:
		# print(item['name'])

	# tracks = sp.search('heartl*', limit=5, offset=0, type='track', market=None)
	# for item in tracks['tracks']['items']:
		# print(item['name'])




# 	if playback == None:
# 		print("No pausing playback was found")
# 		return
# 	else:
# 		if playback['is_playing']:
# 			sp.pause_playback(playback['device']['id'])
# 			print("Playback paused")
# 		return