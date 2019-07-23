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

def createStateKey(size):
	#https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits
	return ''.join(rand.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(size))


def getToken(code):
	token_url = 'https://accounts.spotify.com/api/token'
	authorization = app.config['AUTHORIZATION']
	redirect_uri = app.config['REDIRECT_URI']

	headers = {'Authorization': authorization, 'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
	body = {'code': code, 'redirect_uri': redirect_uri, 'grant_type': 'authorization_code'}
	post_response = requests.post(token_url, headers=headers, data=body)

	try:
		return post_response.json()['access_token']
	except ValueError:
		print('JSON decoding failed')
		return 'value error'


def getUserInformation(sp):
	return sp.current_user()


def getTopTracks(sp):
	track_ids = []
	time_range = ['short_term', 'medium_term', 'long_term']
	for time in time_range:
		track_range_ids = []
		tracks = sp.current_user_top_tracks(limit=5, time_range=time)

		for track in tracks['items']:
			track_range_ids.append(track['id'])
		track_ids.append(track_range_ids)

	return track_ids


def getRecommendedTracks(sp):
	tracks = sp.current_user_top_tracks(limit=2, time_range='short_term')
	artists = sp.current_user_top_artists(limit=3, time_range='short_term')
	track_uri = []
	artist_uri = []
	
	for track in tracks['items']:
		track_uri.append(track['uri'])
	for artist in artists['items']:
		artist_uri.append(artist['uri'])

	recommended = sp.recommendations(seed_artists=artist_uri, seed_tracks=track_uri, limit=10)
	rec_track_ids = []
	
	for track in recommended['tracks']:
		rec_track_ids.append(track['id'])

	return rec_track_ids


def pausePlayback(sp):
	playback = sp.current_playback()

	if playback == None:
		print("No pausing playback was found")
		return
	else:
		if playback['is_playing']:
			sp.pause_playback(playback['device']['id'])
			print("Playback paused")
		return


def startPlayback(sp):
	playback = sp.current_playback()

	print("Playback: " + playback['item']['name'])

	if playback == None:
		print("No starting playback was found")
		return
	else:
		if playback['is_playing']:
			print(playback['device']['id'])
			sp.start_playback(playback['device']['id'])
			print("Playback started")
		return


def currentPlaybackDevice(sp):
	playback = sp.current_playback()

	if playback == None:
		print("No starting playback was found")
		return
	else:
		print(playback['device']['id'])
		return playback['device']['id']


def skipTrack(sp):
	sp.next_track()
	return


def previousTrack(sp):
	sp.previous_track()


def getUserDevices(sp):
	devices = sp.devices()
	device_list = []
	for device in devices['devices']:
		device_list.append([device['id'], device['name'], device['type']])
	return device_list

