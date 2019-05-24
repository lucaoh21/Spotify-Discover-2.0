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
